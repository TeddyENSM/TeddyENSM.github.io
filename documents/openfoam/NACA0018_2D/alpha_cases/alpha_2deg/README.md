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

La commande remplace l'entree par `(Uinf*cos(alpha), Uinf*sin(alpha), 0)`; le profil reste fixe. Commencer les essais par quelques incidences modestes autour de zero et verifier convergence et sensibilite du maillage avant d'etendre la plage. Ces deux champs ne suffisent pas encore a lancer `simpleFoam`: les proprietes du fluide et le modele de turbulence/transition restent a configurer. `kOmegaSSTLM` est disponible dans cette installation, mais il faudra encore verifier les champs auxiliaires et les conditions de paroi requis par ce modele.

## Maillage initial

Le premier maillage est genere avec Gmsh puis importe dans OpenFOAM. Il reprend la boite ci-dessus, avec une extrusion numerique de 1 mm et une seule cellule dans la direction z. Le raffinement est concentre sur le profil et dans le sillage; une couche limite prismatique commence a `1e-5 m`, avec une epaisseur totale de `1.5e-3 m` et un taux de croissance de 1.2. Ces parametres servent de point de depart et devront etre verifies par une etude de sensibilite et par les valeurs de `y+` apres configuration du modele.

Depuis la racine du depot, lance le pipeline complet ainsi:

```sh
sh documents/openfoam/NACA0018_2D/Allrun
```

Le script genere `geometry/naca0018_2d.msh`, l'importe dans `constant/polyMesh`, definit `frontAndBack` en `empty`, puis execute `checkMesh`. Pour afficher la grille, place-toi dans `documents/openfoam/NACA0018_2D`, lance `paraFoam`, clique sur `Apply` et choisis `Surface With Edges`.

Le controle confirme une seule region, la topologie generale et les criteres de determinant/orthogonalite. Il signale toutefois 6 faces de faible poids d'interpolation, toutes dans le sillage immediat, a environ 0.15-0.24 mm derriere le bord de fuite. Un raffinement local a augmente le maillage a environ 140 700 cellules sans supprimer ces six faces. Comme elles sont dans la zone qui influence la trainee, ne pas utiliser ce maillage pour annoncer une polaire finale avant d'avoir examine leur effet et verifie la convergence au raffinement. Les dictionnaires `system/fvSchemes` et `system/fvSolution` sont uniquement des fichiers minimaux pour les outils de maillage; le cas n'est pas encore pret a lancer un solveur.

## Etapes de travail

1. Verifier le contour normalise et les coordonnees a 50 mm.
2. Construire et verifier la surface du profil, puis le domaine 2D.
3. Creer le maillage de fond, raffiner le profil et controler les couches de paroi.
4. Configurer les proprietes du fluide, le modele, les limites et les criteres de convergence.
5. Valider un calcul a incidence nulle, puis produire la polaire sur plusieurs incidences.

Les choix de maillage, de hauteur de premiere cellule, de modele de turbulence/transition et de convergence restent a etablir. A `Re` proche de 98 000, ces choix peuvent modifier fortement la transition et le decollement; une polaire RANS pleinement turbulente ne doit pas etre consideree automatiquement comme une polaire experimentale.
