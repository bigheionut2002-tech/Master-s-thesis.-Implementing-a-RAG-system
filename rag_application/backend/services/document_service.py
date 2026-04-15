"""Document ingestion service (stub)."""

from __future__ import annotations

from pathlib import Path

from models.schemas import DocumentMetadata


class DocumentService:
    """Handle PDF upload, text extraction, chunking, embedding, and storage."""

    def ingest_pdf(self, user_id: int, file_path: Path, filename: str) -> DocumentMetadata:
        raise NotImplementedError

    def list_documents(self, user_id: int) -> list[DocumentMetadata]:
        raise NotImplementedError

    def delete_document(self, user_id: int, document_id: str) -> None:
        raise NotImplementedError
