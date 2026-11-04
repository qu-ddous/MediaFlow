"""Schemas for the /analyze endpoint."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRequest(BaseModel):
    """Request body for URL analysis."""

    url: HttpUrl


class FormatOption(BaseModel):
    """A single downloadable format option."""

    format_id: str
    extension: str
    format_note: str | None = None
    filesize: int | None = None
    filesize_approx: int | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    quality: str | None = None
    has_video: bool = True
    has_audio: bool = True


class ResolutionOption(BaseModel):
    """Available resolution for a video."""

    label: str  # e.g. "1080p"
    width: int | None = None
    height: int
    fps: float | None = None


class AudioOption(BaseModel):
    """Available audio stream."""

    format_id: str
    codec: str | None = None
    bitrate: float | None = None  # kbps
    sample_rate: int | None = None
    language: str | None = None


class EstimatedSize(BaseModel):
    """Estimated file size for a particular format + quality combination."""

    format_id: str
    quality: str
    size_bytes: int | None = None
    size_label: str | None = None  # e.g. "45.2 MB"


class AnalyzeResponse(BaseModel):
    """Full analysis result returned to the frontend."""

    url: str
    title: str | None = None
    thumbnail: str | None = None
    duration: float | None = None  # seconds
    source: str | None = None  # e.g. "youtube", "direct"
    media_type: str | None = None  # "video", "audio", "image"
    formats: List[FormatOption] = Field(default_factory=list)
    resolutions: List[ResolutionOption] = Field(default_factory=list)
    audio_streams: List[AudioOption] = Field(default_factory=list)
    estimated_sizes: List[EstimatedSize] = Field(default_factory=list)
    subtitles: dict[str, str] = Field(default_factory=dict)
    is_live: bool = False
    original_format: str | None = None
