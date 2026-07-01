from datetime import datetime
from zoneinfo import ZoneInfo

from chatbot import ChatbotEngine, IncomingMessage
from config.constants import REPORT_HEADERS


class FakeSheets:
    def __init__(self):
        self.reports = []

    def append_report(self, report):
        self.reports.append(report)
        return 2


NOW = datetime(2026, 7, 1, 12, 0, tzinfo=ZoneInfo("America/Bogota"))


def build_engine():
    sheets = FakeSheets()
    return ChatbotEngine(sheets=sheets, now_provider=lambda: NOW), sheets


def complete_report(engine, phone="573001112233"):
    messages = [
        IncomingMessage(text="hola"),
        IncomingMessage(text="1"),
        IncomingMessage(text="8"),
        IncomingMessage(text="1"),
        IncomingMessage(text="30/06/2026 18:30"),
        IncomingMessage(text="1"),
        IncomingMessage(text="1"),
        IncomingMessage(text="2"),
        IncomingMessage(text="Calle 40 con Carrera 78"),
        IncomingMessage(text="ubicacion", latitude=4.628, longitude=-74.15),
        IncomingMessage(text="Dos personas intimidaron a la víctima"),
        IncomingMessage(text="1"),
    ]
    return [engine.process_message(phone, message) for message in messages]


def test_complete_flow_writes_exact_schema_without_phone_identifier():
    engine, sheets = build_engine()
    responses = complete_report(engine)

    assert "no solicita ni guarda" in responses[0]
    assert "Reporte recibido" in responses[-1]
    assert len(sheets.reports) == 1
    report = sheets.reports[0]
    assert list(report) == REPORT_HEADERS
    assert report["locality_code"] == "08"
    assert report["event_type"] == "hurto_consumado"
    assert report["phone_hash"] == ""
    assert report["source"] == "whatsapp"
    assert report["moderation_status"] == "pending"
    assert report["latitude_private"] == 4.628


def test_rejecting_consent_saves_nothing():
    engine, sheets = build_engine()
    engine.process_message("573001112233", IncomingMessage(text="hola"))
    response = engine.process_message("573001112233", IncomingMessage(text="2"))

    assert "No se guardó" in response
    assert sheets.reports == []


def test_cancel_command_deletes_temporary_session():
    engine, sheets = build_engine()
    engine.process_message("573001112233", IncomingMessage(text="hola"))
    engine.process_message("573001112233", IncomingMessage(text="1"))
    response = engine.process_message("573001112233", IncomingMessage(text="cancelar"))

    assert "información temporal se eliminó" in response
    assert sheets.reports == []


def test_future_event_date_is_rejected():
    engine, _ = build_engine()
    phone = "573001112233"
    engine.process_message(phone, IncomingMessage(text="hola"))
    engine.process_message(phone, IncomingMessage(text="1"))
    engine.process_message(phone, IncomingMessage(text="8"))
    engine.process_message(phone, IncomingMessage(text="1"))
    response = engine.process_message(phone, IncomingMessage(text="02/07/2026 18:00"))

    assert "No se admiten fechas futuras" in response

