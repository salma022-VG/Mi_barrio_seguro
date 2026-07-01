from unittest.mock import MagicMock

import pytest

from config.constants import REPORT_HEADERS
from services.google_sheets import SheetSchemaError, SheetsClient


def fake_client():
    client = SheetsClient.__new__(SheetsClient)
    client.spreadsheet_id = "sheet-id"
    client.sheet_name = "Reportes chatbot"
    client.service = MagicMock()
    return client


def test_append_report_uses_header_order():
    client = fake_client()
    append_call = client.service.spreadsheets.return_value.values.return_value.append
    append_call.return_value.execute.return_value = {
        "updates": {"updatedRange": "'Reportes chatbot'!A9:R9"}
    }
    report = {header: f"value-{header}" for header in reversed(REPORT_HEADERS)}

    row_number = client.append_report(report)

    assert row_number == 9
    kwargs = append_call.call_args.kwargs
    assert kwargs["body"]["values"][0] == [report[header] for header in REPORT_HEADERS]
    assert kwargs["valueInputOption"] == "RAW"


def test_ensure_headers_refuses_mismatched_schema():
    client = fake_client()
    get_call = client.service.spreadsheets.return_value.values.return_value.get
    get_call.return_value.execute.return_value = {"values": [["wrong_header"]]}

    with pytest.raises(SheetSchemaError):
        client.ensure_headers()


def test_unknown_report_fields_are_rejected():
    client = fake_client()
    with pytest.raises(ValueError):
        client.append_report({"report_id": "rpt_test", "telefono": "secret"})

