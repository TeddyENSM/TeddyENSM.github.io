#!/usr/bin/env python3
"""
Post-traitement TD1 Poiseuille.
Compare le profil numérique OpenFOAM à la solution analytique.
Usage : python3 postProcess_Poiseuille.py [répertoire_temps]
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# --- Paramètres physiques ---
nu   = 1e-6    # viscosité cinématique [m²/s]
H    = 0.01    # hauteur canal [m]
L    = 0.1     # longueur canal [m]
dpdx = -0.1   # gradient de pression [Pa/m]

# --- Solution analytique ---
y_ana = np.linspace(0, H, 500)
u_ana = -1.0 / (2 * nu) * dpdx * (H * y_ana - y_ana**2)
u_max_ana = -dpdx * H**2 / (8 * nu)
u_moy_ana = -dpdx * H**2 / (12 * nu)
Re = u_moy_ana * H / nu

print(f"Solution analytique :")
print(f"  u_max  = {u_max_ana:.5f} m/s")
print(f"  u_moy  = {u_moy_ana:.5f} m/s")
print(f"  Re     = {Re:.1f}")

# --- Lecture du profil numérique (export ParaView CSV) ---
# Exporter dans ParaView : Filters > Plot Over Line → Save Data → profil_Ux.csv
csv_file = "profil_Ux.csv"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Analytique (toujours tracé)
ax1.plot(u_ana, y_ana * 1000, "k-", linewidth=2, label="Analytique")

if os.path.isfile(csv_file):
    data = np.genfromtxt(csv_file, delimiter=",", names=True)
    # ParaView exporte : arc_length, U:0, U:1, U:2, ...
    # Les noms exacts dépendent de la version — adapter si nécessaire
    col_y = "Points1" if "Points1" in data.dtype.names else "arc_length"
    col_u = "U0"      if "U0"      in data.dtype.names else "U_0"
    try:
        y_num = data[col_y]
        u_num = data[col_u]
        ax1.plot(u_num, y_num * 1000, "ro--", markersize=4, label="OpenFOAM")
        # Erreur L2
        u_ref = np.interp(y_num, y_ana, u_ana)
        err_L2 = np.sqrt(np.mean((u_num - u_ref)**2)) / u_max_ana
        print(f"\nErreur L2 relative : {err_L2:.4f} ({err_L2*100:.2f} %)")
        ax2.semilogy(y_num * 1000, np.abs(u_num - u_ref) / u_max_ana, "b-")
        ax2.set_xlabel("y [mm]")
        ax2.set_ylabel("|erreur| / u_max [-]")
        ax2.set_title("Erreur locale relative")
        ax2.grid(True)
    except Exception as e:
        print(f"Attention : impossible de lire les colonnes ({e})")
else:
    print(f"\nFichier '{csv_file}' introuvable.")
    print("Exporter depuis ParaView (Plot Over Line, Save Data) puis relancer.")
    ax2.text(0.5, 0.5, "Données numériques\nnon disponibles",
             ha="center", va="center", transform=ax2.transAxes, fontsize=12)

ax1.set_xlabel("$U_x$ [m/s]")
ax1.set_ylabel("y [mm]")
ax1.set_title("Profil de vitesse — Poiseuille plan")
ax1.legend()
ax1.grid(True)

plt.tight_layout()
plt.savefig("profil_Poiseuille.png", dpi=150)
plt.show()
print("Figure sauvegardée : profil_Poiseuille.png")
