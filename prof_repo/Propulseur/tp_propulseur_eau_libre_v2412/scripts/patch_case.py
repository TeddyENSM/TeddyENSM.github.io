#!/usr/bin/env python3
"""
patch_case.py
-------------
Patche un cas propeller_mrf pour un point de fonctionnement (Va, RPM).

Utilise foamDictionary (natif OpenFOAM v2412) — syntaxe foam garantie.

Usage:
    python3 patch_case.py <case_dir> <Va_m_s> <RPM>

Exemple:
    python3 patch_case.py cases/propeller_mrf 2.5 1509
"""

import sys
import subprocess
import math
import os

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2412/etc/bashrc"


def foam_env():
    """Retourne les variables d'environnement OpenFOAM sans sourcer dans ce process."""
    result = subprocess.run(
        ["bash", "-c", f". {FOAM_BASHRC} 2>/dev/null; env"],
        capture_output=True, text=True
    )
    env = os.environ.copy()
    for line in result.stdout.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            env[k] = v
    return env


def foam_dict(case_dir, file_rel, entry, value, env):
    """Appelle foamDictionary pour modifier une entrée."""
    target = os.path.join(case_dir, file_rel)
    cmd = ["foamDictionary", "-entry", entry, "-set", str(value), target]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"[WARN] foamDictionary échec sur {file_rel}:{entry}")
        print(result.stderr.strip())
        return False
    print(f"[OK] {file_rel}  {entry} = {value}")
    return True


def patch(case_dir, Va, RPM):
    env = foam_env()
    omega = RPM * 2 * math.pi / 60   # rad/s
    n_rps = RPM / 60                  # tr/s
    D     = 0.254                     # m — diamètre hélice
    J     = Va / (n_rps * D) if n_rps > 0 else 0

    print(f"\n── Patch cas : {case_dir}")
    print(f"   Va = {Va} m/s  |  RPM = {RPM}  |  omega = {omega:.2f} rad/s  |  J = {J:.4f}\n")

    # 1. Vitesse d'avance dans 0.orig/U  (axe -Y dans ce cas)
    foam_dict(case_dir, "0.orig/U",
              "boundaryField/inlet/value",
              f"uniform (0 -{Va} 0)",
              env)

    # 2. omega dans constant/dynamicMeshDict
    foam_dict(case_dir, "constant/dynamicMeshDict",
              "omega",
              f"{omega:.4f}",
              env)

    # 3. Note dans controlDict pour traçabilité
    foam_dict(case_dir, "system/controlDict",
              "Va_ms",
              f"{Va}",
              env)
    foam_dict(case_dir, "system/controlDict",
              "RPM",
              f"{RPM}",
              env)

    return J, omega


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    case_dir = sys.argv[1]
    Va  = float(sys.argv[2])
    RPM = float(sys.argv[3])

    if not os.path.isdir(case_dir):
        print(f"[ERR] Dossier introuvable : {case_dir}")
        sys.exit(1)

    J, omega = patch(case_dir, Va, RPM)
    print(f"\n[OK] Patch terminé — J={J:.4f}  omega={omega:.2f} rad/s")
