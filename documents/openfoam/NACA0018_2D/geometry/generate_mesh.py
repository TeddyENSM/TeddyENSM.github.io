#!/usr/bin/env python3
"""Generate an exploratory 2D NACA 0018 mesh with Gmsh."""

from pathlib import Path
import os
import shutil
import subprocess


HERE = Path(__file__).resolve().parent
COORDINATES = HERE / "naca0018_50mm.dat"
GEO_FILE = HERE / "naca0018_2d.geo"
MESH_FILE = HERE / "naca0018_2d.msh"

X_MIN = -0.50
X_MAX = 1.05
Y_MIN = -0.50
Y_MAX = 0.50
SPAN = 0.001
PROFILE_SIZE = 0.0005
FAR_SIZE = 0.012
FIRST_LAYER = 1.0e-5
LAYER_THICKNESS = 1.5e-3
LAYER_GROWTH = 1.2


def read_profile():
    rows = COORDINATES.read_text(encoding="ascii").splitlines()[1:]
    points = [tuple(map(float, row.split())) for row in rows if row.strip()]
    if len(points) < 4 or points[0] != points[-1]:
        raise ValueError(f"Expected a closed contour in {COORDINATES}")
    return points[:-1]


def write_geo(points):
    geo = [
        'SetFactory("Built-in");',
        "Mesh.MshFileVersion = 2.2;",
        "Mesh.Binary = 0;",
        "Mesh.MeshSizeFromPoints = 1;",
        "Mesh.MeshSizeFromCurvature = 0;",
        "Mesh.MeshSizeExtendFromBoundary = 0;",
        "Mesh.MeshSizeMin = 0.0003;",
        f"Mesh.MeshSizeMax = {FAR_SIZE};",
        "Mesh.Algorithm = 6;",
        "Mesh.Optimize = 1;",
        "Mesh.OptimizeNetgen = 1;",
        f"Point(1) = {{{X_MIN}, {Y_MIN}, 0, {FAR_SIZE}}};",
        f"Point(2) = {{{X_MAX}, {Y_MIN}, 0, {FAR_SIZE}}};",
        f"Point(3) = {{{X_MAX}, {Y_MAX}, 0, {FAR_SIZE}}};",
        f"Point(4) = {{{X_MIN}, {Y_MAX}, 0, {FAR_SIZE}}};",
        "Line(1) = {4, 1};",
        "Line(2) = {1, 2};",
        "Line(3) = {2, 3};",
        "Line(4) = {3, 4};",
        "Curve Loop(1) = {1, 2, 3, 4};",
    ]

    point_ids = []
    for index, (x, y) in enumerate(points):
        point_id = 5 + index
        point_ids.append(point_id)
        geo.append(f"Point({point_id}) = {{{x:.12g}, {y:.12g}, 0, {PROFILE_SIZE}}};")

    profile_curve_ids = []
    first_curve_id = 5
    for index, point_id in enumerate(point_ids):
        curve_id = first_curve_id + index
        next_point_id = point_ids[(index + 1) % len(point_ids)]
        profile_curve_ids.append(curve_id)
        geo.append(f"Line({curve_id}) = {{{point_id}, {next_point_id}}};")

    geo.extend(
        [
            "Curve Loop(2) = {" + ", ".join(map(str, profile_curve_ids)) + "};",
            "Plane Surface(1) = {1, 2};",
            "out[] = Extrude {0, 0, " + str(SPAN) + "} {",
            "  Surface{1};",
            "  Layers{1};",
            "  Recombine;",
            "};",
            'Physical Volume("fluid", 1) = {out[1]};',
            'Physical Surface("frontAndBack", 2) = {1, out[0]};',
            'Physical Surface("inlet", 3) = {out[2]};',
            'Physical Surface("bottom", 4) = {out[3]};',
            'Physical Surface("outlet", 5) = {out[4]};',
            'Physical Surface("top", 6) = {out[5]};',
            'Physical Surface("profile", 7) = {'
            + ", ".join(f"out[{6 + index}]" for index in range(len(profile_curve_ids)))
            + "};",
            "Field[1] = BoundaryLayer;",
            "Field[1].CurvesList = {"
            + ", ".join(map(str, profile_curve_ids))
            + "};",
            f"Field[1].hwall_n = {FIRST_LAYER};",
            f"Field[1].thickness = {LAYER_THICKNESS};",
            f"Field[1].ratio = {LAYER_GROWTH};",
            "Field[1].Quads = 1;",
            "BoundaryLayer Field = 1;",
            "Field[2] = Distance;",
            "Field[2].CurvesList = {"
            + ", ".join(map(str, profile_curve_ids))
            + "};",
            "Field[2].Sampling = 200;",
            "Field[3] = Threshold;",
            "Field[3].InField = 2;",
            "Field[3].SizeMin = " + str(PROFILE_SIZE) + ";",
            "Field[3].SizeMax = " + str(FAR_SIZE) + ";",
            "Field[3].DistMin = 0.01;",
            "Field[3].DistMax = 0.15;",
            "Field[4] = Box;",
            "Field[4].VIn = 0.0015;",
            f"Field[4].VOut = {FAR_SIZE};",
            "Field[4].XMin = -0.05;",
            "Field[4].XMax = 0.55;",
            "Field[4].YMin = -0.075;",
            "Field[4].YMax = 0.075;",
            "Field[4].ZMin = -0.001;",
            "Field[4].ZMax = 0.002;",
            "Field[5] = Box;",
            "Field[5].VIn = 0.0002;",
            f"Field[5].VOut = {FAR_SIZE};",
            "Field[5].XMin = 0.045;",
            "Field[5].XMax = 0.065;",
            "Field[5].YMin = -0.006;",
            "Field[5].YMax = 0.006;",
            "Field[5].ZMin = -0.001;",
            "Field[5].ZMax = 0.002;",
            "Field[6] = Min;",
            "Field[6].FieldsList = {3, 4, 5};",
            "Background Field = 6;",
        ]
    )
    GEO_FILE.write_text("\n".join(geo) + "\n", encoding="ascii")


def main():
    points = read_profile()
    write_geo(points)
    gmsh_command = os.environ.get("GMSH_BIN", "gmsh")
    if not shutil.which(gmsh_command):
        raise SystemExit(
            f"Gmsh introuvable ({gmsh_command}). Installe Gmsh ou utilise le maillage MSH2 existant."
        )
    subprocess.run(
        [gmsh_command, str(GEO_FILE), "-v", "2", "-3", "-format", "msh2", "-o", str(MESH_FILE)],
        check=True,
        cwd=HERE,
    )
    print(f"Generated {MESH_FILE}")


if __name__ == "__main__":
    main()