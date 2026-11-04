"""Background media processing tasks for downloads and format conversions."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from app.database import async_session_factory
from app.models.audit import DownloadHistory
from app.models.conversion import ConversionJob
from app.models.download import DownloadJob, JobStatus
from app.services.analyzer import _DIRECT_MEDIA_EXTENSIONS
from app.services.converter import ConversionService
from app.services.downloader import DownloadService
from app.utils.file_utils import format_file_size
from app.workers.task_queue import task_queue

logger = logging.getLogger(__name__)


async def run_download_task(
    job_id: str | UUID,
    url: str,
    requested_format: str,
    requested_quality: str,
    is_audio_only: bool = False,
) -> None:
    """Execute complete download pipeline in background, updating DB and SSE."""
    jid = str(job_id)
    downloader = DownloadService()
    converter = ConversionService()

    async with async_session_factory() as session:
        # 1. Update job to DOWNLOADING
        res = await session.execute(select(DownloadJob).where(DownloadJob.id == jid))
        job = res.scalar_one_or_none()
        if not job:
            logger.error("Download job %s not found in DB", jid)
            return

        job.status = JobStatus.DOWNLOADING
        await session.commit()
        await task_queue.update_progress(jid, progress=0.0, status="downloading")

    # Define progress callback
    async def on_progress(pct: float, speed_bytes: float, downloaded_bytes: int):
        speed_str = f"{format_file_size(speed_bytes)}/s" if speed_bytes > 0 else "--"
        await task_queue.update_progress(
            jid,
            progress=pct,
            speed=speed_bytes,
            status="downloading",
            extra={"speed_str": speed_str},
        )
        # Periodic DB update
        async with async_session_factory() as s:
            r = await s.execute(select(DownloadJob).where(DownloadJob.id == jid))
            j = r.scalar_one_or_none()
            if j:
                j.progress = pct
                j.download_speed = speed_str
                await s.commit()

    try:
        # Check if direct media url
        is_direct = any(url.lower().split("?")[0].endswith(ext) for ext in _DIRECT_MEDIA_EXTENSIONS)

        if is_direct:
            filename = url.split("?")[0].split("/")[-1] or f"download_{jid[:8]}.mp4"
            output_file = await downloader.download_direct_stream(
                job_id=jid,
                url=url,
                output_filename=filename,
                progress_callback=on_progress,
            )
        else:
            output_file = await downloader.download_with_ytdlp(
                job_id=jid,
                url=url,
                format_id=requested_quality if requested_quality not in ("best", "default") else None,
                is_audio_only=is_audio_only,
                audio_format=requested_format if is_audio_only else "mp3",
                progress_callback=on_progress,
            )

        # 2. Check if post-download conversion is requested
        final_file = output_file
        ext = output_file.suffix.lstrip(".").lower()
        if requested_format and ext != requested_format.lower() and not is_audio_only:
            await task_queue.update_progress(jid, progress=95.0, status="processing")
            async with async_session_factory() as s:
                r = await s.execute(select(DownloadJob).where(DownloadJob.id == jid))
                j = r.scalar_one_or_none()
                if j:
                    j.status = JobStatus.PROCESSING
                    await s.commit()

            final_file = await converter.convert_file(
                job_id=jid,
                input_file=output_file,
                output_format=requested_format,
            )

        # 3. Mark completed
        file_size = final_file.stat().st_size if final_file.exists() else 0
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=24)

        async with async_session_factory() as s:
            r = await s.execute(select(DownloadJob).where(DownloadJob.id == jid))
            j = r.scalar_one_or_none()
            if j:
                j.status = JobStatus.COMPLETED
                j.progress = 100.0
                j.output_path = str(final_file)
                j.file_size = file_size
                j.expires_at = expires
                if not j.title:
                    j.title = final_file.name

                # Add to download history
                history = DownloadHistory(
                    job_id=j.id,
                    title=j.title,
                    file_name=final_file.name,
                    file_format=final_file.suffix.lstrip(".").lower(),
                    file_size=file_size,
                    source_url=j.source_url,
                    status=JobStatus.COMPLETED.value,
                )
                s.add(history)
                await s.commit()

        await task_queue.update_progress(
            jid,
            progress=100.0,
            status="completed",
            extra={"filename": final_file.name, "file_size": file_size},
        )

    except asyncio.CancelledError:
        logger.info("Download task %s was cancelled", jid)
        async with async_session_factory() as s:
            r = await s.execute(select(DownloadJob).where(DownloadJob.id == jid))
            j = r.scalar_one_or_none()
            if j:
                j.status = JobStatus.CANCELLED
                await s.commit()
        await task_queue.update_progress(jid, progress=0.0, status="cancelled")

    except Exception as exc:
        logger.error("Download task %s failed: %s", jid, exc, exc_info=True)
        async with async_session_factory() as s:
            r = await s.execute(select(DownloadJob).where(DownloadJob.id == jid))
            j = r.scalar_one_or_none()
            if j:
                j.status = JobStatus.FAILED
                j.error_message = str(exc)
                await s.commit()
        await task_queue.update_progress(jid, progress=0.0, status="failed", extra={"error": str(exc)})


async def run_conversion_task(
    job_id: str | UUID,
    input_path: str,
    output_format: str,
    resolution: str | None = None,
    audio_only: bool = False,
    quality: str = "192k",
) -> None:
    """Execute media transcoding in background."""
    jid = str(job_id)
    converter = ConversionService()

    async with async_session_factory() as session:
        res = await session.execute(select(ConversionJob).where(ConversionJob.id == jid))
        job = res.scalar_one_or_none()
        if not job:
            return
        job.status = JobStatus.PROCESSING
        await session.commit()

    async def on_progress(pct: float):
        await task_queue.update_progress(jid, progress=pct, status="processing")
        async with async_session_factory() as s:
            r = await s.execute(select(ConversionJob).where(ConversionJob.id == jid))
            j = r.scalar_one_or_none()
            if j:
                j.progress = pct
                await s.commit()

    try:
        out_file = await converter.convert_file(
            job_id=jid,
            input_file=input_path,
            output_format=output_format,
            resolution=resolution,
            audio_only=audio_only,
            quality=quality,
            progress_callback=on_progress,
        )

        async with async_session_factory() as s:
            r = await s.execute(select(ConversionJob).where(ConversionJob.id == jid))
            j = r.scalar_one_or_none()
            if j:
                j.status = JobStatus.COMPLETED
                j.progress = 100.0
                j.output_path = str(out_file)
                await s.commit()

        await task_queue.update_progress(jid, progress=100.0, status="completed", extra={"output_path": str(out_file)})

    except Exception as exc:
        logger.error("Conversion task %s failed: %s", jid, exc)
        async with async_session_factory() as s:
            r = await s.execute(select(ConversionJob).where(ConversionJob.id == jid))
            j = r.scalar_one_or_none()
            if j:
                j.status = JobStatus.FAILED
                j.error_message = str(exc)
                await s.commit()
        await task_queue.update_progress(jid, progress=0.0, status="failed", extra={"error": str(exc)})
