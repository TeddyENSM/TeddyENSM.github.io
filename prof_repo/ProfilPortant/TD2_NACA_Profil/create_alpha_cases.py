#!/usr/bin/env python3
import math
import os
import shutil
from pathlib import Path

base_dir = Path("simpleFoam")
angles = [5, 15]

if not base_dir.exists():
    raise SystemExit(f"Base directory {base_dir} not found")

numeric_names = {str(i) for i in range(1, 10000)}

for angle in angles:
    target_dir = Path(f"simpleFoam_alpha{angle}")
    if target_dir.exists():
        print(f"Directory {target_dir} already exists; updating initial condition only")
    else:
        print(f"Creating {target_dir}")
        def ignore_func(dir, names):
            ignored = set()
            for name in names:
                if name == 'VTK' or name == 'postProcessing' or name == 'log.simpleFoam':
                    ignored.add(name)
                elif name.isdigit() and name != '0':
                    ignored.add(name)
            return ignored
        shutil.copytree(base_dir, target_dir, ignore=ignore_func)

    flow_velocity = (100.0 * math.cos(math.radians(angle)), 100.0 * math.sin(math.radians(angle)), 0.0)
    ic_file = target_dir / "0" / "include" / "initialConditions"
    if not ic_file.exists():
        raise SystemExit(f"Missing initialConditions file: {ic_file}")

    content = ic_file.read_text().splitlines()
    with ic_file.open("w") as f:
        for line in content:
            if line.strip().startswith("flowVelocity"):
                f.write(f"flowVelocity    ({flow_velocity[0]:.8f} {flow_velocity[1]:.8f} {flow_velocity[2]:.0f});   // [m/s] — vitesse loin du profil à {angle}°\n")
            else:
                f.write(f"{line}\n")
    print(f"Updated {ic_file} with angle {angle}°, flowVelocity={flow_velocity}")

print("Done.")
