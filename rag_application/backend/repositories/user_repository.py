"""User repository (stub) — CRUD on the ``users`` table."""

from __future__ import annotations

from models.db_models import User


class UserRepository:
    """Data access for :class:`User`."""

    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    def create(self, email: str, hashed_password: str) -> User:
        raise NotImplementedError
