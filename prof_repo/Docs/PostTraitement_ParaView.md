# Post-traitement ParaView — PerfNav (OpenFOAM v2412)

> Guide d'usage ParaView 5.x par TD. Chaque section décrit les manipulations
> depuis l'ouverture du cas jusqu'à l'export des figures.

---

## Lancement général

```bash
# Depuis le répertoire du cas (crée un fichier .foam vide si absent)
paraFoam &

# Variante intégrée (sans plugins natifs OpenFOAM, plus légère)
paraFoam -builtin &

# Cas parallèle déjà décomposé → lire directement les processor*/
# Dans ParaView : Properties → Case Type → Decomposed Case
# OU reconstruire d'abord :
reconstructPar && paraFoam &
```

---

## TD1 — Poiseuille (icoFoam)

**Répertoire :** `../Fondamentaux/TD1_Poiseuille/`  
**Champs :** `U` (vecteur), `p` (scalaire)  
**Instants disponibles :** 0 s à 10 s (écriture tous les 0.1 s)

### 1. Profil de vitesse Ux(y) — vérification analytique

```
1. Ouvrir le cas → Properties → cocher U → Apply
2. Sélectionner l'instant t = 10 dans la barre temporelle
3. Filters → Data Analysis → Plot Over Line
     Point1 : (0.05  0      0)
     Point2 : (0.05  0.01   0)   ← section médiane, balayage axe y
4. Series Parameters → décocher tout sauf U_X
5. Apply
```

Résultat attendu : parabole  
`Ux(y) = 6 · Ūbar · y · (H − y) / H²`  
avec Ūbar = 0.04167 m/s, H = 0.01 m → Ux_max ≈ 0.0625 m/s au centre.

**Export CSV :** dans le graphe → File → Save Data → `profil_U.csv`  
Colonnes : `Points:1` (y), `U:0` (Ux) → utiliser `postProcess_Poiseuille.py`

### 2. Visualisation 2D colorée

```
1. Représentation : Surface
2. Colorier par U, composante X
3. Ctrl+R pour rescaler l'échelle
4. Filters → Slice → Normal Z, Origin (0 0 0.0005)
   → section médiane propre, sans les faces avant/arrière
```

### 3. Animation convergence (optionnel)

Barre temporelle → Play : observer la mise en place du profil parabolique depuis U uniforme à t=0.

---

## TD2 — NACA-0012 (simpleFoam + pimpleFoam)

### 2a. simpleFoam (cas stationnaire)

**Répertoire :** `../ProfilPortant/TD2_NACA_Profil/simpleFoam/`  
**Champs :** `U`, `p`, `k`, `omega`, `nut`  
**Instant unique :** t = 4000 (itérations)

#### Champ de pression et coefficient Cp

```
1. Properties → cocher p → Apply
2. Représentation : Surface, colorier par p
3. Filters → Calculator
     Expression : p * 2 / (1.225 * 10000)
     Nom du résultat : Cp
     (formule : Cp = 2p / ρU²∞ = 2p / (1.225 × 100²))
4. Apply → colorier par Cp, palette divergente Blue-White-Red
```

#### Courbe Cp(x/c) sur le profil (intrados / extrados)

```
1. Filters → Slice → Normal Z, Origin (0 0 0)   ← coupe 2D
2. Sur la tranche : Filters → Extract Cells By Region → patch wing
   OU Filters → Extract Surface → sélectionner wing dans le combo
3. Filters → Plot On Intersection Curves
     Plane Normal : Z    →  Apply
4. Variable : Cp calculé
5. File → Save Data → Cp_NACA.csv
```

#### Lignes de courant

```
1. Filters → Stream Tracer
     Seed Type : Line Source
     Point1 : (-3  -3  0)   Point2 : (-3  3  0)
     Max Streamline Length : 30
     Integration Direction : BOTH
2. Apply → Tubes ou Ribbons pour meilleur rendu
3. Colorier par U magnitude ou p
```

#### Couche limite — épaisseur turbulente

```
1. Filters → Plot Over Line, normal au profil (ex. au bord d'attaque x=0)
     Point1 : (0  0     0)   Point2 : (0  0.05  0)
2. Variable : nut ou k
```

#### Résidus simpleFoam en direct (terminal)

```bash
foamMonitor -l postProcessing/residuals/0/solverInfo.dat &
```

### 2b. pimpleFoam (cas instationnaire)

**Répertoire :** `../ProfilPortant/TD2_NACA_Profil/pimpleFoam/`  
**Champs :** mêmes que simpleFoam  
**Instants :** 0 à 5 s (écriture tous les 0.1 s)

Même procédure que simpleFoam. Utiliser la barre temporelle et **Play** pour animer l'évolution du sillage. Exporter une animation :

```
File → Save Animation
  Format : PNG (séquence) ou AVI
  Frame rate : 10 fps
```

---

## TD3 — Voilier 17 m (interFoam + rigidBodyMotion)

**Répertoire :** `../Hull_Design/TD3_Voilier/`  
**Prérequis :** `reconstructPar` pour rassembler les processor*/  
**Champs :** `U`, `p_rgh`, `alpha.water`, `k`, `omega`, `nut`  
**Instants :** 0 à 100 s (écriture tous les ~0.5–1 s selon contrôle)

### 1. Surface libre — iso-contour α = 0.5

```
1. Properties → cocher alpha.water → Apply
2. Filters → Contour
     Contour By : alpha.water
     Isosurface value : 0.5
3. Apply → colorier par U magnitude ou p_rgh
4. Play → observer vagues de Kelvin et sillage
```

### 2. Phase eau — volume immergé

```
1. Filters → Threshold
     Scalars : alpha.water
     Minimum : 0.4   Maximum : 1.0
2. Apply → seule la phase liquide est visible
3. Colorier par p_rgh (pression hydrostatique + dynamique)
```

### 3. Pression sur la carène — coefficient Cp

```
1. Properties → cocher p_rgh → Apply
2. Sélectionner uniquement le patch Carena :
   Filters → Extract Surface → décocher tout sauf Carena
3. Filters → Calculator
     Expression : (p_rgh + 1025*9.81*coordsZ) * 2 / (1025 * 3.874^2)
     Nom : Cp
     (restitue p_total depuis p_rgh = p − ρgh)
4. Apply → colorier par Cp, palette divergente
```

### 4. Plan de coupe XZ — champ de vitesse et sillage

```
1. Filters → Slice
     Normal : Y = (0 1 0)   Origin : (0 0 0)
2. Colorier par U magnitude
3. Filters → Glyph
     Glyph Type : Arrow
     Scale Array : U   Scale Factor : 0.3
     → visualiser direction et intensité du courant
```

### 5. Mouvement du navire (heave + pitch)

Le maillage se déforme avec le corps rigide (`dynamicMotionSolverFvMesh`).

```
Play → observer translation z (pilonnement) et rotation y (tangage)
Pour mesurer : dans le log.interFoam, chercher les lignes :
  "Carena : position" et "Carena : orientation"
  (sorties de rigidBodyMotion avec report yes)
```

Pour tracer les trajectoires z(t) et θ(t) :

```bash
grep "Carena" log.interFoam | grep -E "position|orientation" > mouvement.dat
# ou utiliser le postProcessing/rigidBodyMotion/ si configuré
```

### 6. Pipeline de visualisation recommandé (vue complète)

```
┌─ Threshold alpha.water [0.4, 1.0]   ← volume eau, transparent à 50 %
├─ Contour alpha.water = 0.5          ← surface libre, coloré par U magnitude
├─ Slice Y=0, coloré par p_rgh        ← plan de symétrie navire
└─ Extract Surface Carena, coloré Cp  ← coque colorée pression
```

Rendre la phase eau semi-transparente :  
`Threshold` sélectionné → **Properties → Opacity : 0.3**

---

## Raccourcis et commandes universels

| Action | Raccourci |
|--------|-----------|
| Appliquer un filtre | `Ctrl+Space` → taper le nom |
| Rescaler la colormap | `Ctrl+R` |
| Réinitialiser la caméra | `Spacebar` (fit all) |
| Masquer/afficher un objet | `H` |
| Capture écran | `Ctrl+Shift+C` → Save Screenshot |
| Exporter animation | File → Save Animation → PNG ou AVI |
| Vue Animation | View → Animation View |
| Changer représentation | Barre d'outils : Surface / Wireframe / Surface with Edges |
| Sélection par patch | Properties → Mesh Regions → décocher les patchs inutiles |

## Résidus en temps réel (terminal)

```bash
# TD2 simpleFoam ou pimpleFoam — depuis le répertoire du sous-cas
foamMonitor -l postProcessing/residuals/0/solverInfo.dat &

# TD3 — pas de solverInfo configuré par défaut
# Observer directement le log (tail -f) ou tracer avec gnuplot :
gnuplot Gnuplot_script.txt &          # script fourni dans TD3_Voilier/
tail -f log.interFoam | grep "Time ="  # avancement en temps réel
```
