"""Vector store repository (stub).

Wraps ChromaDB so the service layer works against a stable interface regardless
of the underlying vector database implementation.
"""

from __future__ import annotations

from models.schemas import SourceCitation


class VectorStore:
    """Per-user ChromaDB collection access."""

    def add_chunks(
        self,
        user_id: int,
        chunks: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, str | int]],
    ) -> None:
        raise NotImplementedError

    def query(
        self,
        user_id: int,
        query_embedding: list[float],
        top_k: int,
    ) -> list[tuple[str, SourceCitation]]:
        """Return a list of ``(chunk_text, source_citation)`` pairs."""
        raise NotImplementedError

    def delete_document(self, user_id: int, document_id: str) -> None:
        raise NotImplementedError
