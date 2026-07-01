const express = require('express');
const XLSX = require('xlsx');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const https = require('https');
require('dotenv').config();
const { google } = require('googleapis');

const app = express();
const PORT = 3000;

// Variables de entorno
const GOOGLE_SHEETS_ID = process.env.GOOGLE_SHEETS_ID;
const SHEET_NAME = 'Reportes';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Rutas de archivos
const EXCEL_FILE = path.join(__dirname, 'alimentacion_mapa_datajam_anual.xlsx');
const REPORTS_FILE = path.join(__dirname, 'Reportes_Pepe.xlsx');

// Función para leer reportes del archivo separado
function readReports() {
    try {
        if (!fs.existsSync(REPORTS_FILE)) {
            console.log('⚠️  Archivo de reportes no encontrado');
            return [];
        }

        const workbook = XLSX.readFile(REPORTS_FILE);

        // Buscar hoja de reportes
        if (!workbook.SheetNames.includes(SHEET_NAME)) {
            return [];
        }

        const worksheet = workbook.Sheets[SHEET_NAME];
        let data = XLSX.utils.sheet_to_json(worksheet);

        // Asegurar que siempre sea un array
        if (!Array.isArray(data)) {
            data = data ? [data] : [];
        }

        return data.map(row => ({
            tipo: row['Tipo'] || row['tipo'] || row['Delito'] || '',
            localidad: row['Localidad'] || row['localidad'] || '',
            hora: row['Hora'] || row['hora'] || '',
            descripcion: row['Descripción'] || row['descripcion'] || row['Descripcion'] || '',
            contacto: row['Contacto'] || row['contacto'] || row['Teléfono'] || '',
            timestamp: row['Timestamp'] || row['timestamp'] || row['Fecha'] || new Date().toISOString()
        }));
    } catch (error) {
        console.error('Error al leer reportes:', error);
        return [];
    }
}

// Función para mapear tipo de delito a modalidad
function getModalidadFromTipo(tipo) {
    const modalidades = {
        'hurto_consur': 'hurto',
        'intento_hurto': 'hurto',
        'robo_residencia': 'robo',
        'motocicleta': 'robo',
        'vehiculo': 'robo',
        'computador_halado': 'hurto',
        'documentos': 'hurto',
        'joyas': 'hurto',
        'otro': 'otro'
    };
    return modalidades[tipo] || tipo || 'desconocido';
}

// Función para enviar reporte a Google Sheets usando API
async function sendToGoogleSheets(report) {
    try {
        // Cargar credenciales de la cuenta de servicio
        const credentials = JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_FILE);

        const auth = new google.auth.GoogleAuth({
            credentials,
            scopes: ['https://www.googleapis.com/auth/spreadsheets']
        });

        const sheets = google.sheets({ version: 'v4', auth });

        // Usar la primera hoja disponible (normalmente "Sheet1" o similar)
        const spreadsheet = await sheets.spreadsheets.get({ spreadsheetId: GOOGLE_SHEETS_ID });
        const firstSheet = spreadsheet.data.sheets[0];
        const sheetName = firstSheet.properties.title;

        // Preparar los datos mapeados a las columnas correctas
        const reportData = {
            report_id: Math.random().toString(36).substr(2, 9),
            received_at: new Date().toISOString(),
            event_at: report.timestamp || new Date().toISOString(),
            locality_code: report.localidad || '',
            event_type: report.tipo || '',
            stolen_item_cate: report.modalidad || '',
            modality: report.modalidad || getModalidadFromTipo(report.tipo),
            weapon_type: report.arma || '',
            latitude_private: report.latitude || '',
            longitude_privat: report.longitude || '',
            address_private: report.address || '',
            description_private: report.descripcion || '',
            source: report.fuente || 'web',
            moderation_statu: 'pending',
            consent: false,
            consent_at: '',
            phone_hash: '',
            review_notes_private: `Reporte recibido en ${report.year || new Date().getFullYear()}, hora: ${report.hora || 'no especificada'}`
        };

        // Construir la fila con los valores en el orden correcto
        const values = [[
            reportData.report_id,
            reportData.received_at,
            reportData.event_at,
            reportData.locality_code,
            reportData.event_type,
            reportData.stolen_item_cate,
            reportData.modality,
            reportData.weapon_type,
            reportData.latitude_private,
            reportData.longitude_privat,
            reportData.address_private,
            reportData.description_private,
            reportData.source,
            reportData.moderation_statu,
            reportData.consent,
            reportData.consent_at,
            reportData.phone_hash,
            reportData.review_notes_private
        ]];

        // Agregar datos a Google Sheets
        const response = await sheets.spreadsheets.values.append({
            spreadsheetId: GOOGLE_SHEETS_ID,
            range: `${sheetName}!A:R`,
            valueInputOption: 'USER_ENTERED',
            resource: { values }
        });

        console.log('   ✓ Enviado a Google Sheets (API)');
        return true;
    } catch (error) {
        console.error('   ⚠️  Error al enviar a Google Sheets:', error.message);
        return false;
    }
}

// Función para guardar reportes en ambos archivos
function saveReportToExcel(report) {
    try {
        const reportData = {
            'Tipo': report.tipo,
            'Localidad': report.localidad,
            'Año': report.year,
            'Hora': report.hora,
            'Arma': report.arma,
            'Modalidad': report.modalidad,
            'Descripción': report.descripcion,
            'Fuente': report.fuente,
            'Fecha Reporte': new Date(report.timestamp).toLocaleString('es-CO')
        };

        // Guardar en REPORTES_PEPE.xlsx
        saveToFile(REPORTS_FILE, SHEET_NAME, reportData);

        // Guardar en alimentacion_mapa_datajam_anual.xlsx
        saveToFile(EXCEL_FILE, SHEET_NAME, reportData);

        console.log('✅ Reporte guardado en ambos archivos');
        console.log('   Tipo:', report.tipo, '- Localidad:', report.localidad);
        return true;
    } catch (error) {
        console.error('❌ Error al guardar en Excel:', error);
        return false;
    }
}

// Función auxiliar para guardar en un archivo específico
function saveToFile(filePath, sheetName, reportData) {
    try {
        let workbook;
        let worksheet;

        // Leer o crear workbook
        if (fs.existsSync(filePath)) {
            workbook = XLSX.readFile(filePath);

            // Crear hoja si no existe
            if (!workbook.SheetNames.includes(sheetName)) {
                worksheet = XLSX.utils.json_to_sheet([]);
                XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
            } else {
                worksheet = workbook.Sheets[sheetName];
            }
        } else {
            // Crear nuevo workbook
            workbook = XLSX.utils.book_new();
            worksheet = XLSX.utils.json_to_sheet([]);
            XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
        }

        // Leer datos existentes
        let existingData = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName]);

        // Asegurar que siempre sea un array
        if (!Array.isArray(existingData)) {
            existingData = existingData ? [existingData] : [];
        }

        // Agregar nuevo reporte
        const newData = [...existingData, reportData];

        // Crear nueva hoja con datos
        const newWorksheet = XLSX.utils.json_to_sheet(newData);
        workbook.Sheets[sheetName] = newWorksheet;

        // Guardar archivo usando fs
        const buffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'buffer' });
        fs.writeFileSync(filePath, buffer);
        console.log('   ✓ Guardado en:', filePath.split('\\').pop());
    } catch (error) {
        console.error('Error al guardar en', filePath, ':', error);
    }
}

// API: Obtener todos los reportes
app.get('/api/reports', (req, res) => {
    const reports = readReports();
    res.json(reports);
});

// API: Guardar nuevo reporte
app.post('/api/reports', async (req, res) => {
    const { tipo, localidad, year, hora, arma, modalidad, descripcion, fuente, timestamp } = req.body;

    if (!tipo || !localidad) {
        return res.status(400).json({ error: 'Faltan datos requeridos' });
    }

    const report = {
        tipo,
        localidad,
        year: year || new Date().getFullYear().toString(),
        hora,
        arma: arma === '(no proporcionado)' ? '' : arma,
        modalidad: modalidad === '(no proporcionado)' ? '' : modalidad,
        descripcion,
        fuente: fuente === '(no proporcionado)' ? '' : fuente,
        timestamp: timestamp || new Date().toISOString()
    };

    const success = saveReportToExcel(report);

    // Enviar a Google Sheets (ahora es asíncrono)
    const googleSuccess = await sendToGoogleSheets(report);

    if (success && googleSuccess) {
        res.json({ success: true, message: 'Reporte guardado en Excel y Google Sheets' });
    } else if (success) {
        res.json({ success: true, message: 'Reporte guardado en Excel (Google Sheets pendiente)' });
    } else {
        res.status(500).json({ error: 'Error al guardar reporte' });
    }
});

// API: Obtener reportes con filtros
app.get('/api/reports/filter', (req, res) => {
    const { tipo, localidad } = req.query;
    let reports = readReports();

    if (tipo) {
        reports = reports.filter(r => r.tipo === tipo);
    }
    if (localidad) {
        reports = reports.filter(r => r.localidad === localidad);
    }

    res.json(reports);
});

// API: Obtener todos los datos del Excel con información completa
app.get('/api/excel-data', (req, res) => {
    try {
        if (!fs.existsSync(EXCEL_FILE)) {
            return res.json({ sheets: {} });
        }

        const workbook = XLSX.readFile(EXCEL_FILE);
        const sheetsData = {};

        workbook.SheetNames.forEach(sheetName => {
            const worksheet = workbook.Sheets[sheetName];
            const data = XLSX.utils.sheet_to_json(worksheet);
            sheetsData[sheetName] = data;
        });

        res.json({ sheets: sheetsData });
    } catch (error) {
        console.error('Error al leer Excel:', error);
        res.json({ sheets: {} });
    }
});

// API: Obtener estadísticas anuales desde el Excel
app.get('/api/yearly-stats', (req, res) => {
    try {
        if (!fs.existsSync(EXCEL_FILE)) {
            return res.json({ hurtos: [], incidentes: [] });
        }

        const workbook = XLSX.readFile(EXCEL_FILE);

        // Leer datos de todas las hojas que contengan datos de crimen
        const sheetNames = ['Reportes Pepe', 'Mapa feed anual', 'Datos oficiales anuales'];
        let allData = [];

        for (let sheetName of sheetNames) {
            if (workbook.SheetNames.includes(sheetName)) {
                const worksheet = workbook.Sheets[sheetName];
                const data = XLSX.utils.sheet_to_json(worksheet);

                // Buscar columnas relevantes
                data.forEach(row => {
                    allData.push({
                        year: row['Año'] || row['año'] || extractYear(row),
                        hurtos: row['Hurtos'] || row['hurtos'] || 0,
                        incidentes: row['Incidentes'] || row['incidentes'] || row['Incidents'] || 0,
                        tipo: row['Tipo'] || row['tipo'] || '',
                        localidad: row['Localidad'] || row['localidad'] || ''
                    });
                });
            }
        }

        // Agregar por año
        const yearlyStats = {};
        allData.forEach(item => {
            if (item.year) {
                if (!yearlyStats[item.year]) {
                    yearlyStats[item.year] = { hurtos: 0, incidentes: 0 };
                }
                yearlyStats[item.year].hurtos += (parseInt(item.hurtos) || 0);
                yearlyStats[item.year].incidentes += (parseInt(item.incidentes) || 0);
            }
        });

        // Ordenar por año
        const years = Object.keys(yearlyStats).sort();
        const hurtosData = years.map(y => yearlyStats[y].hurtos);
        const incidentesData = years.map(y => yearlyStats[y].incidentes);

        res.json({
            years: years,
            hurtos: hurtosData,
            incidentes: incidentesData,
            stats: yearlyStats
        });
    } catch (error) {
        console.error('Error al leer estadísticas:', error);
        res.json({ years: [], hurtos: [], incidentes: [], stats: {} });
    }
});

function extractYear(row) {
    // Intentar extraer el año de cualquier campo de fecha
    for (let key in row) {
        const val = row[key];
        if (val && typeof val === 'string') {
            const match = val.match(/20\d{2}/);
            if (match) return parseInt(match[0]);
        }
    }
    return null;
}

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════╗
║   🚨 Mi Barrio Seguro - Servidor      ║
╠════════════════════════════════════════╣
║   ✅ Servidor ejecutándose en:        ║
║   http://localhost:${PORT}              ║
║                                        ║
║   Archivo Reportes: Reportes_Pepe.xlsx║
║   Hoja de datos: ${SHEET_NAME}     ║
╚════════════════════════════════════════╝
    `);

    // Verificar archivo de reportes
    if (fs.existsSync(REPORTS_FILE)) {
        console.log('✅ Archivo de reportes encontrado\n');
    } else {
        console.log('⚠️  Archivo de reportes NO encontrado. Se creará al guardar el primer reporte.\n');
    }
});
