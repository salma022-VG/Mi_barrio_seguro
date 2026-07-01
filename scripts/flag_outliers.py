from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


METRICS = [
    "registered_person_thefts",
    "reported_123_theft_incidents",
    "theft_rate_per_100k",
    "incident_rate_per_100k",
    "incidents_per_registered_theft",
]


def main() -> None:
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    summary_path = Path(sys.argv[3])
    frame = pd.read_csv(input_path, dtype={"locality_code": "string"})
    flags = []
    for year, group in frame.groupby("year"):
        for metric in METRICS:
            values = group[metric].dropna()
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            selected = group.loc[(group[metric] < lower) | (group[metric] > upper)]
            for row in selected.itertuples(index=False):
                flags.append(
                    {
                        "year": int(year),
                        "locality_code": row.locality_code,
                        "locality_name": row.locality_name,
                        "metric": metric,
                        "value": getattr(row, metric),
                        "iqr_lower_bound": lower,
                        "iqr_upper_bound": upper,
                        "action": "kept_for_review",
                    }
                )
    result = pd.DataFrame(flags)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, encoding="utf-8", float_format="%.6f")
    summary = {
        "flagged_values": int(len(result)),
        "flagged_rows": int(result[["year", "locality_code"]].drop_duplicates().shape[0]) if not result.empty else 0,
        "removed_values": 0,
        "method": "IQR 1.5 within each year and metric",
        "decision": "Flags are diagnostic only. Territorial extremes may be meaningful and were not removed.",
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
