"""User repository — CRUD on the ``users`` table."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db_models import User


class UserRepository:
    """Data access for :class:`User`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        return self._session.get(User, user_id)

    def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user
