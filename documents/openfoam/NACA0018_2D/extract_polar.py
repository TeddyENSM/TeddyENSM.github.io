#!/usr/bin/env python3
"""Summarize OpenFOAM forceCoeffs results for the prepared NACA 0018 sweep."""

from __future__ import annotations

import csv
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parent
SWEEP_DIR = CASE_DIR / "alpha_cases_v2406"
OUTPUT_FILE = CASE_DIR / "polaire_coefficients_v2406.csv"
ANGLES = (-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10)
WINDOW_SIZE = 10


def read_coefficients(case_dir: Path) -> list[dict[str, float]]:
    rows_by_time: dict[float, dict[str, float]] = {}
    coefficient_files = sorted(
        case_dir.glob("postProcessing/forceCoeffs1/*/coefficient.dat"),
        key=lambda path: float(path.parent.name) if path.parent.name.replace(".", "", 1).isdigit() else -1,
    )
    for path in coefficient_files:
        with path.open(encoding="ascii") as stream:
            for line in stream:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                values = [float(value) for value in stripped.split()]
                if len(values) < 8:
                    continue
                rows_by_time[values[0]] = {
                    "time": values[0],
                    "Cd": values[1],
                    "Cl": values[4],
                    "CmPitch": values[7],
                }
    return [rows_by_time[time] for time in sorted(rows_by_time)]


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def summarize(angle: int) -> dict[str, float | int | str]:
    case = SWEEP_DIR / f"alpha_{angle}deg"
    if not list(case.glob("postProcessing/forceCoeffs1/*/coefficient.dat")):
        return {"alpha_deg": angle, "status": "missing", "time": "", "Cd": "", "Cl": ""}

    rows = read_coefficients(case)
    if not rows:
        return {"alpha_deg": angle, "status": "no coefficients", "time": "", "Cd": "", "Cl": ""}

    final = rows[-1]
    window = rows[-WINDOW_SIZE:]
    cd_values = [row["Cd"] for row in window]
    cl_values = [row["Cl"] for row in window]
    cd_mean = mean(cd_values)
    cl_mean = mean(cl_values)
    cd_span = max(cd_values) - min(cd_values)
    cl_span = max(cl_values) - min(cl_values)
    cd_span_pct = 100.0 * cd_span / max(abs(cd_mean), 1e-8)
    log_file = case / "log.resume"
    if not log_file.exists():
        candidates = sorted(case.glob("log.resume.from_*.log"))
        log_file = candidates[-1] if candidates else case / "log.simpleFoam"
    completed = log_file.exists() and any(line.strip() == "End" for line in log_file.open(encoding="utf-8", errors="replace"))

    return {
        "alpha_deg": angle,
        "status": "completed" if completed else "incomplete",
        "time": int(final["time"]),
        "Cd": final["Cd"],
        "Cl": final["Cl"],
        "Cd_mean_last_window": cd_mean,
        "Cl_mean_last_window": cl_mean,
        "Cd_window_min": min(row["Cd"] for row in window),
        "Cd_window_max": max(row["Cd"] for row in window),
        "Cl_window_min": min(row["Cl"] for row in window),
        "Cl_window_max": max(row["Cl"] for row in window),
        "Cd_window_span_pct": cd_span_pct,
        "Cl_window_span": cl_span,
        "force_stability": "stable" if cd_span_pct <= 1.0 and cl_span <= 0.01 else "drifting",
        "window_samples": len(window),
    }


def main() -> None:
    summaries = [summarize(angle) for angle in ANGLES]
    columns = [
        "alpha_deg",
        "status",
        "time",
        "Cd",
        "Cl",
        "Cd_mean_last_window",
        "Cl_mean_last_window",
        "Cd_window_min",
        "Cd_window_max",
        "Cl_window_min",
        "Cl_window_max",
        "Cd_window_span_pct",
        "Cl_window_span",
        "force_stability",
        "window_samples",
    ]
    with OUTPUT_FILE.open("w", encoding="ascii", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(summaries)

    print(f"alpha  status      time       Cd         Cl       Cd_mean    Cl_mean   force")
    for row in summaries:
        print(
            f"{row['alpha_deg']:>5}  {row['status']:<10} {str(row['time']):>5}  "
            f"{str(row.get('Cd', '')):>10} {str(row.get('Cl', '')):>10}  "
            f"{str(row.get('Cd_mean_last_window', '')):>10} "
            f"{str(row.get('Cl_mean_last_window', '')):>10} "
            f"{str(row.get('force_stability', ''))}"
        )
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
