"""Unit tests for the text chunker."""

from __future__ import annotations

import pytest

from services.text_chunker import chunk_text


def test_empty_text_returns_empty_list() -> None:
    assert chunk_text("") == []
    assert chunk_text("   \n\t  ") == []


def test_short_text_returns_single_chunk() -> None:
    chunks = chunk_text("hello world", chunk_size=500, overlap=50)
    assert chunks == ["hello world"]


def test_long_text_produces_multiple_overlapping_chunks() -> None:
    words = [f"w{i}" for i in range(1000)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=500, overlap=50)

    assert len(chunks) >= 2
    first_words = chunks[0].split()
    second_words = chunks[1].split()
    assert len(first_words) == 500
    # The second chunk must start 50 words before where the first chunk ends.
    assert second_words[:50] == first_words[-50:]
    # And the first word of the second chunk is w450 (= 500 - 50).
    assert second_words[0] == "w450"


def test_chunking_covers_every_word_at_least_once() -> None:
    words = [f"token{i}" for i in range(1234)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=300, overlap=30)

    seen: set[str] = set()
    for chunk in chunks:
        seen.update(chunk.split())
    assert seen == set(words)


def test_invalid_parameters_raise() -> None:
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=-1)
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=100, overlap=100)
