"""JWT and password hashing utilities.

Only primitive building blocks live here — higher-level authentication flows
(register, login, demo-user seeding) belong in :mod:`services.auth_service`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import get_settings
from core.constants import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash for ``plain_password``."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return ``True`` if ``plain_password`` matches ``hashed_password``."""
    return _pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
    expires_minutes: int = JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Stable user identifier (typically the user id or email).
        extra_claims: Optional extra claims to embed (kept small).
        expires_minutes: Lifetime in minutes.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    now = datetime.now(tz=timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Raises:
        ValueError: If the token is invalid or expired.
    """
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
