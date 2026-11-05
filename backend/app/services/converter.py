"""Conversion service for transcoding video and audio formats."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

from app.config import settings
from app.services.media_engine import FFmpegEngine, FFmpegError
from app.services.storage import StorageService
from app.utils.validators import ALLOWED_AUDIO_FORMATS, ALLOWED_VIDEO_FORMATS

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Raised when media conversion fails."""

    def __init__(self, message: str, code: str = "conversion_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ConversionService:
    """Orchestrates transcoding, audio extraction, and resizing."""

    def __init__(
        self,
        engine: FFmpegEngine | None = None,
        storage: StorageService | None = None,
    ) -> None:
        self.engine = engine or FFmpegEngine()
        self.storage = storage or StorageService()

    async def convert_file(
        self,
        job_id: str | UUID,
        input_file: Path | str,
        output_format: str,
        resolution: str | None = None,
        audio_only: bool = False,
        quality: str = "192k",
        progress_callback: Callable[[float], Any] | None = None,
    ) -> Path:
        """Convert a media file to the requested format."""
        input_path = Path(input_file).resolve()
        if not input_path.exists():
            raise ConversionError(f"Input file not found: {input_path}")

        fmt = output_format.lower().lstrip(".")
        is_audio = audio_only or fmt in ALLOWED_AUDIO_FORMATS

        job_dir = self.storage.get_job_dir(str(job_id))
        stem = input_path.stem
        output_path = job_dir / f"{stem}_converted.{fmt}"

        try:
            if is_audio:
                await self.engine.extract_audio(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    fmt=fmt,
                    quality=quality,
                    progress_callback=progress_callback,
                )
            elif resolution:
                # Map resolution like '720p' or '1080p'
                res_clean = resolution.lower().rstrip("p")
                res_map = {
                    "1080": "1920x1080",
                    "720": "1280x720",
                    "480": "854x480",
                    "360": "640x360",
                    "240": "426x240",
                    "1440": "2560x1440",
                    "2160": "3840x2160",
                }
                target_res = res_map.get(res_clean, resolution)
                await self.engine.resize_video(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    resolution=target_res,
                    progress_callback=progress_callback,
                )
            else:
                # Video format transcode (e.g., webm -> mp4)
                vcodec = "libx264" if fmt in ("mp4", "mkv", "mov") else "libvpx-vp9"
                acodec = "aac" if fmt in ("mp4", "mkv", "mov") else "libopus"
                options = [
                    "-c:v", vcodec,
                    "-preset", "fast",
                    "-crf", "23",
                    "-c:a", acodec,
                    "-b:a", quality,
                    "-movflags", "+faststart",
                ]
                await self.engine.convert(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    options=options,
                    progress_callback=progress_callback,
                )

            # Validate output file
            is_valid = await self.engine.validate_output(str(output_path))
            if not is_valid:
                raise ConversionError("Converted media file failed integrity check")

            return output_path

        except FFmpegError as exc:
            logger.error("FFmpeg error during conversion: %s (stderr: %s)", exc.message, exc.stderr)
            raise ConversionError(f"Conversion failed: {exc.message}")

