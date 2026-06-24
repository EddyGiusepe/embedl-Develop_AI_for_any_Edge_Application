#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script config.py
================
Configurações do sistema de segurança carregadas via .env.
Valores podem ser sobrescritos via .env ou variáveis de ambiente.
"""

import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

# Obrigatórias - usa os.environ para falhar rápido com mensagem clara:
TELEGRAM_TOKEN: str = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID: str = os.environ["TELEGRAM_CHAT_ID"]

# Opcionais - usa os.getenv com fallback default:
YOLO_MODEL: str = os.getenv("YOLO_MODEL", "yolov8n.pt")
CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.68"))
ALERT_COOLDOWN: int = int(os.getenv("ALERT_COOLDOWN", "15"))
MAX_DETECTIONS: int = int(os.getenv("MAX_DETECTIONS", "2"))
IMAGE_SIZE: int = int(os.getenv("IMAGE_SIZE", "320"))

PERSON_CLASS_ID: int = 0
TEMP_ALERT_FILENAME: str = "intruder_alert.jpg"
