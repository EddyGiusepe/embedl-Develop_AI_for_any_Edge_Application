#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script job_manager.py
=====================
In-memory job manager (thread-safe).

For edge devices, using in-memory instead of Redis/Celery reduces dependencies
and resource consumption. Jobs are automatically cleaned up after a configurable TTL.
"""

import logging
import threading
import uuid
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

from app.config import settings
from app.schemas.analysis import (
    AnalysisResult,
    JobStatus,
    JobStatusResponse,
    MediaType,
)

logger = logging.getLogger(__name__)


class Job:
    """Represents an analysis job in memory."""

    __slots__ = (
        "created_at",
        "error",
        "file_path",
        "filename",
        "job_id",
        "media_type",
        "result",
        "status",
        "updated_at",
    )

    def __init__(
        self,
        job_id: str,
        media_type: MediaType,
        filename: str,
        file_path: Path,
    ) -> None:
        """Initialize a new job."""
        now = datetime.utcnow()
        self.job_id = job_id
        self.status = JobStatus.QUEUED
        self.media_type = media_type
        self.filename = filename
        self.file_path = file_path
        self.result: AnalysisResult | None = None
        self.error: str | None = None
        self.created_at = now
        self.updated_at = now

    def to_response(self) -> JobStatusResponse:
        """Serialize the job to the API response schema."""
        return JobStatusResponse(
            job_id=self.job_id,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            result=self.result,
            error=self.error,
        )


class InMemoryJobManager:
    """
    In-memory job manager (thread-safe).

    Uses threading.RLock to allow safe concurrent reads.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.RLock()

    def create(
        self,
        media_type: MediaType,
        filename: str,
        file_path: Path,
    ) -> Job:
        """Create a new job in the QUEUED state."""
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            media_type=media_type,
            filename=filename,
            file_path=file_path,
        )
        with self._lock:
            self._jobs[job_id] = job
        logger.info("Job criado: %s (type=%s)", job_id, media_type.value)
        return job

    def get(self, job_id: str) -> Job | None:
        """Get a job by its id."""
        with self._lock:
            return self._jobs.get(job_id)

    def update_status(self, job_id: str, status: JobStatus) -> None:
        """Update the status of an existing job."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                logger.warning("Attempt to update non-existent job: %s", job_id)
                return
            job.status = status
            job.updated_at = datetime.utcnow()

    def set_result(self, job_id: str, result: AnalysisResult) -> None:
        """Mark the job as completed and store the result."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job.status = JobStatus.COMPLETED
            job.result = result
            job.updated_at = datetime.utcnow()
        logger.info("Job completado: %s", job_id)

    def set_error(self, job_id: str, error: str) -> None:
        """Mark the job as failed and store the error message."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job.status = JobStatus.FAILED
            job.error = error
            job.updated_at = datetime.utcnow()
        logger.error("Job falhou: %s | %s", job_id, error)

    def delete(self, job_id: str) -> bool:
        """
        Remove a job and its associated temporary file.
        Returns True if the job existed, False otherwise.
        """
        with self._lock:
            job = self._jobs.pop(job_id, None)
        if job is None:
            return False
        try:
            if job.file_path.exists():
                job.file_path.unlink()
        except Exception as exc:
            logger.warning("Error removing file %s: %s", job.file_path, exc)
        return True

    def count(self) -> int:
        """Return the current number of jobs in memory."""
        with self._lock:
            return len(self._jobs)

    def iter_jobs(self) -> Iterator[Job]:
        """Itera sobre uma copia dos jobs (snapshot)."""
        with self._lock:
            return iter(list(self._jobs.values()))

    def cleanup_expired(self, ttl_minutes: int | None = None) -> int:
        """
        Remove jobs older than `ttl_minutes` (completed/failed).

        Returns the number of jobs removed.
        """
        ttl = ttl_minutes or settings.JOB_TTL_MINUTES
        cutoff = datetime.utcnow() - timedelta(minutes=ttl)
        removed = 0

        with self._lock:
            expired_ids = [
                job_id
                for job_id, job in self._jobs.items()
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED) and job.updated_at < cutoff
            ]

        for job_id in expired_ids:
            if self.delete(job_id):
                removed += 1

        if removed:
            logger.info("Cleanup of expired jobs: %d removed", removed)
        return removed


job_manager = InMemoryJobManager()
