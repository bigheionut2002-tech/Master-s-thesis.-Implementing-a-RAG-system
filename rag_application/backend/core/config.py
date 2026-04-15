"""Centralised application configuration.

All runtime configuration is loaded from environment variables (or a local
``.env`` file during development) via pydantic-settings. The :class:`Settings`
class is the single source of truth — modules must not read ``os.environ``
directly.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "RAG System"
    app_env: str = Field(default="development", description="development | production")
    debug: bool = False

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # --- PostgreSQL ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "rag_user"
    postgres_password: str = ""
    postgres_db: str = "rag_db"

    # --- JWT ---
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24

    # --- Gemini ---
    gemini_api_key: str = ""

    # --- Storage paths ---
    chroma_persist_dir: Path = Path("./chroma_db")
    upload_dir: Path = Path("./uploads")

    @property
    def database_url(self) -> str:
        """Full SQLAlchemy database URL built from individual components."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance.

    Using an LRU cache guarantees a single instance per process and avoids
    re-parsing the ``.env`` file on every dependency resolution.
    """
    return Settings()
