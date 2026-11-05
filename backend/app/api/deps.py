"""FastAPI dependency injection providers."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.analyzer import MediaAnalyzer
from app.services.converter import ConversionService
from app.services.downloader import DownloadService
from app.services.media_engine import FFmpegEngine
from app.services.storage import StorageService
from app.workers.task_queue import AsyncTaskQueue, task_queue


def get_storage_service() -> StorageService:
    return StorageService()


def get_ffmpeg_engine() -> FFmpegEngine:
    return FFmpegEngine()


def get_analyzer_service() -> MediaAnalyzer:
    return MediaAnalyzer()


def get_download_service() -> DownloadService:
    return DownloadService()


def get_conversion_service() -> ConversionService:
    return ConversionService()


def get_task_queue() -> AsyncTaskQueue:
    return task_queue

