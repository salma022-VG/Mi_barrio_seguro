# Requisitos del dashboard MVP

## Decisión de producto

El dashboard debe responder una sola pregunta con claridad: cómo evolucionó anualmente el hurto a personas entre 2018 y 2025 y cómo cambia su lectura territorial al comparar conteos, tasas e incidentes 123.

La vista inicial será **Hurtos registrados · Tasa · 2024**, último año con cobertura territorial superior al 99%. El año 2025 estará habilitado con alerta visible de cobertura del 82,3%. El dato enero-mayo de 2026 permanecerá separado.

## Componentes obligatorios

1. Cuatro tarjetas distritales: hurtos 2025, incidentes 123 de 2025, cobertura territorial y reportes comunitarios aprobados.
2. Mapa coroplético por localidad.
3. Selector de fuente: hurtos registrados, incidentes 123 o divergencia.
4. Selector de medida: conteo o tasa por 100.000 habitantes.
5. Selector de año completo: 2018 a 2025.
6. Ranking ordenable de localidades.
7. Panel emergente por localidad con conteos, tasas, posiciones y variaciones.
8. Leyenda, fuente, fecha de corte y advertencia metodológica siempre visibles.

## Capas

- **Hurtos registrados:** fuente oficial Delito de Alto Impacto.
- **Incidentes 123:** fuente oficial Incidente Reportado; no equivale a denuncia ni delito confirmado.
- **Divergencia:** diferencia en puntos porcentuales entre el cambio de incidentes y el cambio de hurtos.
- **Comunitaria:** reportes moderados y agregados; control independiente y nunca sumados a cifras oficiales.

## Interacciones mínimas

- Cambiar conteo/tasa debe recolorear el mapa y reordenar el ranking.
- Cambiar de año debe conservar la fuente y medida elegidas.
- Seleccionar una localidad debe resaltarla en mapa y ranking.
- El panel de localidad debe mostrar la serie 2018-2025 sin presentar causalidad.
- Un botón de metodología debe explicar fuentes, limpieza, denominador y límites.

## Mensajes de interpretación

- La tasa usa población residente; no mide población flotante.
- Un incidente 123 no confirma un delito.
- La divergencia entre fuentes es una señal exploratoria, no una estimación de subregistro.
- Los registros sin localización se incluyen en totales distritales, pero no en el mapa.
- En 2025, 21.906 hurtos no tienen localidad y no pueden representarse en el mapa.
- Los datos de 2026 son parciales y corresponden a enero-mayo; no forman parte de la tendencia anual.

## Criterios de aceptación

- Los totales distritales coinciden con `reports/annual_analysis_summary.json`.
- El mapa contiene exactamente 20 localidades.
- No existen colores o textos que mezclen fuentes oficiales y comunitarias.
- La tasa y el conteo muestran unidades diferentes y explícitas.
- La interfaz funciona en computador y móvil.
- La metodología y las fuentes son accesibles sin salir del producto.

## Datos de entrada

- `data/processed/anual/localidades_bogota_anual.geojson`
- `data/processed/anual/seguridad_anual_localidad.csv`
- `reports/annual_analysis_summary.json`
- `reports/annual_district_summary.csv`
