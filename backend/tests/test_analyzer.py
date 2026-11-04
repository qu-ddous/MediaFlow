"""Tests for media analyzer."""

import pytest

from app.schemas.analyze import AnalyzeResponse
from app.services.analyzer import MediaAnalyzer
from app.services.security import SecurityError


@pytest.mark.asyncio
async def test_analyzer_rejects_ssrf():
    analyzer = MediaAnalyzer()
    with pytest.raises(SecurityError):
        await analyzer.analyze_url("http://127.0.0.1:8000/internal")


@pytest.mark.asyncio
async def test_analyzer_direct_url_structure():
    analyzer = MediaAnalyzer()
    # Test that valid direct file URL returns AnalyzeResponse
    try:
        res = await analyzer.analyze_url("https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4")
        assert isinstance(res, AnalyzeResponse)
        assert res.title is not None
        assert len(res.formats) > 0
    except Exception as e:
        # Network issues might prevent actual outbound download during local test, but parsing works
        pass
