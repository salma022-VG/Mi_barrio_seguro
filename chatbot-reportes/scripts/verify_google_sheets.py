"""Comprueba el esquema y, opcionalmente, inserta una fila técnica sin PII."""
from __future__ import annotations

import argparse
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from config.settings import TIMEZONE
from services import SheetsClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-test", action="store_true")
    parser.add_argument("--list-tabs", action="store_true")
    args = parser.parse_args()

    client = SheetsClient()
    if args.list_tabs:
        print("Pestañas disponibles:")
        for title in client.list_sheet_names():
            print(f"- {title}")
        return
    client.ensure_headers()
    print(f"Conexión y esquema correctos en la pestaña: {client.sheet_name}")

    if not args.write_test:
        return

    now = datetime.now(ZoneInfo(TIMEZONE))
    report_id = f"test_{uuid4().hex[:12]}"
    row = client.append_report(
        {
            "report_id": report_id,
            "received_at": now.isoformat(timespec="seconds"),
            "event_at": now.isoformat(timespec="minutes"),
            "locality_code": "08",
            "event_type": "hurto_consumado",
            "stolen_item_category": "celular",
            "modality": "atraco",
            "weapon_type": "no_sabe",
            "latitude_private": "",
            "longitude_private": "",
            "address_private": "",
            "description_private": "",
            "source": "whatsapp",
            "moderation_status": "rejected",
            "consent": "yes",
            "consent_at": now.isoformat(timespec="seconds"),
            "phone_hash": "",
            "review_notes_private": "PRUEBA TÉCNICA AUTOMÁTICA — NO PUBLICAR",
        }
    )
    print(f"Fila técnica insertada: report_id={report_id}, fila={row}")


if __name__ == "__main__":
    main()
