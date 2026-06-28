#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script file_handler.py
======================
Gerencia uploads temporarios de arquivos enviados pela API.
Salva em data/uploads/ com nomes unicos baseados em UUID.
"""

import logging
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.schemas.analysis import MediaType

logger = logging.getLogger(__name__)


class UploadValidationError(Exception):
    """Exception for upload validation failures."""


def detect_media_type(filename: str) -> MediaType:
    """
    Detect if the file is an image or video by its extension.

    Raises:
        UploadValidationError: If the extension is not supported.
    """
    suffix = Path(filename).suffix.lower()

    if suffix in settings.ALLOWED_IMAGE_EXTENSIONS:
        return MediaType.IMAGE
    if suffix in settings.ALLOWED_VIDEO_EXTENSIONS:
        return MediaType.VIDEO

    raise UploadValidationError(f"Extension '{suffix}' not supported. Accepted: {sorted(settings.allowed_extensions)}")


def validate_size(content_length: int | None) -> None:
    """
    Validate the size of the upload against the configured limit.

    Raises:
        UploadValidationError: If it exceeds the limit.
    """
    if content_length is None:
        return
    if content_length > settings.max_upload_bytes:
        raise UploadValidationError(
            f"File too large ({content_length / 1024 / 1024:.1f} MB). Maximum allowed: {settings.MAX_UPLOAD_MB} MB."
        )


async def save_upload(upload: UploadFile) -> tuple[Path, MediaType]:
    """
    Save an upload to disk using a unique name based on UUID.

    Args:
        upload: The file sent by the API.

    Returns:
        Tuple (saved path, media type).

    Raises:
        UploadValidationError: If the extension or size are invalid.
    """
    if not upload.filename:
        raise UploadValidationError("File without name.")

    media_type = detect_media_type(upload.filename)
    validate_size(upload.size)

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    suffix = Path(upload.filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    dest = settings.UPLOAD_DIR / unique_name

    try:
        with dest.open("wb") as f:
            shutil.copyfileobj(upload.file, f)
    finally:
        await upload.close()

    actual_size = dest.stat().st_size
    if actual_size > settings.max_upload_bytes:
        dest.unlink(missing_ok=True)
        raise UploadValidationError(
            f"File too large ({actual_size / 1024 / 1024:.1f} MB). Maximum allowed: {settings.MAX_UPLOAD_MB} MB."
        )

    logger.info(
        "Upload saved: %s (%.2f MB, %s)",
        dest.name,
        actual_size / 1024 / 1024,
        media_type.value,
    )

    return dest, media_type


def delete_file(path: Path) -> None:
    """Remove a file from the disk, ignoring if it does not exist."""
    try:
        path.unlink(missing_ok=True)
    except Exception as exc:
        logger.warning("Failed to remove %s: %s", path, exc)
