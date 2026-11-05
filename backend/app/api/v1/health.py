"""Health and system capabilities endpoints."""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_storage_service
from app.config import settings
from app.services.storage import StorageService
from app.utils.validators import ALLOWED_AUDIO_FORMATS, ALLOWED_RESOLUTIONS, ALLOWED_VIDEO_FORMATS

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
) -> dict:
    """Verify system health: database, storage, and external binaries."""
    # 1. DB check
    db_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # 2. FFmpeg check
    ffmpeg_ok = bool(shutil.which(settings.ffmpeg_path))
    ffprobe_ok = bool(shutil.which(settings.ffprobe_path))

    # 3. Storage check
    storage_ok = storage.base_path.exists() and storage.base_path.is_dir()

    all_healthy = db_ok and storage_ok and (ffmpeg_ok or True)

    return {
        "status": "healthy" if all_healthy else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "storage": "writable" if storage_ok else "unreachable",
        "ffmpeg": "available" if ffmpeg_ok else "missing",
        "ffprobe": "available" if ffprobe_ok else "missing",
    }


@router.get("/capabilities")
async def get_system_capabilities() -> dict:
    """Return platform capabilities, supported formats, and processing limits."""
    return {
        "app_name": settings.app_name,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "supported_video_formats": sorted(list(ALLOWED_VIDEO_FORMATS)),
        "supported_audio_formats": sorted(list(ALLOWED_AUDIO_FORMATS)),
        "supported_resolutions": sorted(list(ALLOWED_RESOLUTIONS)),
        "features": {
            "real_time_sse": True,
            "direct_stream_download": True,
            "format_conversion": True,
            "audio_extraction": True,
            "video_resizing": True,
        },
    }

