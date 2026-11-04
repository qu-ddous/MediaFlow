"""API routes for download lifecycle management."""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_storage_service, get_task_queue
from app.models.download import DownloadJob, JobStatus
from app.schemas.download import DownloadJobDetail, DownloadRequest, DownloadResponse
from app.services.storage import StorageService
from app.workers.media_tasks import run_download_task
from app.workers.task_queue import AsyncTaskQueue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/downloads", tags=["downloads"])


@router.post("", response_model=DownloadResponse, status_code=status.HTTP_201_CREATED)
async def create_download_job(
    req: DownloadRequest,
    db: AsyncSession = Depends(get_db),
    queue: AsyncTaskQueue = Depends(get_task_queue),
) -> DownloadResponse:
    """Create a new download task and queue it in the background."""
    job_id = str(uuid4())
    url_str = str(req.url)
    req_format = req.format or "mp4"
    req_quality = req.quality or "best"
    is_audio = req_format in ("mp3", "m4a", "wav", "flac", "aac", "ogg", "opus")

    job = DownloadJob(
        id=job_id,
        source_url=url_str,
        requested_format=req_format,
        requested_quality=req_quality,
        status=JobStatus.PENDING,
        progress=0.0,
    )
    db.add(job)
    await db.commit()

    # Enqueue background execution
    queue.submit(
        task_id=job_id,
        coro_fn=lambda: run_download_task(
            job_id=job_id,
            url=url_str,
            requested_format=req_format,
            requested_quality=req_quality,
            is_audio_only=is_audio,
        ),
    )

    return DownloadResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Download queued successfully",
    )


@router.get("", response_model=list[DownloadJobDetail])
async def list_downloads(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[DownloadJobDetail]:
    """List recent download jobs."""
    query = select(DownloadJob).order_by(desc(DownloadJob.created_at)).limit(limit)
    result = await db.execute(query)
    jobs = result.scalars().all()

    return [
        DownloadJobDetail(
            job_id=j.id,
            source_url=j.source_url,
            source_type=j.source_type,
            status=j.status,
            title=j.title,
            thumbnail_url=j.thumbnail_url,
            duration=j.duration,
            requested_format=j.requested_format,
            requested_quality=j.requested_quality,
            file_size=j.file_size,
            progress=j.progress,
            download_speed=j.download_speed,
            error_message=j.error_message,
            created_at=j.created_at,
            updated_at=j.updated_at,
        )
        for j in jobs
    ]


@router.get("/{job_id}", response_model=DownloadJobDetail)
async def get_download_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> DownloadJobDetail:
    """Get status and details of a single download job."""
    result = await db.execute(select(DownloadJob).where(DownloadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download job not found")

    return DownloadJobDetail(
        job_id=job.id,
        source_url=job.source_url,
        source_type=job.source_type,
        status=job.status,
        title=job.title,
        thumbnail_url=job.thumbnail_url,
        duration=job.duration,
        requested_format=job.requested_format,
        requested_quality=job.requested_quality,
        file_size=job.file_size,
        progress=job.progress,
        download_speed=job.download_speed,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.post("/{job_id}/cancel")
async def cancel_download_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    queue: AsyncTaskQueue = Depends(get_task_queue),
) -> dict[str, str]:
    """Cancel an active download task."""
    result = await db.execute(select(DownloadJob).where(DownloadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    queue.cancel(job_id)
    job.status = JobStatus.CANCELLED
    await db.commit()

    return {"message": "Job cancelled", "job_id": job_id}


@router.post("/{job_id}/retry", response_model=DownloadResponse)
async def retry_download_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    queue: AsyncTaskQueue = Depends(get_task_queue),
) -> DownloadResponse:
    """Retry a failed or cancelled download task."""
    result = await db.execute(select(DownloadJob).where(DownloadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    job.status = JobStatus.PENDING
    job.progress = 0.0
    job.error_message = None
    await db.commit()

    is_audio = (job.requested_format or "").lower() in ("mp3", "m4a", "wav", "flac", "aac", "ogg", "opus")
    queue.submit(
        task_id=job_id,
        coro_fn=lambda: run_download_task(
            job_id=job_id,
            url=job.source_url,
            requested_format=job.requested_format or "mp4",
            requested_quality=job.requested_quality or "best",
            is_audio_only=is_audio,
        ),
    )

    return DownloadResponse(job_id=job_id, status=JobStatus.PENDING, message="Download restarted")


@router.get("/{job_id}/file")
async def download_file(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download the completed media file to client device."""
    result = await db.execute(select(DownloadJob).where(DownloadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.status != JobStatus.COMPLETED or not job.output_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File is not ready. Current status: {job.status.value}",
        )

    file_path = Path(job.output_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file has expired or was removed")

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )


@router.delete("/{job_id}")
async def delete_download(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
) -> dict[str, str]:
    """Delete a download record and its files from disk."""
    result = await db.execute(select(DownloadJob).where(DownloadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    storage.delete_job_files(job_id)
    await db.delete(job)
    await db.commit()

    return {"message": "Job and files deleted successfully", "job_id": job_id}
