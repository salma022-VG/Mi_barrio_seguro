# Definición del MVP de seguridad

## Decisión

Se mantiene **Delito de Alto Impacto** como fuente principal y se enfoca el relato analítico en **hurto a personas**. Se integran otras dos fuentes públicas:

1. **Incidente Reportado**: llamadas ciudadanas trasladadas a agencias de respuesta, con agregación por localidad, mes y año.
2. **Población en Bogotá D.C. 2005-2035**: denominador por localidad y año para construir tasas comparables. Su recurso CSV incluye sexo, edad y curso de vida, lo que permite añadir contexto demográfico sin complicar la ingesta.

El producto tendrá una cuarta entrada experimental: **reportes comunitarios por WhatsApp o formulario web**. Esta capa no se mezclará con las cifras oficiales.

## Problema público

Los conteos de hurtos registrados no permiten comparar directamente las localidades de Bogotá porque tienen tamaños poblacionales diferentes. Además, la relación entre delitos registrados y llamadas ciudadanas por incidentes de hurto puede variar territorialmente, lo que dificulta identificar dónde se concentran las mayores tasas y dónde existen brechas entre registro institucional y demanda de atención.

## Pregunta analítica

¿Cómo evolucionaron anualmente los hurtos a personas en Bogotá entre 2018 y 2025, qué diferencias existen entre conteos y tasas por localidad y cómo se relacionan con los incidentes de hurto reportados al 123?

## Hipótesis preliminar

Las localidades con más hurtos en valores absolutos no serán necesariamente las de mayor tasa por 100.000 habitantes. También existirán localidades donde la relación entre incidentes 123 y delitos registrados sea atípicamente alta o baja, señalando diferencias territoriales que requieren análisis adicional sobre reporte, atención o registro.

La hipótesis es exploratoria. Una correlación no demostrará causalidad ni permitirá estimar por sí sola el subregistro.

## Unidad de análisis y periodo

- Unidad de análisis: localidad + año completo.
- Los recursos anuales oficiales de Delito de Alto Impacto e Incidente Reportado cubren enero-diciembre de 2018 a 2025.
- El acumulado enero-mayo de 2026 se conserva como referencia parcial separada y no se mezcla con la tendencia anual.
- Las tasas se denominan **tasas anuales por 100.000 habitantes**.
- En 2025 la cobertura territorial de hurtos a personas baja a 82,3%; por ello 2024 será la vista cartográfica inicial.

## Indicadores principales

- Hurtos a personas registrados.
- Tasa de hurtos a personas por 100.000 habitantes.
- Variación interanual para periodos equivalentes.
- Incidentes 123 asociados a hurto.
- Incidentes 123 por cada hurto registrado.
- Diferencia entre ranking por conteo y ranking por tasa.
- Participación de cada localidad en el total distrital.

No se sumarán delitos de naturaleza distinta para fabricar un índice único de inseguridad.

## Dashboard MVP

### Mapa principal

Mapa coroplético por localidad con selector de:

- Indicador: conteo, tasa, variación o brecha de reporte.
- Año completo: 2018 a 2025.
- Categoría delictiva, manteniendo hurto a personas como vista inicial.
- Capa: oficial, incidentes 123 o comunitaria.

Al seleccionar una localidad se mostrará: conteo, tasa, posición relativa, variación interanual, relación con incidentes 123, cobertura territorial y fecha de corte.

### Vistas complementarias

- Tendencia anual 2018-2025 de la localidad seleccionada y Bogotá.
- Ranking de localidades por tasa, no solo por conteo.
- Comparación delitos registrados vs. incidentes 123.
- Metodología, fuentes y limitaciones visibles dentro del producto.

La capa comunitaria mostrará agregados por localidad o celdas espaciales; nunca teléfonos, nombres, direcciones exactas ni descripciones sin moderar.

## Flujo del reporte comunitario

1. Aviso inicial: el canal no sustituye una denuncia ni una llamada de emergencia; para peligro inmediato se debe contactar al 123.
2. Consentimiento informado para el tratamiento de los datos y uso estadístico.
3. Tipo de evento: hurto consumado o intento.
4. Fecha y hora aproximadas.
5. Ubicación compartida o localidad y dirección aproximada.
6. Categoría de lo hurtado.
7. Modalidad del hecho.
8. Arma observada: ninguna, arma blanca, arma de fuego, otra o no sabe.
9. Descripción opcional.
10. Resumen, confirmación y código del reporte.

No se preguntará el nombre. El número de WhatsApp se conservará únicamente si es imprescindible para gestionar el reporte; para analítica se usará un identificador irreversible.

## Estados de moderación

- `pending`: recibido, todavía no publicable.
- `approved`: validación básica completada y apto para agregación.
- `rejected`: spam, duplicado, contenido imposible o malicioso.
- `needs_review`: contiene texto sensible o una ubicación que requiere revisión.

Un reporte comunitario nunca cambia el total oficial. Solo alimenta la capa comunitaria.

## Arquitectura recomendada

```text
WhatsApp / formulario web
          |
          v
Webhook del backend
          |
          +--> validación + conversación + moderación
          |
          +--> Google Sheets privado (bitácora del MVP)
          |
          v
API pública sanitizada y agregada
          |
          v
Dashboard
```

Google Sheets puede funcionar como bitácora del MVP, pero el navegador no debe leer la hoja privada directamente. Un backend debe conservar las credenciales, moderar, eliminar datos personales y exponer únicamente agregados seguros. Google Apps Script permite recibir solicitudes `POST` y devolver JSON, pero para un webhook público se priorizará un endpoint del mismo backend del dashboard, donde también se puedan validar firmas y controlar acceso.

## Datos mínimos del reporte

- `report_id`
- `received_at`
- `event_at`
- `locality_code`
- `address_private`
- `latitude_private`
- `longitude_private`
- `event_type`
- `stolen_item_category`
- `modality`
- `weapon_type`
- `description_private`
- `source`
- `moderation_status`
- `consent_at`
- `phone_hash`

Los campos con sufijo `_private` no se entregan al frontend público.

## Límites que deben aparecer en el dashboard

- Delito registrado, incidente 123 y reporte comunitario miden fenómenos distintos.
- Los datos administrativos pueden tener subregistro, cambios operativos y rezagos.
- La población proyectada es una estimación.
- Los datos de 2026 son provisionales y parciales.
- Un patrón espacial o temporal no demuestra causalidad.
- La capa comunitaria tiene sesgo de autoselección y acceso digital.

## Fuentes oficiales

- Seguridad y Defensa: https://datosabiertos.bogota.gov.co/group/seguridad-y-defensa
- Delito de Alto Impacto: https://datosabiertos.bogota.gov.co/dataset/delito-de-alto-impacto-bogota-d-c
- Incidente Reportado: https://datosabiertos.bogota.gov.co/dataset/incidente-reportado-bogota-d-c
- Población en Bogotá D.C. 2005-2035: https://datosabiertos.bogota.gov.co/dataset/piramide-poblacional-bogota-d-c
