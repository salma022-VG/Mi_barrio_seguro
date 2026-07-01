"""Configuración del chatbot desde variables de entorno."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json").strip()
SERVICE_ACCOUNT_PATH = None if SERVICE_ACCOUNT_FILE.startswith("{") else BASE_DIR / SERVICE_ACCOUNT_FILE

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "").strip()
GOOGLE_SHEETS_REPORTS_TAB = os.getenv(
    "GOOGLE_SHEETS_REPORTS_TAB", "Reportes"
).strip()
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "").strip()
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "").strip()
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "").strip()

TIMEZONE = os.getenv("TIMEZONE", "America/Bogota").strip()
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
