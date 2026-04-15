"""Shared pytest fixtures.

Test environment is isolated from the real ``.env`` by setting stub values for
secrets before any application module is imported. The database is overridden
with an in-memory SQLite instance using a shared connection so that every
request inside a test sees the same schema.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-do-not-use-in-prod")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("POSTGRES_PASSWORD", "test-password")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from core.database import get_db  # noqa: E402
from main import app  # noqa: E402
from models.db_models import Base  # noqa: E402


@pytest.fixture()
def engine() -> Iterator[Engine]:
    """Create a fresh in-memory SQLite engine per test and drop it after."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=test_engine)
    try:
        yield test_engine
    finally:
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture()
def db_session(engine: Engine) -> Iterator[Session]:
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(engine: Engine) -> Iterator[TestClient]:
    """Return a FastAPI TestClient with the DB dependency overridden."""
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    def override_get_db() -> Iterator[Session]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
