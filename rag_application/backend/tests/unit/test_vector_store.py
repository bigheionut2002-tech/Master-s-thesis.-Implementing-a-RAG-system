"""Unit tests for :class:`VectorStore`.

Uses an in-memory Chroma client so every test gets a fresh store with no
on-disk side effects.
"""

from __future__ import annotations

from pathlib import Path

import chromadb
import pytest

from repositories.vector_store import VectorStore


@pytest.fixture()
def store(tmp_path: Path) -> VectorStore:
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    return VectorStore(client)


def _emb(x: float, y: float) -> list[float]:
    """Build a 3-D embedding with a dominant direction for deterministic search."""
    return [x, y, 0.0]


def _meta(document_id: str, filename: str, page: int) -> dict:
    return {"document_id": document_id, "filename": filename, "page": page}


def test_add_and_query_round_trip(store: VectorStore) -> None:
    store.add_chunks(
        user_id=1,
        chunks=["apples are red", "bananas are yellow"],
        embeddings=[_emb(1.0, 0.0), _emb(0.0, 1.0)],
        metadatas=[
            _meta("doc1", "fruits.pdf", 1),
            _meta("doc1", "fruits.pdf", 2),
        ],
    )

    results = store.query(user_id=1, query_embedding=_emb(1.0, 0.0), top_k=2)

    assert len(results) == 2
    top_text, top_citation = results[0]
    assert top_text == "apples are red"
    assert top_citation.filename == "fruits.pdf"
    assert top_citation.page == 1


def test_query_respects_top_k(store: VectorStore) -> None:
    store.add_chunks(
        user_id=1,
        chunks=[f"chunk {i}" for i in range(5)],
        embeddings=[_emb(float(i), 0.0) for i in range(5)],
        metadatas=[_meta("doc1", "f.pdf", i + 1) for i in range(5)],
    )

    results = store.query(user_id=1, query_embedding=_emb(2.0, 0.0), top_k=3)
    assert len(results) == 3


def test_query_empty_collection_returns_empty_list(store: VectorStore) -> None:
    results = store.query(user_id=99, query_embedding=_emb(1.0, 0.0), top_k=5)
    assert results == []


def test_collections_are_isolated_per_user(store: VectorStore) -> None:
    store.add_chunks(
        user_id=1,
        chunks=["user one secret"],
        embeddings=[_emb(1.0, 0.0)],
        metadatas=[_meta("doc1", "a.pdf", 1)],
    )
    store.add_chunks(
        user_id=2,
        chunks=["user two public"],
        embeddings=[_emb(1.0, 0.0)],
        metadatas=[_meta("doc2", "b.pdf", 1)],
    )

    results_u1 = store.query(user_id=1, query_embedding=_emb(1.0, 0.0), top_k=5)
    results_u2 = store.query(user_id=2, query_embedding=_emb(1.0, 0.0), top_k=5)

    assert [text for text, _ in results_u1] == ["user one secret"]
    assert [text for text, _ in results_u2] == ["user two public"]


def test_delete_document_removes_only_that_document(store: VectorStore) -> None:
    store.add_chunks(
        user_id=1,
        chunks=["doc1 chunk a", "doc1 chunk b"],
        embeddings=[_emb(1.0, 0.0), _emb(0.9, 0.1)],
        metadatas=[
            _meta("doc1", "alpha.pdf", 1),
            _meta("doc1", "alpha.pdf", 2),
        ],
    )
    store.add_chunks(
        user_id=1,
        chunks=["doc2 keep"],
        embeddings=[_emb(0.0, 1.0)],
        metadatas=[_meta("doc2", "beta.pdf", 1)],
    )

    store.delete_document(user_id=1, document_id="doc1")

    results = store.query(user_id=1, query_embedding=_emb(0.0, 1.0), top_k=10)
    texts = [text for text, _ in results]
    assert texts == ["doc2 keep"]


def test_list_documents_aggregates_by_document_id(store: VectorStore) -> None:
    store.add_chunks(
        user_id=1,
        chunks=["p1 chunk", "p2 chunk", "p2 chunk extra"],
        embeddings=[_emb(1.0, 0.0), _emb(0.0, 1.0), _emb(0.0, 0.9)],
        metadatas=[
            _meta("doc1", "alpha.pdf", 1),
            _meta("doc1", "alpha.pdf", 2),
            _meta("doc1", "alpha.pdf", 2),
        ],
    )
    store.add_chunks(
        user_id=1,
        chunks=["beta only"],
        embeddings=[_emb(1.0, 0.0)],
        metadatas=[_meta("doc2", "beta.pdf", 1)],
    )

    docs = store.list_documents(user_id=1)
    by_id = {d["id"]: d for d in docs}

    assert set(by_id.keys()) == {"doc1", "doc2"}
    assert by_id["doc1"]["filename"] == "alpha.pdf"
    assert by_id["doc1"]["num_chunks"] == 3
    assert by_id["doc1"]["num_pages"] == 2
    assert by_id["doc2"]["num_chunks"] == 1


def test_add_chunks_noop_on_empty_input(store: VectorStore) -> None:
    store.add_chunks(user_id=1, chunks=[], embeddings=[], metadatas=[])
    assert store.list_documents(user_id=1) == []
