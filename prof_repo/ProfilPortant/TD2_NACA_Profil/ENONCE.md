# TD2 — Profil NACA-0012 : maillage et simulation (simpleFoam / pimpleFoam)

**OpenFOAM v2412 ESI — WSL2**

---

## Objectifs

- Créer un maillage 2D de qualité avec **snappyHexMesh** + **extrudeMesh** + **createPatch**
- Simuler l'aérodynamique d'un profil NACA-0012 en régime turbulent avec **simpleFoam** (RANS k-ω SST)
- Simuler un cas instationnaire avec **pimpleFoam** (décrochage)
- Calculer les coefficients de portance $C_L$ et de traînée $C_D$

---

## 1. Géométrie

Le profil NACA-0012 est fourni dans `geometry/NACA0012.stl`.

Caractéristiques :
- Corde $c = 1$ m
- Envergure simulée : 1 cellule de 0.25 m (extrudé par `extrudeMesh`)
- Incidence $\alpha = 0°$ (sauf indication contraire)
- Vitesse d'entrée $U_\infty = 100$ m/s (air, $\nu = 1.5 \times 10^{-5}$ m²/s)
- $Re = U_\infty c / \nu = 6.67 \times 10^6$

**Question 1** — Calculer $y^+$ cible pour une simulation avec fonctions de paroi ($y^+ \approx 50$). En déduire l'épaisseur de la première couche $\Delta y_1$.

*Rappel :* $y^+ = u_\tau \Delta y_1 / \nu$ avec $u_\tau = U_\infty \sqrt{C_f/2}$ et $C_f \approx 0.027 Re^{-1/7}$.

---

## 2. Maillage de fond (blockMesh)

Le domaine est une boîte rectangulaire $[-2.5, 3.5] \times [-2, 2] \times [-0.125, 0.125]$ (en mètres).

```bash
cd snappyHexMesh
blockMesh
```

**Question 2** — Identifier dans `snappyHexMesh/system/blockMeshDict` :
- La résolution de fond ($\Delta x$, $\Delta y$)
- Les patches `inlet`, `outlet`, `top`, `bottom`, `symFront`, `symBack`

---

## 3. Maillage snappyHexMesh

```bash
surfaceFeatureExtract
snappyHexMesh -overwrite
```

Examiner les paramètres clés dans `snappyHexMesh/system/snappyHexMeshDict` :
- Niveau de raffinement de surface : `(5 5)`
- `nCellsBetweenLevels 4` — contrôle la transition entre niveaux
- Boîte de raffinement $[-2, -1, -1]$ à $[4, 1, 1]$, niveau 2
- Couches : 3 couches, `firstLayerThickness 0.0015`, `relativeSizes false`

**Question 3** — Pourquoi `nCellsBetweenLevels` est-il un paramètre critique pour la qualité du maillage ?

---

## 4. Extrusion 2D

```bash
extrudeMesh
createPatch -overwrite
```

Ces commandes transforment la tranche 3D en un vrai cas 2D avec patches `empty`.

---

## 5. Simulation RANS stationnaire (simpleFoam)

```bash
cd ../simpleFoam
restore0Dir
simpleFoam 2>&1 | tee log.simpleFoam
```

Surveiller la convergence des résidus :

```bash
foamMonitor -f postProcessing/residuals/0/residuals.dat &
```

### Paramètres turbulents initiaux

Dans `0.orig/include/initialConditions` :

```
flowVelocity   (100 0 0);
pressure       0;
turbulentKE    37;       // k = 1.5*(I*U)² avec I=0.01
turbulentOmega 32;       // ω = k^0.5 / (Cμ^0.25 * l), l=0.07c
```

**Question 4** — Vérifier le calcul de `turbulentKE` et `turbulentOmega`.

*Rappel :* $k = \frac{3}{2}(I U_\infty)^2$ avec $I = 0.01$, et $\omega = k^{0.5}/(C_\mu^{0.25} \ell)$ avec $\ell = 0.07c$, $C_\mu = 0.09$.

### Extraction des forces

Les forces sont calculées à chaque pas de temps. Après convergence :

```bash
postProcess -func forces
```

Les coefficients $C_L$ et $C_D$ sont dans `postProcessing/forces/0/force.dat`.

**Question 5** — Calculer $C_L$ et $C_D$ à partir des composantes de force. Comparer avec la théorie des profils minces ($C_L = 2\pi\alpha$ pour $\alpha = 0°$).

---

## 6. Simulation instationnaire (pimpleFoam)

```bash
cd ../pimpleFoam
cp -r ../simpleFoam/constant/polyMesh constant/
restore0Dir
mapFields ../simpleFoam -sourceTime latestTime -consistent
pimpleFoam 2>&1 | tee log.pimpleFoam
```

Le pas de temps est automatiquement ajusté pour $Co \leq 0.9$.

**Question 6** — Que représente le paramètre `nOuterCorrectors 2` dans le dictionnaire `PIMPLE` ? Dans quel cas augmenter cette valeur ?

---

## 7. Post-traitement ParaView

```bash
paraFoam &
```

- Visualiser le champ de pression $C_p = (p - p_\infty) / (0.5 \rho U_\infty^2)$
- Tracer les lignes de courant (Streamlines)
- Visualiser le champ $k$ et identifier les zones de forte turbulence

---

## Fichiers fournis

```
TD2_NACA_Profil/
├── ENONCE.md
├── geometry/
│   └── NACA0012.stl
├── snappyHexMesh/
│   ├── 0/              (champs initiaux vides)
│   ├── constant/       (geometry/ + triSurface/)
│   └── system/         (blockMeshDict, snappyHexMeshDict, extrudeMeshDict,
│                         createPatchDict, surfaceFeatureExtractDict)
├── simpleFoam/
│   ├── 0.orig/         (U, p, k, omega, nut + includes)
│   ├── constant/       (transportProperties, turbulenceProperties)
│   └── system/         (controlDict, fvSchemes, fvSolution, forces)
├── pimpleFoam/
│   ├── 0.orig/
│   ├── constant/       (transportProperties, turbulenceProperties, dynamicMeshDict)
│   └── system/         (controlDict, fvSchemes, fvSolution)
└── Allrun              (script complet)
```
