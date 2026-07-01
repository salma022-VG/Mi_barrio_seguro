from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def iter_positions(coordinates: Any) -> Iterable[list[float]]:
    if not isinstance(coordinates, list):
        return
    if coordinates and all(isinstance(value, (int, float)) for value in coordinates[:2]):
        yield coordinates
        return
    for child in coordinates:
        yield from iter_positions(child)


def iter_rings(geometry: dict[str, Any]) -> Iterable[list[Any]]:
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type == "Polygon" and isinstance(coordinates, list):
        yield from coordinates
    elif geometry_type == "MultiPolygon" and isinstance(coordinates, list):
        for polygon in coordinates:
            if isinstance(polygon, list):
                yield from polygon


def profile_geojson(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    features = data.get("features", [])
    property_names = sorted({key for feature in features for key in feature.get("properties", {})})
    nulls = Counter()
    blanks = Counter()
    numeric_negative = Counter()
    numeric_nonfinite = Counter()
    geometry_types = Counter()
    null_geometry = 0
    malformed_positions = 0
    out_of_wgs84_bounds = 0
    unclosed_rings = 0
    too_short_rings = 0
    exact_fingerprints = Counter()
    candidate_key_fields = [
        name for name in property_names if name.startswith("CMIU") or "COD" in name.upper() or "MES" in name.upper()
    ]
    candidate_key_counts = Counter()
    bbox = [math.inf, math.inf, -math.inf, -math.inf]

    for feature in features:
        properties = feature.get("properties") or {}
        for name in property_names:
            value = properties.get(name)
            if value is None:
                nulls[name] += 1
            elif isinstance(value, str) and not value.strip():
                blanks[name] += 1
            elif isinstance(value, (int, float)):
                if not math.isfinite(value):
                    numeric_nonfinite[name] += 1
                elif value < 0:
                    numeric_negative[name] += 1

        geometry = feature.get("geometry")
        if not geometry:
            null_geometry += 1
        else:
            geometry_types[geometry.get("type", "MISSING")] += 1
            for position in iter_positions(geometry.get("coordinates")):
                if len(position) < 2 or not all(isinstance(value, (int, float)) for value in position[:2]):
                    malformed_positions += 1
                    continue
                x, y = position[:2]
                if not math.isfinite(x) or not math.isfinite(y):
                    malformed_positions += 1
                    continue
                if not (-180 <= x <= 180 and -90 <= y <= 90):
                    out_of_wgs84_bounds += 1
                bbox[0] = min(bbox[0], x)
                bbox[1] = min(bbox[1], y)
                bbox[2] = max(bbox[2], x)
                bbox[3] = max(bbox[3], y)
            for ring in iter_rings(geometry):
                if len(ring) < 4:
                    too_short_rings += 1
                elif ring[0] != ring[-1]:
                    unclosed_rings += 1

        fingerprint = json.dumps(
            {"properties": properties, "geometry": geometry}, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        exact_fingerprints[fingerprint] += 1
        key = tuple(properties.get(name) for name in candidate_key_fields)
        candidate_key_counts[key] += 1

    duplicate_exact = sum(count - 1 for count in exact_fingerprints.values() if count > 1)
    duplicate_candidate_keys = sum(count - 1 for count in candidate_key_counts.values() if count > 1)
    first_properties = features[0].get("properties", {}) if features else {}
    return {
        "file": str(path),
        "sha256": sha256(path),
        "collection_type": data.get("type"),
        "name": data.get("name"),
        "crs": data.get("crs"),
        "feature_count": len(features),
        "property_names": property_names,
        "first_properties": first_properties,
        "null_counts": dict(nulls),
        "blank_string_counts": dict(blanks),
        "negative_numeric_counts": dict(numeric_negative),
        "nonfinite_numeric_counts": dict(numeric_nonfinite),
        "geometry_types": dict(geometry_types),
        "null_geometry_count": null_geometry,
        "malformed_position_count": malformed_positions,
        "out_of_wgs84_bounds_count": out_of_wgs84_bounds,
        "unclosed_ring_count": unclosed_rings,
        "too_short_ring_count": too_short_rings,
        "bbox": None if math.isinf(bbox[0]) else bbox,
        "exact_duplicate_feature_count": duplicate_exact,
        "candidate_key_fields": candidate_key_fields,
        "candidate_key_duplicate_count": duplicate_candidate_keys,
    }


def profile_csv(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype="string")
    stripped = frame.apply(lambda column: column.str.strip() if column.dtype.name == "string" else column)
    blanks = {column: int(stripped[column].eq("").sum()) for column in stripped.columns}
    nulls = {column: int(stripped[column].isna().sum()) for column in stripped.columns}
    logical_key = [name for name in ["ANO", "CODIGO_LOCALIDAD", "SEXO", "EDAD"] if name in stripped.columns]
    numeric_summary = {}
    for column in ["ANO", "EDAD", "POBLACION"]:
        if column in stripped.columns:
            numeric = pd.to_numeric(stripped[column], errors="coerce")
            numeric_summary[column] = {
                "invalid_numeric": int(numeric.isna().sum() - stripped[column].isna().sum()),
                "min": None if numeric.dropna().empty else float(numeric.min()),
                "max": None if numeric.dropna().empty else float(numeric.max()),
                "negative": int((numeric < 0).sum()),
                "zero": int((numeric == 0).sum()),
            }
    code_name_conflicts = {}
    if {"CODIGO_LOCALIDAD", "NOMBRE_LOCALIDAD"}.issubset(stripped.columns):
        mappings = stripped.groupby("CODIGO_LOCALIDAD", dropna=False)["NOMBRE_LOCALIDAD"].nunique(dropna=False)
        code_name_conflicts = {str(code): int(count) for code, count in mappings[mappings > 1].items()}
    return {
        "file": str(path),
        "sha256": sha256(path),
        "row_count": int(len(stripped)),
        "columns": list(stripped.columns),
        "null_counts": nulls,
        "blank_string_counts": blanks,
        "exact_duplicate_row_count": int(stripped.duplicated().sum()),
        "logical_key": logical_key,
        "logical_key_duplicate_count": int(stripped.duplicated(subset=logical_key).sum()) if logical_key else None,
        "numeric_summary": numeric_summary,
        "locality_count": int(stripped["CODIGO_LOCALIDAD"].nunique()) if "CODIGO_LOCALIDAD" in stripped else None,
        "locality_codes": sorted(stripped["CODIGO_LOCALIDAD"].dropna().unique().tolist()) if "CODIGO_LOCALIDAD" in stripped else [],
        "sex_values": sorted(stripped["SEXO"].dropna().unique().tolist()) if "SEXO" in stripped else [],
        "code_name_conflicts": code_name_conflicts,
    }


def main() -> None:
    raw_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    results: dict[str, Any] = {"csv": [], "geojson": []}
    for path in sorted(raw_dir.rglob("*")):
        if path.suffix.lower() == ".csv":
            results["csv"].append(profile_csv(path))
        elif path.suffix.lower() in {".geojson", ".json"}:
            results["geojson"].append(profile_geojson(path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
