"""FastAPI dependencies (DI wiring)."""

from __future__ import annotations

from functools import lru_cache

import chromadb
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.config import get_settings
from core.database import get_db
from core.security import decode_access_token
from models.db_models import User
from repositories.user_repository import UserRepository
from repositories.vector_store import VectorStore
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.generation_service import GenerationService
from services.query_service import QueryService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# --- Auth wiring ---

def get_user_repository(session: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Return the authenticated :class:`User` from the JWT access token."""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = user_repository.get_by_id(int(subject))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def get_current_user_id(current_user: User = Depends(get_current_user)) -> int:
    """Back-compat helper for routes that only need the user id."""
    return current_user.id


# --- RAG wiring ---

@lru_cache(maxsize=1)
def _chroma_client() -> chromadb.api.ClientAPI:
    settings = get_settings()
    return chromadb.PersistentClient(path=str(settings.chroma_persist_dir))


@lru_cache(maxsize=1)
def _cached_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@lru_cache(maxsize=1)
def _cached_generation_service() -> GenerationService:
    return GenerationService()


def get_vector_store() -> VectorStore:
    return VectorStore(_chroma_client())


def get_embedding_service() -> EmbeddingService:
    return _cached_embedding_service()


def get_generation_service() -> GenerationService:
    return _cached_generation_service()


def get_document_service(
    vector_store: VectorStore = Depends(get_vector_store),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> DocumentService:
    return DocumentService(vector_store=vector_store, embedding_service=embedding_service)


def get_query_service(
    vector_store: VectorStore = Depends(get_vector_store),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    generation_service: GenerationService = Depends(get_generation_service),
) -> QueryService:
    return QueryService(
        embedding_service=embedding_service,
        vector_store=vector_store,
        generation_service=generation_service,
    )
