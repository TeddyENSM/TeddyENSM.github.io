#!/usr/bin/env python3
"""
bilan_propulseur.py
-------------------
Lit les fichiers de post-traitement OpenFOAM du cas propeller_mrf
et produit :
  - bilan_convergence.png  : résidus U, p en fonction du temps
  - bilan_forces.png       : Kt, 10*Kq, etaO en fonction du temps
  - bilan_propulseur.txt   : tableau synthèse final
"""

import os
import csv
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")          # pas d'affichage — mode headless
import matplotlib.pyplot as plt

CASE_DIR = os.path.join(os.path.dirname(__file__), "..", "cases", "propeller_mrf")
OUT_DIR   = os.path.dirname(__file__)

# ---------------------------------------------------------------------------
# 1. Lecture du log pimpleFoam pour les résidus
# ---------------------------------------------------------------------------
LOG = os.path.join(CASE_DIR, "log.pimpleFoam")

times, res_Ux, res_Uy, res_Uz, res_p = [], [], [], [], []

with open(LOG) as f:
    t = None
    for line in f:
        if line.startswith("Time = "):
            try:
                t = float(line.split()[2])
            except ValueError:
                pass
        if t is None:
            continue
        if "Solving for Ux" in line:
            res_Ux.append((t, float(line.split("Initial residual = ")[1].split(",")[0])))
        if "Solving for Uy" in line:
            res_Uy.append((t, float(line.split("Initial residual = ")[1].split(",")[0])))
        if "Solving for Uz" in line:
            res_Uz.append((t, float(line.split("Initial residual = ")[1].split(",")[0])))
        if "Solving for p" in line and "GAMG" in line:
            res_p.append((t, float(line.split("Initial residual = ")[1].split(",")[0])))

def arr(lst):
    return np.array(lst) if lst else np.empty((0, 2))

rUx = arr(res_Ux); rUy = arr(res_Uy); rUz = arr(res_Uz); rp = arr(res_p)

# ---------------------------------------------------------------------------
# 2. Lecture des coefficients propulseur depuis propellerInfo
# ---------------------------------------------------------------------------
prop_files = sorted(glob.glob(
    os.path.join(CASE_DIR, "postProcessing", "propellerInfo1", "*", "propellerInfo.dat")
))

times_prop, J_arr, Kt_arr, Kq_arr, eta_arr = [], [], [], [], []

for pf in prop_files:
    with open(pf) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            cols = line.split()
            if len(cols) < 6:
                continue
            try:
                times_prop.append(float(cols[0]))
                J_arr.append(float(cols[1]))
                Kt_arr.append(float(cols[2]))
                Kq_arr.append(float(cols[3]))
                eta_arr.append(float(cols[4]))
            except ValueError:
                pass

# Si pas de propellerInfo.dat, lire depuis le log
if not times_prop:
    with open(LOG) as f:
        t = None
        for line in f:
            if line.startswith("Time = "):
                try:
                    t = float(line.split()[2])
                except ValueError:
                    pass
            if t is None:
                continue
            if "Advance coefficient, J" in line:
                J_arr.append(float(line.split(":")[1]))
                times_prop.append(t)
            if "Thrust coefficient, Kt" in line:
                Kt_arr.append(float(line.split(":")[1]))
            if "Torque coefficient, 10*Kq" in line:
                Kq_arr.append(float(line.split(":")[1]))
            if "Efficiency, etaO" in line:
                eta_arr.append(float(line.split(":")[1]))

times_prop = np.array(times_prop)

# ---------------------------------------------------------------------------
# 3. Figure 1 — Convergence des résidus
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
for r, label, color in [
    (rUx, "Ux", "tab:blue"),
    (rUy, "Uy", "tab:orange"),
    (rUz, "Uz", "tab:green"),
    (rp,  "p",  "tab:red"),
]:
    if r.shape[0] > 0:
        ax.semilogy(r[:, 0], r[:, 1], label=label, lw=0.8, color=color)

ax.set_xlabel("Temps [s]")
ax.set_ylabel("Résidu initial")
ax.set_title("Convergence — pimpleFoam (propeller)")
ax.legend()
ax.grid(True, which="both", ls="--", alpha=0.4)
fig.tight_layout()
out_conv = os.path.join(OUT_DIR, "bilan_convergence.png")
fig.savefig(out_conv, dpi=150)
plt.close(fig)
print(f"[OK] {out_conv}")

# ---------------------------------------------------------------------------
# 4. Figure 2 — Coefficients propulseur
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

def plot_coef(ax, t, y, label, color, unit=""):
    if len(t) == len(y) and len(t) > 0:
        ax.plot(t, y, lw=1.2, color=color)
    ax.set_ylabel(f"{label}{unit}")
    ax.grid(True, ls="--", alpha=0.4)
    ax.set_title(label)

plot_coef(axes[0], times_prop, Kt_arr,  "Kt (thrust coeff.)", "tab:blue")
plot_coef(axes[1], times_prop, Kq_arr,  "10·Kq (torque coeff.)", "tab:orange")
plot_coef(axes[2], times_prop, eta_arr, "ηO (efficiency)", "tab:green")

axes[-1].set_xlabel("Temps [s]")
fig.suptitle("Coefficients propulseur — eau libre", fontsize=13, fontweight="bold")
fig.tight_layout()
out_forces = os.path.join(OUT_DIR, "bilan_forces.png")
fig.savefig(out_forces, dpi=150)
plt.close(fig)
print(f"[OK] {out_forces}")

# ---------------------------------------------------------------------------
# 5a. Export CSV — courbe eau libre (une ligne par point de fonctionnement)
#
#   Structure cible (une ligne = un cas / un J) :
#     J ; Kt_moy ; 10Kq_moy ; etaO_moy ; Kt_final ; 10Kq_final ; etaO_final ; Va [m/s] ; n [tr/s] ; endTime [s]
#
#   Si le fichier existe déjà (run précédent), on AJOUTE une ligne.
#   → Compléter avec d'autres vitesses d'avance Va pour tracer la courbe complète.
# ---------------------------------------------------------------------------

out_csv_eau_libre = os.path.join(OUT_DIR, "courbe_eau_libre.csv")

def mean_zone(arr, frac=0.30):
    """Moyenne sur les derniers `frac` % du tableau (zone stabilisée)."""
    a = np.array(arr)
    if a.size == 0:
        return float("nan")
    n = max(1, int(len(a) * frac))
    return float(np.mean(a[-n:]))

# Lire le Va et n depuis le log pimpleFoam (propellerInfo)
Va_val = ""; n_val = ""; endTime_val = ""
with open(LOG) as f:
    for line in f:
        if "Reference velocity" in line:
            try: Va_val = f"{abs(float(line.split(':')[1])):.4f}"
            except: pass
        if "Revolutions per second" in line:
            try: n_val  = f"{float(line.split(':')[1]):.4f}"
            except: pass
        if line.startswith("Time = "):
            try: endTime_val = line.split()[2]
            except: pass

header = ["J [-]", "Kt_moy [-]", "10Kq_moy [-]", "etaO_moy [-]",
          "Kt_final [-]", "10Kq_final [-]", "etaO_final [-]",
          "Va [m/s]", "n [tr/s]", "endTime [s]"]

file_exists = os.path.isfile(out_csv_eau_libre)

with open(out_csv_eau_libre, "a", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f, delimiter=";")
    if not file_exists:
        writer.writerow(header)   # en-tête seulement à la première création

    if times_prop.size > 0:
        writer.writerow([
            f"{mean_zone(J_arr):.4f}",
            f"{mean_zone(Kt_arr):.4f}",
            f"{mean_zone(Kq_arr):.4f}",
            f"{mean_zone(eta_arr):.4f}",
            f"{Kt_arr[-1]:.4f}",
            f"{Kq_arr[-1]:.4f}",
            f"{eta_arr[-1]:.4f}",
            Va_val, n_val, endTime_val,
        ])
    else:
        writer.writerow(["non disponible"] + [""] * (len(header) - 1))

print(f"[OK] {out_csv_eau_libre}  (mode append — une ligne par point J)")

# ---------------------------------------------------------------------------
# 5b. Export CSV — résidus complets (diagnostic convergence / détection bug)
# ---------------------------------------------------------------------------

out_csv_resid = os.path.join(OUT_DIR, "residus_convergence.csv")
with open(out_csv_resid, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Temps [s]", "Residu_Ux", "Residu_Uy", "Residu_Uz", "Residu_p"])

    times_res = rUx[:, 0] if rUx.shape[0] > 0 else np.array([])

    def at(arr2d, t):
        if arr2d.shape[0] == 0:
            return ""
        idx = np.searchsorted(arr2d[:, 0], t)
        if idx < arr2d.shape[0] and abs(arr2d[idx, 0] - t) < 1e-10:
            return f"{arr2d[idx, 1]:.4e}"
        return ""

    for t in times_res:
        writer.writerow([f"{t:.6f}", at(rUx, t), at(rUy, t), at(rUz, t), at(rp, t)])

print(f"[OK] {out_csv_resid}")

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------

def mean_last(arr, n=20):
    """Moyenne sur les n dernières valeurs disponibles."""
    a = np.array(arr)
    if a.size == 0:
        return float("nan")
    return float(np.mean(a[-n:]))

rows_coef = [
    ["Paramètre", "Valeur finale", "Moyenne (20 derniers pas)", "Unité / Note"],
]

if times_prop.size > 0:
    rows_coef += [
        ["Temps simulé",       f"{times_prop[-1]:.4f} s",      "—",                                 "s"],
        ["J — Advance coeff.", f"{J_arr[-1]:.4f}",             f"{mean_last(J_arr):.4f}",           "sans dim."],
        ["Kt — Thrust coeff.", f"{Kt_arr[-1]:.4f}",            f"{mean_last(Kt_arr):.4f}",          "sans dim."],
        ["10·Kq — Torque",     f"{Kq_arr[-1]:.4f}",           f"{mean_last(Kq_arr):.4f}",          "sans dim."],
        ["ηO — Efficacité",    f"{eta_arr[-1]*100:.1f} %",     f"{mean_last(eta_arr)*100:.1f} %",   "eau libre"],
    ]
else:
    rows_coef += [["Coefficients propulseur", "non disponibles", "—", "—"]]

rows_resid = [
    ["Résidu", "Valeur finale", "Ordre de grandeur"],
]
for r, name in [(rUx, "Ux"), (rUy, "Uy"), (rUz, "Uz"), (rp, "p")]:
    if r.shape[0] > 0:
        v = r[-1, 1]
        rows_resid.append([name, f"{v:.3e}", "bon" if v < 1e-3 else "à surveiller"])

def make_table_fig(rows, title, col_colors, out_path):
    n_rows = len(rows)
    n_cols = len(rows[0])
    fig_h  = max(2.5, 0.45 * n_rows + 1.0)
    fig, ax = plt.subplots(figsize=(12, fig_h))
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)

    header   = rows[0]
    data     = rows[1:]
    tbl = ax.table(
        cellText=data,
        colLabels=header,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.6)

    # En-tête coloré
    for j in range(n_cols):
        tbl[0, j].set_facecolor(col_colors[j % len(col_colors)])
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    # Alternance de lignes
    for i in range(1, len(data) + 1):
        bg = "#f0f4ff" if i % 2 == 0 else "white"
        for j in range(n_cols):
            tbl[i, j].set_facecolor(bg)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {out_path}")

out_tab_coef  = os.path.join(OUT_DIR, "tableau_coefficients.png")
out_tab_resid = os.path.join(OUT_DIR, "tableau_residus.png")

make_table_fig(
    rows_coef,
    "TP Propulseur — Coefficients eau libre (pimpleFoam / AMI)",
    ["#1a5276", "#2471a3", "#2980b9", "#5dade2"],
    out_tab_coef,
)
make_table_fig(
    rows_resid,
    "TP Propulseur — Résidus finaux",
    ["#1e8449", "#27ae60"],
    out_tab_resid,
)

# ---------------------------------------------------------------------------
# 6. Tableau synthèse texte
# ---------------------------------------------------------------------------
out_txt = os.path.join(OUT_DIR, "bilan_propulseur.txt")
with open(out_txt, "w") as f:
    f.write("=" * 55 + "\n")
    f.write("  BILAN TP PROPULSEUR — OpenFOAM ESI v2412\n")
    f.write("=" * 55 + "\n\n")

    if times_prop.size > 0:
        last = -1
        f.write(f"  Temps final simule        : {times_prop[last]:.4f} s\n")
        f.write(f"  J  (advance coeff.)       : {J_arr[last]:.4f}  (moy: {mean_last(J_arr):.4f})\n")
        f.write(f"  Kt (thrust coeff.)        : {Kt_arr[last]:.4f}  (moy: {mean_last(Kt_arr):.4f})\n")
        f.write(f"  10*Kq (torque coeff.)     : {Kq_arr[last]:.4f}  (moy: {mean_last(Kq_arr):.4f})\n")
        f.write(f"  etaO (open-water eff.)    : {eta_arr[last]:.4f}  ({eta_arr[last]*100:.1f} %)\n")
    else:
        f.write("  Coefficients propulseur non disponibles.\n")

    f.write("\n  Residus finaux (derniere iteration) :\n")
    for r, name in [(rUx, "Ux"), (rUy, "Uy"), (rUz, "Uz"), (rp, "p")]:
        if r.shape[0] > 0:
            f.write(f"    {name:4s} : {r[-1, 1]:.3e}\n")

    f.write("\n  Fichiers exportes :\n")
    f.write("    - bilan_convergence.png\n")
    f.write("    - bilan_forces.png\n")
    f.write("    - tableau_coefficients.png\n")
    f.write("    - tableau_residus.png\n")
    f.write("    - courbe_eau_libre.csv        (1 ligne/point J — append auto, Excel/Calc)\n")
    f.write("    - residus_convergence.csv     (residus complets, diagnostic bug)\n")
    f.write("=" * 55 + "\n")

print(f"[OK] {out_txt}")
with open(out_txt) as f:
    print(f.read())
