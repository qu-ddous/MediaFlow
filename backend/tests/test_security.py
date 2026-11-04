"""Tests for SSRF prevention, IP validation, and file sanitization."""

import pytest

from app.services.security import (
    SecurityError,
    resolve_and_validate_ip,
    sanitize_filename,
    validate_file_extension,
    validate_url,
)


def test_validate_url_valid_http_https():
    assert validate_url("https://example.com/video.mp4") == "https://example.com/video.mp4"
    assert validate_url("http://example.com/media/test.mp3") == "http://example.com/media/test.mp3"


def test_validate_url_blocks_file_scheme():
    with pytest.raises(SecurityError) as exc:
        validate_url("file:///etc/passwd")
    assert "not allowed" in str(exc.value).lower()


def test_validate_url_blocks_gopher_and_ftp():
    with pytest.raises(SecurityError):
        validate_url("gopher://127.0.0.1:70")
    with pytest.raises(SecurityError):
        validate_url("ftp://example.com/file.mp4")


def test_private_ip_blocking():
    # Loopback
    with pytest.raises(SecurityError):
        resolve_and_validate_ip("127.0.0.1")

    # RFC 1918 Private ranges
    with pytest.raises(SecurityError):
        resolve_and_validate_ip("10.0.0.1")
    with pytest.raises(SecurityError):
        resolve_and_validate_ip("192.168.1.1")
    with pytest.raises(SecurityError):
        resolve_and_validate_ip("172.16.0.1")

    # Cloud metadata link-local
    with pytest.raises(SecurityError):
        resolve_and_validate_ip("169.254.169.254")


def test_sanitize_filename_prevents_path_traversal():
    dirty = "../../../etc/passwd"
    clean = sanitize_filename(dirty)
    assert ".." not in clean
    assert "/" not in clean
    assert "\\" not in clean


def test_validate_file_extension():
    assert validate_file_extension("video.mp4") is True
    assert validate_file_extension("audio.mp3") is True
    assert validate_file_extension("script.sh") is False
    assert validate_file_extension("executable.exe") is False
