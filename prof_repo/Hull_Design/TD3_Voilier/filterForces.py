#!/usr/bin/env python3
"""
Filtre passe-bas Butterworth sur les forces interFoam.
Format force.dat v2412 ESI (sans parenthèses) :
  col 0 : temps
  col 1 : Ftx (force totale x)
  col 4 : Fpx (force de pression x)
  col 7 : Fvx (force visqueuse x)

Usage : python3 filterForces.py [chemin_force.dat]
"""

import numpy as np
from scipy.signal import butter, filtfilt
import sys
import os

# --- Paramètres ---
cutoff_hz   = 0.1    # fréquence de coupure [Hz]
order       = 2      # ordre du filtre Butterworth

# --- Fichier d'entrée ---
force_file = "postProcessing/forces/0/force.dat"
if len(sys.argv) > 1:
    force_file = sys.argv[1]

if not os.path.isfile(force_file):
    print(f"Erreur : fichier introuvable : {force_file}")
    sys.exit(1)

# --- Lecture ---
times, Ft, Fp, Fv = [], [], [], []
with open(force_file) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        try:
            times.append(float(parts[0]))
            Ft.append(float(parts[1]))
            Fp.append(float(parts[4]))
            Fv.append(float(parts[7]))
        except ValueError:
            continue

times = np.array(times)
Ft    = np.array(Ft)
Fp    = np.array(Fp)
Fv    = np.array(Fv)

if len(times) < 10:
    print("Pas assez de données pour filtrer.")
    sys.exit(1)

# --- Fréquence d'échantillonnage (supposée uniforme) ---
dt = np.mean(np.diff(times))
fs = 1.0 / dt
wn = cutoff_hz / (fs / 2)   # fréquence normalisée ∈ ]0,1[

if wn >= 1:
    print(f"Attention : fréquence de coupure ({cutoff_hz} Hz) ≥ Nyquist ({fs/2:.3f} Hz). Réduire cutoff_hz.")
    wn = 0.99

b, a = butter(order, wn, btype="low")
Ft_f = filtfilt(b, a, Ft)
Fp_f = filtfilt(b, a, Fp)
Fv_f = filtfilt(b, a, Fv)

# --- Écriture ---
out_file = "filteredF.dat"
with open(out_file, "w") as f:
    f.write("# t  Ftotal_x  Fpression_x  Fvisqueux_x\n")
    for i in range(len(times)):
        f.write(f"{times[i]:.6f}  {Ft_f[i]:.6f}  {Fp_f[i]:.6f}  {Fv_f[i]:.6f}\n")

print(f"Fichier filtré écrit : {out_file}")
print(f"  Période couverte : {times[0]:.1f} → {times[-1]:.1f} s")
print(f"  Résistance totale moyenne (t>60s) : {np.mean(Ft_f[times>60]):.1f} N")
print(f"  Résistance pression   (t>60s) : {np.mean(Fp_f[times>60]):.1f} N")
print(f"  Résistance visqueuse  (t>60s) : {np.mean(Fv_f[times>60]):.1f} N")
