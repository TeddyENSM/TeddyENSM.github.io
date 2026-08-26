#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

CASE_FILES = {
    '0°': Path('simpleFoam/postProcessing/forceCoeffs/0/coefficient.dat'),
    '10°': Path('simpleFoam_alpha10/postProcessing/forceCoeffs/0/coefficient.dat'),
}

EXPECTED_COLS = 13


def parse_force_coeffs(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing coefficient file: {path}")

    values = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            for token in line.split():
                try:
                    values.append(float(token))
                except ValueError:
                    continue

    if len(values) % EXPECTED_COLS != 0:
        raise ValueError(
            f"Unexpected number of numeric values in {path}: {len(values)} (expected multiple of {EXPECTED_COLS})"
        )

    data = np.array(values).reshape(-1, EXPECTED_COLS)
    time = data[:, 0]
    cd = data[:, 1]
    cl = data[:, 4]
    return time, cd, cl


def load_case_values():
    points = []
    for angle, filepath in CASE_FILES.items():
        time, cd, cl = parse_force_coeffs(filepath)
        points.append({
            'angle': angle,
            'cd': cd[-1],
            'cl': cl[-1],
            'time': time[-1],
        })
    return points


def plot_polar(points):
    angles = [p['angle'] for p in points]
    cds = [p['cd'] for p in points]
    cls = [p['cl'] for p in points]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(cds, cls, '-o', color='navy', linewidth=2, markersize=8)
    for angle, x, y in zip(angles, cds, cls):
        ax.annotate(angle, (x, y), xytext=(5, 5), textcoords='offset points', fontsize=10)

    ax.set_xlabel('Drag coefficient $C_D$')
    ax.set_ylabel('Lift coefficient $C_L$')
    ax.set_title('Polar $C_L$ vs $C_D$ for NACA-0012')
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    plt.tight_layout()
    out_file = Path('polar_0_10.png')
    plt.savefig(out_file, dpi=150, bbox_inches='tight')
    print(f"Saved polar plot to: {out_file}")
    return out_file


def save_summary(points, path):
    with open(path, 'w') as f:
        f.write('Angle, Cd, Cl, last_time\n')
        for p in points:
            f.write(f"{p['angle']}, {p['cd']:.8f}, {p['cl']:.8f}, {p['time']:.6f}\n")
    print(f"Saved summary to: {path}")


if __name__ == '__main__':
    points = load_case_values()
    out_image = plot_polar(points)
    save_summary(points, Path('polar_0_10_summary.csv'))
    print('\nComputed points:')
    for p in points:
        print(f"{p['angle']}: Cd = {p['cd']:.8f}, Cl = {p['cl']:.8f}")
