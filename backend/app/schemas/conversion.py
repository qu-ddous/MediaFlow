"""Schemas for the /conversions endpoints."""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import JobStatus


class ConversionRequest(BaseModel):
    """Request to start a media conversion."""

    job_id: str | None = None  # source download job id
    input_path: str | None = None  # or explicit local path
    output_format: str  # e.g. "mp4", "mp3"
    resolution: str | None = None  # e.g. "1920x1080"
    bitrate: str | None = None  # e.g. "192k"
    audio_quality: str | None = None  # e.g. "320k"
    codec: str | None = None


class ConversionResponse(BaseModel):
    """Response after a conversion job is created."""

    job_id: str
    status: JobStatus
    message: str = "Conversion queued"


class ConversionProgress(BaseModel):
    """Real-time conversion progress."""

    job_id: str
    status: JobStatus
    progress: float = 0.0
    input_format: str | None = None
    output_format: str | None = None
    error_message: str | None = None
