"""Media download orchestrator for direct files and supported stream extraction."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Callable, Coroutine, Any
from urllib.parse import urlparse
from uuid import UUID

import aiofiles
import aiohttp

from app.config import settings
from app.services.security import resolve_and_validate_ip, validate_url
from app.services.storage import StorageService
from app.utils.file_utils import generate_safe_filename

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Raised when download operation fails."""

    def __init__(self, message: str, code: str = "download_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class DownloadService:
    """Handles downloading media from direct URLs or supported platforms."""

    def __init__(self, storage_service: StorageService | None = None) -> None:
        self.storage = storage_service or StorageService()
        self._active_downloads: dict[str, asyncio.Task[Any]] = {}

    async def download_direct_stream(
        self,
        job_id: str,
        url: str,
        output_filename: str,
        progress_callback: Callable[[float, float, int], Coroutine[Any, Any, None]] | None = None,
    ) -> Path:
        """Stream direct media file with progress tracking."""
        validated_url = validate_url(url)
        parsed = urlparse(validated_url)
        if parsed.hostname:
            resolve_and_validate_ip(parsed.hostname)

        dest_path = self.storage.get_file_path(job_id, output_filename)

        timeout = aiohttp.ClientTimeout(total=settings.DOWNLOAD_TIMEOUT_SECONDS)
        headers = {"User-Agent": "MediaFlow/1.0 (+https://mediaflow.app)"}

        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(validated_url, allow_redirects=True) as response:
                if response.status >= 400:
                    raise DownloadError(f"HTTP error {response.status}: {response.reason}")

                total_size = int(response.headers.get("content-length", 0))
                max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
                if total_size > max_bytes:
                    raise DownloadError(f"File size exceeds maximum allowed ({settings.MAX_FILE_SIZE_MB} MB)")

                downloaded = 0
                start_time = asyncio.get_event_loop().time()
                last_update_time = start_time

                async with aiofiles.open(dest_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(64 * 1024):
                        await f.write(chunk)
                        downloaded += len(chunk)

                        if downloaded > max_bytes:
                            dest_path.unlink(missing_ok=True)
                            raise DownloadError(f"File download exceeded maximum size of {settings.MAX_FILE_SIZE_MB}MB")

                        now = asyncio.get_event_loop().time()
                        if progress_callback and (now - last_update_time >= 0.5 or (total_size and downloaded >= total_size)):
                            last_update_time = now
                            elapsed = max(now - start_time, 0.001)
                            speed = downloaded / elapsed  # bytes/sec
                            progress_pct = (downloaded / total_size * 100) if total_size > 0 else 0.0
                            try:
                                await progress_callback(progress_pct, speed, downloaded)
                            except Exception as e:
                                logger.debug("Error in download progress callback: %s", e)

        return dest_path

    async def download_with_ytdlp(
        self,
        job_id: str,
        url: str,
        format_id: str | None = None,
        is_audio_only: bool = False,
        audio_format: str = "mp3",
        progress_callback: Callable[[float, float, int], Coroutine[Any, Any, None]] | None = None,
    ) -> Path:
        """Download using yt-dlp with argument array (strictly no shell=True)."""
        validated_url = validate_url(url)
        parsed = urlparse(validated_url)
        if parsed.hostname:
            resolve_and_validate_ip(parsed.hostname)

        job_dir = self.storage.get_job_dir(job_id)
        out_tmpl = str(job_dir / "%(title).100s.%(ext)s")

        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--no-warnings",
            "--newline",
            "--max-filesize", f"{settings.MAX_FILE_SIZE_MB}m",
            "-o", out_tmpl,
        ]

        if is_audio_only:
            cmd.extend([
                "-x",
                "--audio-format", audio_format,
                "--audio-quality", "0",
            ])
        elif format_id:
            cmd.extend(["-f", format_id])
        else:
            cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])

        cmd.append(validated_url)

        logger.info("Executing yt-dlp: %s", " ".join(cmd[:6]))

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Regex to parse yt-dlp progress: "[download]  45.2% of ~  24.50MiB at    2.45MiB/s ETA 00:05"
        pct_regex = re.compile(r"\[download\]\s+(\d+\.?\d*)%")
        speed_regex = re.compile(r"at\s+(\d+\.?\d*)([KMG]iB/s|B/s)")

        async def read_stdout():
            while True:
                line_bytes = await process.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").strip()

                pct_match = pct_regex.search(line)
                if pct_match and progress_callback:
                    pct = float(pct_match.group(1))
                    speed = 0.0
                    speed_match = speed_regex.search(line)
                    if speed_match:
                        val = float(speed_match.group(1))
                        unit = speed_match.group(2)
                        multiplier = 1.0
                        if "KiB" in unit:
                            multiplier = 1024.0
                        elif "MiB" in unit:
                            multiplier = 1024.0 * 1024.0
                        elif "GiB" in unit:
                            multiplier = 1024.0 * 1024.0 * 1024.0
                        speed = val * multiplier

                    try:
                        await progress_callback(pct, speed, 0)
                    except Exception:
                        pass

        stdout_task = asyncio.create_task(read_stdout())
        stderr_output = []

        async def read_stderr():
            while True:
                line_bytes = await process.stderr.readline()
                if not line_bytes:
                    break
                stderr_output.append(line_bytes.decode("utf-8", errors="replace"))

        stderr_task = asyncio.create_task(read_stderr())

        try:
            return_code = await asyncio.wait_for(process.wait(), timeout=settings.DOWNLOAD_TIMEOUT_SECONDS)
            await stdout_task
            await stderr_task
        except asyncio.TimeoutError:
            process.kill()
            raise DownloadError("Download timed out after allowed duration")

        if return_code != 0:
            err_msg = "".join(stderr_output)
            if "DRM" in err_msg or "protected" in err_msg.lower():
                raise DownloadError("Media is DRM-protected and cannot be downloaded.", code="drm_protected")
            if "Sign in" in err_msg or "Private" in err_msg:
                raise DownloadError("This media requires authorization or is private.", code="auth_required")
            raise DownloadError(f"yt-dlp failed: {err_msg[:200]}", code="ytdlp_failed")

        # Find the downloaded file in the directory
        files = list(job_dir.glob("*"))
        if not files:
            raise DownloadError("No output file generated by download process")

        # Return the most recently modified file in job dir
        newest = max(files, key=lambda f: f.stat().st_mtime)
        return newest

