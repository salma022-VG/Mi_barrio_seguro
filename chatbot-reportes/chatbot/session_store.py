"""Sesiones efímeras: nunca se escriben teléfonos ni estados de chat en Sheets."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import RLock
from typing import Any

from config.constants import STATES


@dataclass
class ReportSession:
    state: str = STATES["CONSENT"]
    data: dict[str, Any] = field(default_factory=dict)
    started_at: datetime | None = None
    updated_at: datetime | None = None


class SessionStore:
    """Almacén en memoria con expiración automática."""

    def __init__(self, timeout_minutes: int = 30):
        self._timeout = timedelta(minutes=timeout_minutes)
        self._sessions: dict[str, ReportSession] = {}
        self._lock = RLock()

    def get(self, transient_key: str, now: datetime) -> ReportSession | None:
        with self._lock:
            self._purge(now)
            return self._sessions.get(transient_key)

    def create(self, transient_key: str, now: datetime) -> ReportSession:
        with self._lock:
            session = ReportSession(started_at=now, updated_at=now)
            self._sessions[transient_key] = session
            return session

    def touch(self, session: ReportSession, now: datetime) -> None:
        session.updated_at = now

    def delete(self, transient_key: str) -> None:
        with self._lock:
            self._sessions.pop(transient_key, None)

    def _purge(self, now: datetime) -> None:
        expired = [
            key
            for key, value in self._sessions.items()
            if value.updated_at is None or now - value.updated_at > self._timeout
        ]
        for key in expired:
            del self._sessions[key]

