# Fiche recap - Etude 2D du NACA 0018

## Objet et perimetre

Preparer une etude de profil NACA 0018 en 2D pour obtenir, a terme, les coefficients de portance `Cl` et de trainee `Cd` selon l'angle d'attaque. Le foil complet en T, son envergure de 20 cm et les effets 3D d'extremite ne sont pas modelises ici.

Le travail est isole dans `documents/openfoam/NACA0018_2D`. L'ancien cas `run/airFoil2D` n'est pas utilise et n'a pas ete modifie.

## Donnees et hypotheses

| Parametre | Valeur | Statut / remarque |
| --- | ---: | --- |
| Profil | NACA 0018 symetrique | Geometrie analytique a quatre chiffres |
| Corde `c` | 0.05 m | Bord d'attaque a `x = 0`, bord de fuite a `x = 0.05 m` |
| Vitesse `Uinf` | 2.06 m/s | Norme de la vitesse amont, gardee constante selon l'incidence |
| Viscosite cinematique `nu` | `1.05e-6 m2/s` | Valeur de depart pour l'eau vers 20 degC; a confirmer selon le fluide reel |
| Reynolds | environ 98 100 | `Re = Uinf*c/nu`; transition et decollement potentiellement sensibles |
| Regime / solveur de base | Incompressible stationnaire, `simpleFoam`, `kOmegaSST` | Demarrage valide sous OpenFOAM v2406; convergence physique non encore etablie |

Pour une incidence `alpha`, le profil reste fixe et la vitesse est tournee: `Ux = Uinf*cos(alpha)`, `Uy = Uinf*sin(alpha)`. Cette convention est celle du script `set_incidence.py`.

## Geometrie

Les coordonnees sont generees localement par `geometry/generate_naca0018.py`, avec une distribution cosinus des abscisses et un bord de fuite ferme. Les fichiers `geometry/naca0018.dat` (coordonnees normalisees) et `geometry/naca0018_50mm.dat` (metres) conservent les memes points de contour. Le profil compte 201 points, corde 50 mm et epaisseur maximale echantillonnee d'environ 9 mm.

Une image du contour seul est produite par:

```sh
python3 documents/openfoam/NACA0018_2D/geometry/plot_naca0018.py
```

L'image est `geometry/naca0018_50mm.png`. Les fichiers `.dat` et le PNG ne sont pas des maillages.

## Domaine et maillage

La boite initiale est `x = [-0.50, 1.05] m`, `y = [-0.50, 0.50] m`. La geometrie est extrudee de 1 mm en `z`, avec une seule cellule dans cette direction; les deux faces correspondantes sont de type OpenFOAM `empty` pour representer le calcul 2D.

Le maillage MSH2 est genere avec Gmsh lorsqu'il est disponible; sinon `Allrun` reutilise `geometry/naca0018_2d.msh`, puis le convertit avec `gmshToFoam` et le controle avec `checkMesh`. Le patch `profile` est converti en type `wall`:

```sh
bash documents/openfoam/NACA0018_2D/Allrun
```

Parametres principaux du maillage exploratoire:

- taille de maille pres du profil: environ `0.5 mm`;
- taille lointaine maximale visee: `12 mm`;
- couche limite prismatique: premiere hauteur `1e-5 m`, epaisseur totale `1.5e-3 m`, croissance `1.2`;
- raffinement du sillage, avec un raffinement supplementaire juste derriere le bord de fuite.

Le maillage initial comptait 135 848 cellules; apres le raffinement local du sillage, le dernier maillage compte environ 140 744 cellules. Les cellules sont principalement des prismes extrudes depuis le maillage 2D, avec quelques hexaedres.

### Resultat de `checkMesh`

La topologie, l'unicite de la region fluide, les volumes, le determinant des cellules et le critere de non-orthogonalite passent. Au dernier controle, la non-orthogonalite maximale est d'environ 62.6 degres et la moyenne d'environ 2.8 degres; le skewness maximal est d'environ 2.56.

Un avertissement persiste: 6 faces ont un poids d'interpolation inferieur a 0.05 (minimum environ 0.031). Elles sont dans le sillage immediat, a environ 0.15-0.24 mm derriere le bord de fuite. Le raffinement local augmente le nombre de cellules mais ne supprime pas ces faces. Il faut donc examiner la sensibilite de `Cd` au maillage avant de presenter une polaire comme resultat final. Cet avertissement ne prouve pas, a lui seul, que tout calcul serait invalide.

## Conditions aux limites deja posees

Les patches du maillage sont `inlet`, `outlet`, `profile`, `top`, `bottom` et `frontAndBack`.

| Zone | Vitesse `U` | Pression `p` | Interpretation |
| --- | --- | --- | --- |
| Entree | `freestreamVelocity`, vecteur oriente selon `alpha` | `zeroGradient` | Ecoulement incident |
| Sortie | `freestreamVelocity` | `fixedValue uniform 0` | Pression de reference, pas vitesse nulle |
| Profil | `noSlip` | `zeroGradient` | Profil fixe |
| Haut et bas | `freestreamVelocity` | `zeroGradient` | Limites lointaines traversables selon l'incidence |
| Faces avant/arriere | `empty` | `empty` | Direction hors-plan du cas 2D |

Les champs sont dans `0/U` et `0/p`. Pour choisir une incidence, depuis le dossier du cas:

```sh
python3 set_incidence.py 0
python3 set_incidence.py 5
```

Le cas racine est a `0 deg`: `Uin = (2.06, 0, 0) m/s`. Le test a `5 deg` a donne `Uin = (2.052161, 0.179541, 0) m/s`, soit la meme norme de 2.06 m/s. Le generateur tourne aussi `dragDir` et `liftDir` avec l'incidence.

## Visualisation dans ParaView

Le maillage est charge dans ParaView avec le marqueur `NACA0018_2D.foam` (lecteur integre VTK) ou avec `paraFoam` depuis le dossier du cas. Dans ParaView, choisir `Surface With Edges`, puis la vue `+Z` pour observer le profil et les cellules dans le plan. Le zoom est necessaire pour examiner le voisinage du foil et le sillage.

## Extraction des coefficients

Le function object `forceCoeffs1` est configure dans `system/forceCoeffs` et inclus depuis `system/controlDict`. Il calcule les coefficients sur le patch `profile`, avec `rhoInf = 1000 kg/m3`, `magUInf = 2.06 m/s`, `lRef = 0.05 m` et `Aref = 5e-5 m2`, soit la corde de 0.05 m multipliee par l'extrusion de 0.001 m. Le script tourne `dragDir` et `liftDir` selon l'incidence; le centre de moment est `CofR = (0.025 0 0)`.

Les dictionnaires ont ete lus par `foamDictionary`, et le demarrage de `simpleFoam` a ete valide sous OpenFOAM v2406. Le balayage complet de -10 a +10 deg (pas de 2 deg) a ensuite atteint 1500 iterations par incidence sans erreur fatale. Le CSV `polaire_coefficients_v2406.csv` et la figure `polaire_coefficients_v2406.svg` sont generes dans le dossier du cas. Les coefficients sont calcules avec la surface de reference coherente `Aref = 5e-5 m2`.

Les valeurs du tableau sont des moyennes des 10 dernieres mesures (100 iterations). Les forces sont stables selon le controle indicatif pour -10, -4, -2, 0, +2, +6 et +8 deg; elles derivent pour -8, +4 et +10 deg. Le point -6 deg est manifestement suspect (`Cd` moyen environ 0.0012, avec changement de signe pendant le calcul). Tous les cas ont atteint le temps final, mais les residus `SIMPLE` ne respectent pas tous le seuil `1e-5`; ces calculs ne constituent donc pas une polaire validee.

Le balayage peut etre repris avec `JOBS=3 bash AllresumePolar`; il reprend les derniers champs enregistres et saute les angles termines.

## Ce qui reste a faire

1. Diagnostiquer et recalculer -6 deg; son coefficient de trainee quasi nul n'est pas credible.
2. Recalculer les angles derivants ou decroches avec davantage d'iterations et, si les forces restent instationnaires, un solveur transitoire et une moyenne temporelle.
3. Etudier l'effet des 6 faces de faible poids sur `Cd` et comparer plusieurs maillages.
4. Etudier la transition: le cas utilise `kOmegaSST` pleinement turbulent a `Re` proche de 98 000.

La polaire est produite et disponible, mais reste exploratoire. La convergence, la sensibilite au maillage et le modele de transition doivent etre valides avant toute utilisation de dimensionnement ou comparaison experimentale.