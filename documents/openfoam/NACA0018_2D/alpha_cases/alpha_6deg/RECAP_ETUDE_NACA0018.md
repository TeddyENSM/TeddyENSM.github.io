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
| Regime / solveur envisage | Incompressible stationnaire, `simpleFoam` | Hypothese de travail; aucun calcul n'a encore ete lance |

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

Le maillage est genere avec Gmsh 4.12.1, converti avec `gmshToFoam`, puis controle avec `checkMesh`. Le script reproductible est `Allrun`:

```sh
sh documents/openfoam/NACA0018_2D/Allrun
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
| Entree | `fixedValue`, vecteur oriente selon `alpha` | `zeroGradient` | Ecoulement incident |
| Sortie | `zeroGradient` | `fixedValue uniform 0` | Pression de reference, pas vitesse nulle |
| Profil | `noSlip` | `zeroGradient` | Profil fixe |
| Haut et bas | `slip` | `zeroGradient` | Limites eloignees, pas des parois mobiles |
| Faces avant/arriere | `empty` | `empty` | Direction hors-plan du cas 2D |

Les champs sont dans `0/U` et `0/p`. Pour choisir une incidence, depuis le dossier du cas:

```sh
python3 set_incidence.py 0
python3 set_incidence.py 5
```

Le cas a ete remis a `0 deg`: `Uin = (2.06, 0, 0) m/s`. Le test a `5 deg` a donne `Uin = (2.052161, 0.179541, 0) m/s`, soit la meme norme de 2.06 m/s.

## Visualisation dans ParaView

Le maillage est charge dans ParaView avec le marqueur `NACA0018_2D.foam` (lecteur integre VTK) ou avec `paraFoam` depuis le dossier du cas. Dans ParaView, choisir `Surface With Edges`, puis la vue `+Z` pour observer le profil et les cellules dans le plan. Le zoom est necessaire pour examiner le voisinage du foil et le sillage.

## Ce qui reste a faire

1. Examiner les 6 faces de faible poids et comparer des maillages; ne pas figer la trainee sur le seul maillage actuel.
2. Definir les proprietes du fluide et choisir le modele de turbulence/transition. `kOmegaSSTLM` existe dans l'installation OpenFOAM v2412, mais ses champs auxiliaires et conditions de paroi ne sont pas encore configures.
3. Completer `0/` avec les champs du modele choisi et remplacer les dictionnaires minimaux `system/fvSchemes` et `system/fvSolution` par une configuration de calcul valide.
4. Ajouter l'extraction des forces et des coefficients avec les references correctes: corde, vitesse, densite et surface de reference 2D.
5. Valider un calcul a incidence nulle (maillage, residus, bilan et stabilite des forces), puis lancer un balayage d'angles et verifier la convergence de `Cl` et `Cd` avec le maillage.

Aucune simulation de fluide ni polaire n'a encore ete calculee. Le maillage et les conditions `U/p` constituent une base de preparation, pas un resultat aerodynamique valide.