# Guía del repositorio

Este proyecto recibe reportes anónimos de seguridad por WhatsApp y los inserta en Google Sheets.

## Reglas invariantes

- Nunca persistir ni registrar el número de teléfono, nombre, documento o payload completo del webhook.
- `phone_hash` permanece vacío.
- Las sesiones son efímeras y viven únicamente en `SessionStore`.
- No insertar nada antes del consentimiento y la confirmación final.
- Respetar el orden de `REPORT_HEADERS`; cambios de esquema requieren pruebas.
- Todo reporte nuevo entra como `pending`; solo moderación humana puede aprobarlo.
- No exponer columnas `_private` en endpoints o visualizaciones públicas.

## Verificación

Ejecutar `.venv\Scripts\python.exe -m pytest` y `.venv\Scripts\python.exe -m scripts.verify_google_sheets` antes de desplegar.
