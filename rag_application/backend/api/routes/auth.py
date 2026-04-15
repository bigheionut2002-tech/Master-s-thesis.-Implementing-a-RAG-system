"""Authentication routes (stubs)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from models.schemas import TokenResponse, UserLoginRequest, UserPublic, UserRegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest) -> UserPublic:
    del payload
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest) -> TokenResponse:
    del payload
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
