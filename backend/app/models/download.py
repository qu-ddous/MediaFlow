"""Download and MediaMetadata models."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin, _utcnow


class JobStatus(str, enum.Enum):
    """Status enumeration for download / conversion jobs."""

    PENDING = "pending"
    ANALYZING = "analyzing"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DownloadJob(UUIDMixin, TimestampMixin, Base):
    """Represents a single media download job."""

    __tablename__ = "download_jobs"

    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False, length=32),
        default=JobStatus.PENDING,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    requested_format: Mapped[str | None] = mapped_column(String(32), nullable=True)
    requested_quality: Mapped[str | None] = mapped_column(String(32), nullable=True)
    file_size: Mapped[int | None] = mapped_column(nullable=True)
    output_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    download_speed: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    metadata_info: Mapped[MediaMetadata | None] = relationship(
        "MediaMetadata",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    history_entries: Mapped[list["DownloadHistory"]] = relationship(
        "DownloadHistory",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class MediaMetadata(UUIDMixin, Base):
    """Detailed metadata extracted during media analysis."""

    __tablename__ = "media_metadata"

    job_id: Mapped[str] = mapped_column(
        ForeignKey("download_jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    available_formats: Mapped[str | None] = mapped_column(Text, nullable=True)
    available_resolutions: Mapped[str | None] = mapped_column(Text, nullable=True)
    available_audio: Mapped[str | None] = mapped_column(Text, nullable=True)
    subtitles: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_format: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )

    job: Mapped[DownloadJob] = relationship("DownloadJob", back_populates="metadata_info")


# Forward-ref import guard for DownloadHistory
from app.models.audit import DownloadHistory as _DH  # noqa: E402, F401
