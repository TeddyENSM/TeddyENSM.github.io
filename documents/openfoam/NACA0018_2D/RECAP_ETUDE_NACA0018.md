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

Les dictionnaires ont ete lus par `foamDictionary`, et le demarrage de `simpleFoam` a ete valide sous OpenFOAM v2406. Le balayage de -10 a +10 deg (pas de 2 deg) a atteint 1500 iterations; les angles -8, -6, +4 et +10 ont ensuite ete prolonges a 3000 depuis les champs sauvegardes. Le CSV `polaire_coefficients_v2406.csv` et la figure `polaire_coefficients_v2406.svg` sont regeneres avec les valeurs prolongees. La surface de reference est `Aref = 5e-5 m2`.

Les valeurs du tableau sont des moyennes des 10 dernieres mesures (100 iterations). Les forces des onze angles passent maintenant le controle indicatif de stabilite. La prolongation a corrige le point -6 deg: `Cd` est positif et `Cl` est proche de l'oppose du cas +6 deg. Les residus `SIMPLE` ne respectent toutefois pas tous le seuil `1e-5` a 3000 iterations; la polaire n'est donc pas encore validee.

Pour prolonger une selection d'angles depuis son dernier champ sauvegarde: `ANGLES='-8 -6 4 10' END_TIME=3000 JOBS=4 bash AllresumePolar`.

## Comment lire les polaires

Le balayage garde la norme de la vitesse a `Uinf = 2.06 m/s` et le meme fluide; le Reynolds reste donc environ `98 100`. Dans les cas OpenFOAM, le profil est fixe et le vecteur de vitesse est tourne: `U = (Uinf*cos(alpha), Uinf*sin(alpha), 0)`. C'est une transformation de repere equivalente a incliner le profil dans un ecoulement fixe, si l'on conserve la meme incidence relative. Avec l'axe `x` de la corde oriente du bord d'attaque vers le bord de fuite et `y` vers le haut, le `+8 deg` du script correspond a relever le bord d'attaque d'environ 8 deg par rapport a l'ecoulement horizontal. Si les axes du montage ou le signe d'assiette sont definis autrement, verifier cette convention avant de reporter l'angle sur la mecanique du foil.

- Sur `Cl(alpha)`, la courbe montre la portance qui augmente avec l'incidence positive. A `+8 deg`, `Cl = 0.6823`.
- Sur `Cd(alpha)`, la trainee a `+8 deg` vaut `Cd = 0.03432`; elle est plus faible qu'a `+10 deg`, ou `Cd = 0.04257`.
- Sur la polaire `Cl(Cd)`, le rapport `Cl/Cd` compare portance obtenue et trainee payee. A `+8 deg`, il vaut environ `19.88`; a `+10 deg`, il tombe a `18.70`.

Parmi les incidences testees par pas de 2 deg, `+8 deg` donne donc le meilleur rapport portance/trainee pour une portance positive. `+10 deg` fournit plus de portance (`Cl = 0.796` contre `0.682`), mais au prix d'une trainee plus forte et d'une efficacite moindre. Le point optimal continu peut se trouver entre les angles echantillonnes; un balayage plus fin autour de `+7 a +9 deg` serait utile si l'assiette cible est a regler precisement.

A vitesse fixee, la pression dynamique ne change pas: `q = 0.5*rho*Uinf^2 = 2121.8 Pa`. Pour une corde de 50 mm et une envergure ideale de 20 cm (`A = 0.01 m2`), les coefficients de `+8 deg` correspondent approximativement a `L = q*A*Cl = 14.5 N` et `D = q*A*Cd = 0.73 N`, soit `L/D = 19.9`. C'est une extrapolation de la section 2D: les effets d'extremite, le foil complet et les interactions avec la coque ne sont pas inclus.

Le meilleur rapport `Cl/Cd` n'est pas necessairement l'assiette reelle a imposer dans toutes les situations. Il faut aussi satisfaire la portance requise par le bateau, et tenir compte des variations de vitesse, d'assiette de coque et de direction du courant. Les coefficients actuels restent exploratoires tant que la convergence stricte, la sensibilite du maillage et la transition ne sont pas validees.

## Ce qui reste a faire

1. Verifier les residus `SIMPLE` et le bilan de masse, qui ne sont pas tous sous les seuils prescrits.
2. Etudier l'effet des 6 faces de faible poids sur `Cd` et comparer plusieurs maillages.
3. Etudier la transition: le cas utilise `kOmegaSST` pleinement turbulent a `Re` proche de 98 000.
4. Passer a un calcul instationnaire et comparer les moyennes temporelles si une incidence ne converge pas en stationnaire.

La polaire est produite et les forces sont stables selon le controle local, mais elle reste exploratoire. Cela ne signifie pas que les hypotheses sont fausses: elles ne sont simplement pas toutes confirmees par une validation numerique ou des donnees experimentales.

### Pourquoi garder ces reserves

- **Maillage:** un seul maillage est utilise et `checkMesh` signale six faces de faible poids d'interpolation dans le sillage, zone importante pour la trainee. Sans comparaison avec un maillage plus fin, on ne sait pas quelle part de `Cd` depend de ces cellules.
- **Convergence:** les forces varient peu sur les 100 dernieres iterations, ce qui est encourageant, mais certains residus `SIMPLE` restent au-dessus de `1e-5`. La stabilite locale des coefficients ne prouve pas que toutes les equations sont strictement convergees.
- **Transition et turbulence:** `kOmegaSST` est utilise en mode pleinement turbulent. A `Re` proche de 98 000, la transition peut modifier la trainee, le decollement et l'angle de decrochage. Le niveau de turbulence impose a l'entree (5 %) est egalement une valeur supposee, pas une mesure de l'ecoulement reel.
- **Donnees physiques:** `Uinf`, `nu` et `rho` sont les valeurs retenues pour le cas. La vitesse peut etre fixee exactement comme hypothese d'etude, mais il faut confirmer que la viscosite correspond a la temperature et a la salinite reelles pour reproduire le Reynolds du foil.
- **Perimetre 2D:** la polaire represente une section ideale; elle n'inclut ni les effets d'extremite de l'envergure de 20 cm, ni les interactions avec la coque ou une surface libre eventuelle.

Une etude de maillage est donc la prochaine validation prioritaire, au moins aux angles `0`, `+8` et `+10 deg`, en comparant `Cl`, `Cd` et la structure du sillage sur deux ou trois resolutions. Un calcul instationnaire n'est pas automatiquement meilleur: il devient utile si les forces stationnaires ne se stabilisent pas ou si le sillage/decollement oscille. Dans ce cas, il faut eliminer le transitoire initial puis comparer les moyennes temporelles et leur dispersion. Les resultats stationnaires actuels permettent de reperer des tendances et le meilleur angle parmi ceux testes, pas de garantir une performance reelle.