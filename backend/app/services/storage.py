"""Storage service for handling media files, cleanup, and disk limits."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import time
from pathlib import Path
from uuid import UUID

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Manages file storage, path resolution, quotas, and expiration."""

    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = Path(base_path or settings.STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_job_dir(self, job_id: UUID | str) -> Path:
        """Get or create isolated directory for a specific job."""
        job_dir = self.base_path / str(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def get_file_path(self, job_id: UUID | str, filename: str) -> Path:
        """Resolve full path to a job's media file."""
        return self.get_job_dir(job_id) / filename

    def delete_job_files(self, job_id: UUID | str) -> None:
        """Recursively delete all files associated with a job."""
        job_dir = self.base_path / str(job_id)
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
            logger.info("Deleted job storage: %s", job_id)

    def get_file_size(self, file_path: str | Path) -> int:
        """Get file size in bytes safely."""
        p = Path(file_path)
        return p.stat().st_size if p.exists() else 0

    async def cleanup_expired(self, max_age_hours: int | None = None) -> int:
        """Remove directories older than retention window (default 24h)."""
        age_hours = max_age_hours or settings.FILE_EXPIRY_HOURS
        cutoff = time.time() - (age_hours * 3600)
        deleted_count = 0

        for item in self.base_path.iterdir():
            if item.is_dir():
                try:
                    mtime = item.stat().st_mtime
                    if mtime < cutoff:
                        shutil.rmtree(item, ignore_errors=True)
                        deleted_count += 1
                except Exception as exc:
                    logger.warning("Error checking expiration on %s: %s", item, exc)

        if deleted_count > 0:
            logger.info("Cleaned up %d expired storage directories", deleted_count)
        return deleted_count
