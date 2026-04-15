"""Unit tests for :class:`DocumentService`.

A fresh real ChromaDB collection is used per test via :func:`tmp_path`, while
the embedding service is replaced with a deterministic fake that returns a
unique vector per call. PDFs are generated in-memory with PyMuPDF so no
fixture files need to be committed to the repository.
"""

from __future__ import annotations

from pathlib import Path

import chromadb
import fitz
import pytest

from repositories.vector_store import VectorStore
from services.document_service import DocumentService


class _StubEmbeddings:
    def __init__(self) -> None:
        self.batches: list[list[str]] = []

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.batches.append(list(texts))
        return [[float(i), 0.0, 0.0] for i, _ in enumerate(texts)]

    def embed_query(self, text: str) -> list[float]:  # pragma: no cover
        return [0.0, 0.0, 0.0]


def _build_pdf(pages: list[str]) -> bytes:
    doc = fitz.open()
    for body in pages:
        page = doc.new_page()
        page.insert_text((72, 72), body, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture()
def service(tmp_path: Path) -> tuple[DocumentService, VectorStore, _StubEmbeddings]:
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    store = VectorStore(client)
    embeddings = _StubEmbeddings()
    doc_service = DocumentService(vector_store=store, embedding_service=embeddings)
    return doc_service, store, embeddings


def test_ingest_pdf_extracts_chunks_and_stores_them(
    service: tuple[DocumentService, VectorStore, _StubEmbeddings],
) -> None:
    doc_service, store, embeddings = service
    pdf_bytes = _build_pdf(
        [
            "This is page one with information about apples and oranges.",
            "This is page two which talks about bananas and grapes.",
        ]
    )

    metadata = doc_service.ingest_pdf(user_id=1, pdf_bytes=pdf_bytes, filename="fruit.pdf")

    assert metadata.filename == "fruit.pdf"
    assert metadata.num_pages == 2
    assert metadata.num_chunks >= 2  # at least one per non-empty page
    assert embeddings.batches, "embedding service should have been called"

    stored = store.list_documents(user_id=1)
    assert len(stored) == 1
    assert stored[0]["filename"] == "fruit.pdf"
    assert stored[0]["num_chunks"] == metadata.num_chunks
    assert stored[0]["num_pages"] == 2


def test_ingest_pdf_skips_empty_pages(
    service: tuple[DocumentService, VectorStore, _StubEmbeddings],
) -> None:
    doc_service, store, _ = service
    pdf_bytes = _build_pdf(["only page with text"])

    metadata = doc_service.ingest_pdf(user_id=1, pdf_bytes=pdf_bytes, filename="one.pdf")

    assert metadata.num_pages == 1
    assert metadata.num_chunks == 1
    stored = store.list_documents(user_id=1)
    assert stored[0]["num_chunks"] == 1


def test_list_documents_returns_document_metadata(
    service: tuple[DocumentService, VectorStore, _StubEmbeddings],
) -> None:
    doc_service, _, _ = service
    doc_service.ingest_pdf(
        user_id=1, pdf_bytes=_build_pdf(["alpha content"]), filename="a.pdf"
    )
    doc_service.ingest_pdf(
        user_id=1, pdf_bytes=_build_pdf(["beta content"]), filename="b.pdf"
    )

    docs = doc_service.list_documents(user_id=1)
    filenames = sorted(d.filename for d in docs)
    assert filenames == ["a.pdf", "b.pdf"]


def test_delete_document_removes_it_from_vector_store(
    service: tuple[DocumentService, VectorStore, _StubEmbeddings],
) -> None:
    doc_service, _, _ = service
    metadata = doc_service.ingest_pdf(
        user_id=1, pdf_bytes=_build_pdf(["content to be removed"]), filename="gone.pdf"
    )
    assert len(doc_service.list_documents(user_id=1)) == 1

    doc_service.delete_document(user_id=1, document_id=metadata.id)

    assert doc_service.list_documents(user_id=1) == []


def test_ingest_pdf_with_no_extractable_text_returns_zero_chunks(
    service: tuple[DocumentService, VectorStore, _StubEmbeddings],
) -> None:
    doc_service, _, embeddings = service
    doc = fitz.open()
    doc.new_page()  # blank page
    data = doc.tobytes()
    doc.close()

    metadata = doc_service.ingest_pdf(user_id=1, pdf_bytes=data, filename="blank.pdf")
    assert metadata.num_chunks == 0
    # No embedding calls when there is nothing to embed.
    assert embeddings.batches == []
