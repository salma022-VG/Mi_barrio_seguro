"""Escritura mínima y ordenada de reportes en Google Sheets."""
from __future__ import annotations

import json
import re
from typing import Any, Mapping

from google.oauth2 import service_account
from googleapiclient.discovery import build
from loguru import logger

from config.constants import REPORT_HEADERS
from config.settings import (
    GOOGLE_SCOPES,
    GOOGLE_SHEETS_ID,
    GOOGLE_SHEETS_REPORTS_TAB,
    SERVICE_ACCOUNT_FILE,
    SERVICE_ACCOUNT_PATH,
)


class SheetSchemaError(RuntimeError):
    """El encabezado del Sheet no coincide con el contrato del chatbot."""


class SheetsClient:
    def __init__(self, service: Any | None = None):
        if not GOOGLE_SHEETS_ID:
            raise ValueError("GOOGLE_SHEETS_ID no está configurado")

        self.spreadsheet_id = GOOGLE_SHEETS_ID
        self.sheet_name = GOOGLE_SHEETS_REPORTS_TAB
        self.service = service or self._build_service()

    @staticmethod
    def _build_service() -> Any:
        if SERVICE_ACCOUNT_FILE.startswith("{"):
            try:
                info = json.loads(SERVICE_ACCOUNT_FILE)
            except json.JSONDecodeError as exc:
                raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE contiene JSON inválido") from exc
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=GOOGLE_SCOPES
            )
        else:
            if SERVICE_ACCOUNT_PATH is None or not SERVICE_ACCOUNT_PATH.exists():
                raise FileNotFoundError(
                    "No se encontró el archivo de cuenta de servicio configurado"
                )
            credentials = service_account.Credentials.from_service_account_file(
                str(SERVICE_ACCOUNT_PATH), scopes=GOOGLE_SCOPES
            )
        return build("sheets", "v4", credentials=credentials, cache_discovery=False)

    @property
    def _quoted_sheet(self) -> str:
        return "'" + self.sheet_name.replace("'", "''") + "'"

    def list_sheet_names(self) -> list[str]:
        metadata = self.service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id,
            fields="sheets.properties.title",
        ).execute()
        return [sheet["properties"]["title"] for sheet in metadata.get("sheets", [])]

    def ensure_headers(self) -> None:
        """Crea los encabezados si la pestaña está vacía; nunca pisa otro esquema."""
        result = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self._quoted_sheet}!A1:R1",
            )
            .execute()
        )
        values = result.get("values", [])
        current = values[0] if values else []
        if not current:
            (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{self._quoted_sheet}!A1:R1",
                    valueInputOption="RAW",
                    body={"values": [REPORT_HEADERS]},
                )
                .execute()
            )
            logger.info("Encabezados de reportes creados")
            return
        if current != REPORT_HEADERS:
            raise SheetSchemaError(
                "Los encabezados de la pestaña no coinciden con REPORT_HEADERS. "
                f"Esperados: {', '.join(REPORT_HEADERS)}"
            )

    def append_report(self, report: Mapping[str, Any]) -> int | None:
        """Inserta un reporte en el orden exacto del contrato y retorna la fila."""
        unknown = set(report) - set(REPORT_HEADERS)
        if unknown:
            raise ValueError(f"Campos no permitidos en el reporte: {sorted(unknown)}")

        row = [report.get(header, "") for header in REPORT_HEADERS]
        result = (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self._quoted_sheet}!A:R",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": [row]},
            )
            .execute()
        )
        updated_range = result.get("updates", {}).get("updatedRange", "")
        match = re.search(r"![A-Z]+(\d+):", updated_range)
        row_number = int(match.group(1)) if match else None
        logger.info("Reporte {} insertado en Sheets", report.get("report_id", "sin_id"))
        return row_number

    def test_connection(self, verify_schema: bool = True) -> bool:
        try:
            self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id,
                fields="spreadsheetId",
            ).execute()
            if verify_schema:
                self.ensure_headers()
            return True
        except Exception as exc:
            logger.error("Fallo de conexión/esquema con Google Sheets: {}", type(exc).__name__)
            return False
