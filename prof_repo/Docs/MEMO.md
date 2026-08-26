# MEMO — PerfNav (OpenFOAM v2412 ESI, WSL2)

> Généré le 2026-05-25. Source : Archives/07_Dossier.zip + Archives/14_Dossier.zip + Archives/assignment-geometry.zip.

---

## Structure

```
PerfNav/
├── Archives/                    ← sources originales (zips Navalapp)
├── Docs/                        ← COURS_PerfNav.md, AUDIT_COURS.md, PDFs 01–20
│   ├── MEMO.md                  ← ce fichier
│   ├── PostTraitement_ParaView.md
│   └── README_installation.md
├── Fondamentaux/                ← Ch1–5 COURS : CFD intro + Poiseuille
│   └── TD1_Poiseuille/
├── ProfilPortant/               ← Ch6–11 COURS : profils NACA 2D (PYD5 Ch6)
│   ├── TD2_NACA_Profil/
│   └── Devoir_Final/
├── Hull_Design/                 ← Ch12–18 COURS : voilier 3D (PYD5 Ch5)
│   └── TD3_Voilier/
└── Propulseur/                  ← Ch10 PYD5 : TP propulseur eau libre
    ├── Tp_propulseur_eau_libre.md
    ├── master_setup_propulseur_v2412.sh
    └── tp_propulseur_eau_libre_v2412/
```

---

## TD1 — Poiseuille (icoFoam)

**Répertoire :** `../Fondamentaux/TD1_Poiseuille/`

| Paramètre | Valeur |
|-----------|--------|
| Fluide | eau, ν = 1e-6 m²/s |
| Domaine | L=0.1 m × H=0.01 m × e=0.001 m |
| Vitesse cible | Ūbar = 0.04167 m/s (via `fvOptions/meanVelocityForce`) |
| Solveur | icoFoam, endTime=10 s |

**Lancer :** `./Allrun`  
**Nettoyer :** `./Allclean`  
**Post-traitement :** `python3 postProcess_Poiseuille.py` (après export ParaView CSV)

**Fichiers cas :** 0/U, 0/p, constant/transportProperties, system/{blockMeshDict, controlDict, fvSchemes, fvSolution, fvOptions}

---

## TD2 — Profil NACA-0012 (simpleFoam + pimpleFoam)

**Répertoire :** `../ProfilPortant/TD2_NACA_Profil/`

| Paramètre | Valeur |
|-----------|--------|
| Géométrie | geometry/NACA0012.stl (c=1 m) |
| Fluide | air, ν = 1.5e-5 m²/s, ρ = 1.225 kg/m³ |
| Vitesse | U∞ = 100 m/s, Re = 6.67×10⁶ |
| Turbulence | k-ω SST, y⁺ ≈ 50 (firstLayerThickness = 0.0015 m) |
| Solveur stationnaire | simpleFoam, endTime=4000 |
| Solveur instationnaire | pimpleFoam, endTime=5 s, maxCo=0.9 |

**Pipeline complet :** `./Allrun` (blockMesh → surfaceFeatureExtract → snappyHexMesh → extrudeMesh → createPatch → simpleFoam → pimpleFoam MPI×4)

**Adaptation v2412 :**
- `libs (forces);` — sans guillemets ni `.so`
- `turbulenceProperties` — nom ESI (pas `momentumTransport`)
- `div((nuEff*dev2(T(grad(U))))) Gauss linear` — schéma correct v2412

**Sous-cas :**

| Répertoire | Contenu clé |
|---|---|
| `snappyHexMesh/` | blockMeshDict (100×40×1), snappyHexMeshDict (nCellsBetweenLevels 4, 3 couches), extrudeMeshDict, createPatchDict |
| `simpleFoam/0.orig/` | U, p, k, omega, nut + include/initialConditions + include/frontBackTopBottomPatches |
| `simpleFoam/system/` | controlDict (`#include "forces"`), forces (forceCoeffs), fvSchemes, fvSolution (GAMG+SIMPLE), decomposeParDict |
| `pimpleFoam/0.orig/` | U, p, k, omega, nut (toutes BC explicites, pas d'include) |
| `pimpleFoam/system/` | controlDict (adjustTimeStep, maxCo=0.9), fvSchemes (linearUpwind), fvSolution (PIMPLE nOuter=2), decomposeParDict |

---

## TD3 — Voilier 17 m (interFoam + rigidBodyMotion)

**Répertoire :** `../Hull_Design/TD3_Voilier/`

| Paramètre | Valeur |
|-----------|--------|
| Géométrie | constant/triSurface/Carena.stl |
| Fluide | eau ρ=1025 kg/m³, ν=1.0034e-6 m²/s / air ρ=1.225, ν=1.48e-5 |
| Vitesse | U = 3.874 m/s (Fr ≈ 0.30) |
| DDL libres | heave (Pz) + pitch (Ry) via rigidBodyMotion |
| Solveur | interFoam, endTime=100 s, maxCo=10, maxAlphaCo=5 |
| Parallèle | scotch, 4 cœurs |

**Lancer :** `./Allrun` (blockMesh → surfaceFeatureExtract → snappyHexMesh → setFields → decomposePar → interFoam MPI×4 → reconstructPar → filterForces.py)

**Adaptation v2412 :**
- `libs (forces);` — correction vs Archives/14_Dossier qui utilisait `libs ("libforces.so")`
- `turbulenceProperties` — nom ESI
- format force.dat sans parenthèses : col 0=t, 1=Ftx, 4=Fpx, 7=Fvx
- `fluxRequired` supprimé (déprécié v2412)

**Fichiers clés :**

| Fichier | Rôle |
|---|---|
| `system/initialConditions` | Paramètres géométriques via `#calc` (Lpp, Bwl, T, domaine, boîtes SHM) |
| `constant/dynamicMeshDict` | rigidBodyMotion, accelerationRelaxation 0→10s figé, amortisseurs heave+pitch |
| `constant/g` | Gravité (0 0 -9.81) — **critique pour interFoam** |
| `system/setFieldsDict` | alpha.water=1 pour z<0 (eau), 0 sinon |
| `filterForces.py` | Butterworth ordre 2, coupure 0.1 Hz, lit cols 0/1/4/7 |
| `Gnuplot_script.txt` | Tracé Rtotal/Rpression/Rvisqueux sur [0,100]s |

---

## Propulseur — Eau libre (pimpleFoam)

**Répertoire :** `../Propulseur/tp_propulseur_eau_libre_v2412/`

TP propulseur eau libre v2412. Voir `../Propulseur/Tp_propulseur_eau_libre.md` pour la mise en œuvre et `master_setup_propulseur_v2412.sh` pour le pipeline automatisé.

---

## Devoir Final

**Répertoire :** `../ProfilPortant/Devoir_Final/`

5 questions théoriques (méthodes num., théorie profils, maillage, résistance navire, V&V) + 3 exercices numériques :
- **B1** : NACA-0012 à α=4° (simpleFoam, CL/CD, GCI)
- **B2** : Polaire aérodynamique α ∈ {0°,2°,4°,6°,8°}
- **B3** : Distribution Cp, épaisseur couche limite, bilan forces

Géométrie : `../ProfilPortant/Devoir_Final/geometry/NACA0012.stl` (copier le cas depuis `../ProfilPortant/TD2_NACA_Profil/`)

---

## Corrections v2412 ESI appliquées (vs fichiers Archives/)

| Point | Archives/ (ancien) | v2412 corrigé |
|---|---|---|
| Bibliothèque forces | `libs ("libforces.so");` | `libs (forces);` |
| Propriétés turbulence | — | `turbulenceProperties` (pas `momentumTransport`) |
| format force.dat | avec parenthèses | sans parenthèses |
| `fluxRequired` | présent | supprimé |
| typo omega | `value uniform 200vvvvvvvv` | `value uniform 200` |
| Gravité interFoam | dans controlDict parent | `constant/g` dédié |

---

## Géométries

| Fichier | Source | Taille |
|---|---|---|
| `../ProfilPortant/TD2_NACA_Profil/geometry/NACA0012.stl` | Archives/assignment-geometry.zip | 191 Ko |
| `../ProfilPortant/Devoir_Final/geometry/NACA0012.stl` | idem | 191 Ko |
| `../Hull_Design/TD3_Voilier/constant/triSurface/Carena.stl` | Archives/14_Dossier/sailingHull-geometry.zip | 582 Ko |

**Post-traitement ParaView :** voir [`PostTraitement_ParaView.md`](PostTraitement_ParaView.md)
