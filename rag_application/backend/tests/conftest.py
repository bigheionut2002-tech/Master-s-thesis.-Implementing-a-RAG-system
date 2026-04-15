"""Shared pytest fixtures.

Test environment is isolated from the real ``.env`` by setting stub values for
secrets before any application module is imported.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-do-not-use-in-prod")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("POSTGRES_PASSWORD", "test-password")

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402


@pytest.fixture()
def client() -> TestClient:
    """Return a FastAPI TestClient for integration tests."""
    return TestClient(app)
