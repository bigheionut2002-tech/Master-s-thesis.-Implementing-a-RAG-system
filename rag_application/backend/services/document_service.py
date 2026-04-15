"""Document ingestion service.

Orchestrates the PDF ingestion pipeline: open the uploaded bytes with
PyMuPDF, extract the text of each page, split it into overlapping chunks,
compute embeddings via the Gemini API, and persist the chunks in the
per-user ChromaDB collection. Also exposes listing and deletion so that the
HTTP layer does not need to know about the vector store.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

import fitz  # PyMuPDF

from core.constants import CHUNK_OVERLAP_TOKENS, CHUNK_SIZE_TOKENS
from models.schemas import DocumentMetadata
from repositories.vector_store import VectorStore
from services.embedding_service import EmbeddingService
from services.text_chunker import chunk_text

logger = logging.getLogger(__name__)


class DocumentService:
    """Handle PDF upload, text extraction, chunking, embedding, and storage."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
        chunk_size: int = CHUNK_SIZE_TOKENS,
        chunk_overlap: int = CHUNK_OVERLAP_TOKENS,
    ) -> None:
        self._vector_store = vector_store
        self._embeddings = embedding_service
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def ingest_pdf(
        self,
        user_id: int,
        pdf_bytes: bytes,
        filename: str,
    ) -> DocumentMetadata:
        """Ingest one PDF for ``user_id`` and return its stored metadata."""
        document_id = str(uuid.uuid4())
        chunks, metadatas, num_pages = self._extract_chunks(
            pdf_bytes=pdf_bytes,
            filename=filename,
            document_id=document_id,
        )

        if not chunks:
            logger.warning("No extractable text in %s for user %d", filename, user_id)
            return DocumentMetadata(
                id=document_id,
                filename=filename,
                num_pages=num_pages,
                num_chunks=0,
            )

        embeddings = self._embeddings.embed_documents(chunks)
        self._vector_store.add_chunks(
            user_id=user_id,
            chunks=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info(
            "Ingested %s for user %d: %d pages, %d chunks",
            filename,
            user_id,
            num_pages,
            len(chunks),
        )
        return DocumentMetadata(
            id=document_id,
            filename=filename,
            num_pages=num_pages,
            num_chunks=len(chunks),
        )

    def list_documents(self, user_id: int) -> list[DocumentMetadata]:
        """Return a summary of every document stored for ``user_id``."""
        raw = self._vector_store.list_documents(user_id=user_id)
        return [
            DocumentMetadata(
                id=entry["id"],
                filename=entry["filename"],
                num_pages=int(entry["num_pages"]),
                num_chunks=int(entry["num_chunks"]),
            )
            for entry in raw
        ]

    def delete_document(self, user_id: int, document_id: str) -> None:
        """Remove ``document_id`` from the user's collection."""
        self._vector_store.delete_document(user_id=user_id, document_id=document_id)

    def _extract_chunks(
        self,
        pdf_bytes: bytes,
        filename: str,
        document_id: str,
    ) -> tuple[list[str], list[dict[str, Any]], int]:
        chunks: list[str] = []
        metadatas: list[dict[str, Any]] = []
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        try:
            num_pages = pdf.page_count
            for page_index in range(num_pages):
                page = pdf[page_index]
                page_text = page.get_text("text") or ""
                page_chunks = chunk_text(
                    page_text,
                    chunk_size=self._chunk_size,
                    overlap=self._chunk_overlap,
                )
                for chunk in page_chunks:
                    chunks.append(chunk)
                    metadatas.append(
                        {
                            "document_id": document_id,
                            "filename": filename,
                            "page": page_index + 1,
                        }
                    )
        finally:
            pdf.close()
        return chunks, metadatas, num_pages
