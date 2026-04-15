"""SQLAlchemy engine, session factory, and FastAPI dependency.

The real engine is built lazily from :class:`Settings` so tests can override it
with an in-memory SQLite engine via ``app.dependency_overrides``.
"""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings
from models.db_models import Base


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the application-wide SQLAlchemy engine."""
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True, future=True)


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)


def create_all_tables() -> None:
    """Create every table registered on :class:`Base.metadata`."""
    Base.metadata.create_all(bind=get_engine())


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a scoped database session."""
    session = _session_factory()()
    try:
        yield session
    finally:
        session.close()
