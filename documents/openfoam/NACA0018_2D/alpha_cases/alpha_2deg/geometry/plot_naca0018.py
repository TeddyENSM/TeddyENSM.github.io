#!/usr/bin/env python3
"""Plot the scaled NACA 0018 contour from its coordinate file."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
COORDINATES = HERE / "naca0018_50mm.dat"
OUTPUT = HERE / "naca0018_50mm.png"


def main():
    rows = COORDINATES.read_text(encoding="ascii").splitlines()[1:]
    points = [tuple(map(float, row.split())) for row in rows if row.strip()]
    x_mm = [x * 1000 for x, _ in points]
    y_mm = [y * 1000 for _, y in points]

    figure, axis = plt.subplots(figsize=(10, 4), layout="constrained")
    axis.fill(x_mm, y_mm, color="#c7d7f2", zorder=2)
    axis.plot(x_mm, y_mm, color="#17365d", linewidth=1.5, zorder=3)
    axis.plot([0, 50], [0, 0], color="#d06b35", linestyle="--", linewidth=1)
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlim(-2, 52)
    axis.set_ylim(-6, 6)
    axis.set_xlabel("x (mm)")
    axis.set_ylabel("y (mm)")
    axis.set_title("NACA 0018 - corde 50 mm")
    axis.grid(True, color="#d9dee7", linewidth=0.7)
    figure.savefig(OUTPUT, dpi=180)
    print(f"Image written to {OUTPUT}")


if __name__ == "__main__":
    main()