# Chatbot de reportes ciudadanos de seguridad

MVP para recibir por WhatsApp reportes anónimos de hurto o intento de hurto en Bogotá y escribirlos en la pestaña `Reportes` de Google Sheets.

## Privacidad por diseño

- No se solicita nombre, documento ni teléfono.
- El número de WhatsApp solo se usa en memoria para mantener el turno conversacional y se elimina al confirmar, cancelar o expirar la sesión.
- `phone_hash` siempre se escribe vacío.
- No se registran payloads, teléfonos, direcciones ni descripciones en los logs.
- Las coordenadas, la referencia de dirección y la descripción quedan en columnas `_private`.
- Cada reporte entra con `moderation_status=pending`; el mapa público debe mostrar únicamente registros `approved`.

WhatsApp y Evolution API procesan técnicamente el número para transportar mensajes. Por eso el aviso inicial no promete anonimato frente a esos proveedores, sino ausencia de identificación persistente en la base del proyecto.

## Flujo

1. Aviso de privacidad y consentimiento.
2. Localidad.
3. Hurto consumado o intento.
4. Fecha y hora del hecho.
5. Elemento hurtado.
6. Modalidad.
7. Tipo de arma.
8. Punto aproximado opcional.
9. Ubicación de WhatsApp opcional.
10. Descripción opcional.
11. Resumen y confirmación.
12. Inserción en Sheets y entrega del código del reporte.

`cancelar` elimina la sesión temporal. `reiniciar` o `nuevo reporte` comienza desde cero.

## Configuración

1. Copia `.env.example` como `.env` y completa Evolution API, cuenta de servicio e ID del Sheet.
2. Comparte el Google Sheet con el correo de la cuenta de servicio como editor.
3. La pestaña debe llamarse `Reportes` y tener las 18 columnas indicadas en `config/constants.py`.
4. Instala y prueba:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m scripts.verify_google_sheets
.\.venv\Scripts\python.exe main.py
```

Para insertar una fila técnica marcada como rechazada:

```powershell
.\.venv\Scripts\python.exe -m scripts.verify_google_sheets --write-test
```

## Evolution API

Configura el evento `MESSAGES_UPSERT` hacia `https://TU_DOMINIO/webhook`. El webhook acepta texto, respuestas de botones/listas y mensajes de ubicación. Ignora mensajes propios, grupos y duplicados.

Endpoints operativos: `GET /ping`, `GET /health`, `POST /webhook`.

## Despliegue en Dokploy

Usa `./docker-compose.yml` como Compose Path y configura el dominio sobre el servicio `web`, puerto interno `8000`. Las variables reales se agregan en la sección Environment de Dokploy; nunca se suben `.env` ni `service_account.json` a GitHub.

Para `GOOGLE_SERVICE_ACCOUNT_FILE`, pega en Dokploy el JSON completo de la cuenta de servicio en una sola línea. El archivo `.env.example` documenta únicamente los nombres de las variables.

## Criterio para el dashboard

La página debe leer solo filas con `moderation_status=approved`. Nunca debe publicar `address_private`, `description_private`, `latitude_private`, `longitude_private` ni `review_notes_private` directamente; las coordenadas deben agregarse o degradarse espacialmente antes de mostrarse.
