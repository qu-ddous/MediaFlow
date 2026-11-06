"""API routes for media transcoding and conversion."""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_storage_service, get_task_queue
from app.models.conversion import ConversionJob
from app.models.download import DownloadJob, JobStatus
from app.schemas.conversion import ConversionProgress, ConversionRequest, ConversionResponse
from app.services.security import sanitize_filename, validate_file_extension
from app.services.storage import StorageService
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
    """Create a new media conversion task from an existing job or path."""
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


@router.post("/upload", response_model=ConversionResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_convert(
    file: UploadFile = File(...),
    output_format: str = Form(...),
    resolution: str | None = Form(None),
    bitrate: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
    queue: AsyncTaskQueue = Depends(get_task_queue),
) -> ConversionResponse:
    """Upload a local media file directly and start transcoding."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File extension is not permitted for media processing",
        )

    clean_filename = sanitize_filename(file.filename)
    conversion_id = str(uuid4())
    dest_path = storage.get_file_path(conversion_id, clean_filename)

    # Save uploaded chunks
    async with aiofiles.open(dest_path, "wb") as out_f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await out_f.write(chunk)

    job = ConversionJob(
        id=conversion_id,
        source_job_id=None,
        input_path=str(dest_path),
        output_format=output_format.lower().lstrip("."),
        resolution=resolution,
        bitrate=bitrate,
        status=JobStatus.PENDING,
        progress=0.0,
    )
    db.add(job)
    await db.commit()

    is_audio = output_format.lower().lstrip(".") in ("mp3", "m4a", "wav", "flac", "aac", "ogg")
    queue.submit(
        task_id=conversion_id,
        coro_fn=lambda: run_conversion_task(
            job_id=conversion_id,
            input_path=str(dest_path),
            output_format=output_format,
            resolution=resolution,
            audio_only=is_audio,
            quality=bitrate or "192k",
        ),
    )

    return ConversionResponse(
        job_id=conversion_id,
        status=JobStatus.PENDING,
        message="File uploaded and conversion queued",
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


@router.get("/{job_id}/file")
async def download_converted_file(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download the converted media file."""
    result = await db.execute(select(ConversionJob).where(ConversionJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job or not job.output_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Converted file not found")

    file_path = Path(job.output_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File no longer exists on disk")

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )
