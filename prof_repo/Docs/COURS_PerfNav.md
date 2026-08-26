# CFD Appliquée aux Voiliers — Cours PerfNav
**Performances Navires — ENSM**    
*Adaptation pédagogique ENSM : C. Vanhorick*

---

## Plan du cours

1. [Introduction à la CFD navale](#1-introduction-à-la-cfd-navale)
2. [Qu'est-ce que la CFD ?](#2-quest-ce-que-la-cfd-)
3. [OpenFOAM — structure et organisation](#3-openfoam--structure-et-organisation)
4. [Méthodes numériques](#4-méthodes-numériques)
5. [Cas Poiseuille — premier cas OpenFOAM](#5-cas-poiseuille--premier-cas-openfoam)
6. [Théorie des profils hydrodynamiques](#6-théorie-des-profils-hydrodynamiques)
7. [Maillage](#7-maillage)
8. [Configuration d'une simulation](#8-configuration-dune-simulation)
9. [Lancer et monitorer une simulation](#9-lancer-et-monitorer-une-simulation)
10. [Post-traitement](#10-post-traitement)
11. [Vérification et validation](#11-vérification-et-validation)
12. [Fonctionnalités avancées — maillages mobiles](#12-fonctionnalités-avancées--maillages-mobiles)
13. [Résistance du navire — bases](#13-résistance-du-navire--bases)
14. [Cas d'étude : voilier 17 m](#14-cas-détude--voilier-17-m)
15. [Maillage 3D du voilier](#15-maillage-3d-du-voilier)
16. [Configuration simulation multiphasique](#16-configuration-simulation-multiphasique)
17. [Lancer une simulation multiphasique](#17-lancer-une-simulation-multiphasique)
18. [Post-traitement 3D](#18-post-traitement-3d)
19. [Fonctionnalités avancées navire](#19-fonctionnalités-avancées-navire)
20. [Devoir final](#20-devoir-final)

---

## 1. Introduction à la CFD navale

### 1.1 Contexte et objectifs

Ce cours a pour objectif de former les étudiants à la **Mécanique des Fluides Numérique** (CFD — *Computational Fluid Dynamics*) appliquée à l'architecture navale, et plus particulièrement à la résistance à l'avancement des voiliers.

La CFD est aujourd'hui un outil incontournable dans la conception navale. Elle permet d'obtenir des résultats détaillés sur les champs de vitesse, de pression et les forces exercées sur un navire, de manière complémentaire aux essais en bassin et aux méthodes semi-empiriques.

Le cours est structuré en deux parties :
- **Partie 1 (Ch. 1–12)** : bases de la CFD avec OpenFOAM — équations, maillage, configuration, post-traitement, appliqués à un écoulement de Poiseuille et un profil NACA.
- **Partie 2 (Ch. 13–19)** : application à la résistance d'un voilier réel — composantes de résistance, simulation 3D multiphasique avec surface libre.

Dans la spirale de conception navale, la CFD RANS intervient au **3e tour** — après les régressions empiriques et les méthodes de panneaux :
1. **1er tour** : régressions empiriques (Delft III / Holtrop) — estimation rapide à partir des paramètres géométriques de la carène
2. **2e tour** : méthodes potentielles (panneaux BEM : Nemoh, HydroSTAR) — résistance de vagues sans viscosité, tenue à la mer
3. **3e tour** : RANS (interFoam, simpleFoam) — résistance totale avec viscosité, surface libre et mouvements du navire

Ce cours couvre les méthodes du 3e tour tout en s'appuyant sur les résultats des deux premiers tours pour la validation.

### 1.2 Outils utilisés

| Outil | Rôle |
|---|---|
| **OpenFOAM v2412 ESI** | Solveur CFD open-source (volumes finis) |
| **ParaView** | Post-traitement et visualisation |
| **Rhinoceros** | Modélisation géométrique 3D / export STL |
| **Python / gnuplot** | Analyse et tracé des résultats |

Les fichiers de cas sont disponibles sur la plateforme du cours.

![Vue 3D du voilier de 17 m étudié dans ce cours (modélisé sous Rhinoceros)](figures/P01_voilier_17m_rhinoceros.png)

---

## 2. Qu'est-ce que la CFD ?

### 2.1 Définition et applications

La **CFD** désigne l'ensemble des méthodes numériques permettant de résoudre les équations régissant l'écoulement des fluides. En pratique, on cherche à calculer les champs de vitesse $\mathbf{u}(\mathbf{x},t)$, de pression $p(\mathbf{x},t)$ et éventuellement de température $T(\mathbf{x},t)$ en tout point d'un domaine.

Applications en ingénierie navale :
- Calcul de la **résistance à l'avancement** d'un navire
- Analyse des **appendices hydrodynamiques** (quille, safran, hydrofoils)
- Étude de la **stabilité** et des **mouvements** du navire dans la houle
- Conception de **propulseurs**

### 2.2 Pipeline de simulation

Une simulation CFD suit toujours les étapes suivantes :

1. **Définition du problème** : géométrie, conditions aux limites, propriétés du fluide
2. **Maillage** (*meshing*) : discrétisation du domaine en cellules élémentaires
3. **Configuration** : paramètres numériques, modèles physiques, conditions initiales
4. **Calcul** : résolution itérative des équations
5. **Post-traitement** : analyse des résultats (champs, forces, convergence)
6. **Vérification & Validation** : comparaison avec références analytiques ou expérimentales

### 2.3 Classification des méthodes

Les approches CFD se distinguent par leur traitement de la viscosité :

| Méthode | Fluide | Exemple | Coût | Sortie |
|---|---|---|---|---|
| **Potentiel (BEM)** | Parfait (non visqueux) | Nemoh, HydroSTAR | Faible | Résistance de vagues seulement |
| **RANS** | Visqueux, turbulent | OpenFOAM, STAR-CCM+ | Moyen | Résistance complète |
| **LES** | Turbulence résolue à grande échelle | — | Élevé | Fluctuations temporelles |
| **DNS** | Turbulence entièrement résolue | — | Très élevé | Recherche uniquement |

Ce cours se concentre sur les méthodes **RANS** avec OpenFOAM.

Les principaux solveurs de panneaux BEM utilisés en hydrodynamique navale sont :
- **Nemoh** (open-source, École Centrale de Nantes) — tenue à la mer, forces de vague, diffraction/radiation
- **HydroSTAR** (Bureau Veritas) — diffraction/radiation, standard industriel pour la certification navale
- **WAMIT** (MIT) — référence académique, très répandu en recherche

Ces méthodes supposent un fluide parfait (non visqueux) et sont valides pour des corps de faible épaisseur sans sillage visqueux. Elles sont complémentaires à OpenFOAM : les conditions de houle calculées par BEM peuvent être injectées dans interFoam pour des simulations RANS avec vagues incidentes réalistes.

### 2.4 Avantages et limites

| Avantages | Limites |
|---|---|
| Résultats détaillés sur tout le domaine | Coût de calcul important |
| Permet de tester de nombreuses configurations | Modèles de turbulence approximatifs |
| Complémentaire aux essais en bassin | Résultats à valider expérimentalement |
| Accessible via des outils open-source (OpenFOAM) | Nécessite une maîtrise du maillage et des paramètres numériques |

---

## 3. OpenFOAM — Structure et Organisation

### 3.1 Qu'est-ce qu'OpenFOAM ?

**OpenFOAM** (*Open Field Operation And Manipulation*) est un outil CFD open-source basé sur la méthode des volumes finis. Il est développé et maintenu par la *OpenFOAM Foundation* et *ESI Group*. Ses versions majeures récentes sont OpenFOAM v2306 et v2412.

OpenFOAM résout les équations de Navier-Stokes sur des maillages non structurés en 3D, et offre une grande modularité via des dictionnaires de configuration en texte brut.

### 3.2 Structure d'un cas OpenFOAM

Tout cas OpenFOAM est organisé en **trois dossiers** principaux :

```
monCas/
├── 0/               ← Conditions initiales et aux limites (t=0)
│   ├── U
│   ├── p
│   └── ...
├── constant/        ← Propriétés physiques et maillage
│   ├── polyMesh/    ← Maillage (points, faces, cellules)
│   └── transportProperties
└── system/          ← Paramètres numériques
    ├── controlDict
    ├── fvSchemes
    └── fvSolution
```

#### Dossier `0/` — conditions aux limites

Contient un fichier par champ résolu (vitesse `U`, pression `p`, énergie turbulente `k`, etc.). Chaque fichier définit le type et la valeur des conditions aux limites sur chaque *patch* (surface frontière).

Exemple pour la vitesse `U` :
```c
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (1 0 0);

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform (1 0 0);
    }
    outlet
    {
        type    zeroGradient;
    }
    wall
    {
        type    noSlip;
    }
}
```

#### Dossier `constant/` — propriétés physiques

- **`polyMesh/`** : décrit le maillage (fichiers `points`, `faces`, `cells`, `owner`, `neighbour`, `boundary`).
- **`transportProperties`** : viscosité cinématique et modèle de transport.

#### Dossier `system/` — paramètres numériques

- **`controlDict`** : temps de début/fin, pas de temps, fréquences d'écriture.
- **`fvSchemes`** : schémas de discrétisation (dérivées temporelles, divergence, gradient...).
- **`fvSolution`** : solveurs linéaires, tolérances, algorithmes de couplage pression-vitesse.

### 3.3 Structure d'un fichier — en-tête `FoamFile`

Chaque fichier de cas OpenFOAM commence par un en-tête standardisé :

```c
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;    // ou volScalarField, surfaceScalarField, dictionary...
    location    "0";
    object      U;
}
```

La valeur de `class` détermine le type de données :

| Classe | Usage |
|---|---|
| `volVectorField` | Champ vectoriel volumique ($\mathbf{U}$) |
| `volScalarField` | Champ scalaire volumique ($p$, $k$, $\alpha$) |
| `surfaceScalarField` | Flux scalaire sur les faces ($\phi$) |
| `dictionary` | Fichier de configuration (controlDict, fvSchemes…) |

### 3.4 OpenFOAM Foundation vs ESI

Il existe deux branches maintenues en parallèle :

| Distribution | Organisation | Versions | Dictionnaires |
|---|---|---|---|
| **OpenFOAM Foundation** | openfoam.org | v8, v9, v10, v11… | `momentumTransport` |
| **ESI Group** | openfoam.com | v1912, v2106, v2306, **v2412**… | `turbulenceProperties` |

Ce cours utilise **OpenFOAM v2412 ESI**. Certains noms de dictionnaires et de conditions aux limites diffèrent entre les deux branches — les extraits de code de ce document sont tous validés pour v2412 ESI.

### 3.5 Notations et dimensions

OpenFOAM utilise une notation dimensionnelle rigoureuse. Les dimensions sont exprimées sous forme d'un vecteur `[kg m s K mol A cd]` :

```c
dimensions    [0 2 -1 0 0 0 0];   // m²/s  (viscosité cinématique)
dimensions    [0 1 -1 0 0 0 0];   // m/s   (vitesse)
dimensions    [0 2 -2 0 0 0 0];   // m²/s² (pression cinématique p/ρ)
```

---

## 4. Méthodes Numériques

### 4.1 Équations gouvernantes

L'écoulement d'un fluide newtonien incompressible est décrit par les **équations de Navier-Stokes** :

**Continuité** (conservation de la masse) :
$$\nabla \cdot \mathbf{u} = 0$$

**Quantité de mouvement** (bilan des forces) :
$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{f}$$

où $\mathbf{u}$ est le vecteur vitesse, $p$ la pression, $\rho$ la masse volumique, $\nu$ la viscosité cinématique et $\mathbf{f}$ les forces volumiques (gravité, etc.).

**Énergie** (si thermique) :
$$\frac{\partial T}{\partial t} + \mathbf{u} \cdot \nabla T = \alpha \nabla^2 T$$

La **dérivée matérielle** (ou dérivée totale) d'un scalaire $\varphi$ suivant une particule fluide :
$$\frac{D\varphi}{Dt} = \frac{\partial \varphi}{\partial t} + \mathbf{u} \cdot \nabla\varphi$$

Le tenseur des taux de déformation (partie symétrique du gradient de vitesse) :
$$S_{ij} = \frac{1}{2}\left(\frac{\partial U_i}{\partial x_j} + \frac{\partial U_j}{\partial x_i}\right)$$

Le tenseur des contraintes visqueuses pour un fluide newtonien incompressible :
$$\boldsymbol{\tau} = 2\mu\mathbf{S}, \quad \tau_{ij} = 2\mu S_{ij}$$

La contrainte tangentielle en 1D s'en déduit : $\tau = 2\mu\varepsilon$, avec $\varepsilon = \partial u/\partial y = S_{12}$.

La quantité de mouvement sous forme conservative (utilisée par OpenFOAM) :
$$\frac{\partial(\rho\mathbf{u})}{\partial t} + \nabla \cdot (\rho\mathbf{u}\mathbf{u}) = -\nabla p + \nabla \cdot \boldsymbol{\tau} + \rho\mathbf{f}$$

### 4.2 Méthode des Volumes Finis (FVM)

La **méthode des volumes finis** (FVM) est au cœur d'OpenFOAM. Elle consiste à intégrer les équations gouvernantes sur chaque cellule élémentaire du maillage.

Pour une équation de transport $\frac{\partial u}{\partial t} + \nabla \cdot (\mathbf{F}) = S$ intégrée sur un volume de contrôle $V$ :
$$\int_V \frac{\partial u}{\partial t} \, \mathrm{d}V + \oint_{\partial V} \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S = \int_V S \, \mathrm{d}V$$

Le flux à travers chaque face est approché par un schéma numérique (centré, décentré...). Cette approche garantit la **conservation locale** et s'adapte à tout type de maillage non structuré.

Autres méthodes numériques existantes (comparaison) :

| Méthode | Principe | Avantages | Limites |
|---|---|---|---|
| **FVM** | Conservation sur volumes de contrôle | Conservatif, maillages quelconques | Ordre faible par défaut |
| **FEM** | Minimisation résidus pondérés | Haute précision | Formulation complexe |
| **Différences finies** | Approximation différentielle locale | Simple | Maillages structurés uniquement |

### 4.3 Intégration temporelle

Pour résoudre $\frac{\partial u}{\partial t} = f(u)$, on dispose de plusieurs schémas :

**Euler explicite** (ordre 1) :
$$u^{n+1} = u^n + \Delta t \, f(u^n)$$

**Euler implicite** (ordre 1, inconditionnellement stable) :
$$u^{n+1} = u^n + \Delta t \, f(u^{n+1})$$

**Schéma de Heun** (Runge-Kutta ordre 2) :
$$k_1 = f(u^n), \quad k_2 = f(u^n + \Delta t \, k_1)$$
$$u^{n+1} = u^n + \frac{\Delta t}{2}(k_1 + k_2)$$

**Runge-Kutta d'ordre 4** (RK4) :
$$u^{n+1} = u^n + \frac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)$$

### 4.4 Condition CFL

La **condition de Courant-Friedrichs-Lewy** (CFL) impose une limite sur le pas de temps pour les schémas explicites :

$$\mathrm{Co} = \frac{c \, \Delta t}{\Delta x} \leq 1$$

où $c$ est la vitesse caractéristique de convection et $\Delta x$ la taille de maille. Cette condition est essentielle pour les solveurs **explicites** ; les solveurs implicites peuvent dépasser $\mathrm{Co} = 1$ mais au prix d'une précision réduite.

Dans OpenFOAM (solveurs transitoires), le nombre de Courant est surveillé en temps réel et affiché dans les logs.

---

## 5. Cas Poiseuille — Premier Cas OpenFOAM

### 5.1 Problème et solution analytique

L'**écoulement de Poiseuille** est un écoulement visqueux entre deux plaques parallèles (canal 2D) soumis à un gradient de pression imposé. C'est le premier cas de validation classique en CFD.

Géométrie : canal de largeur $L_y$, gradient de pression $\frac{\partial p}{\partial x} = -q$.

Solution analytique du profil de vitesse :
$$u(y) = \frac{q}{2\nu} \left( L_y y - y^2 \right)$$

Vitesse maximale (au centre du canal, $y = L_y/2$) :
$$u_{\max} = \frac{q \, L_y^2}{8\nu}$$

Cette solution parabolique sert de **référence de validation** pour vérifier que la simulation OpenFOAM est correctement configurée (géométrie, conditions aux limites, maillage).

### 5.2 Structure du cas OpenFOAM

Le cas Poiseuille utilise le solveur **`icoFoam`** (Incompressible, laminaire, transitoire).

**Fichier `system/controlDict`** :
```c
application    icoFoam;
startFrom      startTime;
startTime      0;
stopAt         endTime;
endTime        10;
deltaT         0.01;
writeControl   timeStep;
writeInterval  100;
```

**Fichier `constant/transportProperties`** :
```c
transportModel  Newtonian;
nu              nu [0 2 -1 0 0 0 0] 1e-3;
```

**Maillage avec `blockMesh`** : Le fichier `system/blockMeshDict` définit le maillage structuré par blocs hexaédriques. Les dimensions du canal, le nombre de cellules et les graduations sont spécifiés pour chaque bloc.

```c
vertices
(
    (0   0   0)   // 0
    (Lx  0   0)   // 1
    (Lx  Ly  0)   // 2
    (0   Ly  0)   // 3
    ...
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (Nx Ny 1) simpleGrading (1 1 1)
);
```

**Conditions aux limites (`0/U`)** :
- `inlet` : `fixedValue uniform (0 0 0)` → entrée avec profil à développer
- `outlet` : `zeroGradient`
- `topWall` / `bottomWall` : `noSlip`
- faces avant/arrière (2D) : `empty`

> **Point v2412 — Référence de pression** : lorsque toutes les BCs de pression sont `zeroGradient` (condition de Neumann pure), OpenFOAM ne peut pas fixer le niveau absolu de pression et le système linéaire est singulier. Il faut alors déclarer une cellule de référence dans `system/fvSolution` :
> ```c
> PISO { nCorrectors 2; nNonOrthogonalCorrectors 1; pRefCell 0; pRefValue 0; }
> ```
> C'est le cas du TD1 Poiseuille où `meanVelocityForce` pilote l'écoulement et toutes les BCs pression sont `zeroGradient`.

### 5.3 Validation

Après la simulation, on compare le profil de vitesse numérique $u(y)$ au profil analytique parabolique. La concordance doit être excellente pour un maillage suffisamment fin, ce qui confirme la bonne implémentation du cas.

![Comparaison profil de vitesse Poiseuille numérique vs. analytique](figures/P02_poiseuille_profil_validation.png)

---

## 6. Théorie des Profils Hydrodynamiques

### 6.1 Paradoxe de d'Alembert

Dans un **fluide parfait** (non visqueux), la résistance exercée sur un corps en mouvement à vitesse constante est **nulle**. C'est le **paradoxe de d'Alembert** (1752) : l'écoulement potentiel est symétrique avant/arrière, la distribution de pression l'est aussi, et l'intégrale des forces est nulle.

En réalité, le fluide possède une viscosité et la **couche limite** rompt cette symétrie, générant de la résistance visqueuse.

### 6.2 Condition de Kutta et profils portants

Pour un profil avec un bord de fuite aigu, la **condition de Kutta** impose que l'écoulement quitte le bord de fuite tangentiellement (pas de vitesse infinie). Cette condition sélectionne la **circulation** $\Gamma$ autour du profil.

En théorie des profils 2D, le **théorème de Kutta-Joukowski** donne la portance par unité d'envergure :
$$L' = \rho U_0 \Gamma$$

où $U_0$ est la vitesse de l'écoulement amont et $\Gamma$ la circulation (positive dans le sens antihoraire).

### 6.3 Transformation de Joukowsky

La **transformation de Joukowsky** est un outil mathématique qui transforme un cercle (plan $z$) en un profil aérodynamique (plan $\zeta$) :
$$\zeta = z + \frac{a^2}{z}$$

Pour un cercle de centre décalé par rapport à l'origine avec $a = 1$, la transformation produit un profil cambré avec un bord de fuite aigu. Le coefficient de portance du profil de Joukowsky à angle d'attaque $\alpha$ :
$$C_L = 2\pi(\alpha + \beta)$$
où $\beta$ est l'angle de cambrure (déviation de la ligne de cambrure par rapport à la corde). Pour un profil symétrique ($\beta = 0$) : $C_L = 2\pi\alpha$.

Elle permet de calculer analytiquement l'écoulement autour de profils de Joukowsky, fournissant des résultats de référence pour la validation CFD.

> **Du 2D au 3D — Ligne portante de Prandtl (quille et appendices)** : les résultats de Kutta-Joukowski s'appliquent à un profil d'envergure infinie. Pour une surface portante de longueur finie (quille, gouvernail) d'allongement $\mathcal{AR} = b^2/S$, la **théorie de la ligne portante** (Prandtl) donne :
> $$C_L^{3D} = \frac{2\pi(\alpha - \alpha_0)}{1 + 2/\mathcal{AR}}$$
> Pour une quille de voilier : $\mathcal{AR} \approx 1{,}5$ → $C_L^{3D} \approx 0{,}75\,C_L^{2D}$ (réduction de ~25 % par rapport au profil 2D infini). La simulation TD2 donne le $C_L^{2D}$ ; le passage au 3D réel nécessite cette correction ou une simulation 3D complète (TD3).

### 6.4 Nomenclature NACA

Les profils **NACA** (National Advisory Committee for Aeronautics) sont désignés par un code normalisé. Série **4 chiffres** (la plus utilisée en enseignement) :

| Position | Signification | Exemple (NACA-2412) |
|---|---|---|
| 1er chiffre | Cambrure max. en % de corde | 2 % |
| 2ème chiffre | Position cambrure max. en dixièmes de corde | 40 % |
| 3ème–4ème chiffres | Épaisseur max. en % de corde | 12 % |

| Profil | Type | Caractéristique |
|---|---|---|
| **NACA-0012** | Symétrique | Cambrure nulle, épaisseur 12 % — TD2 et Devoir Final |
| NACA-63010 | Laminaire (6ème série) | Couche limite laminaire étendue, épaisseur 10 % |
| NACA-2412 | Cambré | Profil de référence pour ailes classiques |

### 6.5 Effet Magnus

L'**effet Magnus** est la force de portance générée par la rotation d'un cylindre dans un écoulement. C'est la base du fonctionnement des rotors Flettner (propulsion vélique assistée).

Pour un cylindre en rotation : $\Gamma = 2\pi R^2 \omega$, et la portance vaut $L' = \rho U_0 \Gamma$.

### 6.6 Coefficients aérodynamiques

Les forces sur un profil sont exprimées sous forme adimensionnelle :

**Coefficient de portance** :
$$C_L = \frac{L}{\frac{1}{2}\rho U_0^2 c}$$

**Coefficient de traînée** :
$$C_D = \frac{D}{\frac{1}{2}\rho U_0^2 c}$$

où $c$ est la corde du profil.

**Traînée induite** (profil 3D, aspect ratio $AR = b/c$) :
$$C_I = \frac{C_L^2}{\pi AR_e}, \quad AR_e = \frac{b^2}{S}$$

où $b$ est l'envergure et $AR_e$ le rapport d'aspect effectif (tenant compte de l'efficacité de Oswald).

### 6.7 Formule de frottement ITTC-57

La résistance de frottement d'un profil est calculée via le **coefficient de frottement ITTC-57** (International Towing Tank Conference) :

$$C_F(Re) = \frac{0{,}075}{(\log_{10}(Re) - 2)^2}$$

La force de frottement :
$$R_F = \frac{1}{2} \rho u^2 S_m C_F(Re)$$

où $S_m$ est la surface mouillée et $Re = \rho U L / \mu$ le nombre de Reynolds.

### 6.8 Simulation CFD d'un profil NACA

Le cas de référence utilise un profil **NACA-63010** (ou NACA-0012 pour l'examen). Les étapes de simulation sont :
1. Génération de la géométrie (Rhinoceros → STL)
2. Maillage avec `blockMesh` + `snappyHexMesh`
3. Simulation avec `simpleFoam` (régime permanent) ou `pimpleFoam` (transitoire)
4. Post-traitement : champ de pression, lignes de courant, forces

![Maillage autour du profil NACA avec snappyHexMesh — vue de la couche limite](figures/P03_naca_maillage_couche_limite.png)

---

## 7. Maillage

### 7.1 Principes généraux

Le **maillage** est la discrétisation spatiale du domaine de calcul. Sa qualité conditionne directement la précision et la stabilité de la simulation.

Critères de qualité d'un maillage OpenFOAM (vérifiés avec `checkMesh`) :
- **Orthogonalité** : angle entre la normale à la face et la droite joignant les centres de cellules adjacentes — doit rester < 70° (idéalement < 40°).
- **Skewness** : déformation des cellules — doit rester < 4.
- **Aspect ratio** : rapport entre la plus grande et la plus petite dimension d'une cellule.

### 7.2 `blockMesh` — maillage structuré

**`blockMesh`** génère des maillages hexaédriques structurés par blocs. La configuration est définie dans `system/blockMeshDict`.

Éléments clés :
- **`vertices`** : coordonnées des sommets du domaine
- **`blocks`** : définition de chaque bloc hexaédrique (8 sommets + nombre de cellules + graduation)
- **`edges`** : arêtes courbes (arc de cercle, spline...)
- **`boundary`** : association patch ↔ type de condition aux limites

Syntaxe d'un bloc :
```c
blocks
(
    hex (0 1 2 3 4 5 6 7) (Nx Ny Nz) simpleGrading (gx gy gz)
);
```

La **graduation** (*grading*) permet de raffiner le maillage près des parois :
- `simpleGrading (1 10 1)` : facteur 10 dans la direction y (compression vers les parois)
- `edgeGrading` : contrôle indépendant de chaque arête

**Fonctionnalités avancées de blockMesh** :
- **Multiblocs** : décomposition du domaine en plusieurs blocs pour des géométries complexes
- **Multigradation** : plusieurs gradations par arête
- Variables via `#calc` : `Lkw #calc "-1.0 * $kw * $L";`

### 7.3 `snappyHexMesh` — maillage de géométries complexes

**`snappyHexMesh`** (SHM) génère des maillages non structurés autour de géométries arbitraires (format STL). Il fonctionne en trois phases :

1. **`castellatedMesh`** : découpe les cellules du maillage de fond qui intersectent la géométrie STL, selon les niveaux de raffinement définis.
2. **`snap`** : déplace les nœuds du maillage pour épouser exactement la surface STL.
3. **`addLayers`** : génère des couches prismatiques (couche limite) contre les parois.

Configuration dans `system/snappyHexMeshDict` :
```c
castellatedMeshControls
{
    resolveFeatureAngle     30;    // REQUIS v2412 — erreur fatale si absent
    maxLocalCells           2000000;
    maxGlobalCells          5000000;
    nCellsBetweenLevels     3;

    refinementSurfaces
    {
        wing { level (4 5); }    // nom du patch dans le fichier STL
    }
    refinementRegions
    {
        refinementBox { mode inside; levels ((1E15 3)); }
    }
}

snapControls
{
    nSmoothPatch        3;
    tolerance           2.0;
    nSolveIter          100;
    nRelaxIter          5;
    implicitFeatureSnap true;
}

addLayersControls
{
    relativeSizes       false;
    layers
    {
        wing { nSurfaceLayers 4; }
    }
    expansionRatio          1.3;
    firstLayerThickness     0.0015;
    minThickness            0.0001;
    // v2412 : paramètre renommé minMedialAxisAngle (ancienne orthographe minMedianAxisAngle)
    minMedialAxisAngle      90;
}
```

### 7.4 Extraction des arêtes caractéristiques

Avant de lancer SHM, il est recommandé d'extraire les arêtes vives de la géométrie STL avec **`surfaceFeatureExtract`** pour améliorer la qualité du maillage au niveau des discontinuités :

```
Carena.stl
{
    extractionMethod    extractFromSurface;
    extractFromSurfaceCoeffs { includedAngle 150; }
    subsetFeatures { nonManifoldEdges yes; openEdges yes; }
    writeObj yes;
}
```

### 7.5 `topoSet` et `refineMesh`

Pour raffiner sélectivement des régions du domaine sans passer par SHM, on peut combiner :
- **`topoSet`** : sélectionne des cellules selon des critères géométriques et les nomme
- **`refineMesh`** : divise les cellules sélectionnées selon des directions contrôlées

```bash
topoSet -dict system/topoSetDict.i
refineMesh -dict system/refineMeshDict -overwrite
```

Le fichier `topoSetDict` définit une boîte de raffinement :
```c
actions
(
    { name c0; type cellSet; action new; source boxToCell;
      sourceInfo { box (minX minY minZ) (maxX maxY maxZ); } }
);
```

---

## 8. Configuration d'une Simulation

### 8.1 Propriétés de transport

Le fichier `constant/transportProperties` définit les propriétés physiques du fluide.

Pour une simulation monophasique (eau ou air) :
```c
transportModel  Newtonian;
nu              nu [0 2 -1 0 0 0 0] 1e-6;
```

Pour une simulation **multiphasique** (eau + air) :
```c
phases (water air);

water
{
    transportModel  Newtonian;
    nu    nu [0 2 -1 0 0 0 0] 1.0034e-06;
    rho   rho [1 -3 0 0 0 0 0] 1025;
}

air
{
    transportModel  Newtonian;
    nu    nu [0 2 -1 0 0 0 0] 1.48e-05;
    rho   rho [1 -3 0 0 0 0 0] 1;
}

sigma  sigma [1 0 -2 0 0 0 0] 0.0;
```

La tension de surface $\sigma$ est mise à 0 dans ce cours (on néglige les effets capillaires à l'échelle d'un navire).

### 8.2 Conditions aux limites courantes

| Type | Utilisation | Description |
|---|---|---|
| `fixedValue` | Inlet vitesse | Valeur imposée |
| `zeroGradient` | Outlet pression, parois scalaires | Gradient nul (flux nul) |
| `noSlip` | Parois solides | $\mathbf{u} = \mathbf{0}$ |
| `inletOutlet` | Sorties mixtes | Zéro-gradient si sortie, valeur fixe si entrée |
| `fixedFluxPressure` | Inlet pression (multiphase) | Gradient ajusté selon le flux imposé |
| `symmetry` | Plans de symétrie | Composante normale nulle |
| `empty` | Faces 2D (avant/arrière) | Ignorer en 2D |
| `pressureInletOutletVelocity` | Atmosphère (top) | Adaptatif selon la pression |

### 8.3 Modélisation de la turbulence — RANS k-ω SST

Pour les simulations turbulentes (nombres de Reynolds élevés), on utilise le modèle **k-ω SST** (*Shear Stress Transport*), qui combine k-ε loin des parois et k-ω près des parois.

Variables supplémentaires à résoudre :
- **$k$** : énergie cinétique turbulente $[\mathrm{m}^2/\mathrm{s}^2]$
- **$\omega$** : taux de dissipation spécifique $[\mathrm{s}^{-1}]$
- **$\nu_t$** : viscosité turbulente $[\mathrm{m}^2/\mathrm{s}]$

Conditions initiales turbulentes à partir de l'intensité turbulente $Tu$ et du ratio $\nu_t/\nu$ :

$$k = \frac{3}{2}(U \cdot Tu)^2, \quad \omega = \frac{\rho k}{\mu} \cdot \frac{1}{\nu_t/\nu}$$

Fichier `system/turbulenceProperties` :
```c
simulationType  RAS;
RAS { RASModel kOmegaSST; turbulence on; printCoeffs on; }
```

### 8.4 Couche limite et y+

La **couche limite** est la région de l'écoulement proche de la paroi où les effets visqueux dominent. Sa résolution requiert un maillage très fin.

Le paramètre **$y^+$** caractérise la distance adimensionnelle à la paroi de la première cellule :
$$y^+ = \frac{u_\tau y}{\nu}, \quad u_\tau = \sqrt{\tau_w / \rho}$$

| Stratégie | $y^+$ requis | Approche |
|---|---|---|
| Résolution complète | $y^+ < 1$ | Maillage très fin, coûteux |
| Fonctions de paroi | $30 < y^+ < 300$ | Modèle semi-empirique, efficace |

Pour les simulations de résistance navire, on utilise typiquement les **fonctions de paroi** avec $y^+ \in [30, 300]$.

Fonctions de paroi disponibles dans OpenFOAM :
- `kqRWallFunction` (pour $k$)
- `omegaWallFunction` (pour $\omega$)
- `nutkWallFunction` ou `nutkRoughWallFunction` (pour $\nu_t$)

Pour la rugosité de surface (pleine échelle) :
```c
Carena
{
    type  nutkRoughWallFunction;
    Ks    uniform 150e-6;  // hauteur de rugosité (m) — acier commercial neuf, ITTC pleine échelle
    Cs    uniform 0.5;
}
```

### 8.5 Fichier `system/controlDict`

```c
application     simpleFoam;       // ou icoFoam, pimpleFoam, interFoam...
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         500;
deltaT          1;
writeControl    timeStep;
writeInterval   50;
runTimeModifiable yes;

functions
{
    forces
    {
        type        forces;
        libs        (forces);          // v2412 ESI : sans guillemets ni .so
        patches     (wing);            // nom du patch (wing pour TD2, Carena pour TD3)
        rho         rhoInf;
        rhoInf      1.225;             // air pour TD2 ; utiliser 1025 pour TD3
        CofR        (0 0 0);
    }
}
```

### 8.6 Schémas numériques (`fvSchemes`)

```c
ddtSchemes    { default Euler; }
gradSchemes   { default Gauss linear; }
divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss upwind;
    div(phi,omega)  Gauss upwind;
}
laplacianSchemes { default Gauss linear corrected; }
```

---

## 9. Lancer et Monitorer une Simulation

### 9.1 Solveurs OpenFOAM courants

| Solveur | Type | Application |
|---|---|---|
| `icoFoam` | Transitoire, laminaire | Poiseuille, faibles Re |
| `simpleFoam` | Permanent (RANS) | Profil, résistance visqueuse |
| `pimpleFoam` | Transitoire (RANS) | Simulation instationnaire |
| `interFoam` | Transitoire multiphasique | Surface libre, résistance navire |

### 9.2 Workflow typique pour un profil

```bash
# 1. Générer le maillage de fond
blockMesh

# 2. Générer le maillage final
snappyHexMesh -overwrite

# 3. Vérifier le maillage
checkMesh

# 4. Lancer la simulation en régime permanent
simpleFoam > simpleFoam.log &

# 5. Monitorer la convergence
foamMonitor -l postProcessing/residuals/0/solverInfo.dat
```

### 9.3 `mapFields` — initialisation depuis une solution existante

Pour accélérer la convergence, on peut initialiser la simulation transitoire à partir de la solution stationnaire :

```bash
mapFields ../simpleFoam_case -sourceTime latestTime
```

Cela projette les champs ($\mathbf{u}$, $p$, $k$, $\omega$...) depuis le cas source sur le maillage du cas courant.

### 9.4 Calcul parallèle

Pour les cas 3D coûteux, OpenFOAM utilise **MPI** pour paralléliser sur plusieurs processeurs.

**Étape 1** : décomposer le domaine (fichier `system/decomposeParDict`) :
```c
numberOfSubdomains  4;
method  scotch;    // ou simple, hierarchical
```

**Étape 2** : décomposer le maillage et les champs :
```bash
decomposePar
```

**Étape 3** : lancer en parallèle :
```bash
mpirun -np 4 simpleFoam -parallel > simpleFoam.log &
```

**Étape 4** : reconstruire les résultats :
```bash
reconstructPar
```

La méthode **scotch** optimise automatiquement la partition du domaine pour minimiser les communications entre processeurs.

### 9.5 Monitoring de la convergence

Les **résidus** (erreur résiduelle à chaque itération) doivent décroître au moins de 3 décades pour considérer la solution convergée. On les surveille avec :

```bash
foamMonitor -l postProcessing/residuals/0/solverInfo.dat
```

ou directement dans le fichier de log :
```bash
tail -f simpleFoam.log | grep "Solving for"
```

---

## 10. Post-traitement

### 10.1 ParaView

**ParaView** est l'outil de visualisation standard pour OpenFOAM. On le lance depuis le répertoire du cas après avoir créé un fichier `.foam` :

```bash
touch case.foam
paraview case.foam &
```

Opérations de base dans ParaView :
- **Contours** : distribution de pression $p$, vitesse $|\mathbf{u}|$, champ alpha $\alpha$
- **Streamlines** : lignes de courant (filtre *Stream Tracer*)
- **Slices** : coupes transversales du domaine 3D
- **Clip** : découpe du domaine pour visualiser l'intérieur
- **Glyph** : représentation vectorielle de champs (vecteurs vitesse)
- **Calculator** : calcul de grandeurs dérivées (coefficient de pression, hauteur de surface libre)
- **Reflect** : miroir du domaine (exploiter la symétrie)

![Exemple de visualisation du champ de pression autour d'un profil NACA (ParaView)](figures/P04_paraview_naca_pression.png)

### 10.2 Post-processing avec `postProcess`

OpenFOAM fournit des utilitaires de post-traitement en ligne de commande :

```bash
# Calculer les forces sur un patch
postProcess -func forces -latestTime

# Calculer les coefficients de frottement y+
postProcess -func yPlus -latestTime

# Calculer les contraintes pariétales
postProcess -func wallShearStress -latestTime
```

Les résultats sont écrits dans `postProcessing/forces/0/force.dat` avec le format :
```
# Time   Fp(x y z)   Fv(x y z)
1.0      (-1200 0 0)  (-300 0 0)
```

### 10.3 Gnuplot et Python

Pour tracer les courbes de résidus ou de forces, on peut utiliser **gnuplot** ou **Python** :

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('postProcessing/forces/0/force.dat',
                 sep=r'\s+', comment='#',
                 names=['t','Fpx','Fpy','Fpz','Fvx','Fvy','Fvz'])

plt.plot(df['t'], df['Fpx'] + df['Fvx'], label='Fx total')
plt.xlabel('Temps (s)')
plt.ylabel('Force (N)')
plt.legend()
plt.savefig('forces.png', dpi=150)
```

---

## 11. Vérification et Validation

### 11.1 Définitions

- **Vérification** : s'assurer que le code résout correctement les équations mathématiques (convergence de maillage, convergence en pas de temps).
- **Validation** : s'assurer que les équations mathématiques représentent correctement la physique réelle (comparaison avec mesures expérimentales).

### 11.2 Étude de convergence de maillage (GCI)

La **méthode GCI** (*Grid Convergence Index*) quantifie l'incertitude numérique liée au maillage.

**Protocole (3 maillages fin/moyen/grossier, rapport $r = h_1/h_2 \approx 1{,}5$) :**

**Étape 1** — Ordre de convergence apparent :
$$p = \frac{\ln\!\left(\dfrac{f_3 - f_2}{f_2 - f_1}\right)}{\ln r}$$
où $f_1$, $f_2$, $f_3$ sont les valeurs de la quantité d'intérêt sur les maillages fin, moyen, grossier.

**Étape 2** — Extrapolation de Richardson (valeur exacte estimée) :
$$f^* \approx f_1 + \frac{f_1 - f_2}{r^p - 1}$$

**Étape 3** — Indice GCI (incertitude relative) :
$$\text{GCI}_{21} = \frac{F_s \, |e_{21}|}{r^p - 1}, \quad e_{21} = \frac{f_1 - f_2}{f_1}, \quad F_s = 1{,}25$$

**Critère** : GCI < 3 % → solution suffisamment convergée en maillage.

Si $\text{GCI}_{32} / (r^p \cdot \text{GCI}_{21}) \approx 1$ : convergence asymptotique confirmée.

### 11.3 Validation expérimentale

On compare les résultats CFD aux données expérimentales disponibles :
- **Coefficients de portance et traînée** pour un profil → comparaison avec polaires expérimentales
- **Résistance à l'avancement** → comparaison avec essais en bassin ou séries systématiques (Delft, Holtrop)

L'accord attendu en régime turbulent (RANS k-ω SST) est typiquement de **±5–10 %** sur les forces.

---

## 12. Fonctionnalités Avancées — Maillages Mobiles

### 12.1 Types de maillages mobiles

OpenFOAM propose trois approches pour simuler des géométries en mouvement :

| Approche | Principe | Application |
|---|---|---|
| **Morphing (ALE)** | Le maillage se déforme avec le mouvement | Tangage, pilonnement d'un navire |
| **Glissant (AMI/cyclicAMI)** | Zone de glissement entre deux régions de maillage | Rotation de propulseur |
| **Overset** | Maillages superposés avec interpolation | Corps en grands déplacements |

### 12.2 Maillage morphing — `rigidBodyMotion`

#### Principe

Le **maillage morphing** (ALE — *Arbitrary Lagrangian-Eulerian*) déforme le maillage de fond pour suivre le mouvement d'une frontière solide. Contrairement à l'AMI et à l'overset, **le maillage reste connexe** mais ses cellules se déforment. Il est bien adapté aux **petits déplacements** (tangage et pilonnement d'un navire).

Applications : simulation du tangage (*pitch*, rotation Ry) et du pilonnement (*heave*, translation Pz) d'un navire sous l'effet de la résistance et du moment de redressement.

En **OpenFOAM v2412 ESI**, le solveur de corps rigides est `rigidBodyMotion` (remplace l'ancien `sixDoFRigidBodyMotion` des versions antérieures) :

```c
dynamicFvMesh       dynamicMotionSolverFvMesh;
motionSolverLibs    (rigidBodyMeshMotion);   // v2412 : sans guillemets
motionSolver        rigidBodyMotion;

rigidBodyMotionCoeffs
{
    report    yes;
    solver    { type Newmark; }

    bodies
    {
        Carena
        {
            type            rigidBody;
            parent          root;
            mass            14525;
            inertia         ( 40 0 0  262400 0  262400 );
            centreOfMass    (0 0 0);   // requis v2412 — position dans le repère local du corps
            transform       (1 0 0  0 1 0  0 0 1) (5.87 0 0.5);

            joint
            {
                type    composite;
                joints  ( { type Pz; }   // pilonnement
                          { type Ry; } ); // tangage
            }

            // Contraintes — limiter l'amplitude de déplacement
            constraints
            {
                maxHeave
                {
                    sixDoFRigidBodyMotionConstraint    line;
                    centreOfRotation (0 0 0);
                    direction        (0 0 1);  // autoriser uniquement Pz
                }
            }

            // Amortisseurs — stabiliser le transitoire initial
            restraints
            {
                heaveSpring { sixDoFRigidBodyMotionRestraint linearSpring; stiffness 1e4; damping 2e3; refAttachmentPt (0 0 0); }
            }
        }
    }

    // Relaxation initiale du mouvement (progressif sur les 10 premières secondes)
    accelerationRelaxation  0.4;
    accelerationDamping     0.9;
}
```

**Solveur de corps rigide (intégrateur temporel)** : le schéma `Newmark` (implicite, inconditionnellement stable) est recommandé pour les simulations navire. Il résout :
$$M\ddot{x} + C\dot{x} + Kx = F_{fluide}(t)$$
où $M$ est la masse, $C$ l'amortissement, $K$ la rigidité de rappel (restauration hydrostatique), et $F_{fluide}$ la force exercée par le fluide à chaque pas de temps.

> **Intégrateur `symplectic`** (alternatif à Newmark) : schéma explicite conservant l'énergie — adapté aux corps libres sans amortisseur. Plus sensible au pas de temps mais plus rapide par itération. Préférer Newmark pour les simulations longues avec amortisseurs (configuration TD3).

**Ordres de grandeur des paramètres physiques** pour le voilier 17 m (TD3) :

| Paramètre | Valeur | Unité |
|---|---|---|
| `mass` | 14 525 | kg |
| `centreOfMass` | (5,87  0  0,5) | m |
| `inertia` $I_{xx}$ (roulis) | 40 | kg·m² |
| `inertia` $I_{yy}$ (tangage) | 262 400 | kg·m² |
| Amortisseur `heaveSpring` | k = 10 000 N/m, d = 2 000 N·s/m | — |

$I_{yy} \gg I_{xx}$ reflète la géométrie allongée du navire (17 m) : le tangage est très amorti, le roulis très peu.

### 12.3 Maillage glissant — AMI (*Arbitrary Mesh Interface*)

#### Principe

L'**AMI** découpe le domaine en deux régions de maillage indépendantes séparées par une interface glissante. Les deux maillages ne doivent **pas** correspondre géométriquement sur l'interface — OpenFOAM interpole les champs de part et d'autre à chaque pas de temps. Le maillage ne se déforme pas : la région intérieure tourne ou translate librement.

```
     Domaine extérieur (fixe)
  ┌──────────────────────────────┐
  │        ┌──────────┐         │
  │        │ Zone AMI │  ←───── interface cyclicAMI
  │        │ (rotor)  │         │
  │        └──────────┘         │
  └──────────────────────────────┘
```

**Applications navales :** simulation d'hélice en eau libre (TP Propulseur), safran oscillant, rotor Flettner.

#### Configuration `constant/dynamicMeshDict`

```c
dynamicFvMesh    dynamicMotionSolverFvMesh;
motionSolverLibs (fvMotionSolvers);
motionSolver     solidBody;

solidBodyMotionFunctions
{
    rotor
    {
        solidBodyMotionFunction  rotatingMotion;
        rotatingMotionCoeffs
        {
            CofR        (0 0 0);        // centre de rotation
            omega       omega [0 0 -1 0 0 0 0] 20.94;  // rad/s (200 RPM)
        }
    }
}
```

#### Patches `constant/polyMesh/boundary`

La paire d'interfaces AMI se déclare en `cyclicAMI` :

```c
AMI_rotor               // face intérieure (zone tournante)
{
    type            cyclicAMI;
    nFaces          1200;
    startFace       450000;
    matchTolerance  0.001;
    neighbourPatch  AMI_stator;
    transform       noOrdering;
}
AMI_stator              // face extérieure (zone fixe)
{
    type            cyclicAMI;
    nFaces          1200;
    startFace       451200;
    matchTolerance  0.001;
    neighbourPatch  AMI_rotor;
    transform       noOrdering;
}
```

#### Conditions aux limites `0/U` sur les patches AMI

```c
AMI_rotor   { type    cyclicAMI; value uniform (0 0 0); }
AMI_stator  { type    cyclicAMI; value uniform (0 0 0); }
```

> Tous les champs résolus ($U$, $p$, $k$, $\omega$, $\nu_t$) doivent déclarer les deux patches AMI avec le type `cyclicAMI`.

#### Paramètre `fvSchemes` — terme de correction de flux AMI

```c
divSchemes
{
    div(phi,U)   Gauss linearUpwindV grad(U);  // "V" requis en AMI pour correction flux
    ...
}
```

#### Points de vigilance

| Problème | Cause | Remède |
|---|---|---|
| Mismatch AMI à t=0 | Maillages non alignés initialement | Vérifier `checkMesh` et `matchTolerance` |
| Flux non conservatif | Mauvais signe `omega` | Vérifier sens de rotation avec ParaView |
| Divergence au démarrage | AMI avec `adjustTimeStep` | Démarrer avec petit $\Delta t$, puis `maxCo` progressif |

---

### 12.4 Maillage overset (*Chimère*)

#### Principe

Le maillage **overset** (ou *Chimère*) superpose un **maillage composant** (fin, autour de l'objet) sur un **maillage de fond** (fixe, couvre tout le domaine). OpenFOAM identifie les cellules du maillage de fond masquées par l'objet (*holes*) et les exclut du calcul. Les valeurs aux frontières entre maillages sont interpolées.

```
Maillage de fond (background)          Maillage composant (component)
┌──────────────────────────┐            ┌──────────┐
│  ░░░░░░░░░░░░░░░░░░░░░   │   +        │  ┌────┐  │
│  ░░░  HOLE (exclu)  ░░░  │            │  │quil│  │
│  ░░░░░░░░░░░░░░░░░░░░░   │            │  └────┘  │
│  ──── fringe cells ────  │            │ fringe   │
└──────────────────────────┘            └──────────┘
```

**Avantage clé** : le maillage ne se déforme jamais — l'objet peut se déplacer librement (rotation complète, translation illimitée) sans dégradation de la qualité du maillage.

**Applications navales :** manœuvrabilité (gouvernail en grands angles), appendice en mouvement (quille basculante, dérive soulevée), simulation d'entrée de navire dans un port.

#### Workflow de mise en place

1. Générer le maillage de fond (`blockMesh` ou SHM) avec le domaine complet.
2. Générer le maillage composant autour de l'objet (SHM) dans ses propres `0/`, `constant/`, `system/`.
3. Combiner avec `mergeMeshes` :
   ```bash
   mergeMeshes backgroundMesh componentMesh -overwrite
   ```
4. Déclarer les patches `overset` dans `constant/polyMesh/boundary`.
5. Configurer `constant/dynamicMeshDict` avec `oversetFvMesh`.

#### Configuration `constant/dynamicMeshDict`

```c
dynamicFvMesh   oversetFvMesh;

oversetFvMeshCoeffs
{
    interpolation
    {
        type    trackingInverseDistance;
        // Alternative : inverseDistance (plus robuste mais plus lent)
    }

    // Zones à exclure du calcul (trous)
    zoneWeight
    {
        background  1;   // maillage de fond : priorité 1
        component   2;   // maillage composant : priorité haute → prédomine dans la zone de l'objet
    }
}
```

#### Patches `constant/polyMesh/boundary`

```c
overset
{
    type        overset;
    nFaces      ...;
    startFace   ...;
}
```

#### Condition aux limites `0/U` sur le patch overset

```c
overset
{
    type    overset;
    value   uniform (0 0 0);
}
```

> Tous les champs doivent déclarer le patch `overset` avec `type overset;` — c'est une condition spéciale qui délègue la valeur à l'interpolation entre maillages.

#### `fvSchemes` — correction pour overset

```c
interpolationSchemes
{
    default cell;
    interpolate(U) cellPoint;  // interpolation plus précise pour overset
}
```

#### Comparaison des trois approches

| Critère | Morphing (ALE) | AMI | Overset |
|---|---|---|---|
| Maillage | Se déforme | Deux zones indépendantes | Superposition |
| Amplitude de mouvement | Petite (< 10 % de maille) | Illimitée (rotation/translation) | Illimitée |
| Qualité maillage | Se dégrade avec le mouvement | Toujours bonne | Toujours bonne |
| Coût additionnel | Faible | Faible | Élevé (interpolation) |
| Cas typique | Tangage/pilonnement navire | Hélice, rotor Flettner | Manœuvrabilité, grandes rotations |
| Dans ce cours | **TD3 voilier** | **TP Propulseur** | Référence uniquement |

---

## 13. Résistance du Navire — Bases

### 13.1 Composantes de la résistance

La **résistance à l'avancement** (ou traînée) est la force qui s'oppose au mouvement du navire. Elle se décompose en plusieurs termes selon leur origine physique :

**Phénomènes visqueux** (gouvernés par le nombre de Reynolds $Re$) :
- **Résistance de frottement** $R_F$ : forces tangentielles (contraintes de cisaillement) sur la coque
  - Frottement de peau (*skin friction*) $R_F^{plate}$
  - Effet de forme sur le frottement de peau (*form effect*)
- **Résistance de pression visqueuse** $R_{VP}$ : différence de pression avant/arrière liée à la viscosité

**Phénomènes de surface libre** (gouvernés par le nombre de Froude $Fr$) :
- **Résistance de vagues** $R_W$ : énergie dissipée dans la génération du système de vagues

**Autres composantes** :
- Traînée induite des appendices (quille, safran, hydrofoils)
- Résistance aérodynamique au-dessus de la flottaison

$$R_{total} = R_F + R_{VP} + R_W + R_{autres}$$

En CFD visqueux (OpenFOAM), la résistance est calculée directement comme l'intégrale des contraintes sur la coque :
$$\mathbf{R}_\tau = \int_\Omega \tau(\mathbf{x}) \, \mathrm{d}\Omega \quad \text{(frottement)}$$
$$\mathbf{R}_p = \int_\Omega p(\mathbf{x}) \, \mathbf{n}(\mathbf{x}) \, \mathrm{d}\Omega \quad \text{(pression)}$$

### 13.2 Résistance visqueuse — Reynolds

Le nombre de Reynolds du navire :
$$Re = \frac{\rho U L}{\mu}$$

| $Re$ | Type d'écoulement | Forces dominantes |
|---|---|---|
| $Re < 2300$ | Laminaire | Visqueuses |
| $2300 < Re < 10^6$ | Transition | — |
| $10^6 < Re$ | Turbulent | Inertielles |

Pour un voilier navigant, $Re \gg 10^6$ → régime pleinement turbulent.

**Coefficient de frottement ITTC-57** (Hugues) :
$$C_F(Re) = \frac{0{,}075}{(\log_{10}(Re) - 2)^2}$$

**Force de frottement de peau** :
$$R_F = \frac{1}{2} \rho u^2 S_m C_F(Re)$$

où $S_m$ est la surface mouillée.

Les fluides newtoniens vérifient $\tau = 2\mu\varepsilon$ (contrainte tangentielle proportionnelle au gradient de déformation), à la différence des fluides non-newtoniens (plastique de Bingham, pseudoplastique, dilatant) pour lesquels $\mu = \mu(\varepsilon)$.

### 13.3 Résistance de vagues — Froude

La **résistance de vagues** est due aux vagues générées lors du déplacement du navire à l'interface eau/air. Elle est gouvernée par le **nombre de Froude** :
$$Fr = \frac{u}{\sqrt{g L}}$$

Le système de vagues d'un navire en régime de déplacement ($Fr < 0{,}4$) est décrit par le **motif de Kelvin** : interférence de systèmes de vagues transverses et divergents, avec un angle constant $\theta_K = 19{,}47°$ indépendant de la vitesse.

Pour $Fr < 0{,}4$, quatre systèmes de vagues coexistent :
- Système de vagues de l'étrave
- Système de vagues de l'épaulement avant (*bow shoulder*)
- Système de vagues de l'épaulement arrière (*stern shoulder*)
- Système de vagues de la poupe

Pour les voiliers (courbe des aires sans épaulements), les systèmes d'épaulements sont quasi absents.

La vitesse de propagation d'une vague de longueur d'onde $\lambda$ :
$$v = \sqrt{\frac{g\lambda}{2\pi}}$$

### 13.4 Classification ITTC de la résistance (bassin)

En essai en bassin, la résistance est décomposée classiquement en :
- **Résistance de peau** (*skin friction*) : calculée via ITTC-57 au nombre de Reynolds du modèle $Re'$
- **Résistance résiduelle** $R_R$ : $R_{total} - R_F(Re')$ — représente les effets de vagues + pression visqueuse

La résistance résiduelle est transposée à l'échelle réelle en supposant qu'elle ne dépend que du nombre de Froude.

Deux composantes supplémentaires importantes pour un voilier à voile :

**Résistance de gîte $\Delta R_{heel}(\varphi)$** : lorsque le voilier gîte sous l'effet de la voile, la forme immergée de la carène devient asymétrique, augmentant la résistance. Typiquement +5 à +15 % à $\varphi = 20°$. Ce terme entre dans la boucle VPP (§19.4).

**Résistance surajoutée en vagues $R_{AW}$** : résistance due aux mouvements de tangage et pilonnement en mer formée. Peut dépasser la résistance de vagues $R_W$ par conditions sévères. Évaluée par simulation interFoam avec houle incidente ou par formules empiriques (méthode de Salvesen).

**Loi de similitude de Froude** — transposition modèle → échelle réelle :
$$\frac{v'}{\sqrt{g L'}} = \frac{v}{\sqrt{g L}} \quad \Rightarrow \quad L' = L\left(\frac{v'}{v}\right)^2$$

Exemple : voilier 17 m ($L = 17$ m, $v = 3{,}874$ m/s). Modèle à l'échelle 1/25 : $L' = 0{,}68$ m, vitesse d'essai $v' = 3{,}874/\sqrt{25} = 0{,}775$ m/s. La résistance résiduelle (adimensionnée par le déplacement) est supposée identique aux deux échelles pour le même $Fr$.

![Classification des composantes de résistance du navire](figures/P05_classification_resistance_navire.png)

### 13.5 Méthodes de calcul de la résistance

| Méthode | Principe | Limites |
|---|---|---|
| **Essai en bassin** | Modèle réduit tracté à vitesse variable | Coûteux, contraintes de taille |
| **Séries systématiques** | Formules empiriques (Delft, 60 Series, NTUA, Naples) | Valable dans la plage de paramètres |
| **Régression Holtrop** | Régression sur navires réels (Holtrop & Mennen) | Précision ±5–15 % |
| **Théorie du potentiel** | Résistance de vagues sans viscosité | Ne donne pas la résistance visqueuse |
| **CFD** | Simulation complète N-S | Approche de référence de ce cours |

**Méthode Holtrop-Mennen** — décomposition de la résistance totale :
$$R_T = R_F(1+k_1) + R_{APP} + R_W + R_B + R_{TR} + R_A$$

| Terme | Signification |
|---|---|
| $R_F(1+k_1)$ | Friction ITTC-57 + facteur de forme coque |
| $R_{APP}$ | Appendices (quille, gouvernail, safran) |
| $R_W$ | Résistance de vagues (Froude) |
| $R_B + R_{TR}$ | Bosse de proue + tableau arrière |
| $R_A$ | Corrélation modèle-bateau |

La simulation interFoam capture directement $R_F + R_W$ ; $R_{APP}$ est estimé séparément si les appendices ne sont pas maillés. Précision typique de Holtrop : ±5–15 %.

**Série de Delft III** — Keuning & Sonnenberg, 2001 (résistance résiduelle des voiliers) :
$$\frac{R_R}{\Delta} = a_0 + a_1 C_p + a_2 \frac{\text{LCB}}{L_{wl}} + a_3 \frac{B_{wl}}{T_c} + a_4 \frac{L_{wl}}{\nabla^{1/3}} + a_5 C_p^2 + a_6 \left(\frac{B_{wl}}{T_c}\right)^2 + a_7 \frac{L_{wl}}{\nabla^{1/3}} C_p + a_8 \frac{L_{wl}}{\nabla^{1/3}} \frac{B_{wl}}{T_c} + a_9 \left(\frac{L_{wl}}{\nabla^{1/3}}\right)^2$$

Les coefficients $a_0, \ldots, a_9$ sont tabulés par nombre de Froude dans la référence [6] (table disponible dans Keuning & Sonnenberg 2001). Plage de validité :

| Paramètre | Min | Max |
|---|---|---|
| $Fr$ | 0,125 | 0,45 |
| $L_{wl}/\nabla^{1/3}$ | 2,73 | 5,09 |
| $B_{wl}/T_c$ | 2,46 | 9,01 |
| $C_p$ | 0,52 | 0,60 |
| $\text{LCB}/L_{wl}$ | −0,04 | +0,04 |

Les paramètres géométriques du voilier de 17 m : $L_{wl}/\nabla^{1/3} \approx 4{,}12$, $B_{wl}/T_c \approx 4{,}57$, $C_p \approx 0{,}56$ — dans la plage de validité de la série.

---

## 14. Cas d'Étude — Voilier 17 m

### 14.1 Caractéristiques du navire

Le cas d'application de la seconde partie du cours est un **voilier de 17 m** (Carena). Les valeurs de référence bibliographique (PDF Navalapp) et les valeurs utilisées dans la simulation numérique (TD3, fichiers validés v2412) sont :

| Grandeur | PDF Navalapp | Simulation TD3 |
|---|---|---|
| Longueur entre perpendiculaires $L_{pp}$ | 16,25 m | **17 m** |
| Largeur au plan de flottaison $B_{wl}$ | 4,64 m | **4,62 m** |
| Tirant d'eau $T$ | 1,1 m | **1,01 m** |
| Masse déplacée | — | **14 525 kg** |
| Surface mouillée $S_m$ | 60,82 m² | 60,82 m² |
| Vitesse de remorquage $u$ | 3,784 m/s | **3,874 m/s** |

> Les calculs analytiques et numériques de ce chapitre utilisent les **valeurs TD3** (simulation validée). Les valeurs PDF sont fournies à titre de comparaison.

### 14.2 Modélisation géométrique

La géométrie est modélisée sous **Rhinoceros** et exportée au format **STL** pour le maillage avec `snappyHexMesh`.

Le nombre de Reynolds (valeurs TD3) :
$$Re = \frac{\rho u L_{pp}}{\mu} = \frac{1025 \times 3{,}874 \times 17}{1{,}0254 \times 10^{-3}} \approx 6{,}60 \times 10^7$$

Le coefficient de frottement ITTC-57 :
$$C_F = \frac{0{,}075}{(\log_{10}(6{,}60 \times 10^7) - 2)^2} \approx 2{,}20 \times 10^{-3}$$

La résistance de frottement ITTC estimée :
$$R_F = \frac{1}{2} \rho u^2 S_m C_F = \frac{1}{2} \times 1025 \times 3{,}874^2 \times 60{,}82 \times 2{,}20 \times 10^{-3} \approx 1{,}02 \text{ kN}$$

Le nombre de Froude :
$$Fr = \frac{3{,}874}{\sqrt{9{,}81 \times 17}} \approx 0{,}300$$

Ce nombre de Froude correspond au **régime de déplacement** ($Fr < 0{,}4$).

### 14.3 Référence : Série de Delft

Pour un voilier, la résistance de référence est fournie par la **Série Systématique de Delft** (Delft Systematic Yacht Hull Series), qui est une série empirique développée à partir d'essais en bassin de familles de coques de voiliers. Elle fournit la résistance résiduelle en fonction des paramètres géométriques : $L_{wl}/\nabla^{1/3}$, $B_{wl}/T_c$, $C_p$, LCB.

Cette référence permet de valider les résultats CFD.

---

## 15. Maillage 3D du Voilier

### 15.1 Dimensionnement du domaine

Pour capturer correctement la physique de la résistance de vagues, le domaine de calcul doit être suffisamment grand :

![Dimensionnement du domaine pour la résistance du voilier (angle de Kelvin θ=19,47°)](figures/P06_domaine_calcul_voilier.png)

- **$k_f$** (devant le navire) : typiquement $1{,}5$ à $2 \times L$
- **$k_w$** (derrière le navire) : large, pour capturer le sillage et le train de vagues
- **$b$** (largeur) : $b > k_w \times L \times \tan(19{,}47°)$ pour capturer les vagues divergentes
- **$D$** (profondeur) : selon la condition de profondeur infinie de la théorie des vagues

**Symétrie** : le navire étant symétrique par rapport au plan longitudinal, on ne modélise que **la moitié du domaine** avec une condition de symétrie sur le plan de quille. Cela réduit de moitié le coût de calcul.

### 15.2 Génération du maillage 3D

**Étape 1** : maillage de fond avec `blockMesh` (domaine hexaédrique uniforme).

**Étape 2** : extraction des arêtes de la coque :
```bash
surfaceFeatureExtract
```

**Étape 3** : maillage fin avec `snappyHexMesh` (en série ou en parallèle) :
```bash
# En série
snappyHexMesh -overwrite

# En parallèle
mpirun -np 4 snappyHexMesh -parallel > snappyHexMesh.logfile &
reconstructParMesh -mergeTol 0.000001 -constant
```

**Recommandations ITTC pour le maillage surface libre** (ITTC 7.5-03-02-03) :

Longueur d'onde au nombre de Froude de calcul :
$$\lambda = 2\pi Fr^2 L$$

| Direction | Recommandation | Valeur numérique ($Fr=0{,}30$, $L=17$ m) |
|---|---|---|
| Horizontale (direction vague) | $\delta x \leq \lambda / 40$ | $\lambda \approx 9{,}6$ m → $\delta x \leq 0{,}24$ m |
| Verticale (hauteur vague) | $\delta z \leq A_{vague} / 10$ | $A_{vague} \approx 0{,}10$ m → $\delta z \leq 0{,}01$ m |
| Transversale | $\delta y \leq \lambda / 20$ | $\delta y \leq 0{,}48$ m |

La hauteur de vague estimée : $A_{vague} \approx 0{,}005 \times L \times Fr^2$.

**Calcul de la première couche pour $y^+ \approx 50$** (fonctions de paroi) :

1. Vitesse de frottement : $u_\tau = U_\infty \sqrt{C_F / 2} \approx 3{,}874 \times \sqrt{2{,}20 \times 10^{-3} / 2} \approx 0{,}091$ m/s
2. Épaisseur première cellule : $y_1 = y^+ \times \nu / u_\tau = 50 \times 1{,}0 \times 10^{-6} / 0{,}091 \approx 5{,}5 \times 10^{-4}$ m

Cette valeur correspond au paramètre `firstLayerThickness` dans `addLayersControls`.

**Raffinement dynamique** de la surface libre dans `constant/dynamicMeshDict` :
```c
field                 alpha.water;
lowerRefineLevel      0.001;
upperRefineLevel      0.999;
unrefineLevel         10;
nBufferLayers         1;
maxRefinement         2;
maxCells              200000;
```

**Couche limite** : avec fonctions de paroi, viser $30 < y^+ < 300$.

### 15.3 Méthode alternative — blockMesh + topoSet + refineMesh

Une approche alternative au raffinement via SHM utilise :
1. **`blockMesh`** avec multi-blocs et multigradation pour raffiner la surface libre en z
2. **`topoSet` + `refineMesh`** pour créer des boîtes de raffinement autour de la coque
3. **`snappyHexMesh`** uniquement pour la phase de `snap` et `addLayers`

Avantage : contrôle plus précis des directions de raffinement. Inconvénient : les transitions entre boîtes doivent être gérées manuellement.

### 15.4 Qualité du maillage

Après génération :
```bash
checkMesh 2>&1 | tee checkMesh.log
```

**Indicateurs clés et seuils acceptables** :

| Indicateur | Idéal | Acceptable | Critique |
|---|---|---|---|
| Non-orthogonalité max. | < 40° | < 70° | > 85° → divergence |
| Non-orthogonalité moy. | < 10° | < 30° | > 45° → instabilité |
| Skewness max. | < 2 | < 4 | > 4 → oscillations |
| Rapport d'aspect max. | < 20 | < 100 | > 1000 → couche limite très fine |
| Faces concaves | 0 | 0 | Tout nombre → erreur |

**Actions correctives** :

```c
// Dans snappyHexMeshDict — relaxer les contraintes si trop de mauvaises cellules
snapControls
{
    nSolveIter          150;   // augmenter pour meilleur snap
    nRelaxIter          8;
    tolerance           4.0;   // tolérance snap plus large
}

addLayersControls
{
    nRelaxIter              5;
    nSmoothSurfaceNormals   10;
    nSmoothNormals          3;
    featureAngle            130;    // réduire si couches se croisent
    slipFeatureAngle        30;
    nGrow                   0;
    maxFaceThicknessRatio   0.5;    // réduire pour accepter moins de couches
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle      90;     // v2412 obligatoire
}
```

Après corrections SHM, **re-vérifier** avec `checkMesh` avant de lancer la simulation.

---

## 16. Configuration Simulation Multiphasique

### 16.1 Méthode VOF (*Volume of Fluid*)

Pour simuler la **surface libre** (interface eau/air), OpenFOAM utilise la méthode **VOF** (*Volume of Fluid*). Une fraction volumique $\alpha$ est définie en chaque cellule :
- $\alpha = 1$ : cellule remplie d'eau
- $\alpha = 0$ : cellule remplie d'air
- $0 < \alpha < 1$ : cellule à l'interface

Les propriétés du fluide varient continûment :
$$\rho = \alpha \rho_1 + (1-\alpha)\rho_2$$

Dans OpenFOAM, le champ VOF est nommé **`alpha.water`**.

Techniques d'interface dans le FVM :
- **Level Set Method** : interface implicite par une fonction distance signée
- **Volume of Fluid** (utilisé ici) : transport de la fraction volumique

### 16.2 Paramètres `controlDict` pour simulation multiphasique

Pour les solveurs multiphasiques, le pas de temps est contrôlé par deux nombres de Courant :
- **Co maximal global** : typiquement 10–50 pour les solveurs implicites
- **Co maximal à la surface libre** : plus restrictif pour capturer correctement l'interface

Le pas de temps maximal est limité à $\Delta t_{max} = L/(200 U)$ (ordre de grandeur de l'échelle convective). Pour Co > 10, vérifier la convergence en augmentant `nOuterCorrectors` (PIMPLE) et observer l'impact sur $R_F$.

> **Optimisation CPU** : `turbOnFinalIterOnly yes;` dans `fvSolution/PIMPLE` évite le recalcul du modèle de turbulence à chaque itération interne, économisant ~20 % de temps CPU sans dégradation notable de la précision.

### 16.3 Conditions aux limites (7 champs)

La simulation du voilier résout **7 champs** :
- $\mathbf{U}$ : vitesse
- `p_rgh` : pression corrigée ($p - \rho g h$, pratique pour les écoulements à surface libre)
- `pointDisplacement` : déplacement des nœuds du maillage (morphing)
- $k$, $\omega$, $\nu_t$ : variables turbulentes
- `alpha.water` : fraction volumique eau

Conditions aux limites :

| Patch | U | p_rgh | alpha.water |
|---|---|---|---|
| Inlet | `fixedValue (U 0 0)` | `fixedFluxPressure` | `fixedValue 1` (eau) |
| Outlet | `inletOutlet` (valeur amont si reflux) | `zeroGradient` | `variableHeightFlowRate` (avec `lowerBound 0; upperBound 1;` — requis v2412) |
| Symétrie (quille) | `symmetry` | `symmetry` | `symmetry` |
| Côté et fond | `symmetry` | `symmetry` | `symmetry` |
| Atmosphère (top) | `pressureInletOutletVelocity` | `totalPressure` | `inletOutlet 0` (air) |
| Coque (*Carena*) | `noSlip` | `fixedFluxPressure` | `zeroGradient` |

### 16.4 Initialisation de la surface libre avec `setFields`

Le fichier `system/setFieldsDict` initialise la région eau/air :
```c
defaultFieldValues ( volScalarFieldValue alpha.water 0 );

regions
(
    // boxToCell agit sur les cellules (volScalarField) — seule forme valide pour alpha.water
    // boxToFace agit sur les faces et n'est PAS valide pour un volScalarField (erreur v2412)
    boxToCell
    {
        box (-1000 -1000 -1000) (1000 1000 0.0);   // z < 0 → eau
        fieldValues ( volScalarFieldValue alpha.water 1 );
    }
);
```

Puis exécuter (en utilisant `restore0Dir` pour repartir de `0.orig/`) :
```bash
restore0Dir    # restaure 0/ depuis 0.orig/
setFields
```

### 16.5 Turbulence et rugosité de surface

Modèle k-ω SST avec fonctions de paroi rugueuses :
- `k` : `kqRWallFunction` (valeur libre ou $k = 10^{-10}$)
- `ω` : `omegaWallFunction`
- `ν_t` : `nutkRoughWallFunction` avec $K_s = 150 \times 10^{-6}$ m (rugosité pleine échelle selon ITTC)

### 16.6 Maillage morphing — pilonnement et tangage

La simulation laisse le navire libre en **pilonnement** (*heave*) et **tangage** (*pitch*) pour atteindre l'assiette d'équilibre dynamique. Le fichier `constant/dynamicMeshDict` intègre :
- Raffinement dynamique de la surface libre
- Facteur de relaxation de mouvement (introduction progressive du mouvement pour la stabilité)
- Contraintes en pilonnement et tangage (liberté des 2 DDL uniquement)

### 16.7 Solveurs `fvSolution` — spécificités multiphasiques

```c
"alpha.water.*"
{
    nAlphaCorr          2;    // nombre de corrections alpha par pas de temps
    nAlphaSubCycles     1;
    cAlpha              1;    // facteur de compression d'interface
    icAlpha             0;
    MULESCorr           yes;
    nLimiterIter        3;
    solver              smoothSolver;
    smoother            symGaussSeidel;
    tolerance           1e-8;
}
```

Option `turbOnFinalIterOnly yes` dans la configuration PIMPLE : calcule la turbulence uniquement à la dernière itération externe de chaque pas de temps → économie de ressources.

### 16.8 Schémas numériques `fvSchemes` pour interFoam — v2412

En v2412 ESI, interFoam requiert des clés **spécifiques** dans `divSchemes` (en plus des clés classiques) :

```c
divSchemes
{
    default                                         none;
    div(rhoPhi,U)                                   Gauss linearUpwind grad(U);
    div(phi,alpha.water)                            Gauss vanLeer;
    div(phi,alpha)                                  Gauss vanLeer;     // alias requis v2412
    div(phirb,alpha.water)                          Gauss linear;
    div(phirb,alpha)                                Gauss linear;      // alias requis v2412
    div(((rho*nuEff)*dev2(T(grad(U)))))             Gauss linear;      // terme visqueux rho-pondéré
    div(phi,k)                                      Gauss upwind;
    div(phi,omega)                                  Gauss upwind;
}
```

Les clés `div(phi,alpha)` et `div(phirb,alpha)` sont les alias **sans suffixe de phase** — interFoam v2412 les recherche en complément des clés `alpha.water`.

---

## 17. Lancer une Simulation Multiphasique

### 17.1 Solveur `interFoam`

La simulation multiphasique (eau + air avec surface libre) s'exécute avec le solveur **`interFoam`** :

```bash
# En série
interFoam

# En parallèle (méthode scotch recommandée)
decomposePar
mpirun -np 4 interFoam -parallel > interFoam.logfile &

# Visualisation dans ParaView
touch case.foam
paraview case.foam &
```

La méthode de décomposition **scotch** (au lieu de *simple* ou *hierarchical*) optimise la répartition de la charge de calcul entre processeurs en minimisant les communications inter-domaines.

### 17.2 Paramètres `fvSolution` — PIMPLE pour interFoam

La configuration PIMPLE contrôle le couplage pression-vitesse à chaque pas de temps :

```c
PIMPLE
{
    nOuterCorrectors            2;    // boucles PIMPLE (outer) — augmenter si Co > 1
    nCorrectors                 3;    // corrections pression interne (PISO inner)
    nNonOrthogonalCorrectors    1;
    turbOnFinalIterOnly         yes;  // calcule turb. uniquement à la dernière itération → gain CPU
    correctPhi                  yes;  // correction flux pour satisfaire continuité après morphing
    moveMeshOuterCorrectors     yes;  // autorise déplacement maillage dans chaque boucle PIMPLE
}
```

| Paramètre | Rôle | Valeur TD3 |
|---|---|---|
| `nOuterCorrectors` | Stabilité aux grands pas de temps | 2 |
| `nCorrectors` | Précision couplage P-U | 3 |
| `turbOnFinalIterOnly` | Réduction coût turbulence | yes |
| `correctPhi` | Cohérence flux / maillage mobile | yes |

### 17.3 Critère de convergence en transitoire

Pour une simulation transitoire de résistance, la simulation est considérée convergée quand les forces sur la coque atteignent un **régime quasi-stationnaire** (oscillations autour d'une valeur moyenne stable). On moyennera les forces sur les derniers pas de temps pour obtenir la résistance totale.

En pratique, on considère la simulation comme établie lorsque la variation relative de la résistance sur une fenêtre de 10 s est inférieure à 5 % :
$$\frac{|R_{t+10} - R_t|}{R_t} < 5\,\%$$

---

## 18. Post-traitement 3D

### 18.1 Visualisation de la surface libre

La surface libre correspond à l'iso-surface $\alpha = 0{,}5$.

Procédure dans ParaView :
1. Générer un plan à $\alpha = 0{,}5$ (filtre *Contour* sur le champ `alpha.water`)
2. Calculer la hauteur relative de surface libre (filtre *Calculator*) : `coordsZ - T` où $T$ est le tirant d'eau de référence
3. Nommer le champ résultant "Height"
4. Ajuster la plage de couleurs pour visualiser uniquement le train de vagues
5. Appliquer un filtre *Reflect* pour reconstruire la demi-coque symétrique

![Motif de vagues vue de dessus et en perspective — voilier 17 m](figures/P07_surface_libre_voilier.png)

### 18.2 Coefficient de pression autour de la coque

Dans interFoam, OpenFOAM résout `p_rgh` $= p - \rho g h$ (pression corrigée de la hauteur hydrostatique). Pour obtenir la pression totale et le $C_p$ correct :

$$p_{total} = p_{rgh} + \rho g z$$

$$C_p = \frac{p_{total} - p_\infty}{\frac{1}{2}\rho U^2} = \frac{p_{rgh} + \rho g z}{\frac{1}{2}\rho U^2}$$

Procédure dans ParaView :
1. Sélectionner le patch `Carena` (coque)
2. Calculer $C_p$ avec le filtre *Calculator* :
   `(p_rgh + 1025 * 9.81 * coordsZ) * 2 / (1025 * 3.874^2)`
3. Superposer le contour de surface libre ($\alpha = 0{,}5$) sur la coque pour contextualiser
4. Palette divergente Blue-White-Red centrée en $C_p = 0$ : surpression à l'étrave (rouge), dépression sur les flancs (bleu)

![Distribution du coefficient de pression autour de la coque (ParaView)](figures/P08_Cp_coque_voilier.png)

### 18.3 Lignes de courant — analogie avec les fils de laine

Pour visualiser les lignes de courant sur la carène (analogie avec les essais aux fils de laine en bassin) :

1. **Transform** : décaler légèrement la surface de la coque vers l'extérieur pour intercepter les cellules fluides
2. **Threshold** : conserver uniquement les cellules eau ($\alpha > 0{,}5$)
3. **ResampleWithDataSet** : projeter le champ vitesse du fluide sur la surface déplacée
4. **Glyph** : afficher les vecteurs vitesse comme des lignes (type *Lines*, orientation $U$, échelle adaptée)
5. **Tube** : donner une épaisseur aux lignes pour améliorer la visualisation

![Essai numérique aux fils de laine — lignes de courant sur la carène](figures/P09_fils_laine_numeriques.png)

### 18.4 Forces sur la coque

Les forces sont calculées dans le dossier `postProcessing/forces/`. On extrait la composante $x$ (direction d'avance) :
- **Composante normale** (pression) : résistance de pression = $R_{VP} + R_W$
- **Composante tangentielle** (frottement visqueux) : $R_F$
- **Force totale** : $R_{total} = R_{normale} + R_{tangentielle}$

Pour tracer l'évolution temporelle des forces (Python ou gnuplot) :

```python
import pandas as pd, matplotlib.pyplot as plt

df = pd.read_csv('postProcessing/forces/0/force.dat',
                 sep=r'\s+', comment='#')
# Colonnes : t, Fpx, Fpy, Fpz, Fvx, Fvy, Fvz, ...
Rx = df['Fpx'] + df['Fvx']
plt.plot(df['t'], Rx, 'r-', label='Rx total')
plt.xlabel('Temps (s)'); plt.ylabel('Force (N)')
plt.legend(); plt.savefig('resistance.png', dpi=150)
```

![Évolution temporelle de la résistance totale et de ses composantes](figures/P10_forces_temporelles.png)

---

## 19. Fonctionnalités Avancées Navire

### 19.1 Simulation monophasique (*single-phase*)

Dans certains cas, on peut simplifier la simulation en **évitant de résoudre la surface libre**. On utilise alors le solveur `simpleFoam` en **régime permanent**, avec la coque tronquée au niveau du plan de flottaison (modèle de *double coque*) et une condition de symétrie sur ce plan.

Avantages :
- Calcul beaucoup plus rapide (régime permanent, une seule phase)
- Permet d'obtenir rapidement la résistance visqueuse (sans résistance de vagues)

Cas d'usage : design préliminaire, validation de la couche limite, calcul des appendices (quille, safran) sans surface libre.

Le solveur **`potentialFreeSurfaceFoam`** est une variante : il résout les équations de Navier-Stokes monophasiques en ajoutant un champ de hauteur de surface libre, permettant une approximation des effets de surface libre sans VOF.

| Solveur | Surface libre | Coût relatif | Usage typique |
|---------|--------------|-------------|---------------|
| `simpleFoam` | Non (domaine coupé à la WL) | Faible | Résistance visqueuse, couche limite, appendices |
| `potentialFreeSurfaceFoam` | Approchée (1 phase + champ hauteur) | Moyen | Estimation rapide de la résistance de vagues |
| `interFoam` | VOF (2 phases eau/air) | Élevé | Résistance totale, mouvements, sillage complet |

### 19.2 Paramétrer les simulations avec `#calc` et `codeStream`

Pour automatiser la préparation des cas et éviter les erreurs de copier-coller, OpenFOAM supporte des calculs directement dans les dictionnaires.

**Directive `#calc`** (calculs arithmétiques simples) :
```c
L           17;
kw          5.5;
KelvinAngle 19.47;

Lkw   #calc "-1.0 * $kw * $L";           // longueur domaine arrière
b     #calc "1.5 * $kw * $L * tan(degToRad($KelvinAngle))";  // largeur domaine
```

**Directive `codeStream`** (code C++ compilé à la volée) : pour des calculs impliquant des fonctions ou boucles non supportées par `#calc`.

Exemple — calcul automatique de $k$ et $\omega$ depuis l'intensité turbulente :

```c
// Dans system/initialConditions ou 0.orig/k
#include "mathematicalConstants.H"

Tu      0.01;    // intensité turbulente 1 %
U       100.0;   // m/s
nutRatio 10;     // nu_t / nu

k  #codeStream
{
    codeInclude
    #{
        #include "mathematicalConstants.H"
    #};
    code
    #{
        scalar Tu     = $Tu;
        scalar U_inf  = $U;
        os << 1.5 * sqr(U_inf * Tu);    // k = 1.5 (U · Tu)²
    #};
};

omega  #codeStream
{
    code
    #{
        scalar Tu      = $Tu;
        scalar U_inf   = $U;
        scalar nutRatio = $nutRatio;
        scalar nu      = 1.5e-5;
        scalar k       = 1.5 * sqr(U_inf * Tu);
        os << k / (nu * nutRatio);       // ω = k / (ν · ν_t/ν)
    #};
};
```

> `codeStream` compile du C++ à la volée via `wmake` lors du premier lancement. Le résultat est mis en cache dans `dynamicCode/`. En cas d'erreur de compilation, supprimer `dynamicCode/` et relancer.

**Directives d'inclusion utiles :**

```c
#include "initialConditions"          // inclure depuis system/
#includeEtc "caseDicts/meshQuality"   // inclure depuis $FOAM_ETC
#includeIfPresent "localConfig"       // inclure sans erreur si absent
```

**`foamDictionary`** — modifier un dictionnaire sans éditer le fichier (utile dans les scripts) :

```bash
# Lire une valeur
foamDictionary system/controlDict -entry endTime

# Modifier une valeur à la volée (études paramétriques)
foamDictionary system/controlDict -set "endTime=200"
foamDictionary 0/U -entry internalField -set "uniform (5.0 0 0)"
```

L'approche recommandée : créer un fichier `initialConditions` contenant tous les paramètres du problème et l'inclure dans tous les fichiers de configuration via :
```c
#include "initialConditions"
```

Cela permet de **piloter l'ensemble de la simulation depuis un seul fichier**, et de lancer des études paramétriques en modifiant uniquement `initialConditions` (ou via `foamDictionary` dans un script shell).

### 19.3 VPP — Velocity Prediction Program

Le **VPP** est l'outil central de la conception de voilier : il prédit la vitesse du bateau en équilibre pour chaque condition de vent. OpenFOAM (§19.1, régime monophasique) fournit la courbe de résistance $R(V)$ qui alimente le VPP.

#### Principe — 3 équations d'équilibre

À vitesse $V$ et angle de gîte $\varphi$ stabilisés, trois équilibres sont satisfaits simultanément :

| Équation | Condition | Grandeurs |
|----------|-----------|-----------|
| $F_X = 0$ | force propulsive = résistance | $F_D(\lambda, \varphi, V_W) = R(V, \varphi)$ |
| $M_X = 0$ | moment de gîte voile = bras de redressement | $F_H \cdot h_{CE} = \Delta \cdot \overline{GZ}(\varphi)$ |
| $M_Z = 0$ | équilibre en lacet (barre nulle) | $F_{lat} = R_{lat,carène}$ |

avec :
- $F_D$ = composante propulsive de la force voile, $F_H$ = composante de gîte
- $\lambda$ = angle au vent apparent, $V_W$ = vitesse vent apparent
- $h_{CE}$ = hauteur du centre d'effort vélique
- $\overline{GZ}(\varphi)$ = bras de levier de redressement (courbe de stabilité)

#### Inconnues et procédure itérative

Inconnues : vitesse bateau $V$ et angle de gîte $\varphi$.

```
Initialiser V₀, φ₀
Tant que |ΔV| > ε  ET  |Δφ| > ε :
    1. Calculer résistance R(V, φ)       ← simpleFoam ou régression Delft/ITTC
    2. Calculer forces voile FD, FH(V_A, λ, φ)   ← polaire voile ou DES
    3. Résoudre MX = 0 → φ_new
    4. Résoudre FX = 0 → V_new
    5. V ← V_new,  φ ← φ_new
Sortie : V_bateau(λ, V_W) pour un point de vent
```

Répéter pour tous les angles $\lambda \in [30°, 180°]$ et vitesses de vent $V_W \in [6, 20\ \text{nœuds}]$ → **courbe polaire** (polar diagram).

#### Rôle d'OpenFOAM dans la boucle VPP

```
              ┌─────────────────────────────────────┐
              │  Boucle VPP (Python / Matlab)        │
              │                                     │
  Géométrie ──► simpleFoam (§19.1)                  │
  coque       │   → R_visqueux(V)                   │
              │                                     │
  Géométrie ──► potentialFreeSurfaceFoam / Delft III │
  carène      │   → R_vagues(V, Fr)                 │
              │                                     │
              │  R_total = R_vis + R_vagues          │
              │  → résoudre FX=0, MX=0              │
              └──────────────► V_bateau, φ ──────────►  Polaire
```

Avantage : simpleFoam est ~100× plus rapide qu'interFoam → adapté aux nombreux points de la polaire.

#### Sortie — courbe polaire

La polaire fournit la vitesse maximale atteignable pour chaque direction et force de vent. Elle est utilisée pour :
- Optimiser les appendices (quille, gouvernail) — lien direct TD2/§6
- Dimensionner la voilure
- Définir les angles de VMG (Velocity Made Good) optimaux

**Référence :** Larsson, Eliasson, Orych — *Principles of Yacht Design*, Ch.1 §1.8 (algorithme complet) ; Ch.5 §5.9 (résistance de gîte dans la boucle VPP).

---

### 19.4 PyFoam — interface Python pour OpenFOAM

**PyFoam** est une bibliothèque Python permettant de piloter OpenFOAM depuis des scripts Python :

```bash
pip install PyFoam
```

Exemple minimal — lancer `blockMesh` depuis Python :
```bash
python3 basicExample.py
```

PyFoam permet de :
- Modifier les paramètres des dictionnaires OpenFOAM par programmation
- Lancer et monitorer des simulations
- Post-traiter les résultats directement en Python

Combiné avec les directives `#calc` / `include`, PyFoam permet de construire des pipelines de simulation **entièrement automatisés**, par exemple pour des études paramétriques (variation de la vitesse, du tirant d'eau, de l'assiette...).

Rhinoceros supporte également des scripts Python (via rhinoscriptsyntax et Grasshopper) pour automatiser la génération de géométrie.

---

## 20. Devoir Final

### 20.1 Structure

Le devoir final comporte **deux parties** (note minimale **8/10** pour obtenir le **certificat Navalapp** — seuil de la plateforme de cours, indépendant du barème ENSM). Le devoir est **individuel** et soumis directement sur la plateforme Navalapp.

**Partie 1 — Questions théoriques (5 × 0,75 pt = 3,75 pt)** : réponses détaillées en vos propres mots.

**Partie 2 — Exercices pratiques (5 exercices = 6,25 pt)** : simulation d'un profil NACA-0012 à 4° d'angle d'attaque.

### 20.2 Questions théoriques

1. **(0,75 pt)** Expliquer les concepts sur lesquels repose la méthode des volumes finis : type d'équations résolues, discrétisation des grandeurs fluides, bilan entre cellules adjacentes.

2. **(0,75 pt)** Considérer un champ de vitesse 2D $\mathbf{u} = (x, -y)$ dans $\mathbb{R}^2$. Que peut-on dire sur la densité du fluide ?

3. **(0,75 pt)** Pour résoudre $\partial u/\partial t = c \, \partial u/\partial x$ avec $c = 1$ et $\Delta x = 0{,}001$ m : calculer le pas de temps maximum $\Delta t$ satisfaisant la condition CFL. Écrire les schémas d'Euler explicite et implicite. Pour lequel la condition CFL est-elle nécessaire ?

4. **(0,75 pt)** Pour le profil portant simulé dans le cours : calculer le coefficient de portance. Pour une quille de corde $C_m = 3$ m et envergure $b = 1{,}5$ : calculer le coefficient de traînée induite.

5. **(0,75 pt)** Calculer le coefficient de frottement ITTC-57 pour le voilier de 17 m. Le nombre de Reynolds correspondant correspond-il à un régime laminaire, transitionnel ou turbulent ?

### 20.3 Exercices pratiques — Profil NACA-0012 à 4°

Profil NACA-0012 à angle d'attaque $\alpha = 4°$, épaisseur $t = 0{,}1$ m (direction z), géométrie fournie dans les matériaux du cours. Ordres de grandeur attendus (issus du TD2) : $C_l \approx 0{,}40$–$0{,}45$, $C_d \approx 0{,}008$–$0{,}012$, GCI < 3 %.

**Exercice 1 — Maillage de fond (1,25 pt)**

Préparer un maillage de fond `blockMeshDict` exprimé avec des variables et la directive `#calc`. Justifier les facteurs de dimensionnement choisis. Montrer le code `blockMeshDict`.

**Exercice 2 — Maillage final avec snappyHexMesh (1,25 pt)**

Générer le maillage final avec `snappyHexMesh` incluant la géométrie et une boîte de raffinement de niveau 2. Quelle taille de base choisir pour avoir ~50 cellules le long de la corde ? Montrer une image du maillage.

**Exercice 3 — Vitesse de simulation et paramètres turbulents (1,0 pt)**

Calculer la vitesse $U$ pour $Re = 10^7$ avec $\nu = 10^{-6}$ m²/s. Calculer $k$ et $\omega$ pour une intensité turbulente $Tu = 1\,\%$ et un rapport de viscosité turbulente $\nu_t/\nu = 10$.

$$k = \frac{3}{2}(U \cdot Tu)^2, \qquad \omega = \frac{\rho k}{\mu \cdot (\nu_t/\nu)}$$

**Exercice 4 — Coefficients de portance et traînée (1,5 pt)**

Obtenir $C_l$ et $C_d$ pour la simulation transitoire à partir des forces calculées :
$$C_l = \frac{F_y/t}{\frac{1}{2}\rho c U^2}, \qquad C_d = \frac{F_x/t}{\frac{1}{2}\rho c U^2}$$

Fournir les valeurs et le graphe des forces en fonction du temps.

**Exercice 5 — Post-traitement (1,25 pt)**

Représenter :
- Un contour de pression autour du profil (≥ 10 niveaux)
- Les lignes de courant au dernier instant simulé (≥ 20 streamlines)

Fournir deux images.

---

## Références

1. J. Calderón Sánchez, P.E. Merino Alonso — *CFD for Sailing Yachts*, cours Navalapp (navalapp.com/courses/cfd-for-yachts/)
2. H.K. Versteeg, W. Malalasekera — *An Introduction to Computational Fluid Dynamics: The Finite Volume Method*, Longman, 1995
3. Jasak H. — *Error Analysis and Estimation for the Finite Volume Method with Applications to Fluid Flows*, PhD Thesis, Imperial College London, 1996
4. ITTC Recommended Procedures — *Resistance Test*, 7.5-02-02-01 (2017)
5. ITTC Quality Manual — *ITTC-1957 Model-Ship Correlation Line*, 7.5-02-03-01.4
6. Keuning J.A., Sonnenberg U.B. — *Approximation of the Hydrodynamic Forces on a Sailing Yacht based on the Delft Systematic Yacht Hull Series* (Delft Series III), Proc. 15th Chesapeake Sailing Yacht Symposium, 2001
7. Holtrop J., Mennen G.G.J. — *An Approximate Power Prediction Method*, International Shipbuilding Progress, 1982
8. Menter F.R. — *Two-Equation Eddy-Viscosity Turbulence Models for Engineering Applications*, AIAA Journal, 32(8), 1994
9. OpenFOAM Foundation — *OpenFOAM User Guide*, v2306/v2412

---

*Document généré pour le cours Performances Navires — ENSM, 2026-27*
