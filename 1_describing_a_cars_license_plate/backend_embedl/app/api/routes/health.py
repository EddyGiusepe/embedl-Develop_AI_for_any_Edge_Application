#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script health.py
================
Endpoint GET /health for monitoring the application.
Returns information about the status of the service and the model.
Used to check if the backend is ready to receive requests.
"""

import logging

import torch
from fastapi import APIRouter

from app.config import settings
from app.core.model import EmbedlVLM
from app.schemas.analysis import HealthResponse
from app.services.job_manager import job_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Returns information about the status of the service and the model.
    Used to check if the backend is ready to receive requests.
    """
    loaded = EmbedlVLM.is_loaded()
    return HealthResponse(
        status="ok" if loaded else "loading",
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        model_name=settings.MODEL_NAME,
        model_loaded=loaded,
        device=EmbedlVLM.get_device(),
        cuda_available=torch.cuda.is_available(),
        active_jobs=job_manager.count(),
    )
