# Informe de limpieza de datos — recurso parcial reemplazado

> **Documento obsoleto para el análisis principal:** corresponde al recurso enero-mayo. La versión vigente es `INFORME_LIMPIEZA_ANUAL.md`.

## Resultado ejecutivo

La limpieza se ejecutó sin modificar los archivos originales. No se eliminaron outliers, registros vacíos ni duplicados porque las fuentes no presentaron esos problemas. Los registros sin geometría se excluyeron únicamente de las capas para mapa y se conservaron en archivos separados.

## Archivos de entrada

- `poblacion_localidades.csv`: 131.502 filas.
- `DAILoc.geojson`: 21 elementos de Delito de Alto Impacto por localidad.
- `IRLoc.geojson`: 21 elementos de incidentes reportados por localidad.
- `IRUPZ.geojson`: 117 elementos por UPZ.
- `IRSCAT.geojson`: 1.170 elementos por sector catastral.

Los originales se copiaron a `data/raw/` y permanecen intactos.

## Qué se eliminó

### Duplicados

- Población: 0 duplicados exactos eliminados.
- GeoJSON: 0 elementos duplicados eliminados.
- Tabla integrada: 0 duplicados por localidad y año.

### Registros vacíos

- Población: 0 filas con campos vacíos o nulos.
- Métricas de seguridad: 0 valores faltantes en los campos usados.
- Se eliminaron 0 filas por información vacía.

### Outliers

- Se eliminaron 0 outliers.
- El método IQR 1,5 marcó 34 valores para revisión, distribuidos en 31 combinaciones de localidad y año.
- Se conservaron porque los extremos territoriales pueden ser hallazgos reales. Por ejemplo, localidades con mucha población flotante pueden presentar tasas altas al utilizar población residente como denominador.
- Los valores negativos encontrados en los GeoJSON pertenecen a campos porcentuales de variación; no son conteos negativos y se conservaron.
- Los 526 registros con población igual a cero corresponden a combinaciones específicas de edad, sexo, localidad y año. Se conservaron porque no afectan negativamente el total anual y no son valores inválidos.

## Registros separados, no destruidos

### Sin localización

- Delito de Alto Impacto: 1 elemento con código `99`, nombre `Sin Localización` y geometría nula. Se retiró del mapa y sus 99 observaciones normalizadas se guardaron aparte.
- Incidentes por localidad: 1 elemento `Sin Localización` con geometría nula. Se retiró del mapa y sus 81 observaciones se guardaron aparte.
- Incidentes por UPZ: 1 elemento `UPZ999 - Sin Localización` con geometría nula. Se retiró del mapa y se guardó aparte.
- Sector catastral: 0 elementos sin geometría.

### Agregado Bogotá

- El CSV poblacional contiene 6.262 filas con código `00 - Bogotá` además de las 20 localidades.
- Estas filas se separaron en `poblacion_bogota_agregado.csv` para evitar doble conteo.
- La suma de las 20 localidades coincide exactamente con el agregado Bogotá para todos los años; diferencia máxima: 0 habitantes.

## Correcciones y normalización

- Código de localidad convertido a texto de dos caracteres: `1` pasa a `01`.
- Nombre de localidad normalizado con el catálogo poblacional.
- `Candelaria` se normalizó a `La Candelaria` en las dos fuentes de seguridad.
- Años, edades, población y conteos se convirtieron a tipos numéricos.
- Los campos anchos por año se transformaron a formato largo: una fila por fuente, localidad, año y métrica.
- Las geometrías de las 20 localidades son idénticas entre Delito de Alto Impacto e Incidente Reportado; se generó una sola capa geográfica base.
- Los GeoJSON para mapa conservan código y nombre, y omiten los registros sin geometría.

## Hallazgo sobre la granularidad temporal

Los GeoJSON descargados no contienen filas mensuales. Todos los elementos tienen la etiqueta `Ene-May (2025vs2026)` y campos separados para los años 2018-2026. Por tanto:

- La comparación válida actual es enero-mayo contra enero-mayo de cada año.
- Las tasas generadas son tasas del periodo enero-mayo por 100.000 habitantes.
- No deben presentarse como tasas anuales.
- No es posible construir todavía una evolución mes a mes con estos archivos.

## Validación del cruce

La tabla integrada contiene 180 filas: 20 localidades por 9 años, desde 2018 hasta 2026.

- Localidades sin emparejar: 0.
- Años/localidades duplicados: 0.
- Poblaciones faltantes: 0.
- Poblaciones iguales o inferiores a cero en la tabla anual: 0.
- Conteos negativos de hurtos o incidentes: 0.
- Diferencias entre etiquetas de periodo: 0.
- Tasas nulas: 0.
- La razón `incidentes / hurto registrado` queda nula en 9 filas de Sumapaz porque el denominador de hurtos es cero. No se reemplazó por cero ni infinito, ya que matemáticamente la razón no está definida.

Todas las validaciones automáticas pasaron.

## Archivos principales generados

- `data/processed/mapas/localidades_bogota.geojson`
- `data/processed/seguridad/alto_impacto_localidad_long.csv`
- `data/processed/seguridad/incidentes_localidad_long.csv`
- `data/processed/seguridad/seguridad_localidad_integrada.csv`
- `data/processed/poblacion/poblacion_localidades_limpio.csv`
- `data/processed/poblacion/poblacion_localidad_anual.csv`
- `data/processed/mapas/incidentes_upz.geojson`
- `data/processed/mapas/incidentes_sector_catastral.geojson`
- `data/processed/sin_localizacion/`

## Reproducibilidad

La limpieza puede repetirse con:

```powershell
python scripts/profile_sources.py data/raw reports/source_profile.json
python scripts/clean_data.py data/raw data/processed reports/cleaning_report.json
python scripts/build_integrated_table.py data/processed data/processed/seguridad/seguridad_localidad_integrada.csv reports/integrated_quality_checks.json
python scripts/flag_outliers.py data/processed/seguridad/seguridad_localidad_integrada.csv reports/outlier_flags.csv reports/outlier_summary.json
```
