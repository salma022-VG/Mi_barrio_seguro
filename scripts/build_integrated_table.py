from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


def main() -> None:
    processed_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    checks_path = Path(sys.argv[3])

    crime = pd.read_csv(processed_dir / "seguridad" / "alto_impacto_localidad_long.csv", dtype={"locality_code": "string"})
    incidents = pd.read_csv(processed_dir / "seguridad" / "incidentes_localidad_long.csv", dtype={"locality_code": "string"})
    population = pd.read_csv(processed_dir / "poblacion" / "poblacion_localidad_anual.csv", dtype={"locality_code": "string"})

    crime = crime.loc[crime["metric"] == "hurto_personas"].copy()
    crime = crime.rename(columns={"count": "registered_person_thefts"})
    incidents = incidents.loc[incidents["metric"] == "hurto"].copy()
    incidents = incidents.rename(columns={"count": "reported_123_theft_incidents"})

    crime_columns = [
        "locality_code",
        "locality_name",
        "year",
        "registered_person_thefts",
        "period_label",
        "period_start_month",
        "period_end_month",
        "is_partial_year",
    ]
    incident_columns = ["locality_code", "year", "reported_123_theft_incidents", "period_label"]
    integrated = crime[crime_columns].merge(
        incidents[incident_columns],
        on=["locality_code", "year"],
        how="outer",
        validate="one_to_one",
        suffixes=("_crime", "_incident"),
        indicator=True,
    )
    integrated = integrated.merge(
        population[["locality_code", "year", "population"]],
        on=["locality_code", "year"],
        how="left",
        validate="many_to_one",
    )

    integrated["theft_rate_per_100k"] = integrated["registered_person_thefts"] / integrated["population"] * 100_000
    integrated["incident_rate_per_100k"] = integrated["reported_123_theft_incidents"] / integrated["population"] * 100_000
    integrated["incidents_per_registered_theft"] = (
        integrated["reported_123_theft_incidents"] / integrated["registered_person_thefts"].replace(0, pd.NA)
    )
    integrated["count_rank"] = integrated.groupby("year")["registered_person_thefts"].rank(method="min", ascending=False).astype("int16")
    integrated["rate_rank"] = integrated.groupby("year")["theft_rate_per_100k"].rank(method="min", ascending=False).astype("int16")
    integrated["rank_difference_count_minus_rate"] = integrated["count_rank"] - integrated["rate_rank"]
    integrated = integrated.sort_values(["year", "locality_code"]).reset_index(drop=True)

    checks = {
        "row_count": int(len(integrated)),
        "expected_row_count": 20 * 9,
        "locality_count": int(integrated["locality_code"].nunique()),
        "year_min": int(integrated["year"].min()),
        "year_max": int(integrated["year"].max()),
        "duplicate_locality_year_rows": int(integrated.duplicated(["locality_code", "year"]).sum()),
        "unmatched_source_rows": int((integrated["_merge"] != "both").sum()),
        "missing_population_rows": int(integrated["population"].isna().sum()),
        "nonpositive_population_rows": int((integrated["population"] <= 0).sum()),
        "negative_crime_count_rows": int((integrated["registered_person_thefts"] < 0).sum()),
        "negative_incident_count_rows": int((integrated["reported_123_theft_incidents"] < 0).sum()),
        "period_label_mismatches": int((integrated["period_label_crime"] != integrated["period_label_incident"]).sum()),
        "null_rate_rows": int(integrated["theft_rate_per_100k"].isna().sum()),
        "all_checks_passed": False,
    }
    checks["all_checks_passed"] = all(
        [
            checks["row_count"] == checks["expected_row_count"],
            checks["locality_count"] == 20,
            checks["duplicate_locality_year_rows"] == 0,
            checks["unmatched_source_rows"] == 0,
            checks["missing_population_rows"] == 0,
            checks["nonpositive_population_rows"] == 0,
            checks["negative_crime_count_rows"] == 0,
            checks["negative_incident_count_rows"] == 0,
            checks["period_label_mismatches"] == 0,
            checks["null_rate_rows"] == 0,
        ]
    )

    integrated = integrated.drop(columns=["_merge", "period_label_incident"]).rename(
        columns={"period_label_crime": "period_label"}
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    integrated.to_csv(output_path, index=False, encoding="utf-8", float_format="%.6f")
    checks_path.parent.mkdir(parents=True, exist_ok=True)
    checks_path.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))
    if not checks["all_checks_passed"]:
        raise SystemExit("Integrated table validation failed")


if __name__ == "__main__":
    main()
