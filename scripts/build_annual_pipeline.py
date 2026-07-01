from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd


YEARS = list(range(2018, 2026))

LOCALITY_NAMES = {
    "01": "Usaquén",
    "02": "Chapinero",
    "03": "Santa Fe",
    "04": "San Cristóbal",
    "05": "Usme",
    "06": "Tunjuelito",
    "07": "Bosa",
    "08": "Kennedy",
    "09": "Fontibón",
    "10": "Engativá",
    "11": "Suba",
    "12": "Barrios Unidos",
    "13": "Teusaquillo",
    "14": "Los Mártires",
    "15": "Antonio Nariño",
    "16": "Puente Aranda",
    "17": "La Candelaria",
    "18": "Rafael Uribe Uribe",
    "19": "Ciudad Bolívar",
    "20": "Sumapaz",
}

DAI_METRICS = {
    "CMH": "homicidios",
    "CMLP": "lesiones_personales",
    "CMHP": "hurto_personas",
    "CMHR": "hurto_residencias",
    "CMHA": "hurto_automotores",
    "CMHB": "hurto_bicicletas",
    "CMHC": "hurto_comercio",
    "CMHCE": "hurto_celulares",
    "CMHM": "hurto_motocicletas",
    "CMDS": "delitos_sexuales",
    "CMVI": "violencia_intrafamiliar",
}

IR_METRICS = {
    "CMR": "rinas",
    "CMN": "narcoticos",
    "CMAOP": "alteracion_orden_publico",
    "CMMM": "maltrato_mujer",
    "CMM": "maltrato",
    "CMD": "disparos",
    "CMPIA": "porte_ilegal_armas",
    "CMH": "hurto",
    "CMHC": "habitantes_calle",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_geojson_from_zip(path: Path, member: str) -> dict:
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read(member).decode("utf-8-sig"))


def metric_value(properties: dict, prefix: str, year: int) -> int:
    suffix = str(year)[-2:]
    candidates = [f"{prefix}{suffix}CONT", f"{prefix}{suffix}CON"]
    for key in candidates:
        if key in properties:
            value = properties[key]
            return int(round(float(value or 0)))
    raise KeyError(f"No se encontró campo para {prefix}, {year}: {candidates}")


def extract_long(features: list[dict], metrics: dict[str, str], source: str, canonical_names: dict[str, str]) -> pd.DataFrame:
    rows: list[dict] = []
    for feature in features:
        properties = feature["properties"]
        code = str(properties["CMIULOCAL"]).zfill(2)
        name = canonical_names.get(code, "Sin Localización" if code == "99" else str(properties.get("CMNOMLOCAL", "")))
        period_label = str(properties.get("CMMES", ""))
        for year in YEARS:
            for prefix, metric in metrics.items():
                rows.append(
                    {
                        "source": source,
                        "locality_code": code,
                        "locality_name": name,
                        "year": year,
                        "metric": metric,
                        "count": metric_value(properties, prefix, year),
                        "period_label": period_label,
                        "period_start_month": 1,
                        "period_end_month": 12,
                        "coverage": "full_year",
                    }
                )
    return pd.DataFrame(rows)


def iqr_flags(frame: pd.DataFrame) -> pd.DataFrame:
    records: list[dict] = []
    metrics = ["registered_person_thefts", "reported_123_theft_incidents", "theft_rate_per_100k", "incident_rate_per_100k"]
    for year in YEARS:
        current = frame.loc[frame["year"] == year]
        for metric in metrics:
            q1 = current[metric].quantile(0.25)
            q3 = current[metric].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            flagged = current.loc[(current[metric] < lower) | (current[metric] > upper)]
            for row in flagged.itertuples(index=False):
                value = getattr(row, metric)
                records.append(
                    {
                        "year": year,
                        "metric": metric,
                        "locality_code": row.locality_code,
                        "locality_name": row.locality_name,
                        "value": value,
                        "lower_bound": lower,
                        "upper_bound": upper,
                        "decision": "retained_reviewed_not_error",
                    }
                )
    return pd.DataFrame(records)


def spearman(left: pd.Series, right: pd.Series) -> float:
    return float(left.rank(method="average").corr(right.rank(method="average")))


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    raw = root / "data" / "raw"
    processed = root / "data" / "processed" / "anual"
    reports = root / "reports"
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    dai_zip = raw / "alto_impacto" / "dai_anual_geojson.zip"
    ir_zip = raw / "incidentes_reportados" / "ir_anual_geojson.zip"
    population_path = raw / "poblacion_localidades.csv"

    population_detail = pd.read_csv(population_path, sep=";", encoding="utf-8")
    population_detail = population_detail.rename(
        columns={"ANO": "year", "CODIGO_LOCALIDAD": "locality_code", "NOMBRE_LOCALIDAD": "locality_name", "POBLACION": "population"}
    )
    population_detail["locality_code"] = population_detail["locality_code"].astype(str).str.zfill(2)
    population_detail["year"] = pd.to_numeric(population_detail["year"], errors="raise").astype(int)
    population_detail["population"] = pd.to_numeric(population_detail["population"], errors="raise").astype(int)

    canonical = LOCALITY_NAMES.copy()
    population = (
        population_detail.loc[
            (population_detail["locality_code"] != "00") & population_detail["year"].isin(YEARS),
            ["year", "locality_code", "locality_name", "population"],
        ]
        .groupby(["year", "locality_code", "locality_name"], as_index=False)["population"]
        .sum()
    )
    population["locality_name"] = population["locality_code"].map(canonical)

    dai_geojson = load_geojson_from_zip(dai_zip, "DAILoc.geojson")
    ir_geojson = load_geojson_from_zip(ir_zip, "IRLoc.geojson")
    dai_periods = sorted({str(feature["properties"].get("CMMES", "")) for feature in dai_geojson["features"]})
    ir_periods = sorted({str(feature["properties"].get("CMMES", "")) for feature in ir_geojson["features"]})
    if dai_periods != ["Ene-Dic (2024vs2025)"] or ir_periods != ["Ene-Dic (2024vs2025)"]:
        raise ValueError(f"Etiquetas anuales inesperadas: DAI={dai_periods}, IR={ir_periods}")

    dai_long = extract_long(dai_geojson["features"], DAI_METRICS, "delito_alto_impacto_anual", canonical)
    ir_long = extract_long(ir_geojson["features"], IR_METRICS, "incidente_reportado_anual", canonical)

    dai_located = dai_long.loc[dai_long["locality_code"] != "99"].copy()
    dai_unlocated = dai_long.loc[dai_long["locality_code"] == "99"].copy()
    ir_located = ir_long.loc[ir_long["locality_code"] != "99"].copy()
    ir_unlocated = ir_long.loc[ir_long["locality_code"] == "99"].copy()

    thefts = dai_located.loc[dai_located["metric"] == "hurto_personas", ["locality_code", "locality_name", "year", "count"]].rename(
        columns={"count": "registered_person_thefts"}
    )
    incidents = ir_located.loc[ir_located["metric"] == "hurto", ["locality_code", "locality_name", "year", "count"]].rename(
        columns={"count": "reported_123_theft_incidents", "locality_name": "incident_locality_name"}
    )
    integrated = thefts.merge(incidents, on=["locality_code", "year"], how="outer", validate="one_to_one")
    integrated = integrated.merge(population[["locality_code", "year", "population"]], on=["locality_code", "year"], how="left", validate="one_to_one")
    integrated["locality_name"] = integrated["locality_code"].map(canonical)
    integrated["period_label"] = "Enero-Diciembre"
    integrated["coverage"] = "full_year"
    integrated["theft_rate_per_100k"] = integrated["registered_person_thefts"] / integrated["population"] * 100_000
    integrated["incident_rate_per_100k"] = integrated["reported_123_theft_incidents"] / integrated["population"] * 100_000
    integrated["incidents_per_registered_theft"] = integrated["reported_123_theft_incidents"].div(integrated["registered_person_thefts"].replace(0, pd.NA))
    integrated["count_rank"] = integrated.groupby("year")["registered_person_thefts"].rank(method="min", ascending=False).astype(int)
    integrated["rate_rank"] = integrated.groupby("year")["theft_rate_per_100k"].rank(method="min", ascending=False).astype(int)
    integrated = integrated.sort_values(["year", "locality_code"]).reset_index(drop=True)
    integrated["theft_yoy_pct"] = integrated.groupby("locality_code")["registered_person_thefts"].pct_change(fill_method=None) * 100
    integrated["incident_yoy_pct"] = integrated.groupby("locality_code")["reported_123_theft_incidents"].pct_change(fill_method=None) * 100
    integrated["divergence_yoy_pp"] = integrated["incident_yoy_pct"] - integrated["theft_yoy_pct"]

    if len(integrated) != 160:
        raise ValueError(f"Se esperaban 160 filas integradas y se obtuvieron {len(integrated)}")
    if integrated[["registered_person_thefts", "reported_123_theft_incidents", "population"]].isna().any().any():
        raise ValueError("La integración anual contiene valores faltantes")
    if integrated.duplicated(["locality_code", "year"]).any():
        raise ValueError("La llave locality_code + year no es única")

    geometries = []
    for feature in dai_geojson["features"]:
        code = str(feature["properties"]["CMIULOCAL"]).zfill(2)
        if code == "99":
            continue
        geometries.append(
            {
                "type": "Feature",
                "properties": {"locality_code": code, "locality_name": canonical[code]},
                "geometry": feature["geometry"],
            }
        )
    map_geojson = {"type": "FeatureCollection", "name": "localidades_bogota_anual", "features": geometries}

    dai_long.to_csv(processed / "delito_alto_impacto_anual_long.csv", index=False, encoding="utf-8", float_format="%.6f")
    ir_long.to_csv(processed / "incidentes_reportados_anual_long.csv", index=False, encoding="utf-8", float_format="%.6f")
    dai_unlocated.to_csv(processed / "delito_alto_impacto_anual_sin_localizacion.csv", index=False, encoding="utf-8")
    ir_unlocated.to_csv(processed / "incidentes_anual_sin_localizacion.csv", index=False, encoding="utf-8")
    population.to_csv(processed / "poblacion_anual_localidad.csv", index=False, encoding="utf-8")
    integrated.to_csv(processed / "seguridad_anual_localidad.csv", index=False, encoding="utf-8", float_format="%.6f")
    (processed / "localidades_bogota_anual.geojson").write_text(json.dumps(map_geojson, ensure_ascii=False), encoding="utf-8")

    district_rows = []
    for year in YEARS:
        current = integrated.loc[integrated["year"] == year]
        theft_unlocated = int(dai_unlocated.loc[(dai_unlocated["year"] == year) & (dai_unlocated["metric"] == "hurto_personas"), "count"].sum())
        incident_unlocated = int(ir_unlocated.loc[(ir_unlocated["year"] == year) & (ir_unlocated["metric"] == "hurto"), "count"].sum())
        thefts_all = int(current["registered_person_thefts"].sum()) + theft_unlocated
        incidents_all = int(current["reported_123_theft_incidents"].sum()) + incident_unlocated
        population_all = int(current["population"].sum())
        district_rows.append(
            {
                "year": year,
                "registered_person_thefts": thefts_all,
                "reported_123_theft_incidents": incidents_all,
                "population": population_all,
                "mapped_thefts": int(current["registered_person_thefts"].sum()),
                "mapped_incidents": int(current["reported_123_theft_incidents"].sum()),
                "unlocated_thefts": theft_unlocated,
                "unlocated_incidents": incident_unlocated,
                "theft_mapped_coverage_pct": int(current["registered_person_thefts"].sum()) / thefts_all * 100 if thefts_all else None,
                "incident_mapped_coverage_pct": int(current["reported_123_theft_incidents"].sum()) / incidents_all * 100 if incidents_all else None,
                "theft_rate_per_100k": thefts_all / population_all * 100_000,
                "incident_rate_per_100k": incidents_all / population_all * 100_000,
                "incidents_per_registered_theft": incidents_all / thefts_all if thefts_all else None,
            }
        )
    district = pd.DataFrame(district_rows)
    district["theft_yoy_pct"] = district["registered_person_thefts"].pct_change(fill_method=None) * 100
    district["incident_yoy_pct"] = district["reported_123_theft_incidents"].pct_change(fill_method=None) * 100
    district["divergence_yoy_pp"] = district["incident_yoy_pct"] - district["theft_yoy_pct"]
    district.to_csv(reports / "annual_district_summary.csv", index=False, encoding="utf-8", float_format="%.6f")

    flags = iqr_flags(integrated)
    flags.to_csv(reports / "annual_outlier_flags.csv", index=False, encoding="utf-8", float_format="%.6f")

    annual_2025 = integrated.loc[integrated["year"] == 2025].sort_values("registered_person_thefts", ascending=False)
    annual_2025.to_csv(reports / "annual_locality_2025.csv", index=False, encoding="utf-8", float_format="%.6f")

    correlations = {}
    for year in YEARS:
        current = integrated.loc[integrated["year"] == year]
        correlations[str(year)] = {
            "count_vs_rate_spearman": spearman(current["registered_person_thefts"], current["theft_rate_per_100k"]),
            "theft_vs_incident_pearson": float(current["registered_person_thefts"].corr(current["reported_123_theft_incidents"], method="pearson")),
            "theft_vs_incident_spearman": spearman(current["registered_person_thefts"], current["reported_123_theft_incidents"]),
        }

    top_counts = annual_2025.nlargest(5, "registered_person_thefts")[
        ["locality_name", "registered_person_thefts", "theft_rate_per_100k", "count_rank", "rate_rank"]
    ]
    top_rates = annual_2025.nlargest(5, "theft_rate_per_100k")[
        ["locality_name", "registered_person_thefts", "theft_rate_per_100k", "count_rank", "rate_rank"]
    ]
    divergence_2025 = annual_2025.reindex(annual_2025["divergence_yoy_pp"].abs().sort_values(ascending=False).index).head(5)[
        ["locality_name", "theft_yoy_pct", "incident_yoy_pct", "divergence_yoy_pp"]
    ]

    summary = {
        "scope": "Annual January-December, complete years 2018-2025. 2026 excluded from annual trend.",
        "source_files": {
            "dai_zip": {"path": str(dai_zip.relative_to(root)), "sha256": sha256(dai_zip), "period_label": dai_periods[0]},
            "incidents_zip": {"path": str(ir_zip.relative_to(root)), "sha256": sha256(ir_zip), "period_label": ir_periods[0]},
            "population": {"path": str(population_path.relative_to(root)), "sha256": sha256(population_path)},
        },
        "quality": {
            "integrated_rows": len(integrated),
            "localities": int(integrated["locality_code"].nunique()),
            "years": YEARS,
            "missing_required_values": int(integrated[["registered_person_thefts", "reported_123_theft_incidents", "population"]].isna().sum().sum()),
            "duplicate_keys": int(integrated.duplicated(["locality_code", "year"]).sum()),
            "outlier_flags_retained": len(flags),
        },
        "district": district.to_dict(orient="records"),
        "correlations": correlations,
        "top_counts_2025": top_counts.to_dict(orient="records"),
        "top_rates_2025": top_rates.to_dict(orient="records"),
        "top_divergence_2024_2025": divergence_2025.to_dict(orient="records"),
    }
    (reports / "annual_analysis_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    district_lines = "\n".join(
        f"- {int(row.year)}: {int(row.registered_person_thefts):,} hurtos a personas; {int(row.reported_123_theft_incidents):,} incidentes 123."
        .replace(",", ".")
        for row in district.itertuples(index=False)
    )
    markdown = f"""# Análisis anual de seguridad 2018–2025

## Alcance

La serie utiliza años completos enero–diciembre de 2018 a 2025. El dato 2026 disponible corresponde únicamente a enero–mayo y se excluye de toda comparación anual.

## Totales distritales

{district_lines}

## Calidad e integración

- 160 filas integradas: 20 localidades por 8 años.
- 0 llaves duplicadas y 0 valores requeridos faltantes.
- {len(flags)} valores marcados por IQR; todos se conservaron para revisión y ninguno se eliminó automáticamente.
- En 2025, {int(district.loc[district['year'] == 2025, 'unlocated_thefts'].iloc[0]):,} hurtos a personas quedaron sin localidad; la cobertura cartografiable fue {district.loc[district['year'] == 2025, 'theft_mapped_coverage_pct'].iloc[0]:.1f}%.

## Hallazgos de 2025

- Mayores conteos: {', '.join(row.locality_name for row in top_counts.itertuples(index=False))}.
- Mayores tasas: {', '.join(row.locality_name for row in top_rates.itertuples(index=False))}.
- La correlación territorial entre hurtos a personas e incidentes 123 fue {correlations['2025']['theft_vs_incident_pearson']:.3f} (Pearson).

## Advertencia conceptual

Hurto a personas e incidente 123 por hurto son medidas relacionadas, pero no equivalentes. Los reportes comunitarios se mantienen en una capa experimental separada.
"""
    (reports / "ANALISIS_ANUAL.md").write_text(markdown, encoding="utf-8")
    print(json.dumps(summary["quality"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
