# Informe de limpieza e integración anual

## Alcance vigente

La reconstrucción utiliza los recursos oficiales enero-diciembre de Delito de Alto Impacto e Incidente Reportado para 2018-2025. El acumulado enero-mayo de 2026 se conserva separado y no participa en tendencias o variaciones anuales.

## Preservación

- `data/raw/alto_impacto/dai_anual_geojson.zip`: copia del recurso oficial anual.
- `data/raw/incidentes_reportados/ir_anual_geojson.zip`: copia del recurso oficial anual.
- `data/raw/poblacion_localidades.csv`: población por localidad, sexo y edad.
- Las huellas SHA-256 se registran en `reports/annual_analysis_summary.json`.
- Ningún proceso modifica los archivos originales.

## Transformaciones

- Códigos de localidad normalizados a dos caracteres.
- Nombres reconciliados mediante catálogo canónico de veinte localidades.
- Columnas anchas por año transformadas a estructura larga.
- Registros `99 - Sin Localización` conservados fuera de la geometría.
- Población agregada por localidad y año, excluyendo el agregado `00 - Bogotá` para evitar doble conteo.
- Integración mediante `locality_code + year`.

## Resultados de calidad

| Control | Resultado | Decisión |
|---|---:|---|
| Filas integradas | 160 | 20 localidades × 8 años completos |
| Llaves duplicadas | 0 | No se eliminaron filas |
| Valores requeridos faltantes | 0 | No se imputaron datos |
| Outliers marcados por IQR | 29 | Todos se conservaron |
| Outliers eliminados | 0 | Revisión, no borrado automático |
| Geometrías cartografiables | 20 | Una por localidad |
| Registros sin localidad | Conservados | Incluidos en totales distritales |

## Hallazgo de cobertura

En 2025 existen 21.906 hurtos a personas sin localidad asignada, equivalentes al 17,7% del total distrital. La cobertura cartografiable es 82,3%, frente a 99,4% en 2024. Por ello:

- el total distrital de 2025 se conserva;
- los registros no se eliminan ni se distribuyen artificialmente entre localidades;
- 2024 se recomienda como vista territorial inicial;
- el mapa de 2025 debe mostrar una advertencia visible.

## Salidas principales

- `data/processed/anual/seguridad_anual_localidad.csv`
- `data/processed/anual/localidades_bogota_anual.geojson`
- `reports/annual_district_summary.csv`
- `reports/annual_outlier_flags.csv`
- `reports/annual_analysis_summary.json`
