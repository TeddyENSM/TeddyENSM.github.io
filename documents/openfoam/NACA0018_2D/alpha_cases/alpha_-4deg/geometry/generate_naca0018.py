#!/usr/bin/env python3
"""Generate normalized and 50 mm chord NACA 0018 contour coordinates."""

from math import cos, pi, sqrt
from pathlib import Path


HERE = Path(__file__).resolve().parent
CHORD_M = 0.05
THICKNESS_RATIO = 0.18
PANELS_PER_SIDE = 100


def contour_points():
    upper = []
    lower = []

    for index in range(PANELS_PER_SIDE + 1):
        beta = pi * index / PANELS_PER_SIDE
        x = 0.5 * (1.0 + cos(beta))
        thickness = 5.0 * THICKNESS_RATIO * (
            0.2969 * sqrt(x)
            - 0.1260 * x
            - 0.3516 * x**2
            + 0.2843 * x**3
            - 0.1036 * x**4
        )
        if index == 0:
            thickness = 0.0
        upper.append((x, thickness))
        lower.append((x, -thickness))

    return upper + list(reversed(lower[:-1]))


def write_coordinates(path, points, scale):
    with path.open("w", encoding="ascii", newline="\n") as output:
        output.write("NACA 0018\n")
        for x, y in points:
            output.write(f"{x * scale:.9f} {y * scale:.9f}\n")


def main():
    points = contour_points()
    normalized_path = HERE / "naca0018.dat"
    scaled_path = HERE / "naca0018_50mm.dat"
    write_coordinates(normalized_path, points, 1.0)
    write_coordinates(scaled_path, points, CHORD_M)

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    chord = (max(xs) - min(xs)) * CHORD_M
    thickness = (max(ys) - min(ys)) * CHORD_M
    print(f"Wrote {len(points)} contour points to:")
    print(f"  {normalized_path}")
    print(f"  {scaled_path}")
    print(f"Chord: {chord:.6f} m; maximum thickness: {thickness:.6f} m")

    assert len(points) == 2 * PANELS_PER_SIDE + 1
    assert abs(chord - CHORD_M) < 1e-12
    assert abs(thickness / chord - THICKNESS_RATIO) < 5e-5
    assert points[0] == points[-1] == (1.0, 0.0)
    assert points[PANELS_PER_SIDE] == (0.0, 0.0)


if __name__ == "__main__":
    main()