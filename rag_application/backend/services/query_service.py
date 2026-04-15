"""RAG query service.

Pipeline: embed the user's question, retrieve the top-``k`` chunks from the
user's ChromaDB collection, build a prompt that binds the language model to
the retrieved evidence, call Gemini, and return the answer together with a
deduplicated list of source citations.
"""

from __future__ import annotations

import logging

from core.constants import TOP_K_RESULTS
from models.schemas import QueryResponse, SourceCitation
from repositories.vector_store import VectorStore
from services.embedding_service import EmbeddingService
from services.generation_service import GenerationService

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """You are a helpful assistant that answers questions using \
only the provided document excerpts. If the answer is not contained in the \
excerpts, reply exactly: "The answer is not in the provided documents."

Answer in the same language as the question.

Document excerpts:
{context}

Question: {question}

Answer:"""

_FALLBACK_ANSWER = "The answer is not in the provided documents."


class QueryService:
    """Retrieval-augmented question answering."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        generation_service: GenerationService,
        top_k: int = TOP_K_RESULTS,
    ) -> None:
        self._embeddings = embedding_service
        self._vector_store = vector_store
        self._generation = generation_service
        self._top_k = top_k

    def answer(self, user_id: int, question: str) -> QueryResponse:
        """Run the full RAG pipeline for ``question`` on ``user_id``'s corpus."""
        query_embedding = self._embeddings.embed_query(question)
        retrieved = self._vector_store.query(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=self._top_k,
        )

        if not retrieved:
            logger.info("Empty retrieval for user %d; returning fallback", user_id)
            return QueryResponse(answer=_FALLBACK_ANSWER, sources=[])

        context = self._format_context(retrieved)
        prompt = _PROMPT_TEMPLATE.format(context=context, question=question)
        answer_text = self._generation.generate(prompt).strip()

        sources = self._deduplicate_sources(retrieved)
        return QueryResponse(answer=answer_text, sources=sources)

    @staticmethod
    def _format_context(
        retrieved: list[tuple[str, SourceCitation]],
    ) -> str:
        blocks: list[str] = []
        for index, (chunk, citation) in enumerate(retrieved, start=1):
            header = f"[{index}] {citation.filename} (page {citation.page})"
            blocks.append(f"{header}\n{chunk}")
        return "\n\n".join(blocks)

    @staticmethod
    def _deduplicate_sources(
        retrieved: list[tuple[str, SourceCitation]],
    ) -> list[SourceCitation]:
        seen: set[tuple[str, int]] = set()
        unique: list[SourceCitation] = []
        for _, citation in retrieved:
            key = (citation.filename, citation.page)
            if key in seen:
                continue
            seen.add(key)
            unique.append(citation)
        return unique
