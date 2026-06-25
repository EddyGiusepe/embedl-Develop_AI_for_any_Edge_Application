#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script log_setup.py
===================
Configura o sistema de logging para o sistema de segurança.
"""

import logging


def setup_logging() -> None:
    """Configures the logging system"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("security_system.log"),
            logging.StreamHandler(),
        ],
    )


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Sistema de logging configurado com sucesso.")
