"""Conversion job model."""

from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.download import JobStatus


class ConversionJob(UUIDMixin, TimestampMixin, Base):
    """Represents a media format conversion job."""

    __tablename__ = "conversion_jobs"

    source_job_id: Mapped[str | None] = mapped_column(
        ForeignKey("download_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False, length=32),
        default=JobStatus.PENDING,
        nullable=False,
    )
    input_format: Mapped[str | None] = mapped_column(String(32), nullable=True)
    output_format: Mapped[str] = mapped_column(String(32), nullable=False)
    input_codec: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_codec: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resolution: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bitrate: Mapped[str | None] = mapped_column(String(32), nullable=True)
    input_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    output_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
