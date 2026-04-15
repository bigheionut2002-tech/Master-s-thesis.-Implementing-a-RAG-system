"""RAG query routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_user, get_query_service
from models.db_models import User
from models.schemas import QueryRequest, QueryResponse
from services.query_service import QueryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def ask_question(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    query_service: QueryService = Depends(get_query_service),
) -> QueryResponse:
    try:
        return query_service.answer(
            user_id=current_user.id,
            question=payload.question,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Query failed for user %d", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Query pipeline failed",
        ) from exc
