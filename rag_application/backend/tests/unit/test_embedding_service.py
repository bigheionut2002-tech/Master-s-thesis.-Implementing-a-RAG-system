"""Unit tests for :class:`EmbeddingService`.

The Google Gemini SDK is monkeypatched so the tests are hermetic.
"""

from __future__ import annotations

from typing import Any

import pytest

from services import embedding_service as module_under_test
from services.embedding_service import EmbeddingService


@pytest.fixture()
def fake_embed(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Replace ``genai.embed_content`` with a stub and capture its calls."""
    calls: list[dict[str, Any]] = []

    def _fake_embed_content(*, model: str, content: Any, task_type: str) -> dict[str, Any]:
        calls.append({"model": model, "content": content, "task_type": task_type})
        if isinstance(content, list):
            return {"embedding": [[0.1, 0.2, 0.3] for _ in content]}
        return {"embedding": [0.5, 0.6, 0.7]}

    monkeypatch.setattr(module_under_test.genai, "embed_content", _fake_embed_content)
    monkeypatch.setattr(module_under_test.genai, "configure", lambda **_: None)
    return calls


def test_embed_documents_uses_retrieval_document_task_type(
    fake_embed: list[dict[str, Any]],
) -> None:
    service = EmbeddingService(api_key="fake")
    vectors = service.embed_documents(["first chunk", "second chunk"])

    assert len(vectors) == 2
    assert vectors[0] == [0.1, 0.2, 0.3]
    assert len(fake_embed) == 1
    assert fake_embed[0]["task_type"] == "retrieval_document"
    assert fake_embed[0]["content"] == ["first chunk", "second chunk"]


def test_embed_documents_empty_list_returns_empty(
    fake_embed: list[dict[str, Any]],
) -> None:
    service = EmbeddingService(api_key="fake")
    assert service.embed_documents([]) == []
    assert fake_embed == []


def test_embed_query_uses_retrieval_query_task_type(
    fake_embed: list[dict[str, Any]],
) -> None:
    service = EmbeddingService(api_key="fake")
    vector = service.embed_query("what is the probation period?")

    assert vector == [0.5, 0.6, 0.7]
    assert len(fake_embed) == 1
    assert fake_embed[0]["task_type"] == "retrieval_query"
    assert fake_embed[0]["content"] == "what is the probation period?"
