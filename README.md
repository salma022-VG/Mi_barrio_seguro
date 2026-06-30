# 🛡️ Mi Barrio Seguro - Dashboard de Seguridad Ciudadana

**Plataforma integral para mapear, reportar y analizar incidentes de seguridad en Bogotá**

---

## 📋 Tabla de Contenidos

1. [¿Qué es?](#-qué-es)
2. [Inicio Rápido](#-inicio-rápido)
3. [Instalación](#-instalación)
4. [Características](#-características)
5. [Arquitectura](#-arquitectura)
6. [Estructura de Archivos](#-estructura-de-archivos)
7. [Uso de la Aplicación](#-uso-de-la-aplicación)
8. [APIs y Endpoints](#-apis-y-endpoints)
9. [Integración Excel](#-integración-excel)
10. [Troubleshooting](#-troubleshooting)
11. [Tecnologías](#-tecnologías)
12. [Privacidad y Seguridad](#-privacidad-y-seguridad)

---

## 🎯 ¿Qué es?

**Mi Barrio Seguro** es un dashboard web interactivo que permite:

- 📍 **Visualizar** un mapa de calor de incidentes de seguridad en Bogotá
- 💬 **Reportar** incidentes a través de un chatbot conversacional (Pepe)
- 📊 **Ver reportes** en tabla con filtros por tipo y localidad
- 💾 **Guardar automáticamente** en Excel
- 📈 **Analizar** tendencias con gráficos interactivos
- 🗺️ **Cambiar** entre 5 tipos diferentes de mapas base

---

## 🚀 Inicio Rápido

### Instalación del servidor (recomendado)

```powershell
# 1. Abre PowerShell en la carpeta del proyecto
cd "c:\Users\valen\Downloads\Mi barrio seguro"

# 2. Instala dependencias
npm install

# 3. Inicia el servidor
npm start
```

El servidor estará disponible en: **http://localhost:3000**

### Uso sin servidor (alternativa)

Si quieres usar la app sin servidor:
1. Abre `index-all-in-one.html` directamente en tu navegador
2. Los reportes se guardarán en localStorage (no persisten en Excel automáticamente)

---

## ⚙️ Instalación

### Requisitos Mínimos

- ✅ Node.js 14+ (si usas el servidor)
- ✅ Navegador moderno (Edge, Chrome, Firefox)
- ✅ 50 MB de espacio en disco
- ✅ Conexión a internet (para Leaflet, Chart.js, etc.)

### Instalación Detallada

#### Paso 1: Verificar Node.js

```powershell
node --version
npm --version
```

Si no está instalado, descárgalo de: https://nodejs.org

#### Paso 2: Instalar dependencias

```powershell
npm install
```

Esto instala:
- `express` - Servidor web
- `xlsx` - Lectura/escritura de Excel
- `cors` - Permitir solicitudes de la app

#### Paso 3: Iniciar el servidor

```powershell
npm start
```

Verás en la consola:
```
╔════════════════════════════════════════╗
║   🚨 Mi Barrio Seguro - Servidor      ║
╠════════════════════════════════════════╣
║   ✅ Servidor ejecutándose en:        ║
║   http://localhost:3000                ║
║                                        ║
║   Archivo Excel: alimentacion_mapa... ║
║   Hoja de datos: Reportes Pepe        ║
╚════════════════════════════════════════╝
```

#### Paso 4: Acceder a la aplicación

Abre en tu navegador: http://localhost:3000

---

## ✨ Características

### 1️⃣ Chatbot Pepe (Reportes Avanzado)

El chatbot conversacional permite reportar incidentes con detalles completos:

**Cómo funciona:**
1. Haz clic en el botón **Pepe** (esquina inferior derecha o panel lateral)
2. Lee el disclaimer legal de privacidad
3. Responde cada pregunta secuencialmente usando dropdowns:
   - **Tipo de Delito:** Hurto Consumer, Hurto Vivienda, Hurto Moto, Hurto Transporte, Hurto Otro, Robo, etc.
   - **Localidad:** Selecciona de las 20 localidades de Bogotá
   - **Año:** Año del incidente (2018-2025)
   - **Hora:** Hora exacta (formato 24h)
   - **Arma:** ¿Se usó arma? (Sí/No o especificar)
   - **Artículo:** ¿Qué tipo de artículo? (opcional)
   - **Descripción:** Detalles adicionales
   - **Fuente:** ¿Cómo reporta? (Testigo, Víctima, Cámara, Otro)
4. El reporte se guarda automáticamente en Excel y localStorage
5. El dashboard se actualiza en tiempo real

**Campos disponibles:**
- ✅ **Tipo:** Clasificación extendida de delitos
- ✅ **Localidad:** 20 localidades de Bogotá
- ✅ **Año:** Rango 2018-2025
- ✅ **Hora:** Formato 24 horas
- ✅ **Arma:** Información de armas usadas
- ✅ **Artículo:** Clasificación de bienes robados
- ✅ **Descripción:** Texto libre (hasta 500 caracteres)
- ✅ **Fuente:** Tipo de testigo/reporte
- ⭕ *Campos opcionales pueden ser omitidos*

**Ejemplo de diálogo:**
```
[DISCLAIMER LEGAL]
Pepe: ¿Qué tipo de delito reportas?
Tú:   → Selecciona "Hurto Moto" de dropdown
Pepe: ¿En qué localidad ocurrió?
Tú:   → Selecciona "Santa Fe" de dropdown
Pepe: ¿En qué año?
Tú:   → Selecciona "2024"
Pepe: ¿A qué hora?
Tú:   → Escribe "14:30"
Pepe: ¿Se usó arma?
Tú:   → Selecciona "No"
Pepe: ¿Qué tipo de artículo?
Tú:   → Salta (opcional)
Pepe: ¿Descripción adicional?
Tú:   → "Moto roja placa ABC123"
Pepe: ¿Cómo reportas?
Tú:   → Selecciona "Testigo"
✅ Reporte guardado automáticamente
📊 Dashboard actualizado con nuevos datos
📄 Aparece en tabla de reportes (sin contacto)
```

### 2️⃣ Dashboard Principal con KPIs

El dashboard muestra 4 tarjetas de información clave que **se actualizan en tiempo real**:

**Tarjetas de KPI:**
- 🚨 **Hurtos:** Total de reportes de hurtos (se actualiza automáticamente)
- 🔴 **Incidentes:** Total de reportes de robo e incidentes (se actualiza automáticamente)
- 🌍 **Cobertura:** Porcentaje de localidades con reportes
- 👥 **Reportes Comunitarios:** Cantidad total de reportes generados por el sistema Pepe

**Gráficos:**
- 📈 **Tendencia 2018-2025:** Línea mostrando evolución de hurtos por año
- 🥧 **Distribución:** Gráfico de rosquilla con totales por tipo

### 3️⃣ Tabla "Datos Históricos" (DINÁMICA)

- ✅ Actualización **en tiempo real** con reportes de Pepe
- ✅ Filtro por localidad (búsqueda)
- ✅ Agrupación por año
- ✅ Alternancia de colores por fila para legibilidad
- ✅ Efecto hover para interactividad

**Columnas:**
- Localidad
- Año
- Hurtos (total)
- Incidentes (total)

### 4️⃣ Tabla "Localidades con Mayor Incidencia" (ESTÁTICA)

- ✅ **Datos fijos** que NO se actualizan con nuevos reportes
- ✅ Ranking de localidades por incidencia
- ✅ Información de peligrosidad
- ✅ Sin filtros

### 5️⃣ Sección de Reportes Pepe

- ✅ Vista de todos los reportes generados por Pepe
- ✅ Filtro por tipo de delito (Hurto/Robo/etc)
- ✅ Filtro por localidad
- ✅ Botón "🔄 Actualizar" para refrescar datos del Excel
- ✅ Scroll horizontal para ver todas las columnas
- ✅ Botón "💾 Exportar a Excel" para descargar reportes

**Columnas de la tabla:**
- Tipo (clasificación extendida)
- Localidad
- Hora
- Descripción
- Fecha Reporte

### 6️⃣ Mapa Interactivo

- Visualización de reportes en un mapa Leaflet
- Información de localidades cuando haces clic
- 5 tipos de mapas base disponibles

### 7️⃣ Gráficos y Estadísticas

- **Tendencia Anual 2018-2025:** Línea mostrando evolución de hurtos
- **Distribución:** Gráfico de rosquilla mostrando totales
- Datos actualizables desde Excel

---

## 🔄 Sistema de Actualización en Tiempo Real

### Sincronización Automática

Cuando se envía un reporte a través de Pepe:

```
1. Reporte se guarda en localStorage (inmediato)
2. Se envía al servidor (POST /api/reports)
3. Servidor guarda en Excel automáticamente
4. Dashboard recibe confirmación
5. KPIs se recalculan automáticamente
6. Tabla "Datos Históricos" se actualiza
7. Interfaz muestra cambios sin necesidad de refrescar
```

### Tablas Dinámicas vs Estáticas

| Tabla | Comportamiento | Actualización |
|-------|---|---|
| **Datos Históricos** | ✅ Dinámica | Se actualiza con nuevos reportes de Pepe |
| **Localidades con Mayor Incidencia** | ❌ Estática | Valores fijos, no se actualiza nunca |
| **Tabla de Reportes** | ✅ Dinámica | Se recarga al refrescar o cambiar filtros |

---

## 🎨 Interfaz y Experiencia de Usuario

### Diseño Actual

- **Modo oscuro:** Tema oscuro premium (fondo #0f172a)
- **Colores:** Gradientes magenta-púrpura (#d946ef → #9d174d)
- **Sidebar:** Panel lateral colapsable con iconos
- **Responsive:** Adaptado para diferentes tamaños de pantalla
- **Animaciones:** Transiciones suaves en 0.3s cubic-bezier

### Sidebar Navigation

```
┌──────────────────────┐
│ 📊 Dashboard        │ ← Vista principal con KPIs
├──────────────────────┤
│ 🗺️  Mapa             │ ← Visualización geográfica
├──────────────────────┤
│ 📋 Datos Históricos  │ ← Tabla histórica dinámica
├──────────────────────┤
│ ⚠️  Pepe Chatbot    │ ← Chatbot de reportes
├──────────────────────┤
│ 📄 Ver Reportes     │ ← Tabla de reportes Pepe
└──────────────────────┘
```

### Respuestas como Dropdowns

Todas las opciones de múltiple selección ahora son **dropdowns (select)** con estilos personalizados:

```html
<!-- Formato actual en chatbot -->
<select style="background: rgba(13, 27, 42, 0.5); color: white;">
  <option>Hurto Consumer</option>
  <option>Hurto Vivienda</option>
  <option>Hurto Moto</option>
  <option>Robo</option>
</select>
```

### Disclaimer Legal

Cada inicio de conversación con Pepe muestra un aviso importante:

```
⚠️  AVISO DE PRIVACIDAD Y CONSENTIMIENTO

Al reportar incidentes usted entiende que:
✓ La información será guardada en una base de datos local
✓ Se compartirá solo con autoridades autorizadas
✓ Sus datos personales serán tratados con confidencialidad
✓ El reporte es voluntario

Presione "Continuar" para aceptar
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                  Navegador (Cliente)                    │
│  ┌─────────────────────────────────────────────────────┐│
│  │  index-all-in-one.html                              ││
│  │  • Chatbot Pepe (conversacional)                    ││
│  │  • Tabla de reportes (filtros)                      ││
│  │  • Mapa Leaflet                                     ││
│  │  • Gráficos Chart.js                                ││
│  │  • Comunicación con servidor (fetch API)            ││
│  └─────────────────────────────────────────────────────┘│
└──────────────┬──────────────────────────────────────────┘
               │ HTTP (Puerto 3000)
               ↓
┌──────────────────────────────────────────────────────────┐
│         Node.js + Express (Servidor)                     │
│  ┌──────────────────────────────────────────────────────┐│
│  │  server.js                                           ││
│  │  ✅ GET /api/reports         → Lee del Excel        ││
│  │  ✅ POST /api/reports        → Escribe en Excel     ││
│  │  ✅ GET /api/reports/filter  → Filtros            ││
│  │  ✅ GET /api/yearly-stats    → Datos anuales       ││
│  └──────────────────────────────────────────────────────┘│
└──────────────┬──────────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────────┐
│     Excel: alimentacion_mapa_datajam_anual.xlsx         │
│  ┌──────────────────────────────────────────────────────┐│
│  │  Hoja "Reportes Pepe"                               ││
│  │  • Tipo         (Clasificación extendida)           ││
│  │  • Localidad    (20 localidades)                    ││
│  │  • Año          (2018-2025)                         ││
│  │  • Hora         (formato 24h)                       ││
│  │  • Arma         (información de armas)              ││
│  │  • Artículo     (tipo de bien robado)               ││
│  │  • Descripción  (texto libre)                       ││
│  │  • Fuente       (tipo de reporte)                   ││
│  │  • Timestamp    (fecha y hora)                      ││
│  └──────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────┐│
│  │  Otras hojas:                                        ││
│  │  • Datos históricos                                 ││
│  │  • Agregaciones anuales                             ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Archivos

```
Mi barrio seguro/
│
├── 📄 index-all-in-one.html
│   └─ Aplicación principal (todo en uno)
│      • Interfaz UI (HTML)
│      • Estilos (CSS)
│      • Lógica (JavaScript)
│
├── 🖥️  server.js
│   └─ Backend Node.js + Express
│      • API endpoints
│      • Lectura/escritura Excel
│      • Gestión de reportes
│
├── 📦 package.json
│   └─ Configuración del proyecto
│      • Dependencias (express, xlsx, cors)
│      • Scripts (npm start)
│
├── 💾 alimentacion_mapa_datajam_anual.xlsx
│   └─ Base de datos Excel
│      • Hoja "Reportes Pepe" → reportes Chatbot
│      • Otras hojas → datos históricos
│
├── 📖 README.md (este archivo)
│   └─ Documentación completa
│
└── 📁 node_modules/
    └─ Librerías instaladas (no modificar)
```

---

## 💻 Uso de la Aplicación

### Acceso a la aplicación

1. **Con servidor (recomendado):**
   ```powershell
   npm start
   # Luego abre: http://localhost:3000
   ```

2. **Sin servidor:**
   - Abre `index-all-in-one.html` directamente en el navegador
   - Los reportes se guardan en localStorage (no en Excel)

### Panel Izquierdo (Sidebar)

```
┌─ Botones principales ─┐
│ • Reportar Hurto     │  → Icono de "Hurto"
│ • Reportar Robo      │  → Icono de "Robo"
│ • Ver Reportes       │  → Icono de "Reporte"
│                      │
│ • Pepe               │  → Chatbot (puede estar aquí)
└──────────────────────┘
```

### Chatbot Pepe

**Ubicaciones:**
- ✅ Botón flotante en esquina inferior derecha
- ✅ Botón en panel izquierdo

**Cómo usar:**
1. Haz clic en "Pepe"
2. Responde cada pregunta conversacionalmente
3. Al terminar, se guarda automáticamente en Excel

### Tabla de Reportes

**Cómo acceder:**
1. Panel izquierdo → "Ver Reportes"
2. Se abre sección con tabla de todos los reportes

**Funciones:**
- 🔍 Filtrar por tipo (Hurto/Robo)
- 🔍 Filtrar por localidad
- 🔄 Botón "Refrescar" para cargar del Excel
- ⬅️➡️ Scroll horizontal para ver todas las columnas

### Mapa

- Visualiza los reportes de forma geográfica
- Haz clic en localidades para ver información
- Cambia el tipo de mapa en las opciones

---

## 📊 Sistema de KPIs y Actualización en Tiempo Real

### Cómo Funcionan los KPIs

Las 4 tarjetas del dashboard se actualizan automáticamente sin necesidad de refrescar la página:

#### 1️⃣ KPI "Hurtos"
```javascript
// Se calcula sumando todos los reportes con tipo "Hurto*"
// Ejemplo: Hurto Consumer + Hurto Vivienda + Hurto Moto = Total Hurtos

Fórmula: COUNT(reportes WHERE tipo LIKE "Hurto%")
Actualización: Cada vez que se envía un nuevo reporte
Fuente: localStorage['pepeReports']
```

#### 2️⃣ KPI "Incidentes"
```javascript
// Se calcula sumando todos los reportes con tipo "Robo" u otros incidentes
// Diferente de hurtos

Fórmula: COUNT(reportes WHERE tipo NOT LIKE "Hurto%")
Actualización: Cada vez que se envía un nuevo reporte
```

#### 3️⃣ KPI "Cobertura"
```javascript
// Porcentaje de localidades que tienen al menos 1 reporte
// Máximo 100% (20 localidades de Bogotá)

Fórmula: (Localidades con reportes / 20) * 100
Rango: 0% - 100%
```

#### 4️⃣ KPI "Reportes Comunitarios"
```javascript
// Total de reportes generados a través de Pepe

Fórmula: COUNT(reportes)
Actualización: Se incrementa cada vez que se envía un reporte
```

### Flujo de Actualización

```
Usuario completa reporte en Pepe
        ↓
JavaScript valida datos
        ↓
Guardar en localStorage (inmediato)
        ↓
Enviar POST a /api/reports
        ↓
Servidor recibe y valida
        ↓
Servidor guarda en Excel (ambos archivos)
        ↓
Servidor responde con confirmación
        ↓
JavaScript ejecuta updateDashboardWithNewReport()
        ↓
KPIs se recalculan desde localStorage
        ↓
Tabla Datos Históricos se actualiza
        ↓
Interfaz muestra cambios (sin refrescar)
        ↓
✅ Todo sincronizado
```

---

## 🔌 APIs y Endpoints

Todos los endpoints están en el servidor `http://localhost:3000`

### GET /api/reports
Obtiene todos los reportes del Excel

**Respuesta:**
```json
[
  {
    "tipo": "Hurto Moto",
    "localidad": "Santa Fe",
    "hora": "14:30",
    "descripcion": "Moto roja placa ABC123",
    "timestamp": "30/6/2026 14:30:45"
  },
  ...
]
```

### POST /api/reports
Guarda un nuevo reporte en Excel y localStorage

**Datos requeridos:**
```json
{
  "tipo": "Hurto Moto",
  "localidad": "Santa Fe",
  "year": "2024",
  "hora": "14:30",
  "arma": "No",
  "articulo": "Moto",
  "descripcion": "Moto roja placa ABC123",
  "fuente": "Testigo"
}
```

**Notas:**
- Se guardan los campos: tipo, localidad, year, hora, arma, articulo, descripcion, fuente
- El campo de contacto fue removido

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Reporte guardado en Excel"
}
```

**Efecto secundario:**
- Los KPIs del dashboard se actualizan automáticamente
- La tabla "Datos Históricos" se actualiza automáticamente
- El localStorage se sincroniza automáticamente

### GET /api/reports/filter
Obtiene reportes filtrados

**Parámetros:**
- `tipo` - Filtrar por tipo (Hurto/Robo)
- `localidad` - Filtrar por localidad

**Ejemplo:**
```
GET /api/reports/filter?tipo=Robo&localidad=Santa%20Fe
```

### GET /api/yearly-stats
Obtiene estadísticas anuales del Excel

**Respuesta:**
```json
{
  "years": ["2018", "2019", "2020", ...],
  "hurtos": [85000, 90000, 92000, ...],
  "incidentes": [101900, 138440, ...]
}
```

---

## 📋 Opciones Disponibles en Chatbot Pepe

### Pregunta 1: Tipo de Delito

```
Hurto Consumer        (Hurto en comercios)
Hurto Vivienda        (Hurto en casas)
Hurto Moto            (Hurto de motocicletas)
Hurto Transporte      (Hurto en transporte público)
Hurto Otro            (Otros tipos de hurto)
Robo a Mano Armada    (Robo con armas)
Robo Carros           (Robo de vehículos)
Robo Motos            (Robo de motocicletas)
Violencia Intrafamiliar
Lesiones Personales
Otros
```

### Pregunta 2: Localidad (20 opciones)

```
Usaquén               Santa Fe              San Cristóbal
Usme                  Tunjuelito            Bosa
Kennedy               Fontibón              Engativá
Suba                  Barrios Unidos        Teusaquillo
Los Mártires          Antonio Nariño        Puente Aranda
La Candelaria         Rafael Uribe Uribe    Ciudad Bolívar
Sumapaz
```

### Pregunta 3: Año

```
2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025
```

### Pregunta 4: Hora

```
Formato libre: HH:MM (ej: 14:30, 09:15)
Rango válido: 00:00 - 23:59
```

### Pregunta 5: Arma

```
No                    (No se usó arma)
Pistola               (Pistola)
Revolver              (Revólver)
Cuchillo              (Cuchillo/arma blanca)
No especificado       (Se usó arma pero no sabe cuál)
```

### Pregunta 6: Artículo (OPCIONAL)

```
Celular               Laptop/Computadora    Joyería
Moto                  Carro                 Efectivo
Documentos            Ropa                  Otro
(Dejar en blanco si no sabe)
```

### Pregunta 7: Descripción

```
Texto libre (máximo 500 caracteres)
Incluya detalles como:
- Color y marca del bien robado
- Placa (si es vehículo)
- Características especiales
- Cualquier información importante
```

### Pregunta 8: Fuente

```
Testigo             (Presenció el hecho)
Víctima             (Fue víctima directa)
Cámara de seguridad (Información de cámaras)
Otro                (Otra fuente)
```

---

## 💾 Integración Excel

### Ubicación del archivo

```
C:\Users\valen\Downloads\Mi barrio seguro\alimentacion_mapa_datajam_anual.xlsx
```

### Estructura de datos

**Hoja: "Reportes Pepe"**

| Tipo | Localidad | Hora | Descripción | Fecha Reporte |
|------|-----------|------|-------------|---------------|
| Hurto Moto | Santa Fe | 14:30 | Moto roja placa ABC123 | 30/6/2026 14:30 |
| Robo | Chapinero | 10:00 | Celular color plateado | 30/6/2026 10:15 |

**Campos:**
- **Tipo:** Clasificación de delito (Hurto Consumer, Hurto Vivienda, Hurto Moto, Hurto Transporte, Robo, etc.)
- **Localidad:** Localidad donde ocurrió (20 opciones)
- **Hora:** Hora en formato 24h
- **Descripción:** Detalles del incidente (texto libre)
- **Fecha Reporte:** Timestamp de cuándo se reportó

### Flujo de datos

```
Usuario reporta en Pepe
        ↓
JavaScript envia POST a /api/reports
        ↓
server.js recibe solicitud
        ↓
Lee Excel actual (alimentacion_mapa_datajam_anual.xlsx)
        ↓
Busca hoja "Reportes Pepe"
        ↓
Agrega nuevo reporte
        ↓
Guarda Excel modificado
        ↓
Responde al cliente
        ↓
Aplicación actualiza tabla de reportes
```

### Localidades válidas

El sistema acepta estas 20 localidades de Bogotá:

1. Usaquén
2. Chapinero
3. Santa Fe
4. San Cristóbal
5. Usme
6. Tunjuelito
7. Bosa
8. Kennedy
9. Fontibón
10. Engativá
11. Suba
12. Barrios Unidos
13. Teusaquillo
14. Los Mártires
15. Antonio Nariño
16. Puente Aranda
17. Candelaria
18. Rafael Uribe Umaña
19. Ciudad Bolívar
20. Sumapaz

---

## 🔍 Troubleshooting

### El servidor no inicia

**Error:** "Cannot find module 'express'"

**Solución:**
```powershell
npm install express xlsx cors
npm start
```

### El puerto 3000 está en uso

**Error:** "EADDRINUSE: address already in use :::3000"

**Solución:**
```powershell
# Opción 1: Cambiar puerto en server.js
# Abre server.js y cambia: const PORT = 3000; → const PORT = 3001;

# Opción 2: Liberar puerto
# Abre PowerShell como administrador:
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process
npm start
```

### Los reportes no se guardan en Excel

**Problema:** POST a /api/reports devuelve error

**Solución:**
1. Verifica que el archivo Excel existe:
   ```powershell
   Test-Path "c:\Users\valen\Downloads\Mi barrio seguro\alimentacion_mapa_datajam_anual.xlsx"
   ```

2. Verifica en consola del servidor si hay errores

3. Abre Excel y verifica que la hoja "Reportes Pepe" existe

### La tabla de reportes está vacía

**Solución:**
1. Haz clic en "Refrescar" en la sección de reportes
2. Abre DevTools (F12) → Consola para ver errores
3. Verifica que el servidor está corriendo: `http://localhost:3000/api/reports`

### El chatbot no responde

**Problema:** Pepe no entiende el reporte

**Solución:**
1. Asegúrate de seleccionar un tipo válido: **Hurto** o **Robo**
2. Selecciona una localidad de la lista (no inventes nombres)
3. Recarga la página si es necesario

### DevTools (Debugging)

Presiona **F12** para abrir las herramientas de desarrollador:

- 📋 **Consola:** Ver errores JavaScript
- 🌐 **Network:** Ver solicitudes HTTP
- 💾 **Application → localStorage:** Ver datos guardados
- 🔍 **Inspector:** Inspeccionar HTML/CSS

**Búsqueda útil en consola:**
```javascript
// Ver todos los reportes guardados
console.log(JSON.parse(localStorage.getItem('reportes')));

// Ver si el servidor responde
fetch('http://localhost:3000/api/reports').then(r => r.json()).then(d => console.log(d));
```

---

## 🛠️ Tecnologías

### Frontend (HTML/CSS/JavaScript)

| Librería | Versión | Propósito |
|----------|---------|----------|
| Leaflet.js | 1.9+ | Mapas interactivos |
| Chart.js | 3.9+ | Gráficos |
| Bootstrap | 5.3+ | UI Framework |
| Font Awesome | 6.4+ | Iconos |
| PapaParse | 5.4+ | Parsing CSV |

### Backend (Node.js)

| Librería | Versión | Propósito |
|----------|---------|----------|
| Express | 4.18+ | Servidor web |
| XLSX | 0.18+ | Lectura/escritura Excel |
| CORS | 2.8+ | Control de cross-origin |

### Datos

| Formato | Ubicación | Contenido |
|---------|-----------|----------|
| Excel | alimentacion_mapa_datajam_anual.xlsx | Reportes + datos históricos |
| localStorage | Navegador | Reportes temporales (si no hay servidor) |

---

## 🔐 Privacidad y Seguridad

✅ **Seguridad implementada:**

- Los reportes se guardan en el servidor local (no en internet)
- No se envían datos a servidores externos
- El archivo Excel es controlado por el usuario
- Solo se almacenan datos esenciales (tipo, localidad, hora, descripción, contacto)
- Sin rastreo de ubicación exacta
- Sin análisis de comportamiento

⚠️ **Consideraciones:**

- El contacto (teléfono) es opcional
- No se valida información personal
- Se recomienda no compartir direcciones exactas
- El archivo Excel debe guardarse en lugar seguro

---

## 📞 Soporte

### Problemas comunes

1. **Servidor no inicia:** Ver sección Troubleshooting
2. **Reportes no se guardan:** Verifica conexión con Excel
3. **Tabla vacía:** Haz clic en "Refrescar"
4. **Error de módulo:** Ejecuta `npm install`

### Debugging

1. Abre DevTools con **F12**
2. Ve a **Consola**
3. Busca mensajes de error
4. Si es error de red, verifica **Network**

---

## 📊 Información Técnica Adicional

### Variables de entorno

No se requieren configuraciones especiales. El sistema usa valores por defecto:

```javascript
// server.js
const PORT = 3000;
const EXCEL_FILE = 'alimentacion_mapa_datajam_anual.xlsx';
const SHEET_NAME = 'Reportes Pepe';
```

### Limpieza de datos

Para limpiar todos los reportes:

```powershell
# Opción 1: Limpiar localStorage en navegador
# F12 → Application → localStorage → Elimina 'pepeReports'

# Opción 2: Eliminar archivo Excel y recrearlo
# PowerShell: Remove-Item "c:\Users\valen\Downloads\Mi barrio seguro\Reportes_Pepe.xlsx"
# El servidor lo recreará automáticamente al guardar el primer reporte

# Opción 3: Crear nueva hoja en Excel manualmente
# Abre alimentacion_mapa_datajam_anual.xlsx
# Elimina hoja "Reportes Pepe"
# El servidor la recreará automáticamente

# Opción 4: Editar server.js para usar nuevo nombre de hoja
# Cambia: const SHEET_NAME = 'Reportes Pepe'; 
# Por: const SHEET_NAME = 'Reportes Nuevos';
```

### Mantenimiento

**Backup de datos:**
```powershell
Copy-Item "alimentacion_mapa_datajam_anual.xlsx" "alimentacion_mapa_datajam_anual_backup.xlsx"
```

---

## ✅ Checklist de Configuración

- [ ] Node.js instalado (`node --version`)
- [ ] npm instalado (`npm --version`)
- [ ] Carpeta del proyecto descargada
- [ ] `npm install` ejecutado
- [ ] `npm start` funciona sin errores
- [ ] Navegador abre http://localhost:3000
- [ ] Pepe aparece (esquina inferior derecha)
- [ ] Puedo enviar reportes a través de Pepe
- [ ] Los reportes aparecen en la tabla
- [ ] Los reportes se guardan en Excel

---

## 🚀 Primeros Pasos

### Instalación y Ejecución

1. **Abre PowerShell en la carpeta del proyecto:**
   ```powershell
   cd "c:\Users\valen\Downloads\Mi barrio seguro"
   ```

2. **Instala las dependencias:**
   ```powershell
   npm install
   ```

3. **Inicia el servidor:**
   ```powershell
   npm start
   ```

4. **Abre en tu navegador:**
   ```
   http://localhost:3000
   ```

### Prueba la Aplicación

1. **Dashboard:** Verifica que aparezcan las 4 tarjetas de KPI
2. **Chatbot Pepe:** Haz clic en el icono y completa un reporte
3. **Actualización automática:** Verifica que el dashboard se actualiza
4. **Tabla de reportes:** Ve a "Ver Reportes" para ver la tabla
5. **Excel:** Abre `alimentacion_mapa_datajam_anual.xlsx` para verificar que se guardó

### Verificación de Funcionamiento

```powershell
# Verifica que el servidor está corriendo
curl http://localhost:3000/api/reports

# Verifica que el archivo Excel existe
Test-Path "c:\Users\valen\Downloads\Mi barrio seguro\alimentacion_mapa_datajam_anual.xlsx"
```

---

---

## 📝 Historial de Cambios

### Versión 3.1 (2026-06-30) - Eliminación de Contacto

**Cambios:**
- ❌ Removida la columna "Contacto" de la tabla de reportes (no aplica)
- ✅ Tabla ahora solo muestra: Tipo, Localidad, Hora, Descripción, Fecha Reporte
- ✅ Exportación a Excel actualizada sin campo de contacto

### Versión 3.0 (2026-06-30) - Actualización Completa

**Nuevas características:**
- ✅ Dashboard con 4 KPIs que se actualizan en tiempo real
- ✅ Chatbot Pepe mejorado con 8 campos (tipo, localidad, año, hora, arma, artículo, descripción, fuente)
- ✅ Respuestas como dropdowns (select) en lugar de botones
- ✅ Tabla "Datos Históricos" dinámica que se actualiza con reportes
- ✅ Tabla "Localidades con Mayor Incidencia" completamente estática
- ✅ Sistema de disclaimer legal/privacidad
- ✅ Auto-guardado en Excel automático
- ✅ Sincronización localStorage + servidor
- ✅ Exportación a Excel desde tabla de reportes
- ✅ Efectos visuales mejorados (hover, gradientes, animaciones)

**Cambios técnicos:**
- Integración bidireccional localStorage ↔ Excel
- Event-driven UI updates
- Sequential async message display en chatbot
- Multiple dropdown select inputs
- Optional form fields con skip functionality
- Selective dynamic vs static table behavior

**Campos ahora disponibles:**
```
Tipo:         Clasificación extendida (Hurto Consumer, Hurto Vivienda, Hurto Moto, etc.)
Localidad:    20 localidades de Bogotá
Año:          2018-2025
Hora:         Formato 24 horas
Arma:         ¿Se usó arma?
Artículo:     Tipo de bien robado (opcional)
Descripción:  Texto libre (hasta 500 caracteres)
Fuente:       Tipo de reporte (Testigo, Víctima, Cámara, Otro)
```

### Versión 2.0 (Anterior)
- Dashboard básico
- Chatbot simple con pocas preguntas
- Tabla de reportes sin actualización dinámica

---

## 📊 Información Técnica

**Versión actual:** 3.0  
**Fecha de actualización:** 2026-06-30  
**Estado:** ✅ Producción - Totalmente funcional  
**Servidor:** Express.js en puerto 3000  
**Base de datos:** Excel local + localStorage  
**Interfaz:** Single Page Application (SPA)  
**Contacto:** valentona143@gmail.com

---

## 🎯 Características Implementadas (Checklist)

- [x] Chatbot Pepe conversacional
- [x] Dashboard con KPIs
- [x] Tabla histórica dinámica
- [x] Tabla localidades estática
- [x] Sistema de reportes
- [x] Auto-guardado en Excel
- [x] Sincronización localStorage
- [x] Filtros y búsqueda
- [x] Mapa interactivo
- [x] Gráficos Chart.js
- [x] Disclaimer legal
- [x] Exportación Excel
- [x] Interfaz responsiva
- [x] Modo oscuro premium
- [x] Dropdowns personalizados
