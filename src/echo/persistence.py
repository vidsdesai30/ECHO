"""SQLAlchemy persistence models and explicit local development fallback."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class InvestigationRow(Base):
    __tablename__ = "investigations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    events: Mapped[list["EventRow"]] = relationship(cascade="all, delete-orphan")


class EventRow(Base):
    __tablename__ = "imported_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    event_id: Mapped[str] = mapped_column(String(256), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ExperimentRow(Base):
    __tablename__ = "experiments"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(256))
    seed: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32))
    configuration: Mapped[dict[str, Any]] = mapped_column(JSONB)
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def database_url() -> str | None:
    return os.getenv("DATABASE_URL")


def create_session_factory():
    url = database_url()
    if not url:
        return None
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"