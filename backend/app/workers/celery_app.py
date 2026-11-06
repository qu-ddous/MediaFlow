"""Celery configuration and task definitions for distributed production workers."""

from __future__ import annotations

import asyncio
import logging
import os

from app.config import settings

logger = logging.getLogger(__name__)

# Check if redis is configured
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

try:
    from celery import Celery

    celery_app = Celery(
        "mediaflow",
        broker=REDIS_URL,
        backend=REDIS_URL,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=settings.download_timeout_seconds,
        worker_prefetch_multiplier=1,
    )

    @celery_app.task(name="tasks.download_media")
    def celery_download_media(job_id: str, url: str, fmt: str, quality: str):
        """Celery wrapper task for media downloads."""
        from app.workers.media_tasks import run_download_task

        logger.info("[Celery Worker] Starting download for job %s", job_id)
        asyncio.run(run_download_task(job_id, url, fmt, quality))

    @celery_app.task(name="tasks.convert_media")
    def celery_convert_media(job_id: str, input_path: str, output_format: str, resolution: str | None = None):
        """Celery wrapper task for media conversion."""
        from app.workers.media_tasks import run_conversion_task

        logger.info("[Celery Worker] Starting conversion for job %s", job_id)
        asyncio.run(run_conversion_task(job_id, input_path, output_format, resolution))

except ImportError:
    celery_app = None  # Celery optional in local dev mode

