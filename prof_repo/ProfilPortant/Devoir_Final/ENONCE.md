# Devoir Final — CFD Performances Navires (ENSM 2026-27)

**OpenFOAM v2412 ESI — WSL2**

Durée : 4 h (partie numérique) + rapport à rendre sous 1 semaine.

La géométrie `NACA0012.stl` est fournie dans `geometry/`.

---

## Partie A — Questions théoriques (10 points)

### Q1 (2 pts) — Méthodes numériques

a) Énoncer le critère CFL pour un schéma explicite. Pour quel type de schéma ce critère disparaît-il ? Justifier physiquement.

b) Donner la définition complète de la méthode de Runge-Kutta d'ordre 4 (RK4) : écrire les 4 coefficients $k_1, k_2, k_3, k_4$ et la formule finale $y_{n+1}$.

c) Comment OpenFOAM garantit-il la conservation de la masse lors d'une itération PISO ? Décrire en 3 étapes.

### Q2 (2 pts) — Théorie des profils

a) Énoncer le paradoxe de d'Alembert. Quelle hypothèse est levée par la théorie de Prandtl pour obtenir une portance non nulle ?

b) Écrire la relation de Kutta-Joukowski. En déduire la portance par unité d'envergure d'un profil NACA-0012 de corde $c = 1$ m à $\alpha = 4°$ dans un écoulement à $U_\infty = 50$ m/s (air, $\rho = 1.225$ kg/m³). Utiliser $C_L = 2\pi\alpha$ (théorie des profils minces).

c) Qu'est-ce que la traînée induite ? Écrire $C_{D_i}$ en fonction de $C_L$, $AR$ et $e$.

### Q3 (2 pts) — Maillage

a) Décrire en 3 étapes le pipeline snappyHexMesh (castellatedMesh → snap → addLayers). Quel est le rôle de `nCellsBetweenLevels` ?

b) On souhaite un $y^+ \approx 50$ pour un profil de corde $c = 1$ m à $U = 100$ m/s (air). Calculer $\Delta y_1$ (épaisseur de la première couche).

*Rappels :* $C_f \approx 0.027\,Re^{-1/7}$, $u_\tau = U\sqrt{C_f/2}$, $y^+ = u_\tau \Delta y_1 / \nu$.

c) Quelle est la différence entre `extrudeMesh` et `snappyHexMesh` pour créer un maillage 2D ? Quand utiliser l'un ou l'autre ?

### Q4 (2 pts) — Résistance navire

a) Décomposer la résistance totale $R_T$ en ses composantes selon la classification ITTC. Laquelle est prépondérante à faible Froude ? À fort Froude ?

b) Un voilier de $L_{pp} = 12$ m avance à $V = 5$ nœuds ($\approx 2.57$ m/s). Calculer :
- $Re = VL/\nu$ avec $\nu = 1.19 \times 10^{-6}$ m²/s (eau douce à 15°C)
- $Fr = V/\sqrt{gL}$
- $C_F$ (ITTC-57)
- $R_F$ si $S_m = 35$ m², $\rho = 1000$ kg/m³

c) Qu'est-ce que le sillage de Kelvin ? Quel est l'angle caractéristique ? Pourquoi est-il indépendant de la vitesse ?

### Q5 (2 pts) — Vérification et Validation

a) Définir la différence entre Vérification et Validation en CFD.

b) Trois maillages M1, M2, M3 (ratio $r = 2$) donnent $C_D = 0.0085$, $0.0092$, $0.0104$.
- Calculer l'ordre apparent $p$ de convergence.
- Estimer $C_D$ extrapolé (Richardson).
- Calculer l'incertitude GCI sur M1.

c) Citer deux sources d'erreur de modélisation (distinctes des erreurs de discrétisation) pour la simulation d'un voilier.

---

## Partie B — Exercices numériques (10 points)

### Exercice B1 (4 pts) — Profil NACA-0012 à $\alpha = 4°$ (simpleFoam)

**Objectif :** Simuler le profil NACA-0012 incliné à 4° et calculer $C_L$, $C_D$.

**Données :**
- $U_\infty = 100$ m/s, $\nu_{air} = 1.5 \times 10^{-5}$ m²/s, $\rho = 1.225$ kg/m³
- Corde $c = 1$ m, domaine identique au TD2
- Modèle k-ω SST, simpleFoam jusqu'à convergence

**Étapes :**

1. Créer le répertoire de cas en copiant `TD2_NACA_Profil/` :
   ```bash
   cp -r ../TD2_NACA_Profil MonCas_NACA_4deg
   ```

2. Modifier l'incidence à 4° dans `snappyHexMesh/system/blockMeshDict` OU tourner le vecteur vitesse :
   ```
   flowVelocity  (99.756 6.976 0);  // U*cos(4°)  U*sin(4°)  0
   ```
   (Approche recommandée : garder le maillage horizontal, tourner $U$)

3. Adapter les paramètres turbulents si nécessaire.

4. Lancer `Allrun`.

**À rendre :**

a) Convergence des résidus : joindre le graphe.

b) Valeurs de $C_L$ et $C_D$ obtenues. Comparer $C_L$ à la théorie des profils minces.

c) Champ de pression $C_p$ sur l'extrados et l'intrados (capture ParaView).

d) Estimation de l'incertitude GCI sur $C_L$ (utiliser 2 maillages au minimum).

---

### Exercice B2 (3 pts) — Étude paramétrique : influence de l'incidence

**Objectif :** Tracer la polaire aérodynamique $C_L = f(\alpha)$ et $C_D = f(\alpha)$ pour $\alpha \in \{0°, 2°, 4°, 6°, 8°\}$.

**Étapes :**

1. Pour chaque angle $\alpha$, adapter `initialConditions` :
   ```
   flowVelocity  (#calc "100*cos($alpha*3.14159/180)"
                  #calc "100*sin($alpha*3.14159/180)"
                  0);
   ```
   Ou plus simplement, modifier à la main les 5 cas.

2. Utiliser le maillage du TD2 (pas besoin de re-mailler si l'incidence est modélisée par le vecteur vitesse).

3. Relever $C_L$ et $C_D$ à convergence.

**À rendre :**

a) Tableau récapitulatif $(\alpha, C_L, C_D, C_L/C_D)$.

b) Graphes $C_L(\alpha)$ et $C_D(\alpha)$ comparés à la théorie des profils minces ($C_L = 2\pi\alpha$).

c) Identifier l'angle de portance nulle. Coïncide-t-il avec la théorie pour un profil symétrique ?

---

### Exercice B3 (3 pts) — Post-traitement avancé

**Objectif :** Analyser les champs de pression et vitesse pour le cas $\alpha = 4°$.

**À rendre :**

a) **Distribution de $C_p$** : extraire $C_p(x/c)$ sur l'extrados et l'intrados. Comparer à des données expérimentales NACA (fournies ci-dessous).

   Données expérimentales NACA-0012, $\alpha = 4°$, $Re = 3 \times 10^6$ (valeurs approchées) :

   | $x/c$ | $C_p$ extrados | $C_p$ intrados |
   |--------|---------------|---------------|
   | 0.00   | -0.87         | -0.87         |
   | 0.05   | -1.42         | -0.15         |
   | 0.10   | -1.25         | -0.08         |
   | 0.20   | -0.95         | +0.02         |
   | 0.50   | -0.48         | +0.10         |
   | 1.00   |  0.00         |  0.00         |

b) **Épaisseur de couche limite** : à partir du profil $U_x(y)$ à $x/c = 0.5$, estimer $\delta_{99}$ (épaisseur où $U = 0.99 U_\infty$).

c) **Bilan de forces** : vérifier que $C_L^{pression} + C_L^{visqueux} \approx C_L^{total}$. Quelle est la part relative de chaque contribution ?

---

## Critères d'évaluation

| Critère                              | Points |
|--------------------------------------|--------|
| Questions théoriques (A)             | 10     |
| Simulation B1 — mise en place        | 2      |
| Simulation B1 — résultats et analyse | 2      |
| Étude paramétrique B2                | 3      |
| Post-traitement B3                   | 3      |
| **Total**                            | **20** |

**Rapport :** PDF, max 15 pages hors annexes. Inclure les fichiers `initialConditions` modifiés en annexe.

---

## Ressources

- Tutoriels OpenFOAM v2412 : `$FOAM_TUTORIALS/incompressible/simpleFoam/`
- Documentation ESI : [openfoam.com](https://www.openfoam.com/documentation/guides/v2412/)
- Données NACA-0012 expérimentales : Gregory & O'Reilly, NASA TM X-3284, 1973
