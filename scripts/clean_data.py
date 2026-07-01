from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd


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

YEARS = list(range(2018, 2027))


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8")


def load_geojson(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_geojson(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def period_metadata(label: str) -> dict[str, Any]:
    normalized = label.lower()
    month_end = 5 if "may" in normalized else 4 if "abr" in normalized else None
    return {
        "period_label": label,
        "period_start_month": 1 if month_end else None,
        "period_end_month": month_end,
        "is_partial_year": bool(month_end),
    }


def find_year_field(properties: dict[str, Any], prefix: str, year: int) -> str:
    year_short = str(year)[-2:]
    candidates = [f"{prefix}{year_short}CONT", f"{prefix}{year_short}CON"]
    for candidate in candidates:
        if candidate in properties:
            return candidate
    raise KeyError(f"Missing field for prefix={prefix}, year={year}: {candidates}")


def normalize_count(value: Any) -> int | float | None:
    if value is None:
        return None
    number = float(value)
    return int(number) if number.is_integer() else number


def canonical_localities(population: pd.DataFrame) -> dict[str, str]:
    pairs = population.loc[population["CODIGO_LOCALIDAD"] != "00", ["CODIGO_LOCALIDAD", "NOMBRE_LOCALIDAD"]]
    return dict(pairs.drop_duplicates().itertuples(index=False, name=None))


def clean_population(raw_path: Path, output_dir: Path, report: dict[str, Any]) -> dict[str, str]:
    frame = pd.read_csv(raw_path, sep=";", encoding="utf-8-sig", dtype="string")
    frame.columns = [column.strip().upper() for column in frame.columns]
    for column in frame.columns:
        frame[column] = frame[column].str.strip()
    frame["ANO"] = pd.to_numeric(frame["ANO"], errors="raise").astype("int16")
    frame["EDAD"] = pd.to_numeric(frame["EDAD"], errors="raise").astype("int16")
    frame["POBLACION"] = pd.to_numeric(frame["POBLACION"], errors="raise").astype("int64")
    frame["CODIGO_LOCALIDAD"] = frame["CODIGO_LOCALIDAD"].str.zfill(2)

    duplicates = int(frame.duplicated().sum())
    if duplicates:
        frame = frame.drop_duplicates().copy()

    bogota = frame.loc[frame["CODIGO_LOCALIDAD"] == "00"].copy()
    locality = frame.loc[frame["CODIGO_LOCALIDAD"] != "00"].copy()
    locality = locality.sort_values(["ANO", "CODIGO_LOCALIDAD", "SEXO", "EDAD"]).reset_index(drop=True)
    bogota = bogota.sort_values(["ANO", "SEXO", "EDAD"]).reset_index(drop=True)

    annual = (
        locality.groupby(["ANO", "CODIGO_LOCALIDAD", "NOMBRE_LOCALIDAD"], as_index=False, observed=True)["POBLACION"]
        .sum()
        .rename(columns={"ANO": "year", "CODIGO_LOCALIDAD": "locality_code", "NOMBRE_LOCALIDAD": "locality_name", "POBLACION": "population"})
        .sort_values(["year", "locality_code"])
    )
    bogota_annual = bogota.groupby("ANO", as_index=False, observed=True)["POBLACION"].sum().rename(
        columns={"ANO": "year", "POBLACION": "population_bogota_source"}
    )
    locality_sum = annual.groupby("year", as_index=False, observed=True)["population"].sum().rename(
        columns={"population": "population_sum_localities"}
    )
    reconciliation = bogota_annual.merge(locality_sum, on="year", how="outer")
    reconciliation["difference"] = reconciliation["population_bogota_source"] - reconciliation["population_sum_localities"]

    write_csv(locality, output_dir / "poblacion" / "poblacion_localidades_limpio.csv")
    write_csv(bogota, output_dir / "poblacion" / "poblacion_bogota_agregado.csv")
    write_csv(annual, output_dir / "poblacion" / "poblacion_localidad_anual.csv")
    write_csv(reconciliation, output_dir / "poblacion" / "reconciliacion_poblacion.csv")

    report["population"] = {
        "input_rows": int(len(frame) + duplicates),
        "exact_duplicates_removed": duplicates,
        "locality_rows_written": int(len(locality)),
        "bogota_aggregate_rows_separated": int(len(bogota)),
        "annual_locality_rows_written": int(len(annual)),
        "null_rows_removed": 0,
        "outliers_removed": 0,
        "zero_population_rows_kept": int((frame["POBLACION"] == 0).sum()),
        "population_reconciliation_max_abs_difference": int(reconciliation["difference"].abs().max()),
    }
    return canonical_localities(frame)


def long_locality_metrics(
    data: dict[str, Any],
    metrics: dict[str, str],
    source: str,
    canonical_names: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, Any]], dict[str, Any]]:
    located_rows: list[dict[str, Any]] = []
    unlocated_rows: list[dict[str, Any]] = []
    map_features: list[dict[str, Any]] = []
    name_corrections = 0
    missing_counts = 0
    input_features = data.get("features", [])

    for feature in input_features:
        properties = feature.get("properties") or {}
        code = str(properties["CMIULOCAL"]).zfill(2)
        source_name = str(properties["CMNOMLOCAL"]).strip()
        name = canonical_names.get(code, source_name)
        if name != source_name:
            name_corrections += 1
        period = period_metadata(str(properties.get("CMMES", "")).strip())

        target = unlocated_rows if feature.get("geometry") is None or code == "99" else located_rows
        for prefix, metric in metrics.items():
            for year in YEARS:
                field = find_year_field(properties, prefix, year)
                count = normalize_count(properties.get(field))
                if count is None:
                    missing_counts += 1
                target.append(
                    {
                        "source": source,
                        "locality_code": code,
                        "locality_name": name,
                        "year": year,
                        "metric": metric,
                        "count": count,
                        **period,
                    }
                )

        if target is located_rows:
            map_features.append(
                {
                    "type": "Feature",
                    "properties": {"locality_code": code, "locality_name": name},
                    "geometry": feature["geometry"],
                }
            )

    located = pd.DataFrame(located_rows).sort_values(["locality_code", "metric", "year"]).reset_index(drop=True)
    unlocated = pd.DataFrame(unlocated_rows).sort_values(["metric", "year"]).reset_index(drop=True)
    stats = {
        "input_features": len(input_features),
        "map_features_written": len(map_features),
        "unlocated_features_separated": len(input_features) - len(map_features),
        "located_metric_rows_written": len(located),
        "unlocated_metric_rows_written": len(unlocated),
        "locality_names_canonicalized": name_corrections,
        "missing_metric_values": missing_counts,
        "duplicates_removed": 0,
        "outliers_removed": 0,
    }
    return located, unlocated, map_features, stats


def clean_optional_geometry(
    raw_path: Path,
    output_path: Path,
    code_field: str,
    name_field: str,
    code_out: str,
    name_out: str,
) -> dict[str, Any]:
    data = load_geojson(raw_path)
    map_features = []
    unresolved = []
    for feature in data.get("features", []):
        properties = feature.get("properties") or {}
        simplified = {
            code_out: str(properties.get(code_field, "")).strip(),
            name_out: str(properties.get(name_field, "")).strip(),
        }
        if feature.get("geometry") is None:
            unresolved.append({"properties": simplified, "source_properties": properties})
            continue
        map_features.append({"type": "Feature", "properties": simplified, "geometry": feature["geometry"]})
    output = {
        "type": "FeatureCollection",
        "name": output_path.stem,
        "crs": data.get("crs"),
        "features": map_features,
    }
    write_geojson(output, output_path)
    unresolved_path = output_path.parent.parent / "sin_localizacion" / f"{output_path.stem}_sin_geometria.json"
    unresolved_path.parent.mkdir(parents=True, exist_ok=True)
    unresolved_path.write_text(json.dumps(unresolved, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "input_features": len(data.get("features", [])),
        "map_features_written": len(map_features),
        "features_without_geometry_separated": len(unresolved),
        "duplicates_removed": 0,
        "outliers_removed": 0,
    }


def compare_locality_geometry(dai_features: list[dict[str, Any]], ir_features: list[dict[str, Any]]) -> int:
    def by_code(features: list[dict[str, Any]]) -> dict[str, Any]:
        return {feature["properties"]["locality_code"]: feature["geometry"] for feature in features}

    dai = by_code(dai_features)
    ir = by_code(ir_features)
    common = set(dai) & set(ir)
    return sum(dai[code] != ir[code] for code in common)


def main() -> None:
    raw_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    report_path = Path(sys.argv[3])
    report: dict[str, Any] = {
        "policy": {
            "originals_modified": False,
            "null_count_rows_removed": 0,
            "outlier_rows_removed": 0,
            "negative_variations_kept": True,
            "zero_counts_kept": True,
            "rule": "Only exact duplicates and records unusable for a map are removed from map-ready outputs; unusable records are preserved separately.",
        }
    }

    canonical_names = clean_population(raw_dir / "poblacion_localidades.csv", output_dir, report)

    dai_data = load_geojson(raw_dir / "alto_impacto" / "DAILoc.geojson")
    ir_data = load_geojson(raw_dir / "incidentes_reportados" / "IRLoc.geojson")
    dai_long, dai_unlocated, dai_features, dai_stats = long_locality_metrics(
        dai_data, DAI_METRICS, "delito_alto_impacto", canonical_names
    )
    ir_long, ir_unlocated, ir_features, ir_stats = long_locality_metrics(
        ir_data, IR_METRICS, "incidente_reportado_123", canonical_names
    )

    write_csv(dai_long, output_dir / "seguridad" / "alto_impacto_localidad_long.csv")
    write_csv(dai_unlocated, output_dir / "sin_localizacion" / "alto_impacto_sin_localizacion_long.csv")
    write_csv(ir_long, output_dir / "seguridad" / "incidentes_localidad_long.csv")
    write_csv(ir_unlocated, output_dir / "sin_localizacion" / "incidentes_sin_localizacion_long.csv")

    locality_geojson = {
        "type": "FeatureCollection",
        "name": "localidades_bogota",
        "crs": dai_data.get("crs"),
        "features": sorted(dai_features, key=lambda feature: feature["properties"]["locality_code"]),
    }
    write_geojson(locality_geojson, output_dir / "mapas" / "localidades_bogota.geojson")

    report["delito_alto_impacto_localidad"] = dai_stats
    report["incidentes_reportados_localidad"] = ir_stats
    report["locality_geometry_mismatches_between_sources"] = compare_locality_geometry(dai_features, ir_features)
    report["incidentes_reportados_upz"] = clean_optional_geometry(
        raw_dir / "incidentes_reportados" / "IRUPZ.geojson",
        output_dir / "mapas" / "incidentes_upz.geojson",
        "CMIUUPLA",
        "CMNOMUPLA",
        "upz_code",
        "upz_name",
    )
    report["incidentes_reportados_sector_catastral"] = clean_optional_geometry(
        raw_dir / "incidentes_reportados" / "IRSCAT.geojson",
        output_dir / "mapas" / "incidentes_sector_catastral.geojson",
        "CMIUSCAT",
        "CMNOMSCAT",
        "sector_code",
        "sector_name",
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
