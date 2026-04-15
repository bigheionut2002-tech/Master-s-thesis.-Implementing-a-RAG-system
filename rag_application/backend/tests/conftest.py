"""Shared pytest fixtures.

Every secret is stubbed before any application module is imported, the
PostgreSQL dependency is replaced with an in-memory SQLite database, and
the Gemini-backed services (embedding and generation) are replaced with
deterministic fakes so integration tests never touch the network.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-do-not-use-in-prod")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("POSTGRES_PASSWORD", "test-password")

import chromadb  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from api.dependencies import (  # noqa: E402
    get_embedding_service,
    get_generation_service,
    get_vector_store,
)
from core.database import get_db  # noqa: E402
from main import app  # noqa: E402
from models.db_models import Base  # noqa: E402
from repositories.vector_store import VectorStore  # noqa: E402


class FakeEmbeddingService:
    """Deterministic embedding stub: hashes text to a 3-D vector."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

    @staticmethod
    def _vector(text: str) -> list[float]:
        length = float(len(text))
        vowels = float(sum(ch in "aeiou" for ch in text.lower()))
        digits = float(sum(ch.isdigit() for ch in text))
        return [length, vowels, digits]


class FakeGenerationService:
    """Generation stub that echoes the first retrieved excerpt (if any)."""

    def __init__(self) -> None:
        self.last_prompt: str | None = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        # Return a canned reply that contains enough info to assert on.
        return "Answer produced from retrieved excerpts."


@pytest.fixture()
def engine() -> Iterator[Engine]:
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
def client(engine: Engine, tmp_path: Path) -> Iterator[TestClient]:
    """Return a FastAPI TestClient with DB, vector store, and LLM overridden."""
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    def override_get_db() -> Iterator[Session]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    chroma_client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    vector_store = VectorStore(chroma_client)
    embedding_service = FakeEmbeddingService()
    generation_service = FakeGenerationService()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_vector_store] = lambda: vector_store
    app.dependency_overrides[get_embedding_service] = lambda: embedding_service
    app.dependency_overrides[get_generation_service] = lambda: generation_service
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_vector_store, None)
        app.dependency_overrides.pop(get_embedding_service, None)
        app.dependency_overrides.pop(get_generation_service, None)
