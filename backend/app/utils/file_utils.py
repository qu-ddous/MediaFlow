"""File utility functions for formatting, sanitizing, and media detection."""

from __future__ import annotations

import math
import mimetypes
import re
from pathlib import Path


def format_file_size(bytes_count: int | float | None) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    if bytes_count is None or bytes_count < 0:
        return "Unknown size"
    if bytes_count == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = int(math.floor(math.log(bytes_count, 1024))) if bytes_count > 0 else 0
    i = min(i, len(units) - 1)
    p = math.pow(1024, i)
    s = round(bytes_count / p, 2)
    return f"{s} {units[i]}"


def format_duration(seconds: float | int | None) -> str:
    """Format duration in seconds into HH:MM:SS or MM:SS."""
    if seconds is None or seconds < 0:
        return "00:00"
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def generate_safe_filename(title: str, extension: str) -> str:
    """Sanitize title and combine with extension to make a clean, safe filename."""
    clean = re.sub(r'[\\/*?:"<>|]', "", title)
    clean = re.sub(r"[\s_]+", "_", clean).strip("_.")
    if not clean:
        clean = "media_download"
    clean = clean[:120]
    ext = extension.lstrip(".")
    return f"{clean}.{ext}" if ext else clean


def get_mime_type(file_path: str | Path) -> str:
    """Get the MIME type of a file based on its extension."""
    mime, _ = mimetypes.guess_type(str(file_path))
    return mime or "application/octet-stream"
