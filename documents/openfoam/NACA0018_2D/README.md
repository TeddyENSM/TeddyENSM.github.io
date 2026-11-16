# Etude 2D du profil NACA 0018

Espace de travail pour preparer une polaire de profil avant de l'integrer au foil en T. Le cas OpenFOAM existant `run/airFoil2D` reste intact: ses limites et ses proprietes ne sont pas celles retenues ici.

## Donnees de depart

| Grandeur | Valeur | Remarque |
| --- | ---: | --- |
| Profil | NACA 0018 | Profil symetrique, epaisseur relative 18 % |
| Corde `c` | 0.05 m | Bord d'attaque en `x = 0`, profil horizontal |
| Vitesse `Uinf` | 2.06 m/s | Reference des captures; direction modifiee pour l'incidence |
| Viscosite cinematique `nu` | 1.05e-6 m2/s | Valeur de depart pour l'eau de mer vers 20 degC |
| Reynolds `Re = Uinf*c/nu` | environ 98 100 | A recalculer si `Uinf`, `c` ou `nu` change |

Le profil est fixe. Pour une incidence `alpha`, on oriente la vitesse amont: `Ux = Uinf*cos(alpha)` et `Uy = Uinf*sin(alpha)`. Le calcul represente une section 2D, pas le foil complet de 20 cm d'envergure ni ses effets d'extremite.

## Geometrie

`geometry/naca0018.dat` contient les coordonnees normalisees generees par `geometry/generate_naca0018.py`; `geometry/naca0018_50mm.dat` contient les memes points en metres. Les points suivent le contour depuis le bord de fuite sur l'extrados, passent par le bord d'attaque, puis reviennent sur l'intrados au bord de fuite.

La formule analytique NACA a quatre chiffres est utilisee avec une loi d'epaisseur de 18 %, une distribution cosinus des abscisses et un bord de fuite ferme. Les coordonnees normalisees sont conservees pour tracer et verifier le profil avant toute conversion STL. Elles sont generees localement et ne sont pas presentees comme un telechargement de la base UIUC.

Pour regenerer les deux fichiers depuis ce dossier:

```sh
python3 geometry/generate_naca0018.py
```

## Visualisation du profil

Depuis la racine du depot, genere une image du profil a l'echelle:

```sh
python3 documents/openfoam/NACA0018_2D/geometry/plot_naca0018.py
```

Ouvre ensuite `documents/openfoam/NACA0018_2D/geometry/naca0018_50mm.png` dans VS Code. Cette image montre le contour seul; le fichier `.dat` contient des coordonnees, pas un maillage. Une fois le cas maillage cree, il pourra etre ouvert dans ParaView avec `paraFoam`, puis affiche en `Surface With Edges` pour voir les cellules autour du profil.

## Domaine et limites envisages

La premiere boite de calcul a verifier est `x = [-0.50, 1.05] m`, `y = [-0.50, 0.50] m`, avec une epaisseur numerique faible en `z` et une seule cellule dans cette direction. Le profil de 50 mm est place de `x = 0` a `x = 0.05 m`. Cette boite est une hypothese de depart, pas une etude de sensibilite au domaine.

Pour un cas incompressible stationnaire de type `simpleFoam`, les limites candidates sont:

| Zone | `U` | `p` |
| --- | --- | --- |
| Entree | `fixedValue` selon l'incidence | `zeroGradient` |
| Sortie | `zeroGradient` | `fixedValue uniform 0` |
| Profil | `noSlip` | `zeroGradient` |
| Haut et bas | `slip` (ou `symmetryPlane` si le maillage le permet) | compatible avec la limite choisie |
| Faces avant/arriere | `empty` | `empty` |

La pression nulle en sortie est une reference de pression, pas une vitesse nulle. Les limites haut/bas sont eloignees et ne sont pas des parois mobiles.

Les champs cinematiques sont dans `0/U` et `0/p`. Le champ de vitesse est genere a l'angle voulu depuis la racine du cas:

```sh
python3 set_incidence.py 0
python3 set_incidence.py 5
```

La commande impose `(Uinf*cos(alpha), Uinf*sin(alpha), 0)` sur les limites lointaines et tourne les directions de trainee et de portance de `forceCoeffs`; le profil reste fixe. Le cas est configure pour OpenFOAM v2406 avec `simpleFoam`, `kOmegaSST`, les champs `k`, `omega`, `nut`, les schemas et solveurs SIMPLE. Ce modele est pleinement turbulent et ne predit pas la transition laminaire-turbulente, ce qui limite l'interpretation a `Re` proche de 98 000. Le modele transitionnel `kOmegaSSTLM` n'est pas fourni par l'installation v2406 verifiee ici.

## Maillage initial

Le maillage est genere avec Gmsh puis importe dans OpenFOAM. Le script utilise Gmsh s'il est installe; sinon il reutilise le fichier MSH2 versionne `geometry/naca0018_2d.msh`. Il reprend la boite ci-dessus, avec une extrusion numerique de 1 mm et une seule cellule dans la direction z. Le raffinement est concentre sur le profil et dans le sillage; une couche limite prismatique commence a `1e-5 m`, avec une epaisseur totale de `1.5e-3 m` et un taux de croissance de 1.2. Ces parametres servent de point de depart et devront etre verifies par une etude de sensibilite et par les valeurs de `y+`.

Depuis la racine du depot, lance le pipeline complet ainsi:

```sh
bash documents/openfoam/NACA0018_2D/Allrun
```

Le script genere ou reutilise le maillage, l'importe dans `constant/polyMesh`, definit le profil comme une paroi et `frontAndBack` en `empty`, puis execute `checkMesh`. Pour afficher la grille, place-toi dans `documents/openfoam/NACA0018_2D`, lance `paraFoam`, clique sur `Apply` et choisis `Surface With Edges`.

Pour preparer puis executer le balayage de `alpha_list.txt` sous OpenFOAM v2406, depuis ce dossier:

```sh
bash AllrunPolar
```

Les nouveaux cas sont crees dans `alpha_cases_v2406/`; les anciens `alpha_cases/` sont preserves. Le script refuse egalement d'ecraser un precedent `alpha_cases_v2406/`. Chaque cas conserve son journal `log.simpleFoam` et ses coefficients dans `postProcessing/forceCoeffs1/`.

Pour reprendre un balayage interrompu depuis les derniers champs ecrits et sauter les angles deja termines:

```sh
bash AllresumePolar
```

`AllresumePolar` utilise trois calculs en parallele par defaut; modifier ce nombre avec `JOBS=2 bash AllresumePolar` si la machine est moins puissante.

Pour regenerer le tableau CSV (valeurs finales et moyenne des 10 dernieres mesures, soit 100 iterations) et la figure:

```sh
python3 extract_polar.py
python3 plot_polar.py
```

Les fichiers produits sont `polaire_coefficients_v2406.csv` et `polaire_coefficients_v2406.svg` (portance selon l'incidence, trainee selon l'incidence et polaire `Cl(Cd)`). Le CSV agrege aussi les fichiers de coefficients ecrits dans plusieurs sous-dossiers lors des reprises.

## Resultats du balayage v2406

Les onze incidences de -10 a +10 degres ont atteint le temps de calcul 1500 sans erreur fatale. Le tableau donne la moyenne de `Cd` et `Cl` sur les 100 dernieres iterations, plus informative qu'une seule valeur finale.

| Incidence | `Cd` moyen | `Cl` moyen | Forces sur les 100 dernieres iterations |
| ---: | ---: | ---: | --- |
| -10 deg | 0.041890 | -0.805588 | stable |
| -8 deg | 0.036295 | -0.674393 | derivantes |
| -6 deg | 0.001197 | -0.908442 | derivantes, `Cd` aberrant |
| -4 deg | 0.027650 | -0.348893 | stable |
| -2 deg | 0.025890 | -0.173907 | stable |
| 0 deg | 0.025135 | 0.013181 | stable |
| +2 deg | 0.025907 | 0.170528 | stable |
| +4 deg | 0.027893 | 0.327659 | derivantes |
| +6 deg | 0.031036 | 0.509809 | stable |
| +8 deg | 0.034323 | 0.682311 | stable |
| +10 deg | 0.046423 | 0.757390 | derivantes |

Le statut `stable` est un controle pratique, pas un critere officiel de convergence: l'etendue de `Cd` sur la fenetre doit etre <= 1 % de sa moyenne et celle de `Cl` <= 0.01. Les residus `SIMPLE` ne satisfont pas tous le seuil de `1e-5` a 1500 iterations; atteindre `End` signifie que le temps impose est atteint, pas que la solution est convergee.

Le resultat a -6 deg est manifestement suspect: `Cd` reste presque nul et a change de signe pendant le calcul, alors que les angles voisins donnent une trainee positive. Ne pas utiliser ce point dans une polaire physique. Les resultats a -8, +4 et +10 deg presentent aussi une derive mesurable des forces.

La symetrie est raisonnable entre -4 et +4 deg: `Cl` vaut environ -0.349 a -4 deg et +0.328 a +4 deg; les points a +/-2 deg sont egalement proches en valeur absolue. A 0 deg, `Cl` est proche de zero (0.013). La portance augmente ensuite jusqu'a environ 0.76 a +10 deg, mais les angles eleves restent sensibles a la convergence et au modele turbulent.

Le controle confirme une seule region, la topologie generale et les criteres de determinant/orthogonalite. Il signale toutefois 6 faces de faible poids d'interpolation, toutes dans le sillage immediat, a environ 0.15-0.24 mm derriere le bord de fuite. Un raffinement local a augmente le maillage a environ 140 700 cellules sans supprimer ces six faces. Comme elles sont dans la zone qui influence la trainee, les coefficients de trainee doivent etre verifies par sensibilite au maillage. Le balayage ci-dessus est une premiere polaire numerique exploratoire, pas un resultat valide pour dimensionnement.

## Etapes de travail

1. Reprendre le calcul a -6 deg depuis un champ convergent voisin ou avec une initialisation/amortissement plus robuste; verifier le signe et la valeur de `Cd`.
2. Etendre les iterations ou passer a un solveur instationnaire (`pimpleFoam`) aux incidences ou les forces continuent de varier, puis calculer des moyennes temporelles.
3. Generer un maillage raffine et comparer `Cd/Cl`, en eliminant si possible les 6 faces de faible poids dans le sillage.
4. Etudier la sensibilite au modele de transition: le cas actuel est `kOmegaSST` pleinement turbulent, sans transition, alors que `Re` est proche de 98 000.
5. Verifier les residus, le bilan de masse et la stabilite des forces avant de presenter une polaire physique finale.

Le calcul est executable, mais la polaire actuelle reste exploratoire: le maillage conserve les 6 faces de faible poids d'interpolation, plusieurs incidences n'ont pas atteint le seuil de stabilite et le modele pleinement turbulent SST peut deplacer la transition et le decollement. Elle n'est pas directement equivalente a une polaire experimentale.
