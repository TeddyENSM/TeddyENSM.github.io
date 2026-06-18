# TD1 — Écoulement de Poiseuille plan (icoFoam)

**OpenFOAM v2412 ESI — WSL2**

---

## Objectifs

- Créer un maillage structuré 2D avec **blockMesh**
- Configurer un écoulement laminaire avec **entrée vitesse imposée** et **pression de référence en sortie**
- Comparer le profil numérique à la **solution analytique**
- Initier le post-traitement avec **ParaView** et Python

---

## 1. Contexte physique

On considère un canal plan de longueur $L = 0.1$ m et de hauteur $H = 0.01$ m.

Le fluide est de l'eau cinématiquement : $\nu = 10^{-6}$ m²/s, $\rho = 1000$ kg/m³.

Un gradient de pression $\nabla p = -0.1$ Pa/m est imposé dans la direction $x$.

**Solution analytique de Poiseuille :**

$$u(y) = -\frac{1}{2\nu}\frac{\partial p}{\partial x}\left(H y - y^2\right)$$

avec $y \in [0, H]$.

Le débit volumique par unité de largeur :

$$q = \int_0^H u\,dy = -\frac{1}{12\nu}\frac{\partial p}{\partial x} H^3$$

Le nombre de Reynolds basé sur la vitesse débitante $\bar{u} = q/H$ :

$$Re = \frac{\bar{u}\,H}{\nu}$$

**Question 1** — Calculer $\bar{u}$, $u_{max}$, $Re$, et vérifier que l'écoulement est bien laminaire.

---

## 2. Maillage (blockMesh)

Le cas est **2D** : on extrude d'une cellule en $z$ (épaisseur $e = 0.001$ m).

Domaine : $[0, L] \times [0, H] \times [0, e]$.

**Question 2** — Ouvrir `system/blockMeshDict` et identifier :
- Les 8 sommets du bloc
- Le nombre de cellules en $x$, $y$, $z$
- Le grading en $y$ (raffinage près des parois)

Lancer le maillage :

```bash
blockMesh
```

Vérifier avec `checkMesh`.

---

## 3. Conditions aux limites

| Frontière  | Type géométrique | $U$              | $p$           |
|------------|-----------------|------------------|---------------|
| `inlet`    | patch           | `fixedValue`     | `zeroGradient`|
| `outlet`   | patch           | `zeroGradient`   | `fixedValue`  |
| `top`      | wall            | `noSlip`         | `zeroGradient`|
| `bottom`   | wall            | `noSlip`         | `zeroGradient`|
| `front`    | empty           | `empty`          | `empty`       |
| `back`     | empty           | `empty`          | `empty`       |

L'écoulement est piloté par les **conditions aux limites** :

- `U` imposée à l'entrée (`fixedValue`)
- `p` imposée à la sortie (`fixedValue`)

**Question 3** — Expliquer le rôle physique de `U` imposée à l'entrée et de `p` imposée à la sortie.

---

## 4. Simulation

```bash
icoFoam 2>&1 | tee log.icoFoam
```

La simulation tourne jusqu'à `endTime = 10` s (convergence vers régime permanent).

Surveiller la résidence avec `foamMonitor` ou :

```bash
grep "^Time" log.icoFoam | tail -5
```

---

## 5. Post-traitement

### 5.1 ParaView

```bash
paraFoam &
```

- Afficher le champ $U_x$ à `t = 10` s en coupe $z = 0.0005$ m
- Extraire un profil `Plot Over Line` de $(0.05, 0, 0.0005)$ à $(0.05, H, 0.0005)$

### 5.2 Python — comparaison analytique

```bash
python3 postProcess_Poiseuille.py
```

Le script trace $u_{num}(y)$ et $u_{analytique}(y)$ sur le même graphe et calcule l'erreur $L_2$.

**Question 4** — Quelle est l'erreur $L_2$ entre numérique et analytique ? Comment évolue-t-elle si vous doublez le nombre de cellules en $y$ ?

---

## 6. Étude de convergence en maillage

**Question 5** — Réaliser une étude GCI avec 3 maillages ($N_y = 10$, $20$, $40$) :

1. Modifier `system/blockMeshDict` (paramètre `Ny`)
2. Relancer `blockMesh` et `icoFoam`
3. Relever $u_{max}$ numérique pour chaque maillage
4. Calculer le rapport de raffinement $r = 2$ et l'ordre apparent $p$
5. Estimer l'incertitude GCI sur le maillage fin

---

## Fichiers fournis

```
TD1_Poiseuille/
├── ENONCE.md             ← ce fichier
├── Allrun                ← script de lancement complet
├── Allclean              ← script de nettoyage
├── 0/
│   ├── U
│   └── p
├── constant/
│   └── transportProperties
├── system/
│   ├── blockMeshDict
│   ├── controlDict
│   ├── fvSchemes
│   ├── fvSolution
│   └── fvOptions
└── postProcess_Poiseuille.py
```
