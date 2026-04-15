"""Authentication business logic."""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError

from core.security import create_access_token, hash_password, verify_password
from models.schemas import TokenResponse, UserPublic
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Base class for authentication failures."""


class DuplicateEmailError(AuthError):
    """Raised when attempting to register an email that already exists."""


class InvalidCredentialsError(AuthError):
    """Raised when login credentials do not match any user."""


class AuthService:
    """Register users, authenticate credentials, issue JWT tokens."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def register(self, email: str, password: str) -> UserPublic:
        """Create a new user. Raises :class:`DuplicateEmailError` on conflict."""
        if self._users.get_by_email(email) is not None:
            raise DuplicateEmailError(email)
        try:
            user = self._users.create(email=email, hashed_password=hash_password(password))
        except IntegrityError as exc:
            raise DuplicateEmailError(email) from exc
        logger.info("Registered user %s", email)
        return UserPublic.model_validate(user)

    def login(self, email: str, password: str) -> TokenResponse:
        """Validate credentials and return a signed JWT access token."""
        user = self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError(email)
        token = create_access_token(
            subject=str(user.id),
            extra_claims={"email": user.email},
        )
        logger.info("Login success for user %s", email)
        return TokenResponse(access_token=token)

    def seed_demo_users(self, demo_users: tuple[tuple[str, str], ...]) -> None:
        """Insert each demo user if it does not already exist."""
        for email, password in demo_users:
            if self._users.get_by_email(email) is None:
                try:
                    self.register(email=email, password=password)
                    logger.info("Seeded demo user %s", email)
                except DuplicateEmailError:
                    # Race with a concurrent startup — safe to ignore.
                    logger.debug("Demo user %s already present", email)
