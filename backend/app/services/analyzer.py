"""Media URL analyzer — extracts metadata via yt-dlp or direct HTTP HEAD."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any
from urllib.parse import urlparse

import aiohttp

from app.config import settings
from app.schemas.analyze import (
    AnalyzeResponse,
    AudioOption,
    EstimatedSize,
    FormatOption,
    ResolutionOption,
)
from app.services.security import (
    SecurityError,
    check_redirect_safety,
    resolve_and_validate_ip,
    validate_url,
)
from app.utils.file_utils import format_file_size

logger = logging.getLogger(__name__)

# Extensions that indicate a direct-download media file
_DIRECT_MEDIA_EXTENSIONS = {
    ".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".wmv",
    ".mp3", ".aac", ".flac", ".wav", ".ogg", ".opus", ".m4a",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp",
}


class AnalyzerError(Exception):
    """Raised when media analysis fails."""

    def __init__(self, message: str, code: str = "analyze_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class MediaAnalyzer:
    """Analyze a media URL and return available download options."""

    async def analyze_url(self, url: str) -> AnalyzeResponse:
        """Main entry point: validate, detect source type, extract metadata."""
        # Step 1 — validate URL
        validated_url = validate_url(url)

        # Step 2 — DNS resolution + SSRF check
        parsed = urlparse(validated_url)
        hostname = parsed.hostname
        if hostname:
            resolve_and_validate_ip(hostname)

        # Step 3 — detect source type
        source_type = self._detect_source_type(validated_url)

        # Step 4 — branch on source type
        if source_type == "direct":
            return await self._analyze_direct(validated_url)
        else:
            return await self._analyze_ytdlp(validated_url, source_type)

    # ── Source-type detection ─────────────────────────────────────────

    @staticmethod
    def _detect_source_type(url: str) -> str:
        """Heuristically classify the URL."""
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        path = parsed.path.lower()

        if any(h in host for h in ("youtube.com", "youtu.be")):
            return "youtube"
        if "vimeo.com" in host:
            return "vimeo"
        if "twitter.com" in host or "x.com" in host:
            return "twitter"
        if "reddit.com" in host:
            return "reddit"
        if "tiktok.com" in host:
            return "tiktok"
        if "instagram.com" in host:
            return "instagram"
        if "soundcloud.com" in host:
            return "soundcloud"
        if "twitch.tv" in host:
            return "twitch"
        if "dailymotion.com" in host:
            return "dailymotion"
        if "facebook.com" in host or "fb.watch" in host:
            return "facebook"

        # Check path extension for direct downloads
        for ext in _DIRECT_MEDIA_EXTENSIONS:
            if path.endswith(ext):
                return "direct"

        # Fall back to yt-dlp (it supports 1000+ sites)
        return "generic"

    # ── Direct media URL analysis ─────────────────────────────────────

    async def _analyze_direct(self, url: str) -> AnalyzeResponse:
        """Analyze a direct media file URL via HTTP HEAD."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url,
                    allow_redirects=True,
                    timeout=aiohttp.ClientTimeout(total=15),
                    max_redirects=5,
                ) as resp:
                    # Validate redirect destinations
                    if resp.history:
                        final_url = str(resp.url)
                        try:
                            check_redirect_safety(final_url)
                        except SecurityError as exc:
                            raise AnalyzerError(
                                f"Redirect destination blocked: {exc.message}",
                                "redirect_blocked",
                            )

                    content_type = resp.headers.get("Content-Type", "")
                    content_length = resp.headers.get("Content-Length")
                    file_size = int(content_length) if content_length else None

                    parsed = urlparse(url)
                    filename = parsed.path.rsplit("/", 1)[-1] if "/" in parsed.path else parsed.path
                    ext = ""
                    if "." in filename:
                        ext = filename.rsplit(".", 1)[-1].lower()

                    media_type = "video" if "video" in content_type else (
                        "audio" if "audio" in content_type else (
                            "image" if "image" in content_type else "unknown"
                        )
                    )

                    fmt = FormatOption(
                        format_id="direct",
                        extension=ext or "bin",
                        format_note="Direct download",
                        filesize=file_size,
                        has_video=media_type == "video",
                        has_audio=media_type in ("video", "audio"),
                    )

                    estimated: list[EstimatedSize] = []
                    if file_size:
                        estimated.append(EstimatedSize(
                            format_id="direct",
                            quality="original",
                            size_bytes=file_size,
                            size_label=format_file_size(file_size),
                        ))

                    return AnalyzeResponse(
                        url=url,
                        title=filename,
                        source="direct",
                        media_type=media_type,
                        formats=[fmt],
                        estimated_sizes=estimated,
                        original_format=ext,
                    )

        except aiohttp.ClientError as exc:
            raise AnalyzerError(f"HTTP error while analyzing URL: {exc}") from exc

    # ── yt-dlp analysis ───────────────────────────────────────────────

    async def _analyze_ytdlp(self, url: str, source_type: str) -> AnalyzeResponse:
        """Use yt-dlp --dump-json to extract metadata without downloading."""
        args = [
            settings.ytdlp_path,
            "--no-download",
            "--dump-json",
            "--no-warnings",
            "--no-playlist",
            "--socket-timeout", "15",
            url,
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        except asyncio.TimeoutError:
            raise AnalyzerError("yt-dlp timed out while analyzing URL", "timeout")

        if proc.returncode != 0:
            err_text = stderr.decode(errors="replace").strip()
            raise AnalyzerError(
                self._parse_ytdlp_error(err_text),
                "ytdlp_error",
            )

        try:
            info: dict[str, Any] = json.loads(stdout.decode(errors="replace"))
        except json.JSONDecodeError as exc:
            raise AnalyzerError(f"yt-dlp returned invalid JSON: {exc}") from exc

        return self._build_response(url, info, source_type)

    # ── Build response from yt-dlp info dict ──────────────────────────

    def _build_response(self, url: str, info: dict[str, Any], source: str) -> AnalyzeResponse:
        """Convert yt-dlp's JSON info_dict into our AnalyzeResponse."""
        formats: list[FormatOption] = []
        resolutions: list[ResolutionOption] = []
        audio_streams: list[AudioOption] = []
        estimated_sizes: list[EstimatedSize] = []
        seen_resolutions: set[int] = set()

        for f in info.get("formats", []):
            fmt_id = f.get("format_id", "unknown")
            ext = f.get("ext", "")
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            has_video = vcodec not in ("none", None)
            has_audio = acodec not in ("none", None)
            height = f.get("height")
            width = f.get("width")
            filesize = f.get("filesize") or f.get("filesize_approx")
            fps = f.get("fps")

            formats.append(FormatOption(
                format_id=fmt_id,
                extension=ext,
                format_note=f.get("format_note"),
                filesize=f.get("filesize"),
                filesize_approx=f.get("filesize_approx"),
                video_codec=vcodec if has_video else None,
                audio_codec=acodec if has_audio else None,
                quality=f.get("format_note"),
                has_video=has_video,
                has_audio=has_audio,
            ))

            # Collect distinct resolutions
            if has_video and height and height not in seen_resolutions:
                seen_resolutions.add(height)
                resolutions.append(ResolutionOption(
                    label=f"{height}p",
                    width=width,
                    height=height,
                    fps=fps,
                ))

            # Audio-only streams
            if has_audio and not has_video:
                abr = f.get("abr") or f.get("tbr")
                audio_streams.append(AudioOption(
                    format_id=fmt_id,
                    codec=acodec,
                    bitrate=abr,
                    sample_rate=f.get("asr"),
                    language=f.get("language"),
                ))

            # Estimated sizes
            if filesize:
                estimated_sizes.append(EstimatedSize(
                    format_id=fmt_id,
                    quality=f.get("format_note", "unknown"),
                    size_bytes=int(filesize),
                    size_label=format_file_size(int(filesize)),
                ))

        # Sort resolutions descending
        resolutions.sort(key=lambda r: r.height, reverse=True)

        # Subtitles
        subtitles_raw = info.get("subtitles") or {}
        subtitles: dict[str, str] = {}
        for lang, subs in subtitles_raw.items():
            if isinstance(subs, list) and subs:
                subtitles[lang] = subs[0].get("url", "")

        return AnalyzeResponse(
            url=url,
            title=info.get("title"),
            thumbnail=info.get("thumbnail"),
            duration=info.get("duration"),
            source=source,
            media_type="video" if info.get("vcodec", "none") != "none" else "audio",
            formats=formats,
            resolutions=resolutions,
            audio_streams=audio_streams,
            estimated_sizes=estimated_sizes,
            subtitles=subtitles,
            is_live=bool(info.get("is_live")),
            original_format=info.get("ext"),
        )

    # ── Error parsing ─────────────────────────────────────────────────

    @staticmethod
    def _parse_ytdlp_error(stderr: str) -> str:
        """Extract a user-friendly message from yt-dlp stderr."""
        if "is not a valid URL" in stderr:
            return "The provided URL is not valid or not supported"
        if "Private video" in stderr:
            return "This video is private and cannot be accessed"
        if "Sign in" in stderr or "login" in stderr.lower():
            return "Authentication required to access this content"
        if "Geo-restricted" in stderr or "not available in your country" in stderr:
            return "This content is geo-restricted"
        if "Video unavailable" in stderr:
            return "This video is unavailable"
        if "Unsupported URL" in stderr:
            return "This URL is not supported"

        # Try to extract ERROR: line
        for line in stderr.splitlines():
            if line.strip().startswith("ERROR:"):
                return line.strip().removeprefix("ERROR:").strip()

        return stderr[:300] if stderr else "Unknown analysis error"
