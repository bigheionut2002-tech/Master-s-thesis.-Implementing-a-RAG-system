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
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import numpy as np

from core.constants import CHUNK_OVERLAP_TOKENS, CHUNK_SIZE_TOKENS
from models.schemas import DocumentMetadata, VectorMapResponse
from repositories.vector_store import VectorStore
from services.embedding_service import EmbeddingService
from services.text_chunker import chunk_text

logger = logging.getLogger(__name__)


def _compute_chunk_bbox(chunk: str, pdf_words: list) -> str:
    """Return "x0,y0,x1,y1" for the word sequence that makes up *chunk*.

    Both *chunk* and *pdf_words* originate from the same PyMuPDF page, so the
    word tokens are identical after split(). We slide a fingerprint of the
    first few chunk words over the word list to locate the start, then take the
    union bounding-box of all words in the chunk.
    """
    chunk_words = chunk.split()
    if not chunk_words or not pdf_words:
        return ""

    n = len(chunk_words)
    m = len(pdf_words)
    if n > m:
        return ""

    fp_len = min(5, n)
    fp = chunk_words[:fp_len]

    start_idx: int | None = None
    for i in range(m - fp_len + 1):
        if [w[4] for w in pdf_words[i : i + fp_len]] == fp:
            start_idx = i
            break

    if start_idx is None:
        return ""

    end_idx = min(start_idx + n - 1, m - 1)
    relevant = pdf_words[start_idx : end_idx + 1]
    x0 = min(w[0] for w in relevant)
    y0 = min(w[1] for w in relevant)
    x1 = max(w[2] for w in relevant)
    y1 = max(w[3] for w in relevant)
    return f"{x0:.2f},{y0:.2f},{x1:.2f},{y1:.2f}"


class DocumentService:
    """Handle PDF upload, text extraction, chunking, embedding, and storage."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
        upload_dir: Path,
        chunk_size: int = CHUNK_SIZE_TOKENS,
        chunk_overlap: int = CHUNK_OVERLAP_TOKENS,
    ) -> None:
        self._vector_store = vector_store
        self._embeddings = embedding_service
        self._upload_dir = upload_dir
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def ingest_pdf(
        self,
        user_id: int,
        pdf_bytes: bytes,
        filename: str,
    ) -> DocumentMetadata:
        """Ingest one PDF for ``user_id`` and return its stored metadata."""
        user_dir = self._upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        (user_dir / filename).write_bytes(pdf_bytes)

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

    def get_vector_map(self, user_id: int) -> list[dict]:
        """Return all chunks projected to 2-D via PCA (SVD) for vector map visualisation."""
        chunks = self._vector_store.get_all_chunks_with_embeddings(user_id)
        if len(chunks) < 2:
            for i, c in enumerate(chunks):
                c["x"], c["y"] = float(i), 0.0
            return chunks
        embeddings = np.array([c["embedding"] for c in chunks], dtype=float)
        embeddings -= embeddings.mean(axis=0)
        _, _, Vt = np.linalg.svd(embeddings, full_matrices=False)
        projected = embeddings @ Vt[:2].T
        # Normalize to [-1, 1] range
        for axis in range(2):
            col = projected[:, axis]
            rng = col.max() - col.min()
            if rng > 0:
                projected[:, axis] = (col - col.min()) / rng * 2 - 1
        for i, c in enumerate(chunks):
            c["x"] = float(projected[i, 0])
            c["y"] = float(projected[i, 1])
        return chunks

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
                pdf_words = page.get_text("words")  # (x0,y0,x1,y1,word,block,line,word_no)
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
                            "bbox": _compute_chunk_bbox(chunk, pdf_words),
                        }
                    )
        finally:
            pdf.close()
        return chunks, metadatas, num_pages
