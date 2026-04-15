"""Embedding service (stub).

Wraps the Google Gemini embeddings API so the rest of the codebase does not
depend on the vendor SDK directly.
"""

from __future__ import annotations


class EmbeddingService:
    """Compute dense embeddings via Google Gemini."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError
