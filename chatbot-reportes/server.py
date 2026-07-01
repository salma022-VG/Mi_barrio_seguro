"""Webhook FastAPI para el chatbot de reportes anónimos."""
from __future__ import annotations

import hashlib
import sys
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from loguru import logger
from pydantic import BaseModel

from chatbot import ChatbotEngine, IncomingMessage
from config.settings import DEBUG, HOST, PORT
from services import EvolutionAPI, SheetsClient


logger.remove()
logger.add(sys.stderr, level="DEBUG" if DEBUG else "INFO")

app = FastAPI(
    title="Chatbot de reportes ciudadanos de seguridad",
    description="Recepción anónima de reportes por WhatsApp y registro en Google Sheets",
    version="3.0.0",
)

_chatbot: ChatbotEngine | None = None
_sheets: SheetsClient | None = None
_evolution: EvolutionAPI | None = None
_message_cache: dict[str, float] = {}
CACHE_TIMEOUT_SECONDS = 30


def get_services() -> tuple[ChatbotEngine, SheetsClient, EvolutionAPI]:
    global _chatbot, _sheets, _evolution
    if _sheets is None:
        _sheets = SheetsClient()
    if _chatbot is None:
        _chatbot = ChatbotEngine(sheets=_sheets)
    if _evolution is None:
        _evolution = EvolutionAPI()
    return _chatbot, _sheets, _evolution


class SendMessageRequest(BaseModel):
    telefono: str
    mensaje: str


def _extract_message(message: dict[str, Any]) -> IncomingMessage:
    text = ""
    if isinstance(message.get("conversation"), str):
        text = message["conversation"]
    elif isinstance(message.get("extendedTextMessage"), dict):
        text = message["extendedTextMessage"].get("text", "")
    elif isinstance(message.get("imageMessage"), dict):
        text = message["imageMessage"].get("caption", "")
    elif isinstance(message.get("buttonsResponseMessage"), dict):
        text = message["buttonsResponseMessage"].get("selectedButtonId", "")
    elif isinstance(message.get("listResponseMessage"), dict):
        text = (
            message["listResponseMessage"].get("singleSelectReply", {}).get("selectedRowId", "")
        )

    location = message.get("locationMessage") or {}
    latitude = location.get("degreesLatitude")
    longitude = location.get("degreesLongitude")
    if location and not text:
        text = "ubicacion"
    return IncomingMessage(text=text, latitude=latitude, longitude=longitude)


def _deduplicated(phone: str, message_id: str) -> bool:
    now = time.monotonic()
    digest = hashlib.sha256(f"{phone}:{message_id}".encode()).hexdigest()
    previous = _message_cache.get(digest)
    _message_cache[digest] = now
    expired = [key for key, value in _message_cache.items() if now - value > CACHE_TIMEOUT_SECONDS]
    for key in expired:
        _message_cache.pop(key, None)
    return previous is not None and now - previous < CACHE_TIMEOUT_SECONDS


async def process_webhook(data: dict[str, Any]) -> dict[str, str]:
    event = str(data.get("event", "")).lower().replace("_", ".")
    if event != "messages.upsert":
        return {"status": "ignored"}

    payload = data.get("data") or {}
    key = payload.get("key") or {}
    if key.get("fromMe"):
        return {"status": "ignored"}

    remote_jid = str(key.get("remoteJid", ""))
    if remote_jid.endswith("@g.us"):
        return {"status": "ignored"}
    phone = remote_jid.split("@")[0]
    incoming = _extract_message(payload.get("message") or {})
    if not phone or (not incoming.text and incoming.latitude is None):
        return {"status": "ignored"}

    message_id = str(key.get("id", ""))
    if message_id and _deduplicated(phone, message_id):
        logger.info("Mensaje duplicado ignorado")
        return {"status": "duplicate"}

    chatbot, _, evolution = get_services()
    try:
        response = chatbot.process_message(phone, incoming)
    except Exception as exc:
        logger.exception("Error procesando mensaje: {}", type(exc).__name__)
        response = "Ocurrió un error temporal. Escribe *reiniciar* para comenzar nuevamente."
    evolution.send_message(phone, response)
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, Any]:
    return {"status": "online", "service": "chatbot-reportes-seguridad", "version": "3.0.0"}


@app.get("/ping")
async def ping() -> dict[str, bool]:
    return {"pong": True}


@app.post("/")
@app.post("/webhook")
async def webhook(request: Request) -> dict[str, str]:
    try:
        data = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="JSON inválido") from exc
    logger.info("Webhook recibido")
    return await process_webhook(data)


@app.post("/webhook/{event}")
async def webhook_by_event(event: str, request: Request) -> dict[str, str]:
    data = await request.json()
    data.setdefault("event", event)
    logger.info("Webhook por evento recibido")
    return await process_webhook(data)


@app.get("/health")
async def health() -> dict[str, str]:
    status = {"status": "healthy", "sheets": "unknown", "evolution": "unknown"}
    try:
        _, sheets, evolution = get_services()
        status["sheets"] = "connected" if sheets.test_connection() else "error"
        status["evolution"] = "connected" if evolution.get_instance_status() else "error"
    except Exception as exc:
        logger.error("Health check falló: {}", type(exc).__name__)
        status["status"] = "degraded"
        status["sheets"] = "error"
    if "error" in status.values():
        status["status"] = "degraded"
    return status


@app.post("/send-message")
async def send_message(request: SendMessageRequest) -> dict[str, str]:
    _, _, evolution = get_services()
    if not evolution.send_message(request.telefono, request.mensaje):
        raise HTTPException(status_code=502, detail="No se pudo enviar el mensaje")
    return {"status": "sent"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
