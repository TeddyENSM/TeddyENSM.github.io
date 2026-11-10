#!/usr/bin/env python3
"""Prepare one OpenFOAM case per incidence angle without running the solver."""

from __future__ import annotations

import shutil
from pathlib import Path
from subprocess import run


CASE_DIR = Path(__file__).resolve().parent
ANGLE_FILE = CASE_DIR / "alpha_list.txt"
OUTPUT_DIR = CASE_DIR / "alpha_cases"


def default_angles():
    return [-10.0, -8.0, -6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0, 8.0, 10.0]


def read_angles():
    if ANGLE_FILE.exists():
        return [float(line.strip()) for line in ANGLE_FILE.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]
    return default_angles()


def main():
    angles = read_angles()
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for angle in angles:
        label = f"alpha_{int(angle) if float(angle).is_integer() else angle}deg"
        dest = OUTPUT_DIR / label
        shutil.copytree(CASE_DIR, dest, dirs_exist_ok=False, ignore=shutil.ignore_patterns("alpha_cases", "__pycache__"))
        run(["python3", "set_incidence.py", str(angle)], cwd=dest, check=True)
        print(f"Prepared {dest} for alpha={angle} deg")

    print(f"Generated angle cases in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
