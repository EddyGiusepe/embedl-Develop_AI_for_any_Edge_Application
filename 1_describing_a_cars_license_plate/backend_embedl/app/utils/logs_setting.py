#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script logs_setting.py
======================
Configures the logging system for the license plate analyzer.
"""

import logging
from pathlib import Path

# utils/ → app/ → backend_embedl/ → 1_describing_a_cars_license_plate/
_LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "license_plate_analyzer.log"


def setup_logging() -> None:
    """Configures the logging system"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(_LOG_FILE),
            logging.StreamHandler(),
        ],
    )


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Logging system configured successfully.")
