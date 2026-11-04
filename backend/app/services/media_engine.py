"""FFmpeg / FFprobe engine — probe, convert, extract, resize, thumbnail."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any, Callable

from app.config import settings

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float], Any]  # progress 0-100


class FFmpegError(Exception):
    """Raised when an FFmpeg/FFprobe operation fails."""

    def __init__(self, message: str, stderr: str = "") -> None:
        self.message = message
        self.stderr = stderr
        super().__init__(message)


class FFmpegEngine:
    """Wrapper around FFmpeg and FFprobe binaries."""

    def __init__(
        self,
        ffmpeg_path: str = settings.ffmpeg_path,
        ffprobe_path: str = settings.ffprobe_path,
    ) -> None:
        self.ffmpeg = ffmpeg_path
        self.ffprobe = ffprobe_path

    # ── Probe ─────────────────────────────────────────────────────────

    async def probe_file(self, path: str) -> dict[str, Any]:
        """Run ffprobe and return parsed JSON metadata."""
        args = [
            self.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        if proc.returncode != 0:
            raise FFmpegError(
                f"ffprobe failed (rc={proc.returncode})",
                stderr=stderr.decode(errors="replace"),
            )

        try:
            return json.loads(stdout.decode(errors="replace"))
        except json.JSONDecodeError as exc:
            raise FFmpegError(f"ffprobe returned invalid JSON: {exc}") from exc

    # ── Convert ───────────────────────────────────────────────────────

    async def convert(
        self,
        input_path: str,
        output_path: str,
        options: list[str] | None = None,
        progress_callback: ProgressCallback | None = None,
        timeout: int = settings.conversion_timeout_seconds,
    ) -> str:
        """Run an ffmpeg conversion with optional progress reporting.

        Returns the output_path on success.
        """
        # Determine total duration for progress calculation
        total_duration = await self._get_duration(input_path)

        args = [
            self.ffmpeg,
            "-y",  # overwrite
            "-progress", "pipe:1",
            "-i", input_path,
            *(options or []),
            output_path,
        ]

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            await self._read_progress(proc, total_duration, progress_callback, timeout)
        except asyncio.TimeoutError:
            proc.kill()
            raise FFmpegError(f"FFmpeg conversion timed out after {timeout}s")

        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise FFmpegError(
                f"ffmpeg conversion failed (rc={proc.returncode})",
                stderr=stderr.decode(errors="replace"),
            )

        return output_path

    # ── Extract audio ─────────────────────────────────────────────────

    async def extract_audio(
        self,
        input_path: str,
        output_path: str,
        fmt: str = "mp3",
        quality: str = "192k",
        progress_callback: ProgressCallback | None = None,
    ) -> str:
        """Extract the audio track from a video file."""
        codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "flac": "flac",
            "wav": "pcm_s16le",
            "ogg": "libvorbis",
            "opus": "libopus",
        }
        codec = codec_map.get(fmt, "libmp3lame")
        options = ["-vn", "-acodec", codec, "-b:a", quality]
        return await self.convert(input_path, output_path, options, progress_callback)

    # ── Resize video ──────────────────────────────────────────────────

    async def resize_video(
        self,
        input_path: str,
        output_path: str,
        resolution: str,
        progress_callback: ProgressCallback | None = None,
    ) -> str:
        """Resize / scale a video. *resolution* like '1920x1080' or '1280x720'."""
        width, height = resolution.lower().split("x")
        scale = f"scale={width}:{height}:force_original_aspect_ratio=decrease"
        pad = f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        options = ["-vf", f"{scale},{pad}", "-c:a", "copy"]
        return await self.convert(input_path, output_path, options, progress_callback)

    # ── Thumbnail ─────────────────────────────────────────────────────

    async def generate_thumbnail(
        self,
        input_path: str,
        output_path: str,
        timestamp: str = "00:00:01",
    ) -> str:
        """Generate a single thumbnail image from a video."""
        args = [
            self.ffmpeg,
            "-y",
            "-ss", timestamp,
            "-i", input_path,
            "-frames:v", "1",
            "-q:v", "2",
            output_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        if proc.returncode != 0:
            raise FFmpegError(
                "Thumbnail generation failed",
                stderr=stderr.decode(errors="replace"),
            )
        return output_path

    # ── Validate output ───────────────────────────────────────────────

    async def validate_output(self, path: str) -> bool:
        """Quick probe to verify the output file is a valid media container."""
        if not Path(path).is_file():
            return False
        try:
            info = await self.probe_file(path)
            return bool(info.get("streams"))
        except FFmpegError:
            return False

    # ── Capabilities ──────────────────────────────────────────────────

    async def get_capabilities(self) -> dict[str, Any]:
        """Return supported codecs, formats, and feature flags."""
        result: dict[str, Any] = {"encoders": [], "decoders": [], "formats": []}
        for flag, key in [("-encoders", "encoders"), ("-decoders", "decoders"), ("-formats", "formats")]:
            try:
                proc = await asyncio.create_subprocess_exec(
                    self.ffmpeg, flag,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
                result[key] = self._parse_capability_list(stdout.decode(errors="replace"))
            except Exception:
                logger.debug("Failed to query ffmpeg %s", flag, exc_info=True)
        return result

    # ── Internal helpers ──────────────────────────────────────────────

    async def _get_duration(self, path: str) -> float:
        """Return the duration in seconds, or 0.0 if unknown."""
        try:
            info = await self.probe_file(path)
            dur = info.get("format", {}).get("duration")
            return float(dur) if dur else 0.0
        except Exception:
            return 0.0

    async def _read_progress(
        self,
        proc: asyncio.subprocess.Process,
        total_duration: float,
        callback: ProgressCallback | None,
        timeout: int,
    ) -> None:
        """Parse ffmpeg `-progress pipe:1` output and call *callback*."""
        if proc.stdout is None or callback is None or total_duration <= 0:
            return

        time_re = re.compile(r"out_time_us=(\d+)")

        async def _reader() -> None:
            assert proc.stdout is not None
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                decoded = line.decode(errors="replace").strip()
                match = time_re.search(decoded)
                if match:
                    current_us = int(match.group(1))
                    current_s = current_us / 1_000_000
                    pct = min((current_s / total_duration) * 100, 99.9)
                    try:
                        callback(pct)
                    except Exception:
                        pass

        await asyncio.wait_for(_reader(), timeout=timeout)

    @staticmethod
    def _parse_capability_list(text: str) -> list[str]:
        """Extract codec/format names from ffmpeg list output."""
        names: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("=") or not stripped:
                continue
            parts = stripped.split()
            if len(parts) >= 2:
                names.append(parts[1] if parts[0].startswith(("D", "E", " ")) else parts[0])
        return names[:200]  # cap to avoid huge payloads
