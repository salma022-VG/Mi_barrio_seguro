# Mi Barrio Seguro

Proyecto integral de analítica de seguridad ciudadana para Bogotá desarrollado para DataJam 2026. Reúne el dashboard, las fuentes de datos, el pipeline reproducible de limpieza y análisis, los entregables metodológicos y el chatbot anónimo de reportes por WhatsApp.

## Componentes

- **Dashboard:** aplicación Node.js ubicada en la raíz (`index.html` y `server.js`).
- **Chatbot de WhatsApp:** servicio Python/FastAPI en `chatbot-reportes/`, integrado con Evolution API y Google Sheets.
- **Datos:** fuentes originales en `data/raw/` y resultados estandarizados en `data/processed/`.
- **Pipeline reproducible:** scripts de perfilamiento, limpieza, integración, análisis anual y generación de visualizaciones en `scripts/`.
- **Auditoría:** controles de calidad, informes de limpieza y resultados analíticos en `reports/`.
- **Informe:** fuente LaTeX, figuras y guía para Overleaf en `docs/latex/`.
- **Entregables:** libros de alimentación y paquetes finales en `outputs/` y `output/`.

## Estructura

```text
Mi_barrio_seguro/
├── index.html, server.js        # Dashboard y API Node.js
├── chatbot-reportes/            # Bot anónimo para WhatsApp
├── data/
│   ├── raw/                     # Fuentes descargadas
│   └── processed/               # Datos limpios e integrados
├── scripts/                     # Pipeline reproducible
├── reports/                     # Auditoría y análisis
├── docs/                        # Metodología e informe LaTeX
├── outputs/ y output/           # Entregables generados
└── CONTEXT.md                   # Contexto técnico del procesamiento
```

## Dashboard

```bash
npm install
npm start
```

Disponible por defecto en `http://localhost:3000`. La documentación histórica del dashboard se conserva en `docs/README_DASHBOARD_ORIGINAL.md`.

## Chatbot

```powershell
cd chatbot-reportes
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe main.py
```

La configuración se documenta en `chatbot-reportes/.env.example`. Los valores reales se administran localmente o como secretos del proveedor de despliegue.

## Reproducibilidad

Los scripts mantienen separadas las fuentes, los datos procesados, los controles de calidad y los entregables. Consulta `reports/INFORME_LIMPIEZA_ANUAL.md`, `reports/ANALISIS_ANUAL.md` y `docs/latex/README_OVERLEAF.md` para reconstruir y auditar el análisis.

## Privacidad y secretos

- No se versionan archivos `.env`, cuentas de servicio, llaves privadas ni credenciales.
- El chatbot no persiste nombre, documento o número telefónico; `phone_hash` permanece vacío.
- Las sesiones conversacionales son efímeras.
- Los campos con sufijo `_private` no deben publicarse en el dashboard.
- Los reportes comunitarios requieren moderación antes de alimentar visualizaciones públicas.

## Periodo analizado

El análisis histórico principal cubre los años completos 2018–2025. Los artefactos posteriores o incompletos se identifican separadamente en los informes de calidad.
