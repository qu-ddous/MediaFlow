"""API route for URL media analysis."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_analyzer_service
from app.database import get_db
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import AnalyzerError, MediaAnalyzer
from app.services.security import SecurityError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_media_url(
    req: AnalyzeRequest,
    analyzer: MediaAnalyzer = Depends(get_analyzer_service),
) -> AnalyzeResponse:
    """Analyze a media URL to extract metadata and available download options."""
    try:
        url_str = str(req.url)
        return await analyzer.analyze_url(url_str)
    except SecurityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Security validation failed", "message": exc.message, "code": "ssrf_violation"},
        )
    except AnalyzerError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Analysis failed", "message": exc.message, "code": exc.code},
        )
    except Exception as exc:
        logger.error("Unexpected error in /analyze: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal error", "message": "Failed to analyze URL. Please check the link and try again."},
        )
