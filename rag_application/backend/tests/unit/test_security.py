"""Smoke tests for JWT + password hashing primitives."""

from __future__ import annotations

import pytest

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip() -> None:
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_access_token_round_trip() -> None:
    token = create_access_token(subject="42", extra_claims={"email": "user@test.com"})
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["email"] == "user@test.com"


def test_decode_invalid_token_raises() -> None:
    with pytest.raises(ValueError):
        decode_access_token("not-a-real-token")
