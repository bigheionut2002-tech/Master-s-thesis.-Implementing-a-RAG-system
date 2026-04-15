"""Word-based sliding-window text chunker.

Used by :class:`services.document_service.DocumentService` to split the text
of each PDF page into overlapping fragments of approximately ``chunk_size``
whitespace-separated tokens, with an overlap of ``overlap`` tokens between
consecutive chunks. The result is a list of plain strings preserving the
original word order.
"""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split ``text`` into overlapping word chunks.

    Args:
        text: The input text. Empty or whitespace-only input yields an empty
            list so callers can flat-map pages without having to filter.
        chunk_size: Maximum number of whitespace tokens per chunk. Must be
            strictly positive.
        overlap: Number of tokens shared between consecutive chunks. Must be
            in the half-open interval ``[0, chunk_size)``.

    Returns:
        A list of chunks. For input shorter than ``chunk_size`` the result is
        a single-element list containing the normalised text.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be strictly positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be in [0, chunk_size)")

    if text is None or not text.strip():
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [" ".join(words)]

    step = chunk_size - overlap
    chunks: list[str] = []
    for start in range(0, len(words), step):
        window = words[start : start + chunk_size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks
