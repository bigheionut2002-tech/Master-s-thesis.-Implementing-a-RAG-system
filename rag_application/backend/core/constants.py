"""Project-wide constants.

Collected here so no magic numbers or literals leak into services, repositories,
or routes. Values that must be tunable at deploy time live in ``config.Settings``
instead.
"""

from __future__ import annotations

# --- PDF ingestion ---
MAX_UPLOAD_SIZE_MB: int = 20
MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_UPLOAD_MIME_TYPES: tuple[str, ...] = ("application/pdf",)

# --- Chunking ---
CHUNK_SIZE_TOKENS: int = 500
CHUNK_OVERLAP_TOKENS: int = 50

# --- Retrieval ---
TOP_K_RESULTS: int = 5

# --- Gemini model identifiers (free tier, verified via list_models 2026-04) ---
GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"
GEMINI_GENERATION_MODEL: str = "models/gemini-2.5-flash"

# --- Authentication ---
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h
BCRYPT_ROUNDS: int = 12

# --- ChromaDB ---
CHROMA_COLLECTION_PREFIX: str = "user_"

# --- Demo seed users (passwords are plaintext here only as the seed source;
# they are hashed before being stored in PostgreSQL). ---
DEMO_USERS: tuple[tuple[str, str], ...] = (
    ("avocatura@demo.com", "demo1234"),
    ("restaurant@demo.com", "demo1234"),
    ("admin@demo.com", "demo1234"),
)
