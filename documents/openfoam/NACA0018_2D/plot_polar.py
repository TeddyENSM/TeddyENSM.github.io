#!/usr/bin/env python3
"""Create a dependency-free SVG overview of the extracted polar data."""

from __future__ import annotations

import csv
import math
import xml.etree.ElementTree as ET
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parent
DATA_FILE = CASE_DIR / "polaire_coefficients_v2406.csv"
OUTPUT_FILE = CASE_DIR / "polaire_coefficients_v2406.svg"
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def element(parent: ET.Element, tag: str, attributes: dict[str, str], text: str | None = None) -> ET.Element:
    node = ET.SubElement(parent, f"{{{SVG_NS}}}{tag}", attributes)
    if text is not None:
        node.text = text
    return node


def load_rows() -> list[dict[str, float]]:
    with DATA_FILE.open(encoding="ascii", newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row["status"] == "completed"]
    return [
        {
            "alpha": float(row["alpha_deg"]),
            "Cd": float(row["Cd_mean_last_window"]),
            "Cl": float(row["Cl_mean_last_window"]),
        }
        for row in rows
    ]


def draw_panel(
    svg: ET.Element,
    title: str,
    x_label: str,
    y_label: str,
    points: list[tuple[float, float]],
    x: int,
    color: str,
) -> None:
    panel_width = 360
    left = x + 58
    top = 72
    plot_width = 270
    plot_height = 260
    values_x = [point[0] for point in points]
    values_y = [point[1] for point in points]
    x_min, x_max = min(values_x), max(values_x)
    y_min, y_max = min(values_y), max(values_y)
    x_pad = max((x_max - x_min) * 0.08, 0.1)
    y_pad = max((y_max - y_min) * 0.12, 0.005)
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad

    element(svg, "text", {"x": str(x + panel_width / 2), "y": "34", "text-anchor": "middle", "class": "panel-title"}, title)
    for tick in range(6):
        fraction = tick / 5
        grid_x = left + fraction * plot_width
        grid_y = top + fraction * plot_height
        x_value = x_min + fraction * (x_max - x_min)
        y_value = y_max - fraction * (y_max - y_min)
        element(svg, "line", {"x1": f"{grid_x:.1f}", "y1": str(top), "x2": f"{grid_x:.1f}", "y2": str(top + plot_height), "class": "grid"})
        element(svg, "line", {"x1": str(left), "y1": f"{grid_y:.1f}", "x2": str(left + plot_width), "y2": f"{grid_y:.1f}", "class": "grid"})
        element(svg, "text", {"x": f"{grid_x:.1f}", "y": str(top + plot_height + 18), "text-anchor": "middle", "class": "tick"}, f"{x_value:.2f}")
        element(svg, "text", {"x": str(left - 8), "y": f"{grid_y + 4:.1f}", "text-anchor": "end", "class": "tick"}, f"{y_value:.3f}")

    element(svg, "line", {"x1": str(left), "y1": str(top + plot_height), "x2": str(left + plot_width), "y2": str(top + plot_height), "class": "axis"})
    element(svg, "line", {"x1": str(left), "y1": str(top), "x2": str(left), "y2": str(top + plot_height), "class": "axis"})
    element(svg, "text", {"x": str(left + plot_width / 2), "y": str(top + plot_height + 42), "text-anchor": "middle", "class": "axis-label"}, x_label)
    element(svg, "text", {"x": str(x + 16), "y": str(top + plot_height / 2), "text-anchor": "middle", "class": "axis-label", "transform": f"rotate(-90 {x + 16} {top + plot_height / 2})"}, y_label)

    coordinates = []
    for point_x, point_y in points:
        mapped_x = left + (point_x - x_min) / (x_max - x_min) * plot_width
        mapped_y = top + (y_max - point_y) / (y_max - y_min) * plot_height
        coordinates.append((mapped_x, mapped_y))
    element(svg, "polyline", {"points": " ".join(f"{px:.1f},{py:.1f}" for px, py in coordinates), "class": "curve", "stroke": color})
    for point_x, point_y in coordinates:
        element(svg, "circle", {"cx": f"{point_x:.1f}", "cy": f"{point_y:.1f}", "r": "4", "fill": color})


def main() -> None:
    rows = load_rows()
    if len(rows) < 2:
        raise SystemExit("Need at least two completed angles to plot the polar.")

    svg = ET.Element(
        f"{{{SVG_NS}}}svg",
        {"viewBox": "0 0 1120 400", "role": "img", "aria-labelledby": "title description"},
    )
    element(svg, "title", {"id": "title"}, "NACA 0018 coefficient polar")
    element(svg, "desc", {"id": "description"}, "Lift and drag coefficients against incidence, and drag polar, averaged over the last 100 solver iterations.")
    element(svg, "rect", {"width": "1120", "height": "400", "fill": "#ffffff"})
    element(svg, "text", {"x": "560", "y": "385", "text-anchor": "middle", "class": "note"}, "Exploratory kOmegaSST RANS; Cd/Cl are averages over the final 100 iterations")
    style = ET.SubElement(svg, f"{{{SVG_NS}}}style")
    style.text = ".panel-title{font:600 16px sans-serif;fill:#253238}.axis-label{font:13px sans-serif;fill:#253238}.tick{font:10px sans-serif;fill:#65747b}.grid{stroke:#dbe2e4;stroke-width:1}.axis{stroke:#586970;stroke-width:1.2}.curve{fill:none;stroke-width:2.5;stroke-linejoin:round;stroke-linecap:round}.note{font:12px sans-serif;fill:#53636a}"

    ordered = sorted(rows, key=lambda row: row["alpha"])
    draw_panel(svg, "Lift vs incidence", "Incidence alpha (deg)", "Cl", [(row["alpha"], row["Cl"]) for row in ordered], 0, "#007f78")
    draw_panel(svg, "Drag vs incidence", "Incidence alpha (deg)", "Cd", [(row["alpha"], row["Cd"]) for row in ordered], 375, "#c24f28")
    draw_panel(svg, "Drag polar", "Cd", "Cl", [(row["Cd"], row["Cl"]) for row in ordered], 750, "#386cb0")

    ET.ElementTree(svg).write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {OUTPUT_FILE} with {len(rows)} completed angles.")


if __name__ == "__main__":
    main()