"""Validation helpers for URLs, media formats, and parameters."""

from __future__ import annotations

import re
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_VIDEO_FORMATS = {"mp4", "webm", "mkv", "mov", "avi"}
ALLOWED_AUDIO_FORMATS = {"mp3", "m4a", "wav", "flac", "aac", "ogg", "opus"}
ALLOWED_RESOLUTIONS = {"144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"}


def is_valid_url(url: str) -> bool:
    """Check if string is a syntactically valid HTTP/HTTPS URL."""
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme.lower() in ALLOWED_SCHEMES and bool(parsed.netloc)
    except Exception:
        return False


def normalize_resolution(resolution_str: str) -> str:
    """Normalize resolution strings like '1080', '1080p', '1920x1080' to standard '1080p'."""
    res = resolution_str.lower().strip()
    match = re.search(r"(\d{3,4})p?", res)
    if match:
        val = match.group(1)
        return f"{val}p"
    return res

