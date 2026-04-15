"""Unit tests for :class:`AuthService`."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from core.security import decode_access_token, verify_password
from repositories.user_repository import UserRepository
from services.auth_service import AuthService, DuplicateEmailError, InvalidCredentialsError


def _make_service(db_session: Session) -> AuthService:
    return AuthService(UserRepository(db_session))


def test_register_hashes_password_and_returns_public_user(db_session: Session) -> None:
    service = _make_service(db_session)
    user = service.register(email="new@test.com", password="supersecret1")

    assert user.id is not None
    assert user.email == "new@test.com"

    stored = UserRepository(db_session).get_by_email("new@test.com")
    assert stored is not None
    assert stored.hashed_password != "supersecret1"
    assert verify_password("supersecret1", stored.hashed_password)


def test_register_rejects_duplicate_email(db_session: Session) -> None:
    service = _make_service(db_session)
    service.register(email="dup@test.com", password="supersecret1")
    with pytest.raises(DuplicateEmailError):
        service.register(email="dup@test.com", password="anotherpass")


def test_login_returns_token_on_valid_credentials(db_session: Session) -> None:
    service = _make_service(db_session)
    created = service.register(email="login@test.com", password="supersecret1")

    token_response = service.login(email="login@test.com", password="supersecret1")

    assert token_response.token_type == "bearer"
    assert token_response.access_token

    payload = decode_access_token(token_response.access_token)
    assert payload["sub"] == str(created.id)


def test_login_rejects_wrong_password(db_session: Session) -> None:
    service = _make_service(db_session)
    service.register(email="wp@test.com", password="supersecret1")
    with pytest.raises(InvalidCredentialsError):
        service.login(email="wp@test.com", password="wrongpass")


def test_login_rejects_unknown_email(db_session: Session) -> None:
    service = _make_service(db_session)
    with pytest.raises(InvalidCredentialsError):
        service.login(email="ghost@test.com", password="whatever1")


def test_seed_demo_users_inserts_once(db_session: Session) -> None:
    service = _make_service(db_session)
    demo = (
        ("one@demo.com", "password1"),
        ("two@demo.com", "password2"),
    )
    service.seed_demo_users(demo)
    service.seed_demo_users(demo)  # idempotent

    repo = UserRepository(db_session)
    assert repo.get_by_email("one@demo.com") is not None
    assert repo.get_by_email("two@demo.com") is not None


def test_register_duplicate_integrity_error_is_wrapped(db_session: Session) -> None:
    """If the pre-check misses a race, the IntegrityError path must wrap too."""
    service = _make_service(db_session)
    service.register(email="race@test.com", password="supersecret1")

    repo = UserRepository(db_session)
    captured: list[str] = []
    original_create = repo.create

    def fake_check_returning_none(email: str) -> None:
        captured.append(email)
        return None

    service._users.get_by_email = fake_check_returning_none  # type: ignore[method-assign]
    service._users.create = original_create  # type: ignore[method-assign]

    with pytest.raises(DuplicateEmailError):
        service.register(email="race@test.com", password="another1")
