from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import app_logger


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    app_logger.info(
        "{} version {} started",
        settings.APP_NAME,
        settings.APP_VERSION,
    )

    yield

    app_logger.info(
        "{} stopped",
        settings.APP_NAME,
    )


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Local-first document question-answering API "
        "powered by FastAPI, ChromaDB, Sentence Transformers, "
        "and Ollama."
    ),
    lifespan=lifespan,
)


app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get(
    "/",
    tags=["Root"],
)
async def root() -> dict[str, str]:
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "documentation": "/docs",
    }
