"""Aggregate router for v1 API endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.analyze import router as analyze_router
from app.api.v1.conversions import router as conversions_router
from app.api.v1.downloads import router as downloads_router
from app.api.v1.events import router as events_router
from app.api.v1.health import router as health_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(health_router)
v1_router.include_router(analyze_router)
v1_router.include_router(downloads_router)
v1_router.include_router(conversions_router)
v1_router.include_router(events_router)

