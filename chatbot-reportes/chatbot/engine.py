"""Máquina de estados para reportes anónimos de hurto por WhatsApp."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable
from uuid import uuid4
from zoneinfo import ZoneInfo

from loguru import logger

from chatbot.session_store import ReportSession, SessionStore
from chatbot.validaciones import (
    is_no,
    is_skip,
    is_yes,
    normalize,
    parse_event_datetime,
    valid_bogota_coordinates,
)
from config.constants import (
    EVENT_TYPES,
    ITEM_CATEGORIES,
    LOCALITIES,
    MODALITIES,
    STATES,
    WEAPON_TYPES,
)
from config.settings import SESSION_TIMEOUT_MINUTES, TIMEZONE
from services import SheetsClient


@dataclass(frozen=True)
class IncomingMessage:
    text: str = ""
    latitude: float | None = None
    longitude: float | None = None


def _menu(title: str, options: dict[str, tuple[str, str]]) -> str:
    lines = [f"*{title}*", "Responde con el número de una opción.", ""]
    lines.extend(f"{number}. {label}" for number, (_, label) in options.items())
    return "\n".join(lines)


class ChatbotEngine:
    def __init__(
        self,
        sheets: SheetsClient | None = None,
        sessions: SessionStore | None = None,
        now_provider: Callable[[], datetime] | None = None,
    ):
        self.sheets = sheets or SheetsClient()
        self.sessions = sessions or SessionStore(SESSION_TIMEOUT_MINUTES)
        timezone = ZoneInfo(TIMEZONE)
        self._now = now_provider or (lambda: datetime.now(timezone))

    def process_message(self, transient_phone: str, incoming: IncomingMessage) -> str:
        now = self._now()
        text = incoming.text.strip()
        normalized = normalize(text)

        if normalized in {"cancelar", "salir"}:
            self.sessions.delete(transient_phone)
            return "El reporte fue cancelado y la información temporal se eliminó. Escribe *hola* para comenzar otro."

        if normalized in {"reiniciar", "nuevo reporte"}:
            self.sessions.delete(transient_phone)

        session = self.sessions.get(transient_phone, now)
        if session is None:
            session = self.sessions.create(transient_phone, now)
            return self._privacy_notice()

        self.sessions.touch(session, now)
        handler = getattr(self, f"_handle_{session.state}", None)
        if handler is None:
            self.sessions.delete(transient_phone)
            logger.error("Estado conversacional desconocido")
            return "La conversación se reinició de forma segura. Escribe *hola* para comenzar."
        return handler(transient_phone, session, incoming, now)

    # Compatibilidad con el webhook anterior.
    def procesar_mensaje(self, telefono: str, texto: str) -> str:
        return self.process_message(telefono, IncomingMessage(text=texto))

    @staticmethod
    def _privacy_notice() -> str:
        return (
            "👋 *Reporte ciudadano anónimo de seguridad*\n\n"
            "Este canal no solicita ni guarda en la base del proyecto tu nombre, documento ni número de teléfono. "
            "WhatsApp y el proveedor técnico sí procesan temporalmente el número para entregar los mensajes, bajo sus propias políticas.\n\n"
            "Solo registraremos datos del hecho y una ubicación aproximada para análisis estadístico. "
            "No incluyas nombres, teléfonos, documentos ni direcciones de vivienda.\n\n"
            "⚠️ Este reporte *no reemplaza una denuncia oficial* ni atiende emergencias. Si hay peligro inmediato, comunícate con el 123.\n\n"
            "¿Autorizas el uso anónimo de la información del hecho para fines estadísticos?\n"
            "1. Sí, acepto\n2. No acepto"
        )
    def _handle_consent(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        if is_no(incoming.text):
            self.sessions.delete(key)
            return "Entendido. No se guardó ninguna información."
        if not is_yes(incoming.text):
            return "Para continuar responde *1* (Sí, acepto) o *2* (No acepto)."
        session.data["consent"] = "yes"
        session.data["consent_at"] = now.isoformat(timespec="seconds")
        session.state = STATES["LOCALITY"]
        return _menu("¿En qué localidad ocurrió?", LOCALITIES)

    def _handle_locality(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        option = LOCALITIES.get(incoming.text.strip())
        if not option:
            return _menu("Opción inválida. ¿En qué localidad ocurrió?", LOCALITIES)
        session.data["locality_code"], session.data["locality_label"] = option
        session.state = STATES["EVENT_TYPE"]
        return _menu("¿Qué ocurrió?", EVENT_TYPES)

    def _handle_event_type(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        option = EVENT_TYPES.get(incoming.text.strip())
        if not option:
            return _menu("Opción inválida. ¿Qué ocurrió?", EVENT_TYPES)
        session.data["event_type"], session.data["event_type_label"] = option
        session.state = STATES["EVENT_AT"]
        return (
            "*¿Cuándo ocurrió?*\n"
            "Escribe la fecha y, si la recuerdas, la hora.\n"
            "Ejemplos: *25/06/2026 18:30*, *ayer 21:00* o *hoy 08:15*."
        )

    def _handle_event_at(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        parsed = parse_event_datetime(incoming.text, now)
        if parsed is None:
            return (
                "No pude validar la fecha. Usa *DD/MM/AAAA HH:MM*, *ayer HH:MM* o *hoy HH:MM*. "
                "No se admiten fechas futuras."
            )
        session.data["event_at"] = parsed.isoformat(timespec="minutes")
        session.data["event_at_label"] = parsed.strftime("%d/%m/%Y %H:%M")
        session.state = STATES["ITEM"]
        return _menu("¿Qué fue hurtado?", ITEM_CATEGORIES)

    def _handle_item(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        option = ITEM_CATEGORIES.get(incoming.text.strip())
        if not option:
            return _menu("Opción inválida. ¿Qué fue hurtado?", ITEM_CATEGORIES)
        session.data["stolen_item_category"], session.data["item_label"] = option
        session.state = STATES["MODALITY"]
        return _menu("¿Cuál fue la modalidad?", MODALITIES)

    def _handle_modality(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        option = MODALITIES.get(incoming.text.strip())
        if not option:
            return _menu("Opción inválida. ¿Cuál fue la modalidad?", MODALITIES)
        session.data["modality"], session.data["modality_label"] = option
        session.state = STATES["WEAPON"]
        return _menu("¿Se utilizó algún tipo de arma?", WEAPON_TYPES)

    def _handle_weapon(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        option = WEAPON_TYPES.get(incoming.text.strip())
        if not option:
            return _menu("Opción inválida. ¿Se utilizó algún tipo de arma?", WEAPON_TYPES)
        session.data["weapon_type"], session.data["weapon_label"] = option
        session.state = STATES["ADDRESS"]
        return (
            "*¿En qué punto aproximado ocurrió?*\n"
            "Escribe un barrio, vía o intersección (ej.: *Calle 72 con Carrera 10*). "
            "No escribas una dirección de vivienda ni datos personales. También puedes responder *omitir*."
        )

    def _handle_address(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        value = "" if is_skip(incoming.text) else incoming.text.strip()
        if len(value) > 160:
            return "La referencia debe tener máximo 160 caracteres. Intenta de nuevo o responde *omitir*."
        session.data["address_private"] = value
        session.state = STATES["LOCATION"]
        return (
            "*Ubicación opcional*\n"
            "Puedes enviar la ubicación de WhatsApp del lugar del hecho. Se guardará como dato privado para georreferenciar el mapa; "
            "no envíes la ubicación de tu vivienda. Si prefieres no compartirla, responde *omitir*."
        )

    def _handle_location(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        if incoming.latitude is not None and incoming.longitude is not None:
            if not valid_bogota_coordinates(incoming.latitude, incoming.longitude):
                return "La ubicación parece estar fuera de Bogotá. Envía otra ubicación o responde *omitir*."
            session.data["latitude_private"] = round(incoming.latitude, 6)
            session.data["longitude_private"] = round(incoming.longitude, 6)
        elif is_skip(incoming.text):
            session.data["latitude_private"] = ""
            session.data["longitude_private"] = ""
        else:
            return "Envía una ubicación de WhatsApp o responde *omitir*."
        session.state = STATES["DESCRIPTION"]
        return (
            "*Descripción opcional*\n"
            "Cuéntanos brevemente cómo ocurrió (máximo 500 caracteres). No incluyas nombres, teléfonos, documentos ni placas. "
            "Puedes responder *omitir*."
        )

    def _handle_description(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        value = "" if is_skip(incoming.text) else incoming.text.strip()
        if len(value) > 500:
            return "La descripción debe tener máximo 500 caracteres. Acórtala o responde *omitir*."
        session.data["description_private"] = value
        session.state = STATES["CONFIRM"]
        return self._summary(session)

    def _handle_confirm(self, key: str, session: ReportSession, incoming: IncomingMessage, now: datetime) -> str:
        if is_no(incoming.text):
            self.sessions.delete(key)
            return "Reporte cancelado. La información temporal fue eliminada."
        if not is_yes(incoming.text):
            return self._summary(session, invalid=True)

        report_id = f"rpt_{uuid4().hex[:12]}"
        data = session.data
        report = {
            "report_id": report_id,
            "received_at": session.started_at.isoformat(timespec="seconds") if session.started_at else now.isoformat(timespec="seconds"),
            "event_at": data["event_at"],
            "locality_code": data["locality_code"],
            "event_type": data["event_type"],
            "stolen_item_category": data["stolen_item_category"],
            "modality": data["modality"],
            "weapon_type": data["weapon_type"],
            "latitude_private": data.get("latitude_private", ""),
            "longitude_private": data.get("longitude_private", ""),
            "address_private": data.get("address_private", ""),
            "description_private": data.get("description_private", ""),
            "source": "whatsapp",
            "moderation_status": "pending",
            "consent": data["consent"],
            "consent_at": data["consent_at"],
            "phone_hash": "",
            "review_notes_private": "",
        }
        try:
            self.sheets.append_report(report)
        except Exception as exc:
            logger.error("No se pudo guardar el reporte {}: {}", report_id, type(exc).__name__)
            return (
                "No fue posible guardar el reporte en este momento. Tu información sigue temporalmente en esta conversación. "
                "Responde *1* para volver a intentarlo o *2* para eliminarla."
            )

        self.sessions.delete(key)
        return (
            f"✅ *Reporte recibido*\nCódigo: *{report_id}*\n\n"
            "Quedó pendiente de moderación antes de alimentar las visualizaciones públicas. "
            "Gracias por aportar a una Bogotá más segura.\n\n"
            "Recuerda: este registro no reemplaza una denuncia oficial."
        )

    @staticmethod
    def _summary(session: ReportSession, invalid: bool = False) -> str:
        data = session.data
        prefix = "Responde únicamente *1* o *2*.\n\n" if invalid else ""
        location = data.get("address_private") or "No informada"
        return (
            prefix
            + "*Revisa tu reporte*\n\n"
            + f"Localidad: {data['locality_label']}\n"
            + f"Hecho: {data['event_type_label']}\n"
            + f"Fecha: {data['event_at_label']}\n"
            + f"Elemento: {data['item_label']}\n"
            + f"Modalidad: {data['modality_label']}\n"
            + f"Arma: {data['weapon_label']}\n"
            + f"Punto aproximado: {location}\n\n"
            + "¿Deseas enviarlo?\n1. Confirmar y enviar\n2. Cancelar y eliminar"
        )
