"""Unit tests for :class:`UserRepository`."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from repositories.user_repository import UserRepository


def test_create_and_get_by_email(db_session: Session) -> None:
    repo = UserRepository(db_session)
    created = repo.create(email="user@test.com", hashed_password="hashed")

    assert created.id is not None
    assert created.email == "user@test.com"

    fetched = repo.get_by_email("user@test.com")
    assert fetched is not None
    assert fetched.id == created.id


def test_get_by_email_returns_none_for_missing(db_session: Session) -> None:
    repo = UserRepository(db_session)
    assert repo.get_by_email("missing@test.com") is None


def test_create_duplicate_email_raises(db_session: Session) -> None:
    repo = UserRepository(db_session)
    repo.create(email="dup@test.com", hashed_password="h1")
    with pytest.raises(Exception):
        repo.create(email="dup@test.com", hashed_password="h2")


def test_get_by_id(db_session: Session) -> None:
    repo = UserRepository(db_session)
    created = repo.create(email="lookup@test.com", hashed_password="hashed")
    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.email == "lookup@test.com"
