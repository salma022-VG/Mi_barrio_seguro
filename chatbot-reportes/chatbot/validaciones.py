"""Validaciones del flujo de reporte."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timedelta


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(char for char in value if not unicodedata.combining(char))


def is_yes(text: str) -> bool:
    return normalize(text) in {"1", "si", "acepto", "aceptar", "confirmar", "confirmo"}


def is_no(text: str) -> bool:
    return normalize(text) in {"2", "no", "no acepto", "cancelar", "cancelo"}


def is_skip(text: str) -> bool:
    return normalize(text) in {"omitir", "saltar", "no se", "no aplica", "ninguna"}


def parse_event_datetime(text: str, now: datetime) -> datetime | None:
    """Acepta DD/MM/AAAA [HH:MM], hoy [HH:MM] o ayer [HH:MM]."""
    clean = normalize(text)
    base_date = None
    time_part = "12:00"

    relative = re.fullmatch(r"(hoy|ayer)(?:\s+(\d{1,2}:\d{2}))?", clean)
    if relative:
        base_date = now.date() - timedelta(days=1 if relative.group(1) == "ayer" else 0)
        if relative.group(2):
            time_part = relative.group(2)
    else:
        match = re.fullmatch(r"(\d{1,2}/\d{1,2}/\d{4})(?:\s+(\d{1,2}:\d{2}))?", clean)
        if not match:
            return None
        try:
            base_date = datetime.strptime(match.group(1), "%d/%m/%Y").date()
        except ValueError:
            return None
        if match.group(2):
            time_part = match.group(2)

    try:
        hour, minute = (int(piece) for piece in time_part.split(":"))
        parsed = datetime.combine(base_date, datetime.min.time(), tzinfo=now.tzinfo).replace(
            hour=hour, minute=minute
        )
    except (ValueError, TypeError):
        return None

    if parsed > now + timedelta(minutes=5) or parsed < now - timedelta(days=3650):
        return None
    return parsed


def valid_bogota_coordinates(latitude: float, longitude: float) -> bool:
    return 3.65 <= latitude <= 4.90 and -74.55 <= longitude <= -73.90
