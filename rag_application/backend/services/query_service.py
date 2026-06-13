"""RAG query service.

Pipeline: embed the user's question, retrieve the top-``k`` chunks from the
user's ChromaDB collection, build a prompt that binds the language model to
the retrieved evidence, call Gemini, and return the answer together with a
deduplicated list of source citations.
"""

from __future__ import annotations

import base64
import logging
from pathlib import Path

import fitz  # PyMuPDF

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
        upload_dir: Path,
        top_k: int = TOP_K_RESULTS,
    ) -> None:
        self._embeddings = embedding_service
        self._vector_store = vector_store
        self._generation = generation_service
        self._upload_dir = upload_dir
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

        sources = self._build_sources_with_previews(user_id, retrieved)
        return QueryResponse(answer=answer_text, sources=sources)

    @staticmethod
    def _format_context(retrieved: list[tuple[str, dict]]) -> str:
        blocks: list[str] = []
        for index, (chunk, meta) in enumerate(retrieved, start=1):
            header = f"[{index}] {meta['filename']} (page {meta['page']})"
            blocks.append(f"{header}\n{chunk}")
        return "\n\n".join(blocks)

    def _build_sources_with_previews(
        self,
        user_id: int,
        retrieved: list[tuple[str, dict]],
    ) -> list[SourceCitation]:
        # Group bbox strings by (filename, page) — one page may have multiple chunks.
        bboxes_by_page: dict[tuple[str, int], list[str]] = {}
        for _chunk, meta in retrieved:
            key = (meta["filename"], meta["page"])
            if key not in bboxes_by_page:
                bboxes_by_page[key] = []
            bboxes_by_page[key].append(meta.get("bbox", ""))

        result: list[SourceCitation] = []
        for (filename, page), bboxes in bboxes_by_page.items():
            image_b64 = self._render_page_preview(user_id, filename, page, bboxes)
            result.append(SourceCitation(filename=filename, page=page, page_image_b64=image_b64))
        return result

    def _render_page_preview(
        self,
        user_id: int,
        filename: str,
        page: int,
        bboxes: list[str],
    ) -> str:
        pdf_path = self._upload_dir / str(user_id) / filename
        if not pdf_path.exists():
            logger.warning("PDF not found on disk: %s", pdf_path)
            return ""
        try:
            doc = fitz.open(str(pdf_path))
            try:
                page_obj = doc[page - 1]
                for bbox_str in bboxes:
                    if not bbox_str:
                        continue
                    x0, y0, x1, y1 = map(float, bbox_str.split(","))
                    rect = fitz.Rect(x0, y0, x1, y1)
                    annot = page_obj.add_highlight_annot(rect)
                    annot.set_colors(stroke=(1, 1, 0))
                    annot.update()
                pixmap = page_obj.get_pixmap(dpi=150)
                return base64.b64encode(pixmap.tobytes("png")).decode()
            finally:
                doc.close()
        except Exception:
            logger.warning("Failed to render preview for %s page %d", filename, page)
            return ""
