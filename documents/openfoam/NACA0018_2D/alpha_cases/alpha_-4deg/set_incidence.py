#!/usr/bin/env python3
"""Write the inlet velocity for a requested angle of attack."""

import math
from pathlib import Path
import sys


CASE_DIR = Path(__file__).resolve().parent
SPEED = 2.06


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 set_incidence.py ANGLE_DEGREES")

    try:
        angle_degrees = float(sys.argv[1])
    except ValueError as error:
        raise SystemExit("Angle must be a number in degrees") from error
    if not math.isfinite(angle_degrees):
        raise SystemExit("Angle must be finite")

    angle_radians = math.radians(angle_degrees)
    velocity_x = SPEED * math.cos(angle_radians)
    velocity_y = SPEED * math.sin(angle_radians)

    initial_dir = CASE_DIR / "0"
    initial_dir.mkdir(exist_ok=True)
    velocity_file = initial_dir / "U"
    velocity_file.write_text(
        f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform ({velocity_x:.10g} {velocity_y:.10g} 0);
    }}
    outlet
    {{
        type            zeroGradient;
    }}
    profile
    {{
        type            noSlip;
    }}
    top
    {{
        type            slip;
    }}
    bottom
    {{
        type            slip;
    }}
    frontAndBack
    {{
        type            empty;
    }}
}}
""",
        encoding="ascii",
    )
    print(
        f"alpha={angle_degrees:g} deg: Uin=({velocity_x:.6f}, "
        f"{velocity_y:.6f}, 0) m/s; wrote {velocity_file}"
    )


if __name__ == "__main__":
    main()