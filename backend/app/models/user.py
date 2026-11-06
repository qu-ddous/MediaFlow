"""User and SystemSettings models for authentication, preferences, and system limits."""

from __future__ import annotations

import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(UUIDMixin, TimestampMixin, Base):
    """User account model for persistent history and personal preferences."""

    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(32), default=UserRole.GUEST.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferred_format: Mapped[str | None] = mapped_column(String(32), default="mp4", nullable=True)
    preferred_quality: Mapped[str | None] = mapped_column(String(32), default="1080p", nullable=True)


class SystemSetting(UUIDMixin, TimestampMixin, Base):
    """Key-value system configuration stored in database."""

    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

