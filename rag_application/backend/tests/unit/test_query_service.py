"""Unit tests for :class:`QueryService`.

Uses a real in-memory vector store seeded with known chunks, while the
embedding and generation services are replaced with deterministic fakes.
"""

from __future__ import annotations

from pathlib import Path

import chromadb
import pytest

from models.schemas import QueryResponse
from repositories.vector_store import VectorStore
from services.query_service import QueryService


class _FakeEmbeddings:
    def __init__(self, vector: list[float]) -> None:
        self._vector = vector
        self.query_calls: list[str] = []

    def embed_documents(self, texts: list[str]) -> list[list[float]]:  # pragma: no cover
        return [list(self._vector) for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        self.query_calls.append(text)
        return list(self._vector)


class _FakeGenerator:
    def __init__(self, reply: str = "Perioada de probă este de 90 de zile.") -> None:
        self._reply = reply
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._reply


@pytest.fixture()
def seeded_store(tmp_path: Path) -> VectorStore:
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    store = VectorStore(client)
    store.add_chunks(
        user_id=1,
        chunks=[
            "Perioada de proba este de 90 de zile conform contractului colectiv.",
            "Concediul de odihna este de 21 de zile lucratoare.",
        ],
        embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        metadatas=[
            {"document_id": "doc1", "filename": "contract.pdf", "page": 12},
            {"document_id": "doc1", "filename": "contract.pdf", "page": 18},
        ],
    )
    return store


def test_answer_returns_llm_reply_and_unique_sources(seeded_store: VectorStore) -> None:
    embeddings = _FakeEmbeddings(vector=[1.0, 0.0, 0.0])
    generator = _FakeGenerator()
    service = QueryService(
        embedding_service=embeddings,  # type: ignore[arg-type]
        vector_store=seeded_store,
        generation_service=generator,  # type: ignore[arg-type]
        top_k=5,
    )

    response = service.answer(user_id=1, question="Care este perioada de proba?")

    assert isinstance(response, QueryResponse)
    assert response.answer == "Perioada de probă este de 90 de zile."
    assert len(response.sources) >= 1
    assert response.sources[0].filename == "contract.pdf"
    assert embeddings.query_calls == ["Care este perioada de proba?"]
    assert len(generator.prompts) == 1
    assert "Perioada de proba" in generator.prompts[0]


def test_answer_with_empty_collection_returns_fallback(tmp_path: Path) -> None:
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    store = VectorStore(client)
    embeddings = _FakeEmbeddings(vector=[1.0, 0.0, 0.0])
    generator = _FakeGenerator()
    service = QueryService(
        embedding_service=embeddings,  # type: ignore[arg-type]
        vector_store=store,
        generation_service=generator,  # type: ignore[arg-type]
    )

    response = service.answer(user_id=42, question="Orice intrebare")

    assert "not in the provided documents" in response.answer.lower()
    assert response.sources == []
    # The LLM must not be invoked when there is nothing to ground on.
    assert generator.prompts == []


def test_answer_deduplicates_sources_by_filename_and_page(tmp_path: Path) -> None:
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    store = VectorStore(client)
    store.add_chunks(
        user_id=1,
        chunks=["first chunk on page 3", "second chunk on page 3"],
        embeddings=[[1.0, 0.0, 0.0], [0.9, 0.1, 0.0]],
        metadatas=[
            {"document_id": "doc1", "filename": "manual.pdf", "page": 3},
            {"document_id": "doc1", "filename": "manual.pdf", "page": 3},
        ],
    )
    service = QueryService(
        embedding_service=_FakeEmbeddings(vector=[1.0, 0.0, 0.0]),  # type: ignore[arg-type]
        vector_store=store,
        generation_service=_FakeGenerator(),  # type: ignore[arg-type]
    )

    response = service.answer(user_id=1, question="anything")
    assert len(response.sources) == 1
    assert response.sources[0].filename == "manual.pdf"
    assert response.sources[0].page == 3
