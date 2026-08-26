#!/usr/bin/env python3
"""
Post-processing script for transient pimpleFoam force coefficients.
Compares transient (pimpleFoam) vs steady (simpleFoam) aerodynamic coefficients.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Data file paths
pimple_forces_file = Path("pimpleFoam/postProcessing/forceCoeffs/0/coefficient.dat")
simple_forces_file = Path("simpleFoam/postProcessing/forceCoeffs/0/coefficient.dat")

def parse_openfoam_forces(filepath):
    """Parse OpenFOAM forceCoeffs output file (removes formatting breaks)."""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Split by spaces and convert to float
            try:
                parts = line.split()
                # Reconstruct valid numbers (handles broken lines from formatting)
                values = []
                i = 0
                while i < len(parts):
                    try:
                        val = float(parts[i])
                        values.append(val)
                        i += 1
                    except ValueError:
                        # Skip non-numeric parts
                        i += 1
                if len(values) >= 11:  # Time + 10 force coefficients
                    data.append(values)
            except:
                continue
    
    if not data:
        return None, None, None, None, None
    
    data = np.array(data)
    time = data[:, 0]
    cd = data[:, 1]  # Cd
    cl = data[:, 3]  # Cl (assuming standard column layout)
    
    return time, cd, cl, data

# Load data
print("Loading transient (pimpleFoam) forces...")
time_trans, cd_trans, cl_trans, data_trans = parse_openfoam_forces(pimple_forces_file)

print(f"Transient simulation: {len(time_trans)} time steps")
print(f"Time range: {time_trans[0]:.6f} - {time_trans[-1]:.6f} seconds")
print(f"Transient CL range: [{cl_trans.min():.6f}, {cl_trans.max():.6f}]")
print(f"Transient CD range: [{cd_trans.min():.6f}, {cd_trans.max():.6f}]")

# Create plots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Transient CL
axes[0, 0].plot(time_trans, cl_trans, 'b-', linewidth=1.5, label='pimpleFoam (transient)')
axes[0, 0].axhline(y=0.4566, color='r', linestyle='--', label='simpleFoam steady (α=0°)')
axes[0, 0].set_xlabel('Time (s)')
axes[0, 0].set_ylabel('Lift Coefficient Cl')
axes[0, 0].set_title('Transient Lift Coefficient Evolution')
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].legend()

# Plot 2: Transient CD
axes[0, 1].plot(time_trans, cd_trans, 'b-', linewidth=1.5, label='pimpleFoam (transient)')
axes[0, 1].axhline(y=0.0123, color='r', linestyle='--', label='simpleFoam steady (α=0°)')
axes[0, 1].set_xlabel('Time (s)')
axes[0, 1].set_ylabel('Drag Coefficient Cd')
axes[0, 1].set_title('Transient Drag Coefficient Evolution')
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].legend()

# Plot 3: CL vs CD (polar diagram)
axes[1, 0].plot(cd_trans, cl_trans, 'b-', linewidth=1.5, label='pimpleFoam trajectory')
axes[1, 0].plot(0.0123, 0.4566, 'rs', markersize=10, label='simpleFoam (0°)')
axes[1, 0].set_xlabel('Drag Coefficient Cd')
axes[1, 0].set_ylabel('Lift Coefficient Cl')
axes[1, 0].set_title('Aerodynamic Polar (transient trajectory)')
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].legend()

# Plot 4: Statistics
axes[1, 1].axis('off')
stats_text = f"""
Transient Statistics (pimpleFoam):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Time range: {time_trans[0]:.6f} → {time_trans[-1]:.6f} s
Duration: {time_trans[-1] - time_trans[0]:.6f} s
Samples: {len(time_trans)}

Lift Coefficient Cl:
  Min: {cl_trans.min():.6f}
  Max: {cl_trans.max():.6f}
  Mean: {cl_trans.mean():.6f}
  Std: {cl_trans.std():.6f}

Drag Coefficient Cd:
  Min: {cd_trans.min():.6f}
  Max: {cd_trans.max():.6f}
  Mean: {cd_trans.mean():.6f}
  Std: {cd_trans.std():.6f}

Steady-state reference (simpleFoam α=0°):
  Cl: 0.4566  |  Cd: 0.0123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
axes[1, 1].text(0.1, 0.5, stats_text, fontfamily='monospace', fontsize=10,
                verticalalignment='center', transform=axes[1, 1].transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('transient_analysis.png', dpi=150, bbox_inches='tight')
print("\n✓ Plot saved to: transient_analysis.png")

# Save summary statistics
with open('transient_summary.txt', 'w') as f:
    f.write(stats_text)
    f.write(f"\nFirst 5 timesteps (time, Cd, Cl):\n")
    for i in range(min(5, len(time_trans))):
        f.write(f"  {time_trans[i]:.8f}  {cd_trans[i]:.8f}  {cl_trans[i]:.8f}\n")
    f.write(f"\nLast 5 timesteps (time, Cd, Cl):\n")
    for i in range(max(0, len(time_trans)-5), len(time_trans)):
        f.write(f"  {time_trans[i]:.8f}  {cd_trans[i]:.8f}  {cl_trans[i]:.8f}\n")

print("✓ Summary saved to: transient_summary.txt")
print("\nAnalysis complete!")
