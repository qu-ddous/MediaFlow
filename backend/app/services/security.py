"""Security utilities — SSRF protection, filename sanitization, file validation."""

from __future__ import annotations

import ipaddress
import logging
import mimetypes
import re
import socket
from pathlib import PurePosixPath
from urllib.parse import urlparse

from app.config import settings

logger = logging.getLogger(__name__)

# ── Magic-byte signatures for common media files ──────────────────────────
_MAGIC_SIGNATURES: dict[str, list[bytes]] = {
    ".mp4": [b"\x00\x00\x00\x18ftypmp4", b"\x00\x00\x00\x1cftypmp4", b"\x00\x00\x00\x20ftypisom", b"\x00\x00\x00"],
    ".mkv": [b"\x1a\x45\xdf\xa3"],
    ".webm": [b"\x1a\x45\xdf\xa3"],
    ".avi": [b"RIFF"],
    ".mov": [b"\x00\x00\x00\x14ftypqt", b"\x00\x00\x00\x08wide", b"moov", b"\x00\x00\x00"],
    ".flv": [b"FLV"],
    ".wmv": [b"\x30\x26\xb2\x75"],
    ".mp3": [b"\xff\xfb", b"\xff\xf3", b"\xff\xf2", b"ID3"],
    ".aac": [b"\xff\xf1", b"\xff\xf9"],
    ".flac": [b"fLaC"],
    ".wav": [b"RIFF"],
    ".ogg": [b"OggS"],
    ".opus": [b"OggS"],
    ".m4a": [b"\x00\x00\x00\x20ftypM4A", b"\x00\x00\x00"],
    ".jpg": [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".png": [b"\x89PNG"],
    ".gif": [b"GIF87a", b"GIF89a"],
    ".webp": [b"RIFF"],
    ".bmp": [b"BM"],
}

# ── Private / reserved IP ranges ──────────────────────────────────────────
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
]


class SecurityError(Exception):
    """Raised when a security check fails."""

    def __init__(self, message: str, code: str = "security_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


# ── URL Validation ────────────────────────────────────────────────────────


def validate_url(url: str) -> str:
    """Validate a URL: scheme, length, parsability. Returns the normalised URL.

    Raises SecurityError for invalid or disallowed URLs.
    """
    if not url or not url.strip():
        raise SecurityError("URL must not be empty", "empty_url")

    url = url.strip()

    if len(url) > settings.max_url_length:
        raise SecurityError(
            f"URL exceeds maximum length of {settings.max_url_length} characters",
            "url_too_long",
        )

    parsed = urlparse(url)

    if parsed.scheme not in settings.allowed_schemes:
        raise SecurityError(
            f"URL scheme '{parsed.scheme}' is not allowed. Use http or https.",
            "invalid_scheme",
        )

    if not parsed.hostname:
        raise SecurityError("URL must have a valid hostname", "no_hostname")

    # Block user:password@ in URLs
    if parsed.username or parsed.password:
        raise SecurityError("URLs with embedded credentials are not allowed", "credentials_in_url")

    return url


def _is_ip_blocked(ip_str: str) -> bool:
    """Return True if the IP address falls into any blocked range."""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # unparsable → block

    for network in _BLOCKED_NETWORKS:
        if addr in network:
            return True
    return False


def resolve_and_validate_ip(hostname: str) -> str:
    """DNS-resolve *hostname* and ensure it doesn't point to a private IP.

    Returns the resolved IP on success.
    Raises SecurityError when the IP is private / loopback / link-local.
    """
    try:
        results = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise SecurityError(f"DNS resolution failed for '{hostname}': {exc}", "dns_failure")

    if not results:
        raise SecurityError(f"No DNS results for '{hostname}'", "dns_failure")

    for family, _type, _proto, _canonname, sockaddr in results:
        ip_str = sockaddr[0]
        if _is_ip_blocked(ip_str):
            logger.warning("Blocked SSRF attempt: %s resolved to %s", hostname, ip_str)
            raise SecurityError(
                f"Access to private/reserved IP address ({ip_str}) is not allowed",
                "ssrf_blocked",
            )

    # Return the first resolved IP for logging purposes
    return results[0][4][0]


def check_redirect_safety(url: str) -> str:
    """Validate that a redirect destination is also safe.

    Runs the same checks as validate_url + resolve_and_validate_ip.
    """
    validated = validate_url(url)
    hostname = urlparse(validated).hostname
    if hostname:
        resolve_and_validate_ip(hostname)
    return validated


# ── Filename Sanitization ─────────────────────────────────────────────────

_UNSAFE_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WHITESPACE_RUN = re.compile(r"\s+")
_MAX_FILENAME_LEN = 200


def sanitize_filename(name: str, max_length: int = _MAX_FILENAME_LEN) -> str:
    """Remove path-traversal attacks and special characters from *name*.

    Returns a filesystem-safe basename.
    """
    # Take only the basename (strip directory components)
    name = PurePosixPath(name).name
    # Also handle Windows-style separators
    name = name.replace("\\", "/")
    if "/" in name:
        name = name.rsplit("/", 1)[-1]

    # Strip leading dots / spaces (hidden files, current-dir attacks)
    name = name.lstrip(". ")

    # Remove unsafe characters
    name = _UNSAFE_CHARS.sub("_", name)

    # Collapse whitespace
    name = _WHITESPACE_RUN.sub(" ", name).strip()

    # Limit length while preserving extension
    if len(name) > max_length:
        stem, _, ext = name.rpartition(".")
        if ext:
            allowed = max_length - len(ext) - 1
            name = stem[:allowed] + "." + ext
        else:
            name = name[:max_length]

    return name or "unnamed_file"


# ── File Extension Validation ─────────────────────────────────────────────


def validate_file_extension(filename: str) -> bool:
    """Return True if the file extension is in the allowed list."""
    ext = _get_extension(filename)
    return ext in settings.allowed_media_extensions


def _get_extension(filename: str) -> str:
    parts = filename.rsplit(".", 1)
    if len(parts) == 2:
        return "." + parts[1].lower()
    return ""


# ── Magic-byte validation ─────────────────────────────────────────────────


def validate_file_signature(filepath: str, expected_ext: str | None = None) -> bool:
    """Check that the file's magic bytes match its claimed extension.

    If *expected_ext* is None, the extension is derived from *filepath*.
    Returns True if the signature matches or the extension is unknown.
    """
    ext = expected_ext or _get_extension(filepath)
    sigs = _MAGIC_SIGNATURES.get(ext)
    if sigs is None:
        # Unknown extension — can't verify, let it pass
        return True

    try:
        with open(filepath, "rb") as fh:
            header = fh.read(32)
    except OSError:
        return False

    return any(header.startswith(sig) for sig in sigs)


# ── MIME type helper ──────────────────────────────────────────────────────


def guess_mime_type(filename: str) -> str:
    """Return a MIME type for *filename*, falling back to application/octet-stream."""
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"
