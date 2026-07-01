const fs = require('fs');
const path = require('path');

const sharpPath = process.env.CODEX_SHARP_PATH;
if (!sharpPath) throw new Error('Set CODEX_SHARP_PATH to the bundled sharp package path');
const sharp = require(sharpPath);

const ROOT = process.cwd();
const OUT = path.join(ROOT, 'docs', 'latex', 'figures');
fs.mkdirSync(OUT, { recursive: true });

const summary = JSON.parse(fs.readFileSync(path.join(ROOT, 'reports', 'analysis_summary.json'), 'utf8'));
const csvText = fs.readFileSync(path.join(ROOT, 'reports', 'locality_comparison_2025_2026.csv'), 'utf8');

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(',');
  return lines.slice(1).map((line) => {
    const values = line.split(',');
    return Object.fromEntries(headers.map((header, index) => [header, values[index]]));
  });
}

const rows = parseCsv(csvText).map((row) => {
  for (const [key, value] of Object.entries(row)) {
    if (key !== 'locality_code' && key !== 'locality_name') row[key] = Number(value);
  }
  return row;
});

const COLORS = {
  navy: '#14213D',
  blue: '#1F6E8C',
  teal: '#2A9D8F',
  yellow: '#F4D35E',
  red: '#B23A48',
  gray: '#5B6573',
  light: '#F5F7FA',
  white: '#FFFFFF',
  grid: '#DDE3EA',
};

function esc(value) {
  return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function number(value) {
  return Math.round(value).toLocaleString('es-CO');
}

function pct(value) {
  return `${value.toFixed(1).replace('.', ',')}%`;
}

function svgShell(title, subtitle, body, footer) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <rect width="1600" height="900" fill="${COLORS.white}"/>
  <rect width="1600" height="14" fill="${COLORS.yellow}"/>
  <text x="90" y="82" font-family="Arial, sans-serif" font-size="42" font-weight="700" fill="${COLORS.navy}">${esc(title)}</text>
  <text x="90" y="121" font-family="Arial, sans-serif" font-size="22" fill="${COLORS.gray}">${esc(subtitle)}</text>
  ${body}
  <line x1="90" y1="838" x2="1510" y2="838" stroke="${COLORS.grid}"/>
  <text x="90" y="872" font-family="Arial, sans-serif" font-size="17" fill="${COLORS.gray}">${esc(footer)}</text>
  </svg>`;
}

async function save(name, svg) {
  const svgPath = path.join(OUT, `${name}.svg`);
  const pngPath = path.join(OUT, `${name}.png`);
  fs.writeFileSync(svgPath, svg, 'utf8');
  await sharp(Buffer.from(svg)).png().toFile(pngPath);
}

function districtChart() {
  const d = summary.district;
  const groups = [
    { label: 'Hurtos registrados', v2025: d.thefts_2025, v2026: d.thefts_2026, change: d.theft_change_pct, color: COLORS.red },
    { label: 'Incidentes 123', v2025: d.incidents_2025, v2026: d.incidents_2026, change: d.incident_change_pct, color: COLORS.blue },
  ];
  const max = 65000;
  const chartTop = 190;
  const chartBottom = 690;
  const chartHeight = chartBottom - chartTop;
  let body = '';
  for (let tick = 0; tick <= 60000; tick += 10000) {
    const y = chartBottom - (tick / max) * chartHeight;
    body += `<line x1="150" y1="${y}" x2="1120" y2="${y}" stroke="${COLORS.grid}" stroke-width="1"/>`;
    body += `<text x="135" y="${y + 6}" text-anchor="end" font-family="Arial" font-size="17" fill="${COLORS.gray}">${number(tick)}</text>`;
  }
  groups.forEach((group, index) => {
    const center = 390 + index * 470;
    const values = [group.v2025, group.v2026];
    values.forEach((value, j) => {
      const x = center - 105 + j * 130;
      const height = (value / max) * chartHeight;
      const y = chartBottom - height;
      const fill = j === 0 ? `${group.color}99` : group.color;
      body += `<rect x="${x}" y="${y}" width="92" height="${height}" rx="8" fill="${fill}"/>`;
      body += `<text x="${x + 46}" y="${y - 13}" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700" fill="${COLORS.navy}">${number(value)}</text>`;
      body += `<text x="${x + 46}" y="${chartBottom + 34}" text-anchor="middle" font-family="Arial" font-size="19" fill="${COLORS.gray}">${j === 0 ? '2025' : '2026'}</text>`;
    });
    body += `<text x="${center - 40}" y="${chartBottom + 82}" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700" fill="${group.color}">${esc(group.label)}</text>`;
    body += `<rect x="${center + 100}" y="245" width="170" height="72" rx="14" fill="${group.change < 0 ? COLORS.teal : COLORS.yellow}"/>`;
    body += `<text x="${center + 185}" y="290" text-anchor="middle" font-family="Arial" font-size="28" font-weight="700" fill="${COLORS.navy}">${pct(group.change)}</text>`;
  });
  body += `<rect x="1190" y="220" width="320" height="355" rx="22" fill="${COLORS.light}" stroke="${COLORS.blue}" stroke-width="2"/>`;
  body += `<text x="1350" y="275" text-anchor="middle" font-family="Arial" font-size="25" font-weight="700" fill="${COLORS.navy}">Razón incidentes / hurto</text>`;
  body += `<text x="1350" y="375" text-anchor="middle" font-family="Arial" font-size="58" font-weight="700" fill="${COLORS.blue}">${d.incident_to_theft_ratio_2025.toFixed(2).replace('.', ',')}</text>`;
  body += `<text x="1350" y="410" text-anchor="middle" font-family="Arial" font-size="19" fill="${COLORS.gray}">2025</text>`;
  body += `<path d="M1270 455 H1430" stroke="${COLORS.teal}" stroke-width="8" marker-end="url(#arrow)"/>`;
  body += `<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="${COLORS.teal}"/></marker></defs>`;
  body += `<text x="1350" y="530" text-anchor="middle" font-family="Arial" font-size="58" font-weight="700" fill="${COLORS.teal}">${d.incident_to_theft_ratio_2026.toFixed(2).replace('.', ',')}</text>`;
  body += `<text x="1350" y="565" text-anchor="middle" font-family="Arial" font-size="19" fill="${COLORS.gray}">2026 · +${pct(d.incident_to_theft_ratio_change_pct)}</text>`;
  return svgShell(
    'Las dos fuentes evolucionan en direcciones distintas',
    'Bogotá, acumulado enero–mayo de 2025 frente a 2026',
    body,
    'Incluye registros sin localización. La divergencia no demuestra subregistro ni causalidad.'
  );
}

function rankChart() {
  const selectedNames = ['La Candelaria', 'Suba', 'Kennedy', 'Engativá', 'Antonio Nariño', 'Los Mártires', 'Barrios Unidos'];
  const selected = rows.filter((row) => selectedNames.includes(row.locality_name));
  const xCount = 520;
  const xRate = 1080;
  const yTop = 195;
  const yBottom = 750;
  const yForRank = (rank) => yTop + ((rank - 1) / 19) * (yBottom - yTop);
  let body = '';
  body += `<text x="${xCount}" y="165" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700" fill="${COLORS.red}">Ranking por conteo</text>`;
  body += `<text x="${xRate}" y="165" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700" fill="${COLORS.blue}">Ranking por tasa</text>`;
  body += `<line x1="${xCount}" y1="${yTop}" x2="${xCount}" y2="${yBottom}" stroke="${COLORS.grid}" stroke-width="5"/>`;
  body += `<line x1="${xRate}" y1="${yTop}" x2="${xRate}" y2="${yBottom}" stroke="${COLORS.grid}" stroke-width="5"/>`;
  [1, 5, 10, 15, 20].forEach((rank) => {
    const y = yForRank(rank);
    body += `<text x="${xCount - 42}" y="${y + 7}" text-anchor="end" font-family="Arial" font-size="18" fill="${COLORS.gray}">${rank}</text>`;
    body += `<text x="${xRate + 42}" y="${y + 7}" font-family="Arial" font-size="18" fill="${COLORS.gray}">${rank}</text>`;
  });
  selected.forEach((row, index) => {
    const y1 = yForRank(row.count_rank_2026);
    const y2 = yForRank(row.rate_rank_2026);
    const color = index % 2 === 0 ? COLORS.blue : COLORS.teal;
    body += `<line x1="${xCount}" y1="${y1}" x2="${xRate}" y2="${y2}" stroke="${color}" stroke-width="4" opacity="0.8"/>`;
    body += `<circle cx="${xCount}" cy="${y1}" r="9" fill="${COLORS.red}"/>`;
    body += `<circle cx="${xRate}" cy="${y2}" r="9" fill="${COLORS.blue}"/>`;
    body += `<text x="${xCount - 60}" y="${y1 + 7}" text-anchor="end" font-family="Arial" font-size="19" font-weight="700" fill="${COLORS.navy}">${esc(row.locality_name)}</text>`;
    body += `<text x="${xRate + 60}" y="${y2 + 7}" font-family="Arial" font-size="19" font-weight="700" fill="${COLORS.navy}">${esc(row.locality_name)}</text>`;
  });
  body += `<rect x="1220" y="655" width="290" height="105" rx="18" fill="${COLORS.light}"/>`;
  body += `<text x="1365" y="688" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="${COLORS.navy}">Asociación de rangos</text>`;
  body += `<text x="1365" y="731" text-anchor="middle" font-family="Arial" font-size="40" font-weight="700" fill="${COLORS.teal}">0,205</text>`;
  body += `<text x="1365" y="752" text-anchor="middle" font-family="Arial" font-size="15" fill="${COLORS.gray}">Spearman · 2026</text>`;
  return svgShell(
    'El mapa cambia cuando se ajusta por población',
    'Localidades con mayores diferencias entre ranking por conteo y ranking por tasa, 2026',
    body,
    'La tasa usa población residente; en localidades centrales debe considerarse la población flotante.'
  );
}

function divergenceChart() {
  const xMin = -25;
  const xMax = 15;
  const yMin = -20;
  const yMax = 35;
  const left = 180;
  const right = 1450;
  const top = 175;
  const bottom = 750;
  const x = (value) => left + ((value - xMin) / (xMax - xMin)) * (right - left);
  const y = (value) => bottom - ((value - yMin) / (yMax - yMin)) * (bottom - top);
  let body = '';
  for (let tick = -20; tick <= 10; tick += 10) {
    body += `<line x1="${x(tick)}" y1="${top}" x2="${x(tick)}" y2="${bottom}" stroke="${tick === 0 ? COLORS.gray : COLORS.grid}" stroke-width="${tick === 0 ? 2 : 1}"/>`;
    body += `<text x="${x(tick)}" y="${bottom + 35}" text-anchor="middle" font-family="Arial" font-size="18" fill="${COLORS.gray}">${tick}%</text>`;
  }
  for (let tick = -20; tick <= 30; tick += 10) {
    body += `<line x1="${left}" y1="${y(tick)}" x2="${right}" y2="${y(tick)}" stroke="${tick === 0 ? COLORS.gray : COLORS.grid}" stroke-width="${tick === 0 ? 2 : 1}"/>`;
    body += `<text x="${left - 20}" y="${y(tick) + 6}" text-anchor="end" font-family="Arial" font-size="18" fill="${COLORS.gray}">${tick}%</text>`;
  }
  body += `<text x="${(left + right) / 2}" y="815" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700" fill="${COLORS.red}">Cambio en hurtos registrados 2025–2026</text>`;
  body += `<text x="45" y="${(top + bottom) / 2}" text-anchor="middle" transform="rotate(-90 45 ${(top + bottom) / 2})" font-family="Arial" font-size="22" font-weight="700" fill="${COLORS.blue}">Cambio en incidentes 123</text>`;
  const labelNames = new Set(['Teusaquillo', 'Ciudad Bolívar', 'Barrios Unidos', 'Engativá', 'Suba', 'Bosa', 'Santa Fe', 'Chapinero']);
  rows.filter((row) => Number.isFinite(row.theft_change_pct) && Number.isFinite(row.incident_change_pct)).forEach((row) => {
    const cx = x(row.theft_change_pct);
    const cy = y(row.incident_change_pct);
    const isKey = labelNames.has(row.locality_name);
    body += `<circle cx="${cx}" cy="${cy}" r="${isKey ? 10 : 7}" fill="${isKey ? COLORS.teal : COLORS.blue}" opacity="${isKey ? 1 : 0.55}"/>`;
    if (isKey) {
      const isTeusaquillo = row.locality_name === 'Teusaquillo';
      const dx = isTeusaquillo ? 14 : 14;
      const dy = isTeusaquillo ? 28 : -13;
      body += `<text x="${cx + dx}" y="${cy + dy}" text-anchor="start" font-family="Arial" font-size="18" font-weight="700" fill="${COLORS.navy}">${esc(row.locality_name)}</text>`;
    }
  });
  body += `<rect x="250" y="205" width="390" height="70" rx="14" fill="${COLORS.yellow}" opacity="0.85"/>`;
  body += `<text x="445" y="235" text-anchor="middle" font-family="Arial" font-size="19" font-weight="700" fill="${COLORS.navy}">Hurtos bajan, incidentes suben</text>`;
  body += `<text x="445" y="260" text-anchor="middle" font-family="Arial" font-size="17" fill="${COLORS.navy}">Cuadrante de mayor divergencia</text>`;
  return svgShell(
    'La divergencia no es uniforme entre localidades',
    'Cambio porcentual entre enero–mayo de 2025 y enero–mayo de 2026',
    body,
    'Cada punto representa una localidad. Señal exploratoria: no implica que una fuente sea correcta y la otra incorrecta.'
  );
}

(async () => {
  await save('fig_distrito_divergencia', districtChart());
  await save('fig_ranking_conteo_tasa', rankChart());
  await save('fig_divergencia_localidades', divergenceChart());
  console.log('Charts generated in', OUT);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
