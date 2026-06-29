#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script memory.py
================
Utilities for memory cleanup (CPU and GPU).
Important for edge devices with limited VRAM/RAM.
"""

import gc

import torch


def cleanup_memory() -> None:
    """
    Force garbage collection and empty GPU cache if available.

    Should be called after each heavy inference to avoid memory accumulation,
    especially on edge devices.
    """
    gc.collect()

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def get_device() -> str:
    """
    Detect the best available device automatically.

    Returns:
        "cuda" if NVIDIA GPU is available,
        "mps" if Apple Silicon is available,
        "cpu" otherwise.
    """
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def resolve_device(device_config: str) -> str:
    """
    Resolve the device configuration to a concrete value.

    Args:
        device_config: "auto", "cuda", "cpu", "mps", etc.

    Returns:
        Concrete device to be used.
    """
    if device_config == "auto":
        return get_device()
    return device_config


def resolve_dtype(dtype_config: str, device: str) -> "torch.dtype":
    """
    Resolve the dtype configuration to a concrete torch.dtype.

    Args:
        dtype_config: "auto", "float16", "float32", "bfloat16".
        device: Concrete device where the model will run.

    Returns:
        Appropriate torch.dtype for the device.
    """
    if dtype_config == "auto":
        return torch.float16 if device in ("cuda", "mps") else torch.float32

    dtype_map = {
        "float16": torch.float16,
        "float32": torch.float32,
        "bfloat16": torch.bfloat16,
    }
    return dtype_map.get(dtype_config, torch.float32)


def get_memory_info() -> dict:
    """
    Return GPU memory usage information if available.

    Returns:
        Dictionary with allocated and reserved memory in MB.
    """
    if not torch.cuda.is_available():
        return {"cuda_available": False}

    return {
        "cuda_available": True,
        "allocated_mb": torch.cuda.memory_allocated() / 1024**2,
        "reserved_mb": torch.cuda.memory_reserved() / 1024**2,
        "max_allocated_mb": torch.cuda.max_memory_allocated() / 1024**2,
    }
