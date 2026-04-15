"""Authentication business logic (stub).

Actual register/login/seed-demo implementations land in Phase 2 proper — this
file only declares the service surface so routes and tests can import it.
"""

from __future__ import annotations

from models.schemas import TokenResponse, UserPublic


class AuthService:
    """Register users, authenticate credentials, issue JWT tokens."""

    def register(self, email: str, password: str) -> UserPublic:
        raise NotImplementedError

    def login(self, email: str, password: str) -> TokenResponse:
        raise NotImplementedError

    def seed_demo_users(self) -> None:
        """Insert the demo users on first startup if they do not exist."""
        raise NotImplementedError
