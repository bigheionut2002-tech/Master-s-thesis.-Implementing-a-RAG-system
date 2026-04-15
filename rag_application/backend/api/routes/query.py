"""RAG query routes (stubs)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_user_id
from models.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def ask_question(
    payload: QueryRequest,
    user_id: int = Depends(get_current_user_id),
) -> QueryResponse:
    del payload, user_id
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
