"""Schemas for the /downloads endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, HttpUrl

from app.schemas.common import JobStatus


class DownloadRequest(BaseModel):
    """Request to start a download."""

    url: HttpUrl
    format: str | None = None  # format_id or "best"
    quality: str | None = None  # e.g. "1080p", "720p", "best"


class DownloadResponse(BaseModel):
    """Response after a download job is created."""

    job_id: str
    status: JobStatus
    message: str = "Download queued"


class DownloadProgress(BaseModel):
    """Real-time progress information for a download."""

    job_id: str
    status: JobStatus
    progress: float = 0.0  # 0-100
    speed: str | None = None  # e.g. "2.5 MB/s"
    eta: str | None = None  # e.g. "00:01:30"
    title: str | None = None
    file_size: int | None = None
    error_message: str | None = None


class DownloadJobDetail(BaseModel):
    """Full detail of a download job."""

    job_id: str
    source_url: str
    source_type: str | None = None
    status: JobStatus
    title: str | None = None
    thumbnail_url: str | None = None
    duration: float | None = None
    requested_format: str | None = None
    requested_quality: str | None = None
    file_size: int | None = None
    progress: float = 0.0
    download_speed: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class DownloadListResponse(BaseModel):
    """List of download jobs."""

    items: List[DownloadJobDetail]
    total: int
