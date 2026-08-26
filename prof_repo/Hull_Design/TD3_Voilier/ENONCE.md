# TD3 — Résistance d'un voilier : simulation multiphase (interFoam)

**OpenFOAM v2412 ESI — WSL2**

---

## Objectifs

- Configurer une simulation **VOF (Volume of Fluid)** avec **interFoam**
- Simuler la résistance totale d'un voilier 17 m à vitesse de service
- Prendre en compte les **degrés de liberté** (tangage + pilonnement) via `rigidBodyMotion`
- Post-traiter les composantes de résistance et la surface libre

---

## 1. Caractéristiques du voilier

| Paramètre | Valeur |
|-----------|--------|
| Longueur entre perpendiculaires $L_{pp}$ | 17 m |
| Largeur à la flottaison $B_{wl}$ | 4.62 m |
| Tirant d'eau $T$ | 1.01 m |
| Déplacement $\Delta$ | 14 525 kg |
| Vitesse de service $U$ | 3.874 m/s |
| Nombre de Froude $Fr$ | — |
| Nombre de Reynolds $Re$ | — |

**Question 1** — Calculer $Fr = U/\sqrt{gL_{pp}}$ et $Re = UL_{pp}/\nu$ avec $\nu = 1.0034 \times 10^{-6}$ m²/s, $\rho = 1025$ kg/m³.

Pourquoi la résistance de vague est-elle prépondérante pour ce $Fr$ ? Tracer schématiquement $R_W/\Delta$ en fonction de $Fr$.

---

## 2. Domaine et maillage

Le domaine est paramétré dans `system/initialConditions` via `#calc` :

```
Lpp = 17 m
domaine : [-2.5·Lpp ... 5.5·Lpp] en x
          [-3·Bwl/2 ... 3·Bwl/2] en y
          [-3·T     ... 1.5·D   ] en z
```

**Question 2** — Identifier dans `system/blockMeshDict` les 5 boîtes de raffinement (`Box0` à `Box4`) et leur rôle physique (sillage, étrave, surface libre...).

Lancer le maillage :

```bash
blockMesh
snappyHexMesh -overwrite
```

Vérifier avec `checkMesh` — noter la non-orthogonalité maximale et moyenne.

---

## 3. Conditions aux limites (VOF)

| Frontière   | $U$                          | $p_{rgh}$             | $\alpha_{eau}$ |
|-------------|------------------------------|-----------------------|---------------|
| `inlet`     | `fixedValue (-3.874 0 0)`    | `fixedFluxPressure`   | `fixedValue 0` (AIR) |
| `outlet`    | `outletPhaseMeanVelocity`    | `zeroGradient`        | `variableHeightFlowRate` |
| `atmosphere`| `pressureInletOutletVelocity`| `totalPressure p0=0`  | `inletOutlet 0` |
| `Carena`    | `movingWallVelocity`         | `fixedFluxPressure`   | `zeroGradient` |

**Question 3** — Pourquoi `alpha.water = 0` (AIR) à l'inlet alors qu'on simule un voilier partiellement immergé ? Comment est initialisée la surface libre ?

Examiner `system/setFieldsDict` : quelle boîte est remplie d'eau ($\alpha_{eau} = 1$) ?

---

## 4. Modèle de mouvement du corps (rigidBodyMotion)

Le voilier est libre en **pilonnement** ($z$, joint $P_z$) et **tangage** ($\theta_y$, joint $R_y$).

Dans `constant/dynamicMeshDict` :

```c++
motionSolver    rigidBodyMotion;
accelerationRelaxation  table (
    (0  0)    // t=0 : figé
    (10 0)    // t=10: figé
    (20 0.15) // montée progressive
    (50 0.3)
    (100 0.3) // relaxation finale
);
```

**Question 4** — Pourquoi bloquer le mouvement pendant les 10 premières secondes ? Quel est le rôle du `linearDamper` et du `sphericalAngularDamper` ?

---

## 5. Lancement de la simulation

```bash
# Initialiser les champs
restore0Dir
setFields

# Décomposer le domaine (parallèle)
decomposePar

# Lancer interFoam en parallèle (adapter -np au nombre de cœurs)
mpirun -np 4 interFoam -parallel 2>&1 | tee log.interFoam

# Reconstruire
reconstructPar
```

La simulation dure jusqu'à `endTime = 100` s. Le régime établi est atteint vers $t \approx 60$ s.

---

## 6. Post-traitement

### 6.1 Filtrage des forces

Le fichier de forces brutes est dans `postProcessing/forces/0/force.dat`.

Format (v2412 ESI, sans parenthèses) :

```
# Time   Ftx  Fty  Ftz   Fpx  Fpy  Fpz   Fvx  Fvy  Fvz
```

Lancer le filtre passe-bas (Butterworth ordre 2, coupure 0.1 Hz) :

```bash
python3 filterForces.py
```

Le fichier `filteredF.dat` est produit avec : temps, Ftotal, Fpression, Fvisqueux.

### 6.2 Tracé gnuplot

```bash
gnuplot Gnuplot_script.txt
```

### 6.3 ParaView

```bash
paraFoam &
```

- Visualiser $\alpha_{eau} = 0.5$ (isosurface = surface libre)
- Afficher la pression de surface $C_p$
- Streaklines dans le sillage
- Champ de vitesse dans le plan de symétrie $y = 0$

**Question 5** — Séparer les composantes $R_F$ (friction), $R_{VP}$ (pression visqueuse) et $R_W$ (vague). Comparer la résistance totale à la prédiction Holtrop-Mennen.

---

## 7. Comparaison avec les méthodes de régression

Calculer la résistance de friction ITTC-57 :

$$C_F = \frac{0.075}{(\log_{10} Re - 2)^2}$$

$$R_F = C_F \cdot \frac{1}{2}\rho U^2 \cdot S_m$$

avec $S_m = 60.82$ m² (surface mouillée).

**Question 6** — Quel est l'écart relatif entre $R_F$ (ITTC-57) et la composante visqueuse CFD ? Discuter des causes possibles (rugosité, 3D vs 2D...).

---

## Fichiers fournis

```
TD3_Voilier/
├── ENONCE.md
├── Allrun
├── Allclean
├── 0.orig/
│   ├── U
│   ├── p_rgh
│   ├── alpha.water.orig
│   ├── k
│   ├── omega
│   ├── nut
│   └── pointDisplacement
├── constant/
│   ├── transportProperties
│   ├── turbulenceProperties
│   └── dynamicMeshDict
├── system/
│   ├── initialConditions
│   ├── blockMeshDict
│   ├── snappyHexMeshDict
│   ├── controlDict
│   ├── fvSchemes
│   ├── fvSolution
│   ├── setFieldsDict
│   └── decomposeParDict
├── filterForces.py
└── Gnuplot_script.txt
```

> **Note :** La géométrie STL de la carène (`Carena.stl`) doit être placée dans
> `constant/triSurface/` avant le lancement. Contacter l'enseignant.
