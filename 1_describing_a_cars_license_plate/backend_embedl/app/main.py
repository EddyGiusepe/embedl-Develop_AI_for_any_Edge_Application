#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script main.py
==============
Entry point for the FastAPI backend for analyzing vehicle license plates.

RUN
---
* backend_embedl
  ==============
  $ uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  Recomendation
  -------------
  $ cd ../backend_embedl
  $ ./run.sh
  
* frontend_embedl
  ===============
  $ cd ../frontend_embedl
  $ npm run dev

Documentation automatically generated:
  - Swagger UI: http://localhost:8000/docs
  - ReDoc:      http://localhost:8000/redoc
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, health
from app.config import settings
from app.core.model import EmbedlVLM
from app.utils.logs_setting import setup_logging
from app.utils.memory import cleanup_memory

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events of the application.

    On startup: load the VLM model in memory.
    On shutdown: unload the model and clean memory.
    """
    logger.info("=" * 60)
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("=" * 60)

    try:
        EmbedlVLM.load()
    except Exception as exc:
        logger.exception("Failed to load the model on startup: %s", exc)

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    yield

    logger.info("Finalizing application...")
    EmbedlVLM.unload()
    cleanup_memory()
    logger.info("Application finalized.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analysis.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
async def root() -> dict:
    """Endpoint root with basic information about the API."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "analyze": f"{settings.API_V1_PREFIX}/jobs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
