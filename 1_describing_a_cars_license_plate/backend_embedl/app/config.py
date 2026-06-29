#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script config.py
================
Configurations of the backend loaded via pydantic-settings.
Values can be overridden via .env file or environment variables.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurations of the application."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "License Plate Analyzer API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "Analyzes vehicle license plates in images and videos using the "
        "embedl/Cosmos-Reason2-2B-W4A16 (Vision Language Model optimized for Edge AI)."
    )

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
    ]

    MODEL_NAME: str = "embedl/Cosmos-Reason2-2B-W4A16"
    DEVICE: str = "auto"
    DTYPE: str = "auto"
    ATTN_IMPLEMENTATION: str = "sdpa"
    MAX_NEW_TOKENS: int = 600
    REPETITION_PENALTY: float = 1.05
    VIDEO_FPS: int = 4
    # Default=2. More fps is more chance of capturing the plate in the ideal
    # position (sharpness, angle, lighting). Useful for videos with fast movement.

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"

    MAX_UPLOAD_MB: int = 100
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    ALLOWED_VIDEO_EXTENSIONS: set[str] = {".mp4", ".avi", ".mov", ".webm", ".mkv"}

    JOB_TTL_MINUTES: int = 30
    JOB_CLEANUP_INTERVAL_SECONDS: int = 300

    API_V1_PREFIX: str = "/api/v1"

    @property
    def max_upload_bytes(self) -> int:
        """Upload limit in bytes."""
        return self.MAX_UPLOAD_MB * 1024 * 1024

    @property
    def allowed_extensions(self) -> set[str]:
        """Set of all allowed extensions."""
        return self.ALLOWED_IMAGE_EXTENSIONS | self.ALLOWED_VIDEO_EXTENSIONS


@lru_cache
def get_settings() -> Settings:
    """Return a unique instance of the configurations (cached)."""
    return Settings()


settings = get_settings()
