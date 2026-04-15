"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import auth, documents, query
from core.config import get_settings
from core.constants import DEMO_USERS
from core.database import create_all_tables, get_db
from core.logging import configure_logging
from repositories.user_repository import UserRepository
from services.auth_service import AuthService

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting %s in %s mode", settings.app_name, settings.app_env)
    try:
        create_all_tables()
        session = next(get_db())
        try:
            AuthService(UserRepository(session)).seed_demo_users(DEMO_USERS)
        finally:
            session.close()
    except Exception:  # pragma: no cover - startup best effort
        logger.exception("Startup initialisation failed; continuing")
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}
