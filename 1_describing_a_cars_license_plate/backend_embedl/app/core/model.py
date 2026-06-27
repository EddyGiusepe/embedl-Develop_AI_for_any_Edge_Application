#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script model.py
===============
Manager of the VLM model (Vision Language Model) from embedl.

The EmbedlVLM class maintains the model and processor as class
attributes, ensuring they are loaded only once in memory (important
for edge devices with limited resources).
"""

import logging
import os
from typing import Any

import torch
import transformers

from app.config import settings
from app.utils.memory import resolve_device, resolve_dtype

logger = logging.getLogger(__name__)

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")


class EmbedlVLM:
    """
    Manages the Vision-Language model from embedl (embedl/Cosmos-Reason2-2B-W4A16).
    Maintains the model and processor as class attributes to be loaded
    only once during the application lifecycle.
    """

    _model: Any = None
    _processor: Any = None
    _device: str | None = None
    _dtype: torch.dtype | None = None
    _loaded: bool = False

    @classmethod
    def load(cls) -> None:
        """
        Loads the VLM model and processor into memory.

        Must be called once at startup (lifespan event).
        If already loaded, returns without doing anything.
        """
        if cls._loaded:
            logger.info("Model already loaded, ignoring reload.")
            return

        cls._device = resolve_device(settings.DEVICE)
        cls._dtype = resolve_dtype(settings.DTYPE, cls._device)

        logger.info(
            "Loading model '%s' on device='%s' with dtype=%s...",
            settings.MODEL_NAME,
            cls._device,
            cls._dtype,
        )

        cls._model = transformers.Qwen3VLForConditionalGeneration.from_pretrained(
            settings.MODEL_NAME,
            torch_dtype=cls._dtype,
            device_map=cls._device,
            low_cpu_mem_usage=True,
            attn_implementation=settings.ATTN_IMPLEMENTATION,
        )

        cls._processor = transformers.AutoProcessor.from_pretrained(settings.MODEL_NAME)

        cls._model.eval()
        cls._loaded = True

        logger.info("Model loaded successfully.")

    @classmethod
    def unload(cls) -> None:
        """
        Unloads the model from memory (useful at shutdown).
        """
        cls._model = None
        cls._processor = None
        cls._loaded = False
        logger.info("Model unloaded from memory.")

    @classmethod
    def is_loaded(cls) -> bool:
        """Indicates if the model is loaded."""
        return cls._loaded

    @classmethod
    def get_model(cls) -> Any:
        """Returns the loaded model instance."""
        if not cls._loaded:
            raise RuntimeError("Model has not been loaded. Call EmbedlVLM.load() first.")
        return cls._model

    @classmethod
    def get_processor(cls) -> Any:
        """Returns the processor (tokenizer + image processor)."""
        if not cls._loaded:
            raise RuntimeError("Processor has not been loaded. Call EmbedlVLM.load() first.")
        return cls._processor

    @classmethod
    def get_device(cls) -> str:
        """Returns the device where the model is running."""
        return cls._device or "unknown"

    @classmethod
    def get_dtype(cls) -> str:
        """Returns the dtype of the model as a string."""
        return str(cls._dtype) if cls._dtype else "unknown"
