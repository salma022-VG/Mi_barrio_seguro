# Análisis exploratorio de seguridad — versión reemplazada

> **Documento obsoleto:** esta comparación parcial fue reemplazada por `ANALISIS_ANUAL.md`, basado en los recursos oficiales enero-diciembre de 2018 a 2025.

## Alcance válido

El análisis inferencial se limita a la comparación enero-mayo de 2025 contra enero-mayo de 2026. Los campos 2018-2024 se conservan como referencia histórica, pero la ventana temporal no está suficientemente documentada en el archivo para tratarlos como una serie homogénea.

## Hallazgo principal: divergencia entre registros e incidentes

- Hurtos a personas registrados: 54.196 en 2025 y 48.483 en 2026 (-10,5%).
- Incidentes 123 asociados a hurto: 57.979 en 2025 y 58.193 en 2026 (0,4%).
- La razón incidentes/hurtos pasó de 1,07 a 1,20, un aumento relativo de 12,2%.

La divergencia indica que las dos fuentes no evolucionaron de la misma manera. No demuestra subregistro ni causalidad; justifica revisar diferencias entre demanda de atención, denuncia y registro administrativo.

## Hallazgo 2: conteo y tasa producen mapas distintos

La asociación de rangos entre conteo y tasa fue baja en 2026 (Spearman = 0,205). Los mayores conteos fueron: Suba (4.858), Engativá (4.556), Kennedy (4.068), Chapinero (3.865), Teusaquillo (3.404). Las mayores tasas por cada 100.000 habitantes fueron: La Candelaria (3769,2), Santa Fe (2620,7), Los Mártires (2596,4), Chapinero (2413,0), Teusaquillo (2200,9).

El ejemplo más claro es La Candelaria: puesto 19 por conteo y puesto 1 por tasa. Suba ocupa el puesto 1 por conteo y el 14 por tasa. Esto confirma que el dashboard debe permitir alternar entre ambas lecturas.

Las tasas altas del centro deben interpretarse con cautela porque el denominador usa población residente y no población flotante.

## Hallazgo 3: divergencias territoriales 2025-2026

- **Teusaquillo:** hurtos -8,8%; incidentes 29,9%; brecha 38,8 p.p.
- **Ciudad Bolívar:** hurtos -22,5%; incidentes 12,3%; brecha 34,8 p.p.
- **Barrios Unidos:** hurtos -10,1%; incidentes 8,7%; brecha 18,8 p.p.
- **Engativá:** hurtos -13,7%; incidentes 1,4%; brecha 15,1 p.p.
- **Suba:** hurtos -15,7%; incidentes -0,6%; brecha 15,0 p.p.

Estas brechas son señales para priorizar revisión, no para afirmar que una fuente es correcta y la otra incorrecta.

## Asociación entre fuentes

En 2026 los hurtos registrados y los incidentes 123 presentan asociación territorial alta: Pearson = 0,888 y Spearman = 0,868. Sin embargo, la razón incidentes/hurto varía entre localidades, por lo que las fuentes son complementarias y no sustituibles.

## Revisión de outliers

Para 2025-2026 se marcaron 7 valores: altos incidentes en Kennedy, Engativá y Suba, y una tasa alta de hurto en La Candelaria. Todos se conservaron porque son coherentes con tamaño poblacional, centralidad o volumen de actividad y no hay evidencia de error de captura.

## Evaluación de la hipótesis

- **Confirmada parcialmente:** el ranking por conteo difiere sustancialmente del ranking por tasa.
- **Confirmada como patrón exploratorio:** existen localidades con relaciones atípicas entre incidentes 123 y hurtos registrados.
- **No demostrada:** no puede concluirse causalidad ni estimar directamente subregistro con estas fuentes agregadas.
