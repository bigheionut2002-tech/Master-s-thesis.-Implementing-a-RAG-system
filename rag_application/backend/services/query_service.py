"""RAG query service (stub).

Pipeline: embed query, search the user's ChromaDB collection, build the
prompt with retrieved context, call Gemini, return answer plus source
citations.
"""

from __future__ import annotations

from models.schemas import QueryResponse


class QueryService:
    """Retrieval-augmented question answering."""

    def answer(self, user_id: int, question: str) -> QueryResponse:
        raise NotImplementedError
