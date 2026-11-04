"""Application configuration using pydantic-settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "MediaFlow"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./mediaflow.db"
    database_echo: bool = False

    # --- Storage ---
    storage_path: str = str(Path("./storage").resolve())
    temp_path: str = str(Path("./storage/temp").resolve())
    max_storage_size_gb: float = 50.0

    # --- File Limits ---
    max_file_size_bytes: int = 10 * 1024 * 1024 * 1024  # 10 GB
    max_upload_size_bytes: int = 5 * 1024 * 1024 * 1024  # 5 GB
    file_expiry_hours: int = 24

    # --- Download ---
    download_timeout_seconds: int = 3600  # 1 hour
    max_concurrent_downloads: int = 5
    download_chunk_size: int = 8 * 1024 * 1024  # 8 MB

    # --- Conversion ---
    conversion_timeout_seconds: int = 7200  # 2 hours
    max_concurrent_conversions: int = 3

    # --- FFmpeg ---
    ffmpeg_path: str = os.environ.get(
        "FFMPEG_PATH",
        r"C:\Users\mqudd\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe",
    )
    ffprobe_path: str = os.environ.get(
        "FFPROBE_PATH",
        r"C:\Users\mqudd\AppData\Local\Microsoft\WinGet\Links\ffprobe.exe",
    )

    # --- Rate Limiting ---
    rate_limit_default: str = "60/minute"
    rate_limit_analyze: str = "20/minute"
    rate_limit_download: str = "10/minute"

    # --- CORS ---
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # --- Security ---
    allowed_schemes: List[str] = ["http", "https"]
    max_url_length: int = 2048
    allowed_media_extensions: List[str] = [
        ".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".wmv",
        ".mp3", ".aac", ".flac", ".wav", ".ogg", ".opus", ".m4a",
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp",
        ".srt", ".vtt", ".ass",
    ]

    # --- yt-dlp ---
    ytdlp_path: str = "yt-dlp"


settings = Settings()
