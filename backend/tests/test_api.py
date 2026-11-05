"""Tests for FastAPI endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "MediaFlow"
    assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_capabilities_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert "supported_video_formats" in data
    assert "mp4" in data["supported_video_formats"]
    assert "supported_audio_formats" in data


@pytest.mark.asyncio
async def test_create_and_get_download_job(client: AsyncClient):
    payload = {
        "url": "https://example.com/sample.mp4",
        "format": "mp4",
        "quality": "1080p",
    }
    create_resp = await client.post("/api/v1/downloads", json=payload)
    assert create_resp.status_code == 201
    create_data = create_resp.json()
    assert "job_id" in create_data
    job_id = create_data["job_id"]

    # Fetch job detail
    detail_resp = await client.get(f"/api/v1/downloads/{job_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["job_id"] == job_id
    assert detail_data["source_url"] == "https://example.com/sample.mp4"

    # Cancel job
    cancel_resp = await client.post(f"/api/v1/downloads/{job_id}/cancel")
    assert cancel_resp.status_code == 200

