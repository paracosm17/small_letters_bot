from __future__ import annotations

from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CreatedMixin:
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
