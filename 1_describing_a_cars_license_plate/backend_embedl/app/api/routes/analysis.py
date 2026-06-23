#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script analysis.py
==================
Endpoints of the API for analyzing vehicle license plates.

Flow:
  POST /api/v1/analyze       -> create job and return job_id immediately
  GET  /api/v1/jobs/{job_id} -> query job status (polling from frontend)
  DELETE /api/v1/jobs/{job_id} -> remove job and temporary file
"""

import logging
from pathlib import Path

import torch
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from app.config import settings
from app.core.analyzer import analyze_media
from app.core.model import EmbedlVLM
from app.schemas.analysis import (
    JobCreatedResponse,
    JobStatus,
    JobStatusResponse,
    MediaType,
)
from app.services.file_handler import (
    UploadValidationError,
    save_upload,
)
from app.services.job_manager import job_manager
from app.utils.memory import cleanup_memory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["analysis"])


def _process_job(
    job_id: str,
    file_path: Path,
    media_type: MediaType,
    original_filename: str,
) -> None:
    """
    Function executed in background to process the analysis.
    Update the job status in the manager according to the progress.
    """
    job_manager.update_status(job_id, JobStatus.PROCESSING)

    try:
        result = analyze_media(
            media_path=file_path,
            media_type=media_type,
            original_filename=original_filename,
        )
        job_manager.set_result(job_id, result)
    except torch.cuda.OutOfMemoryError as exc:
        job_manager.set_error(
            job_id,
            f"CUDA out of memory. Try a smaller media. ({exc})",
        )
        cleanup_memory()
    except Exception as exc:
        logger.exception("Failed to process job %s", job_id)
        job_manager.set_error(job_id, f"Error during analysis: {exc}")
    finally:
        try:
            file_path.unlink(missing_ok=True)
        except Exception as exc:
            logger.warning("Failed to remove %s: %s", file_path, exc)


@router.post(
    "",
    response_model=JobCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create a job to analyze an image or video of a vehicle license plate",
)
async def create_analysis_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(
        ..., description="Image or video of the vehicle license plate."
    ),
) -> JobCreatedResponse:
    """
    Accept upload of image or video and create a job for analysis in background.

    Return immediately a `job_id` that must be used to query the status
    at the endpoint `GET /api/v1/jobs/{job_id}`.
    """
    if not EmbedlVLM.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VLM model has not been loaded yet. Please wait a few seconds.",
        )

    try:
        file_path, media_type = await save_upload(file)
    except UploadValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    job = job_manager.create(
        media_type=media_type,
        filename=file.filename or file_path.name,
        file_path=file_path,
    )

    background_tasks.add_task(
        _process_job,
        job_id=job.job_id,
        file_path=file_path,
        media_type=media_type,
        original_filename=file.filename or file_path.name,
    )

    return JobCreatedResponse(
        job_id=job.job_id,
        status=job.status,
        media_type=media_type,
        filename=job.filename,
        created_at=job.created_at,
        poll_url=f"{settings.API_V1_PREFIX}/jobs/{job.job_id}",
    )


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Query the status of a job for analysis (polling)",
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Return the current status of a job. The frontend must poll this
    endpoint until the status is `completed` or `failed`.
    """
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return job.to_response()


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a job and its temporary file",
)
async def delete_job(job_id: str) -> None:
    """Remove a job from memory and delete the associated temporary file."""
    deleted = job_manager.delete(job_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
