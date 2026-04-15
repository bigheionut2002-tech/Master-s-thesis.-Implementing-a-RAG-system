"""Vector store repository backed by ChromaDB.

Encapsulates every call to the ChromaDB API so that the service layer works
against a stable, narrow interface regardless of the underlying vector
database implementation. The store uses one collection per user, named
``user_<id>``, to enforce data isolation at the storage layer.
"""

from __future__ import annotations

import uuid
from typing import Any

from chromadb.api import ClientAPI
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from core.constants import CHROMA_COLLECTION_PREFIX
from models.schemas import SourceCitation


class _NoopEmbeddingFunction(EmbeddingFunction[Documents]):
    """Placeholder embedder — we always pass ``embeddings=`` explicitly.

    ChromaDB requires every collection to have an embedding function, but
    because this codebase computes embeddings upstream via the Gemini API
    we install a function that raises if invoked. This makes accidental
    fall-through to ChromaDB's default embedder impossible.
    """

    def __call__(self, input: Documents) -> Embeddings:  # pragma: no cover
        raise RuntimeError(
            "VectorStore requires explicit embeddings; the default embedder is disabled",
        )


class VectorStore:
    """Per-user ChromaDB collection access."""

    def __init__(self, client: ClientAPI) -> None:
        self._client = client
        self._embedding_function = _NoopEmbeddingFunction()

    def _collection_name(self, user_id: int) -> str:
        return f"{CHROMA_COLLECTION_PREFIX}{user_id}"

    def _get_collection(self, user_id: int):
        return self._client.get_or_create_collection(
            name=self._collection_name(user_id),
            embedding_function=self._embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        user_id: int,
        chunks: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Persist a batch of chunks with their pre-computed embeddings."""
        if not chunks:
            return
        if not (len(chunks) == len(embeddings) == len(metadatas)):
            raise ValueError("chunks, embeddings and metadatas must have the same length")

        collection = self._get_collection(user_id)
        ids = [str(uuid.uuid4()) for _ in chunks]
        collection.add(
            ids=ids,
            documents=list(chunks),
            embeddings=list(embeddings),
            metadatas=list(metadatas),
        )

    def query(
        self,
        user_id: int,
        query_embedding: list[float],
        top_k: int,
    ) -> list[tuple[str, SourceCitation]]:
        """Return the top-``top_k`` chunks for the given user, ordered by distance."""
        collection = self._get_collection(user_id)
        if collection.count() == 0:
            return []

        effective_k = min(top_k, collection.count())
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=effective_k,
        )
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]

        pairs: list[tuple[str, SourceCitation]] = []
        for document, metadata in zip(documents, metadatas, strict=True):
            citation = SourceCitation(
                filename=str(metadata["filename"]),
                page=int(metadata["page"]),
            )
            pairs.append((document, citation))
        return pairs

    def delete_document(self, user_id: int, document_id: str) -> None:
        """Remove every chunk tagged with ``document_id`` from the user's collection."""
        collection = self._get_collection(user_id)
        collection.delete(where={"document_id": document_id})

    def list_documents(self, user_id: int) -> list[dict[str, Any]]:
        """Return a summary of every distinct document stored for the user.

        The result is a list of dictionaries with keys ``id``, ``filename``,
        ``num_pages``, and ``num_chunks``.
        """
        collection = self._get_collection(user_id)
        if collection.count() == 0:
            return []
        payload = collection.get()
        metadatas = payload.get("metadatas") or []

        aggregated: dict[str, dict[str, Any]] = {}
        for metadata in metadatas:
            document_id = str(metadata["document_id"])
            page = int(metadata["page"])
            record = aggregated.get(document_id)
            if record is None:
                aggregated[document_id] = {
                    "id": document_id,
                    "filename": str(metadata["filename"]),
                    "num_pages": page,
                    "num_chunks": 1,
                }
            else:
                record["num_chunks"] += 1
                if page > record["num_pages"]:
                    record["num_pages"] = page
        return list(aggregated.values())
