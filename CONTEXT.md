# Observatorio territorial de seguridad ciudadana

Este contexto define el lenguaje con el que el proyecto compara registros oficiales, demanda ciudadana de atención y reportes comunitarios sin confundir su alcance probatorio.

## Language

**Delito registrado**:
Hecho incluido en el conjunto oficial Delito de Alto Impacto, agregado por localidad, mes, año y categoría delictiva. Es un registro administrativo y no equivale a la totalidad de delitos ocurridos.
_Avoid_: delito real, inseguridad real, denuncia ciudadana

**Incidente 123**:
Llamada ciudadana trasladada a una agencia de respuesta y publicada en el conjunto Incidente Reportado. Indica demanda de atención, no confirmación de un delito.
_Avoid_: denuncia, delito confirmado

**Reporte comunitario**:
Relato voluntario recibido por WhatsApp o por el formulario web del proyecto. Es información autodeclarada, pendiente de moderación y sin validez como denuncia oficial.
_Avoid_: denuncia, caso policial, delito confirmado

**Hurto a personas**:
Categoría principal usada para comparar localidades y periodos dentro de Delito de Alto Impacto.
_Avoid_: inseguridad total, criminalidad total

**Tasa de hurto**:
Cantidad de hurtos a personas registrados por cada 100.000 habitantes de una localidad y periodo comparables.
_Avoid_: cantidad de hurtos, nivel de inseguridad

**Brecha de reporte**:
Diferencia o razón entre incidentes 123 asociados a hurto y hurtos a personas registrados para la misma localidad y periodo. Es una señal exploratoria y no una estimación directa de subregistro.
_Avoid_: cifra negra, delitos no denunciados

**Capa oficial**:
Visualización construida exclusivamente con fuentes públicas institucionales.
_Avoid_: mapa en tiempo real

**Capa comunitaria**:
Visualización agregada de reportes comunitarios moderados, separada de la capa oficial.
_Avoid_: capa oficial, denuncias en vivo

**Fecha de corte**:
Último periodo comparable incluido en un análisis. La serie anual vigente termina en diciembre de 2025; enero-mayo de 2026 se conserva como referencia parcial separada.
_Avoid_: fecha de actualización del portal

**Cobertura territorial**:
Porcentaje del total distrital asignado a una de las veinte localidades y representable en el mapa. En 2025 la cobertura de hurtos a personas es 82,3%.
_Avoid_: completitud total, porcentaje de denuncia
