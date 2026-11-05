"""API routes for media transcoding and conversion."""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_task_queue
from app.models.conversion import ConversionJob
from app.models.download import DownloadJob, JobStatus
from app.schemas.conversion import ConversionProgress, ConversionRequest, ConversionResponse
from app.workers.media_tasks import run_conversion_task
from app.workers.task_queue import AsyncTaskQueue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversions", tags=["conversions"])


@router.post("", response_model=ConversionResponse, status_code=status.HTTP_201_CREATED)
async def create_conversion_job(
    req: ConversionRequest,
    db: AsyncSession = Depends(get_db),
    queue: AsyncTaskQueue = Depends(get_task_queue),
) -> ConversionResponse:
    """Create a new media conversion task."""
    input_file_path: str | None = req.input_path

    if req.job_id:
        res = await db.execute(select(DownloadJob).where(DownloadJob.id == req.job_id))
        source_job = res.scalar_one_or_none()
        if not source_job or not source_job.output_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source download job not found or does not have a completed file",
            )
        input_file_path = source_job.output_path

    if not input_file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either job_id or input_path must be provided",
        )

    conversion_id = str(uuid4())
    job = ConversionJob(
        id=conversion_id,
        source_job_id=req.job_id,
        input_path=input_file_path,
        output_format=req.output_format.lower().lstrip("."),
        resolution=req.resolution,
        bitrate=req.bitrate or req.audio_quality,
        status=JobStatus.PENDING,
        progress=0.0,
    )
    db.add(job)
    await db.commit()

    is_audio = req.output_format.lower().lstrip(".") in ("mp3", "m4a", "wav", "flac", "aac", "ogg")
    queue.submit(
        task_id=conversion_id,
        coro_fn=lambda: run_conversion_task(
            job_id=conversion_id,
            input_path=input_file_path,
            output_format=req.output_format,
            resolution=req.resolution,
            audio_only=is_audio,
            quality=req.bitrate or "192k",
        ),
    )

    return ConversionResponse(
        job_id=conversion_id,
        status=JobStatus.PENDING,
        message="Conversion job queued",
    )


@router.get("/{job_id}", response_model=ConversionProgress)
async def get_conversion_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> ConversionProgress:
    """Get status of a conversion job."""
    result = await db.execute(select(ConversionJob).where(ConversionJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversion job not found")

    return ConversionProgress(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        input_format=job.input_format,
        output_format=job.output_format,
        error_message=job.error_message,
    )

