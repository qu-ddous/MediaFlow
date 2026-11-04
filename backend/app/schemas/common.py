"""Common Pydantic schemas shared across the API."""

from __future__ import annotations

import enum
from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class JobStatus(str, enum.Enum):
    """Mirror of the DB enum for use in schemas."""

    PENDING = "pending"
    ANALYZING = "analyzing"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    error: str
    detail: str | None = None
    code: str | None = None


class SuccessResponse(BaseModel):
    """Generic success envelope."""

    message: str
    data: Any | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list envelope."""

    items: List[T]
    total: int
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)
    has_next: bool = False
