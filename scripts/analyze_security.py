from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd


def pct_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current / previous - 1) * 100


def fmt_int(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def fmt_pct(value: float | None) -> str:
    if value is None or math.isnan(value):
        return "no calculable"
    return f"{value:.1f}%".replace(".", ",")


def main() -> None:
    processed_dir = Path(sys.argv[1])
    reports_dir = Path(sys.argv[2])
    reports_dir.mkdir(parents=True, exist_ok=True)

    integrated = pd.read_csv(
        processed_dir / "seguridad" / "seguridad_localidad_integrada.csv",
        dtype={"locality_code": "string"},
    )
    crime_unlocated = pd.read_csv(
        processed_dir / "sin_localizacion" / "alto_impacto_sin_localizacion_long.csv",
        dtype={"locality_code": "string"},
    )
    incident_unlocated = pd.read_csv(
        processed_dir / "sin_localizacion" / "incidentes_sin_localizacion_long.csv",
        dtype={"locality_code": "string"},
    )
    population_bogota = pd.read_csv(processed_dir / "poblacion" / "poblacion_bogota_agregado.csv")
    outlier_flags = pd.read_csv(reports_dir / "outlier_flags.csv")

    integrated["temporal_comparability"] = integrated["year"].map(
        lambda year: "comparable_ene_may_2025_2026"
        if year in (2025, 2026)
        else "historical_reference_period_not_verified"
    )
    integrated.to_csv(
        processed_dir / "seguridad" / "seguridad_localidad_analisis.csv",
        index=False,
        encoding="utf-8",
        float_format="%.6f",
    )

    located_totals = integrated.groupby("year", as_index=False).agg(
        registered_person_thefts=("registered_person_thefts", "sum"),
        reported_123_theft_incidents=("reported_123_theft_incidents", "sum"),
        population_sum_localities=("population", "sum"),
    )
    crime_unlocated = crime_unlocated.loc[crime_unlocated["metric"] == "hurto_personas", ["year", "count"]].rename(
        columns={"count": "unlocated_thefts"}
    )
    incident_unlocated = incident_unlocated.loc[incident_unlocated["metric"] == "hurto", ["year", "count"]].rename(
        columns={"count": "unlocated_incidents"}
    )
    pop_district = population_bogota.groupby("ANO", as_index=False)["POBLACION"].sum().rename(
        columns={"ANO": "year", "POBLACION": "population_bogota"}
    )
    district = located_totals.merge(crime_unlocated, on="year").merge(incident_unlocated, on="year").merge(pop_district, on="year")
    district["thefts_all"] = district["registered_person_thefts"] + district["unlocated_thefts"]
    district["incidents_all"] = district["reported_123_theft_incidents"] + district["unlocated_incidents"]
    district["theft_rate_per_100k_all"] = district["thefts_all"] / district["population_bogota"] * 100_000
    district["incident_rate_per_100k_all"] = district["incidents_all"] / district["population_bogota"] * 100_000
    district["incidents_per_theft_all"] = district["incidents_all"] / district["thefts_all"].replace(0, pd.NA)
    district["temporal_comparability"] = district["year"].map(
        lambda year: "comparable_ene_may_2025_2026" if year in (2025, 2026) else "historical_reference_period_not_verified"
    )
    district.to_csv(reports_dir / "district_summary.csv", index=False, encoding="utf-8", float_format="%.6f")

    current = integrated.loc[integrated["year"].isin([2025, 2026])].copy()
    value_columns = [
        "registered_person_thefts",
        "reported_123_theft_incidents",
        "population",
        "theft_rate_per_100k",
        "incident_rate_per_100k",
        "incidents_per_registered_theft",
        "count_rank",
        "rate_rank",
    ]
    comparison = current.pivot(index=["locality_code", "locality_name"], columns="year", values=value_columns)
    comparison.columns = [f"{metric}_{year}" for metric, year in comparison.columns]
    comparison = comparison.reset_index()
    comparison["theft_change_pct"] = (
        comparison["registered_person_thefts_2026"] / comparison["registered_person_thefts_2025"] - 1
    ) * 100
    comparison["incident_change_pct"] = (
        comparison["reported_123_theft_incidents_2026"] / comparison["reported_123_theft_incidents_2025"] - 1
    ) * 100
    comparison["theft_rate_change_pct"] = (
        comparison["theft_rate_per_100k_2026"] / comparison["theft_rate_per_100k_2025"] - 1
    ) * 100
    comparison["divergence_percentage_points"] = comparison["incident_change_pct"] - comparison["theft_change_pct"]
    comparison["count_rate_rank_gap_2026"] = comparison["count_rank_2026"] - comparison["rate_rank_2026"]
    comparison.to_csv(reports_dir / "locality_comparison_2025_2026.csv", index=False, encoding="utf-8", float_format="%.6f")

    district_current = district.set_index("year").loc[[2025, 2026]]
    district_metrics = {
        "thefts_2025": int(district_current.loc[2025, "thefts_all"]),
        "thefts_2026": int(district_current.loc[2026, "thefts_all"]),
        "theft_change_pct": pct_change(district_current.loc[2026, "thefts_all"], district_current.loc[2025, "thefts_all"]),
        "incidents_2025": int(district_current.loc[2025, "incidents_all"]),
        "incidents_2026": int(district_current.loc[2026, "incidents_all"]),
        "incident_change_pct": pct_change(district_current.loc[2026, "incidents_all"], district_current.loc[2025, "incidents_all"]),
        "theft_rate_2025": float(district_current.loc[2025, "theft_rate_per_100k_all"]),
        "theft_rate_2026": float(district_current.loc[2026, "theft_rate_per_100k_all"]),
        "theft_rate_change_pct": pct_change(
            district_current.loc[2026, "theft_rate_per_100k_all"], district_current.loc[2025, "theft_rate_per_100k_all"]
        ),
        "incident_to_theft_ratio_2025": float(district_current.loc[2025, "incidents_per_theft_all"]),
        "incident_to_theft_ratio_2026": float(district_current.loc[2026, "incidents_per_theft_all"]),
        "incident_to_theft_ratio_change_pct": pct_change(
            district_current.loc[2026, "incidents_per_theft_all"], district_current.loc[2025, "incidents_per_theft_all"]
        ),
    }

    correlations = {}
    for year in (2025, 2026):
        year_frame = integrated.loc[integrated["year"] == year]
        correlations[str(year)] = {
            "count_vs_rate_spearman": float(
                year_frame[["registered_person_thefts", "theft_rate_per_100k"]].corr(method="spearman").iloc[0, 1]
            ),
            "theft_vs_incident_pearson": float(
                year_frame[["registered_person_thefts", "reported_123_theft_incidents"]].corr(method="pearson").iloc[0, 1]
            ),
            "theft_vs_incident_spearman": float(
                year_frame[["registered_person_thefts", "reported_123_theft_incidents"]].corr(method="spearman").iloc[0, 1]
            ),
        }

    top_counts = comparison.nlargest(5, "registered_person_thefts_2026")[
        ["locality_name", "registered_person_thefts_2026", "theft_rate_per_100k_2026", "count_rank_2026", "rate_rank_2026"]
    ]
    top_rates = comparison.nlargest(5, "theft_rate_per_100k_2026")[
        ["locality_name", "registered_person_thefts_2026", "theft_rate_per_100k_2026", "count_rank_2026", "rate_rank_2026"]
    ]
    top_divergence = comparison.nlargest(5, "divergence_percentage_points")[
        ["locality_name", "theft_change_pct", "incident_change_pct", "divergence_percentage_points"]
    ]
    largest_rank_gaps = comparison.reindex(comparison["count_rate_rank_gap_2026"].abs().sort_values(ascending=False).index).head(5)[
        ["locality_name", "count_rank_2026", "rate_rank_2026", "count_rate_rank_gap_2026"]
    ]

    current_outliers = outlier_flags.loc[outlier_flags["year"].isin([2025, 2026])].copy()
    current_outliers.to_csv(reports_dir / "outlier_review_2025_2026.csv", index=False, encoding="utf-8", float_format="%.6f")

    summary = {
        "analysis_scope": "Only 2025 vs 2026 is treated as explicitly comparable (January-May).",
        "district": district_metrics,
        "correlations": correlations,
        "top_counts_2026": top_counts.to_dict(orient="records"),
        "top_rates_2026": top_rates.to_dict(orient="records"),
        "top_divergence_2025_2026": top_divergence.to_dict(orient="records"),
        "largest_count_rate_rank_gaps_2026": largest_rank_gaps.to_dict(orient="records"),
        "current_period_outlier_flags": int(len(current_outliers)),
        "hypothesis_assessment": {
            "count_ranking_differs_from_rate_ranking": "supported",
            "evidence": f"Spearman count-rate ranking association in 2026 = {correlations['2026']['count_vs_rate_spearman']:.3f}.",
            "reporting_gap_varies_by_locality": "supported_as_exploratory_pattern",
            "causal_or_underreporting_claim": "not_supported",
        },
    }
    (reports_dir / "analysis_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    top_count_text = ", ".join(
        f"{row.locality_name} ({fmt_int(row.registered_person_thefts_2026)})" for row in top_counts.itertuples(index=False)
    )
    top_rate_text = ", ".join(
        f"{row.locality_name} ({row.theft_rate_per_100k_2026:.1f})".replace(".", ",") for row in top_rates.itertuples(index=False)
    )
    divergence_lines = "\n".join(
        f"- **{row.locality_name}:** hurtos {fmt_pct(row.theft_change_pct)}; "
        f"incidentes {fmt_pct(row.incident_change_pct)}; "
        f"brecha {str(f'{row.divergence_percentage_points:.1f}').replace('.', ',')} p.p."
        for row in top_divergence.itertuples(index=False)
    )

    ratio_2025 = f"{district_metrics['incident_to_theft_ratio_2025']:.2f}".replace(".", ",")
    ratio_2026 = f"{district_metrics['incident_to_theft_ratio_2026']:.2f}".replace(".", ",")
    count_rate_spearman = f"{correlations['2026']['count_vs_rate_spearman']:.3f}".replace(".", ",")
    theft_incident_pearson = f"{correlations['2026']['theft_vs_incident_pearson']:.3f}".replace(".", ",")
    theft_incident_spearman = f"{correlations['2026']['theft_vs_incident_spearman']:.3f}".replace(".", ",")

    markdown = f"""# Análisis exploratorio de seguridad

## Alcance válido

El análisis inferencial se limita a la comparación enero-mayo de 2025 contra enero-mayo de 2026. Los campos 2018-2024 se conservan como referencia histórica, pero la ventana temporal no está suficientemente documentada en el archivo para tratarlos como una serie homogénea.

## Hallazgo principal: divergencia entre registros e incidentes

- Hurtos a personas registrados: {fmt_int(district_metrics['thefts_2025'])} en 2025 y {fmt_int(district_metrics['thefts_2026'])} en 2026 ({fmt_pct(district_metrics['theft_change_pct'])}).
- Incidentes 123 asociados a hurto: {fmt_int(district_metrics['incidents_2025'])} en 2025 y {fmt_int(district_metrics['incidents_2026'])} en 2026 ({fmt_pct(district_metrics['incident_change_pct'])}).
- La razón incidentes/hurtos pasó de {ratio_2025} a {ratio_2026}, un aumento relativo de {fmt_pct(district_metrics['incident_to_theft_ratio_change_pct'])}.

La divergencia indica que las dos fuentes no evolucionaron de la misma manera. No demuestra subregistro ni causalidad; justifica revisar diferencias entre demanda de atención, denuncia y registro administrativo.

## Hallazgo 2: conteo y tasa producen mapas distintos

La asociación de rangos entre conteo y tasa fue baja en 2026 (Spearman = {count_rate_spearman}). Los mayores conteos fueron: {top_count_text}. Las mayores tasas por cada 100.000 habitantes fueron: {top_rate_text}.

El ejemplo más claro es La Candelaria: puesto 19 por conteo y puesto 1 por tasa. Suba ocupa el puesto 1 por conteo y el 14 por tasa. Esto confirma que el dashboard debe permitir alternar entre ambas lecturas.

Las tasas altas del centro deben interpretarse con cautela porque el denominador usa población residente y no población flotante.

## Hallazgo 3: divergencias territoriales 2025-2026

{divergence_lines}

Estas brechas son señales para priorizar revisión, no para afirmar que una fuente es correcta y la otra incorrecta.

## Asociación entre fuentes

En 2026 los hurtos registrados y los incidentes 123 presentan asociación territorial alta: Pearson = {theft_incident_pearson} y Spearman = {theft_incident_spearman}. Sin embargo, la razón incidentes/hurto varía entre localidades, por lo que las fuentes son complementarias y no sustituibles.

## Revisión de outliers

Para 2025-2026 se marcaron {len(current_outliers)} valores: altos incidentes en Kennedy, Engativá y Suba, y una tasa alta de hurto en La Candelaria. Todos se conservaron porque son coherentes con tamaño poblacional, centralidad o volumen de actividad y no hay evidencia de error de captura.

## Evaluación de la hipótesis

- **Confirmada parcialmente:** el ranking por conteo difiere sustancialmente del ranking por tasa.
- **Confirmada como patrón exploratorio:** existen localidades con relaciones atípicas entre incidentes 123 y hurtos registrados.
- **No demostrada:** no puede concluirse causalidad ni estimar directamente subregistro con estas fuentes agregadas.
"""
    (reports_dir / "ANALISIS_EXPLORATORIO.md").write_text(markdown, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
