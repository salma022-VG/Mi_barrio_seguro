const fs = require('fs');
const path = require('path');
const sharp = require(process.env.CODEX_SHARP_PATH || 'sharp');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'docs', 'latex', 'figures');
fs.mkdirSync(OUT, { recursive: true });

const COLORS = {
  navy: '#14213D', blue: '#1F6E8C', teal: '#2A9D8F', yellow: '#F4D35E',
  red: '#B23A48', light: '#F5F7FA', gray: '#5B6573', grid: '#DDE4EC', white: '#FFFFFF',
};

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines.shift().split(',');
  return lines.map((line) => {
    const values = line.split(',');
    return Object.fromEntries(headers.map((header, index) => {
      const value = values[index] ?? '';
      const numeric = Number(value);
      return [header, value !== '' && Number.isFinite(numeric) ? numeric : value];
    }));
  });
}

const district = parseCsv(fs.readFileSync(path.join(ROOT, 'reports', 'annual_district_summary.csv'), 'utf8'));
const integrated = parseCsv(fs.readFileSync(path.join(ROOT, 'data', 'processed', 'anual', 'seguridad_anual_localidad.csv'), 'utf8'));

function esc(value) {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function fmtInt(value) {
  return Math.round(value).toLocaleString('es-CO');
}

function fmtPct(value) {
  return `${value.toFixed(1).replace('.', ',')}%`;
}

function shell(title, subtitle, body, footnote) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <rect width="1600" height="900" fill="${COLORS.white}"/>
  <rect width="1600" height="14" fill="${COLORS.yellow}"/>
  <text x="90" y="82" font-family="Arial" font-size="42" font-weight="700" fill="${COLORS.navy}">${esc(title)}</text>
  <text x="90" y="124" font-family="Arial" font-size="23" fill="${COLORS.gray}">${esc(subtitle)}</text>
  ${body}
  <line x1="90" y1="838" x2="1510" y2="838" stroke="${COLORS.grid}"/>
  <text x="90" y="873" font-family="Arial" font-size="17" fill="${COLORS.gray}">${esc(footnote)}</text>
  </svg>`;
}

function annualTrend() {
  const left = 155, right = 1450, top = 190, bottom = 720;
  const min = 75000, max = 165000;
  const x = (index) => left + (index / (district.length - 1)) * (right - left);
  const y = (value) => bottom - ((value - min) / (max - min)) * (bottom - top);
  let body = '';
  for (let tick = 80000; tick <= 160000; tick += 20000) {
    body += `<line x1="${left}" y1="${y(tick)}" x2="${right}" y2="${y(tick)}" stroke="${COLORS.grid}"/>`;
    body += `<text x="${left - 22}" y="${y(tick) + 6}" text-anchor="end" font-family="Arial" font-size="18" fill="${COLORS.gray}">${Math.round(tick / 1000)} mil</text>`;
  }
  const line = (field, color) => district.map((row, index) => `${index ? 'L' : 'M'} ${x(index)} ${y(row[field])}`).join(' ');
  body += `<path d="${line('registered_person_thefts', COLORS.red)}" fill="none" stroke="${COLORS.red}" stroke-width="6"/>`;
  body += `<path d="${line('reported_123_theft_incidents', COLORS.blue)}" fill="none" stroke="${COLORS.blue}" stroke-width="6"/>`;
  district.forEach((row, index) => {
    const px = x(index);
    body += `<text x="${px}" y="${bottom + 38}" text-anchor="middle" font-family="Arial" font-size="18" fill="${COLORS.gray}">${row.year}</text>`;
    body += `<circle cx="${px}" cy="${y(row.registered_person_thefts)}" r="8" fill="${COLORS.red}"/>`;
    body += `<circle cx="${px}" cy="${y(row.reported_123_theft_incidents)}" r="8" fill="${COLORS.blue}"/>`;
  });
  const peak = district.findIndex((row) => row.year === 2023);
  body += `<rect x="${x(peak) - 145}" y="${y(district[peak].registered_person_thefts) - 82}" width="290" height="56" rx="12" fill="${COLORS.light}"/>`;
  body += `<text x="${x(peak)}" y="${y(district[peak].registered_person_thefts) - 49}" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="${COLORS.navy}">Pico 2023: ${fmtInt(district[peak].registered_person_thefts)}</text>`;
  body += `<line x1="180" y1="165" x2="230" y2="165" stroke="${COLORS.red}" stroke-width="6"/><text x="245" y="172" font-family="Arial" font-size="19" fill="${COLORS.navy}">Hurtos a personas</text>`;
  body += `<line x1="445" y1="165" x2="495" y2="165" stroke="${COLORS.blue}" stroke-width="6"/><text x="510" y="172" font-family="Arial" font-size="19" fill="${COLORS.navy}">Incidentes 123</text>`;
  const last = district[district.length - 1];
  body += `<rect x="110" y="760" width="650" height="60" rx="14" fill="#FBEAEC"/>`;
  body += `<text x="435" y="797" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700" fill="${COLORS.red}">2024–2025: hurtos ${fmtPct(last.theft_yoy_pct)} · incidentes +${fmtPct(last.incident_yoy_pct)}</text>`;
  return shell('La trayectoria anual no es lineal', 'Totales distritales de años completos, 2018–2025', body, 'Fuentes: Delito de Alto Impacto e Incidente Reportado. Los conceptos son relacionados, no equivalentes.');
}

function coverageChart() {
  const left = 150, right = 1450, top = 205, bottom = 720;
  const y = (value) => bottom - ((value - 75) / 25) * (bottom - top);
  const step = (right - left) / district.length;
  let body = '';
  [75, 80, 85, 90, 95, 100].forEach((tick) => {
    body += `<line x1="${left}" y1="${y(tick)}" x2="${right}" y2="${y(tick)}" stroke="${COLORS.grid}"/>`;
    body += `<text x="${left - 20}" y="${y(tick) + 6}" text-anchor="end" font-family="Arial" font-size="18" fill="${COLORS.gray}">${tick}%</text>`;
  });
  district.forEach((row, index) => {
    const bx = left + index * step + 22;
    const width = step - 44;
    const color = row.year === 2025 ? COLORS.red : COLORS.teal;
    const topY = y(row.theft_mapped_coverage_pct);
    body += `<rect x="${bx}" y="${topY}" width="${width}" height="${bottom - topY}" rx="7" fill="${color}"/>`;
    body += `<text x="${bx + width / 2}" y="${bottom + 35}" text-anchor="middle" font-family="Arial" font-size="18" fill="${COLORS.gray}">${row.year}</text>`;
    body += `<text x="${bx + width / 2}" y="${topY - 12}" text-anchor="middle" font-family="Arial" font-size="17" font-weight="700" fill="${color}">${row.theft_mapped_coverage_pct.toFixed(1).replace('.', ',')}%</text>`;
  });
  const last = district[district.length - 1];
  body += `<rect x="860" y="245" width="530" height="145" rx="18" fill="#FBEAEC"/>`;
  body += `<text x="1125" y="292" text-anchor="middle" font-family="Arial" font-size="26" font-weight="700" fill="${COLORS.red}">${fmtInt(last.unlocated_thefts)} hurtos sin localidad</text>`;
  body += `<text x="1125" y="330" text-anchor="middle" font-family="Arial" font-size="20" fill="${COLORS.navy}">17,7% del total distrital de 2025</text>`;
  body += `<text x="1125" y="365" text-anchor="middle" font-family="Arial" font-size="18" fill="${COLORS.gray}">El total sirve; el mapa requiere advertencia.</text>`;
  return shell('2025 tiene una ruptura de cobertura territorial', 'Porcentaje de hurtos a personas con localidad asignada', body, 'Cobertura = registros ubicados en una de las 20 localidades / total distrital del año.');
}

function rankChart2024() {
  const rows = integrated.filter((row) => row.year === 2024);
  const selected = rows
    .map((row) => ({ ...row, gap: Math.abs(row.count_rank - row.rate_rank) }))
    .sort((a, b) => b.gap - a.gap)
    .slice(0, 8);
  const xCount = 520, xRate = 1080, yTop = 195, yBottom = 750;
  const yForRank = (rank) => yTop + ((rank - 1) / 19) * (yBottom - yTop);
  let body = '';
  body += `<text x="${xCount}" y="165" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700" fill="${COLORS.red}">Ranking por conteo</text>`;
  body += `<text x="${xRate}" y="165" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700" fill="${COLORS.blue}">Ranking por tasa</text>`;
  body += `<line x1="${xCount}" y1="${yTop}" x2="${xCount}" y2="${yBottom}" stroke="${COLORS.grid}" stroke-width="5"/>`;
  body += `<line x1="${xRate}" y1="${yTop}" x2="${xRate}" y2="${yBottom}" stroke="${COLORS.grid}" stroke-width="5"/>`;
  [1, 5, 10, 15, 20].forEach((rank) => {
    const yy = yForRank(rank);
    body += `<text x="${xCount - 42}" y="${yy + 7}" text-anchor="end" font-family="Arial" font-size="18" fill="${COLORS.gray}">${rank}</text>`;
    body += `<text x="${xRate + 42}" y="${yy + 7}" font-family="Arial" font-size="18" fill="${COLORS.gray}">${rank}</text>`;
  });
  selected.forEach((row, index) => {
    const y1 = yForRank(row.count_rank), y2 = yForRank(row.rate_rank);
    const color = index % 2 === 0 ? COLORS.blue : COLORS.teal;
    body += `<line x1="${xCount}" y1="${y1}" x2="${xRate}" y2="${y2}" stroke="${color}" stroke-width="4" opacity="0.8"/>`;
    body += `<circle cx="${xCount}" cy="${y1}" r="9" fill="${COLORS.red}"/><circle cx="${xRate}" cy="${y2}" r="9" fill="${COLORS.blue}"/>`;
    body += `<text x="${xCount - 60}" y="${y1 + 7}" text-anchor="end" font-family="Arial" font-size="18" font-weight="700" fill="${COLORS.navy}">${esc(row.locality_name)}</text>`;
    body += `<text x="${xRate + 85}" y="${y2 + 7}" font-family="Arial" font-size="18" font-weight="700" fill="${COLORS.navy}">${esc(row.locality_name)}</text>`;
  });
  body += `<rect x="1225" y="660" width="285" height="100" rx="16" fill="${COLORS.light}"/>`;
  body += `<text x="1367" y="695" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="${COLORS.navy}">Asociación de rangos</text>`;
  body += `<text x="1367" y="740" text-anchor="middle" font-family="Arial" font-size="40" font-weight="700" fill="${COLORS.teal}">0,296</text>`;
  return shell('Conteo y tasa siguen contando historias distintas', 'Último año con cobertura territorial superior al 99%: 2024', body, 'La tasa usa población residente y debe interpretarse con cautela en localidades con alta población flotante.');
}

async function save(name, svg) {
  fs.writeFileSync(path.join(OUT, `${name}.svg`), svg, 'utf8');
  await sharp(Buffer.from(svg)).png().toFile(path.join(OUT, `${name}.png`));
}

(async () => {
  await save('fig_tendencia_anual_2018_2025', annualTrend());
  await save('fig_cobertura_territorial_anual', coverageChart());
  await save('fig_ranking_anual_2024', rankChart2024());
  console.log('Annual charts generated in', OUT);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
