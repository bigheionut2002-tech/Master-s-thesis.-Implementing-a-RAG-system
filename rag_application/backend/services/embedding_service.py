"""Dense embedding service backed by the Google Gemini API.

Wraps :func:`google.generativeai.embed_content` so that the rest of the
codebase depends on a narrow, typed interface rather than on the vendor SDK.
This makes unit tests straightforward to write with ``monkeypatch`` and keeps
the option of swapping Gemini for another provider open.
"""

from __future__ import annotations

import google.generativeai as genai

from core.config import get_settings
from core.constants import GEMINI_EMBEDDING_MODEL

_TASK_DOCUMENT = "retrieval_document"
_TASK_QUERY = "retrieval_query"


class EmbeddingService:
    """Compute dense embeddings via Google Gemini."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = GEMINI_EMBEDDING_MODEL,
    ) -> None:
        self._model = model
        resolved_key = api_key if api_key is not None else get_settings().gemini_api_key
        genai.configure(api_key=resolved_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding per input text, preserving order."""
        if not texts:
            return []
        response = genai.embed_content(
            model=self._model,
            content=texts,
            task_type=_TASK_DOCUMENT,
        )
        return list(response["embedding"])

    def embed_query(self, text: str) -> list[float]:
        """Return a single embedding for a user query."""
        response = genai.embed_content(
            model=self._model,
            content=text,
            task_type=_TASK_QUERY,
        )
        return list(response["embedding"])
