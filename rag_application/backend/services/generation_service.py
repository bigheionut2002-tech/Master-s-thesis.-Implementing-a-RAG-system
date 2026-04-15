"""Generative answer service backed by the Google Gemini API.

Wraps :class:`google.generativeai.GenerativeModel` so that the rest of the
codebase depends on a narrow, typed interface rather than on the vendor SDK.
"""

from __future__ import annotations

import google.generativeai as genai

from core.config import get_settings
from core.constants import GEMINI_GENERATION_MODEL


class GenerationService:
    """Produce natural-language answers conditioned on a prompt."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = GEMINI_GENERATION_MODEL,
    ) -> None:
        self._model_name = model
        resolved_key = api_key if api_key is not None else get_settings().gemini_api_key
        genai.configure(api_key=resolved_key)

    def generate(self, prompt: str) -> str:
        """Send ``prompt`` to the configured Gemini model and return its answer."""
        model = genai.GenerativeModel(self._model_name)
        response = model.generate_content(prompt)
        return str(response.text)
