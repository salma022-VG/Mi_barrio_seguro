"""Regresiones del arranque dentro de un contenedor sin escritura en /app."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path


def test_server_import_does_not_require_a_writable_logs_directory(monkeypatch):
    original_mkdir = Path.mkdir

    def deny_logs_directory(path: Path, *args, **kwargs):
        if path == Path("logs"):
            raise PermissionError("read-only application directory")
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", deny_logs_directory)
    sys.modules.pop("server", None)

    module = importlib.import_module("server")

    assert module.app.title == "Chatbot de reportes ciudadanos de seguridad"
