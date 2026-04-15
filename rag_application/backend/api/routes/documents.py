"""Document management routes (stubs)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status

from api.dependencies import get_current_user_id
from models.schemas import DocumentMetadata

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentMetadata, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile,
    user_id: int = Depends(get_current_user_id),
) -> DocumentMetadata:
    del file, user_id  # unused in stub
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("", response_model=list[DocumentMetadata])
def list_documents(user_id: int = Depends(get_current_user_id)) -> list[DocumentMetadata]:
    del user_id
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    user_id: int = Depends(get_current_user_id),
) -> Response:
    del document_id, user_id
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
