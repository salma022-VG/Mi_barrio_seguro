# Estrategia MVP - DataJam Bogotá 2026

## Lectura ejecutiva

El reto no premia el dashboard más vistoso de forma aislada. El 80% de la ponderación está en la pertinencia, el rigor, la calidad técnica y la solidez del diagnóstico; visualización y comunicación pesan 10%, y el uso estratégico de datos públicos, 10%. Por eso el MVP debe ser una cadena verificable: problema público -> fuentes -> limpieza e integración -> hallazgo -> recomendación aplicable.

## Decisión de alcance recomendada

Trabajar con una unidad común que pueda sostener el cruce, idealmente `localidad + periodo`. El problema debe ser específico, territorializable, temporalizable, medible y respondible con los datos disponibles. Si los datos no permiten causalidad, presentaremos asociaciones y limitaciones con honestidad metodológica.

La segunda fuente no debe añadirse para cumplir una casilla. Debe aportar al menos una de estas funciones:

1. Denominador para construir tasas comparables.
2. Dimensión explicativa o contextual de la seguridad.
3. Segmentación territorial o poblacional útil para priorizar acciones.
4. Validación o contraste del patrón observado en la fuente principal.

Antes de elegirla comprobaremos: cobertura temporal común, territorio comparable, llave de integración, actualización, diccionario de variables, faltantes y costo técnico de preparación.

## MVP mínimo que sí compite

- Pipeline reproducible desde datos crudos hasta tablas finales.
- Reporte de calidad y decisiones de limpieza.
- Cruce real de mínimo dos fuentes públicas.
- Uno o dos indicadores defendibles, preferiblemente tasas y no solo conteos.
- Un hallazgo principal y, como máximo, dos secundarios.
- Dashboard con mapa territorial y tendencia anual 2018-2025; 2024 será la vista espacial inicial y 2025 mostrará una alerta por cobertura territorial del 82,3%.
- Recomendación concreta: actor responsable, territorio prioritario y acción sugerida.
- README ejecutable, formulario completo y nota técnica de una página.
- Pitch de tres minutos centrado en problema, evidencia, hallazgo y decisión.

## Riesgos que debemos evitar

- Empezar por una solución o por gráficos antes de fijar la pregunta.
- Mezclar granularidades incompatibles.
- Confundir correlación con causalidad.
- Usar conteos brutos para comparar localidades de tamaños distintos.
- Elegir un segundo dataset sin una llave de integración defendible.
- Sobreconstruir el dashboard y dejar débil la reproducibilidad.
- Mostrar demasiados hallazgos en un pitch de tres minutos.

## Próximo paso al recibir el dataset principal

Auditar columnas, cobertura, granularidad, calidad y metadatos; después formular tres preguntas candidatas y evaluar para cada una una segunda fuente cruzable. Elegiremos la combinación con mayor valor público y menor riesgo técnico dentro del tiempo disponible.
