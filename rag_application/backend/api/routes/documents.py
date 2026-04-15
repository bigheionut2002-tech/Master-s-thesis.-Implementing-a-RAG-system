"""Document management routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status

from api.dependencies import get_current_user, get_document_service
from core.constants import ALLOWED_UPLOAD_MIME_TYPES, MAX_UPLOAD_SIZE_BYTES
from models.db_models import User
from models.schemas import DocumentMetadata
from services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload",
    response_model=DocumentMetadata,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentMetadata:
    if file.content_type not in ALLOWED_UPLOAD_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted",
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds maximum allowed size",
        )
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    try:
        return document_service.ingest_pdf(
            user_id=current_user.id,
            pdf_bytes=contents,
            filename=file.filename or "document.pdf",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Ingestion failed for user %d", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Document ingestion failed",
        ) from exc


@router.get("", response_model=list[DocumentMetadata])
def list_documents(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> list[DocumentMetadata]:
    return document_service.list_documents(user_id=current_user.id)


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service),
) -> Response:
    document_service.delete_document(user_id=current_user.id, document_id=document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
