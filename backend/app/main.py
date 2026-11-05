"""Main FastAPI application entrypoint for MediaFlow."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import v1_router
from app.config import settings
from app.database import create_tables, dispose_engine
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import limiter
from app.middleware.security import SecurityHeadersMiddleware
from app.services.storage import StorageService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mediaflow")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle handler."""
    logger.info("Initializing MediaFlow backend (version %s)...", settings.app_version)
    # Ensure tables exist
    await create_tables()
    # Ensure storage paths exist
    storage = StorageService()
    logger.info("Storage initialized at: %s", storage.base_path)
    yield
    logger.info("Shutting down MediaFlow...")
    await dispose_engine()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Universal Media Downloader & Transcoder Engine",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Mount API Routers
app.include_router(v1_router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "api_v1": "/api/v1",
    }

