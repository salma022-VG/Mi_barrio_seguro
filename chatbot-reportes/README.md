# Chatbot de reportes ciudadanos de seguridad

Canal anónimo de WhatsApp para reportar hurtos o intentos de hurto en Bogotá. Los reportes se almacenan en Google Sheets con estado de moderación y alimentan la capa comunitaria del dashboard territorial del proyecto **Mi Barrio Seguro**.

## Por qué existe este chatbot

El análisis de datos del proyecto reveló que los hurtos registrados superan consistentemente los incidentes reportados al sistema 123 en varias localidades de Bogotá. Muchas víctimas no reportan el hecho porque perciben el proceso como lento, burocrático o riesgoso. Este chatbot propone una vía complementaria: un canal anónimo, breve y accesible desde WhatsApp, que no reemplaza la denuncia formal ni la línea 123, pero captura información que hoy se pierde.

## Arquitectura

```
Usuario WhatsApp
      │
      ▼
Evolution API (v2.x)
      │ webhook POST /webhook
      ▼
FastAPI (server.py)
      │
      ▼
Máquina de estados (chatbot/engine.py)
      │ consentimiento → localidad → tipo → fecha → objeto → modalidad → arma → ubicación → descripción → confirmación
      ▼
Google Sheets (services/google_sheets.py)
      │ estado: pending
      ▼
Dashboard (capa comunitaria, solo registros approved)
```

## Privacidad por diseño

- **No se solicita** nombre, documento ni teléfono.
- El número de WhatsApp solo se usa en memoria para mantener la conversación y se elimina al confirmar, cancelar o expirar la sesión.
- `phone_hash` siempre se escribe vacío en la hoja de cálculo.
- Las coordenadas, dirección y descripción se almacenan en columnas `_private` que no se exponen en el dashboard público.
- Cada reporte ingresa con `moderation_status=pending`; el dashboard solo muestra registros `approved`.
- El aviso inicial informa que WhatsApp y Evolution API procesan técnicamente el número bajo sus propias políticas.

## Flujo conversacional

| Paso | Pregunta | Tipo de respuesta |
|------|----------|-------------------|
| 1 | Aviso de privacidad y consentimiento | Sí / No |
| 2 | Localidad del hecho | Menú (20 localidades de Bogotá) |
| 3 | Tipo de evento | Hurto consumado / Intento |
| 4 | Fecha y hora | Texto libre (DD/MM/AAAA HH:MM, ayer, hoy) |
| 5 | Elemento hurtado | Menú (celular, bicicleta, etc.) |
| 6 | Modalidad | Menú (atraco, cosquilleo, etc.) |
| 7 | Tipo de arma | Menú (sin arma, arma blanca, etc.) |
| 8 | Punto aproximado | Texto libre o "omitir" |
| 9 | Ubicación de WhatsApp | Ubicación GPS o "omitir" |
| 10 | Descripción | Texto libre (máx. 500 caracteres) o "omitir" |
| 11 | Confirmación | Confirmar / Cancelar |
| 12 | Código de reporte | Generado automáticamente |

Comandos disponibles: `cancelar` elimina la sesión, `reiniciar` comienza de cero.

## Estructura del proyecto

```
chatbot-reportes/
├── server.py              # Webhook FastAPI y punto de entrada
├── main.py                # Arranque con uvicorn
├── start.py               # Script de inicio alternativo
├── chatbot/
│   ├── engine.py          # Máquina de estados conversacional
│   ├── session_store.py   # Almacén de sesiones en memoria
│   └── validaciones.py    # Validaciones de fecha, coordenadas, texto
├── config/
│   ├── settings.py        # Variables de entorno
│   └── constants.py       # Localidades, modalidades, armas, estados
├── services/
│   ├── evolution_api.py   # Cliente HTTP para Evolution API
│   └── google_sheets.py   # Cliente para Google Sheets API
├── scripts/
│   └── verify_google_sheets.py  # Verificación de conexión a Sheets
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── service_account.json.example
```

## Configuración e instalación

### 1. Variables de entorno

Copia `.env.example` como `.env` y completa:

| Variable | Descripción |
|----------|-------------|
| `EVOLUTION_API_URL` | URL base de tu instancia de Evolution API |
| `EVOLUTION_API_KEY` | API key de Evolution API |
| `EVOLUTION_INSTANCE_NAME` | Nombre de la instancia de WhatsApp |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Ruta al JSON de cuenta de servicio de Google |
| `GOOGLE_SHEETS_ID` | ID del Google Sheet (de la URL) |
| `GOOGLE_SHEETS_REPORTS_TAB` | Nombre de la pestaña (default: `Reportes`) |

### 2. Google Sheets

1. Crea un Google Sheet con una pestaña llamada `Reportes`.
2. Agrega las 18 columnas definidas en `config/constants.py` como encabezados.
3. Comparte el Sheet con el correo de la cuenta de servicio como **editor**.

### 3. Evolution API

1. Crea una instancia en Evolution API y conecta tu WhatsApp escaneando el QR.
2. Configura el webhook del evento `MESSAGES_UPSERT` apuntando a `https://TU_DOMINIO/webhook`.

### 4. Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .\.venv\Scripts\activate       # Windows
pip install -r requirements.txt
python main.py
```

### 5. Despliegue con Docker

```bash
docker compose up -d
```

El servicio expone el puerto 8000. Configura tu proxy inverso (Nginx, Traefik, Dokploy) para servir HTTPS en el dominio del webhook.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Estado del servicio |
| `GET` | `/ping` | Health check simple |
| `GET` | `/health` | Health check detallado (Sheets + Evolution) |
| `POST` | `/webhook` | Receptor de webhooks de Evolution API |
| `POST` | `/send-message` | Envío manual de mensaje (JSON: `telefono`, `mensaje`) |

## Tecnologías

- **Python 3.11+** con FastAPI y uvicorn
- **Evolution API v2.x** para la conexión con WhatsApp
- **Google Sheets API** para persistencia de reportes
- **Docker** para despliegue containerizado

## Contexto del proyecto

Este chatbot es uno de los componentes del proyecto **Mi Barrio Seguro**, desarrollado en el marco del Bogotá DataJam: Uso y Aprovechamiento de Datos (Edición 2, 2026). El proyecto completo incluye:

- **Dashboard cartográfico** con mapa, indicadores distritales, tendencias y tablas comparativas.
- **Mini chatbot web** integrado en el dashboard para reportes desde la interfaz.
- **Chatbot de WhatsApp** (este componente) para reportes anónimos desde el celular.
- **Análisis territorial reproducible** de hurtos a personas en Bogotá (2018-2025).
