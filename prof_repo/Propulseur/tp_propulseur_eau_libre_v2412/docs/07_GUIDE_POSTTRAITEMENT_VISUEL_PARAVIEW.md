# Guide pas a pas - Post-traitement visuel ParaView (propulseur)

## 1. Objectif
Ce guide vous permet de:
1. Ouvrir rapidement le cas calcule.
2. Produire des vues comparables de vitesse et pression.
3. Visualiser le sillage (wake) et les structures d'ecoulement.
4. Exporter des captures propres pour le rapport.
5. Sauvegarder un etat ParaView reutilisable.

## 2. Pre-requis
- Le calcul est termine (dossiers de temps presents).
- ParaView est installe.
- Vous etes dans le projet:

```bash
cd /home/chrisvhk/Work_OpenFoam/WorkSpace/Proppeler/tp_propulseur_eau_libre_v2412
```

## 3. Ouvrir les resultats
### Option A (recommandee): ouvrir le fichier .foam du cas calcule

```bash
cd cases/propeller_mrf
paraview propeller_mrf.foam
```

### Option B: ouvrir depuis l'interface
1. Lancer ParaView.
2. File > Open.
3. Selectionner `cases/propeller_mrf/propeller_mrf.foam`.
4. Cliquer Apply.

## 4. Reglages de base avant visualisation
1. Dans Animation View, aller au dernier pas de temps.
2. Dans Pipeline Browser, renommer la source en `propeller_mrf`.
3. Representation: Surface.
4. Activer l'axe si utile: View > Axes Grid.

## 5. Vue 1 - Champ de vitesse (U)
1. Selectionner la source `propeller_mrf`.
2. Dans Coloring, choisir `U` puis `Magnitude`.
3. Cliquer sur Rescale to Data Range.
4. Afficher la barre de couleurs (Show Color Legend).
5. Noter les bornes min/max pour garder la meme echelle sur toutes les figures.

## 6. Vue 2 - Champ de pression (p)
1. Dupliquer la vue ou changer le champ actif.
2. Dans Coloring, choisir `p`.
3. Rescale to Data Range.
4. Fixer une echelle explicite (min/max) pour des comparaisons robustes.

## 7. Vue 3 - Coupe axiale du sillage
1. Source `propeller_mrf` selectionnee.
2. Filters > Slice.
3. Slice Type: Plane.
4. Plane Normal: choisir l'axe d'avancement (souvent X: `1 0 0`).
5. Positionner l'origine de coupe au voisinage de l'axe helicoide.
6. Coloring: `U Magnitude`.
7. Ajuster la camera pour voir la zone aval du propulseur.

## 8. Vue 4 - Lignes de courant (streamlines)
1. Selectionner `propeller_mrf`.
2. Filters > Stream Tracer.
3. Vectors: `U`.
4. Seed Type: Line Source.
5. Placer la ligne d'injection en amont de l'helice.
6. Augmenter progressivement le nombre de graines (ex: 50 puis 100) pour la lisibilite.
7. Representation: Surface (ou Tube si besoin de contraste visuel).

## 9. Vue 5 - Iso-surfaces de vitesse (option avancee)
1. Selectionner la source.
2. Filters > Contour.
3. Champ: `U Magnitude`.
4. Definir 1 a 3 niveaux d'iso-valeur pertinents.
5. Utiliser cette vue pour montrer les zones de forte acceleration autour des pales.

## 10. Verifications de qualite (important)
1. Toutes les captures sont prises au meme temps (dernier pas, ou temps indique).
2. Les echelles de couleurs sont homogenes entre figures comparables.
3. Les legends affichent clairement la grandeur et les unites.
4. Le cadrage met en evidence helice + sillage, pas seulement le domaine complet.

## 11. Export des figures
1. Positionner la camera.
2. File > Save Screenshot.
3. Resolution conseillee:
   - 1920x1080 pour rapport standard.
   - 2560x1440 pour zooms detail.
4. Fond blanc si rapport PDF classique.

Convention de nommage recommandee:
- `U_surface_tXXXX.png`
- `p_slice_axial_tXXXX.png`
- `U_streamlines_tXXXX.png`
- `U_contour_tXXXX.png`

Dossier conseille:

```bash
mkdir -p post/paraview_images
```

## 12. Sauvegarder l'etat ParaView
1. File > Save State.
2. Nom recommande: `post/propeller_mrf_visual_state.pvsm`.
3. Ce fichier vous permet de recharger rapidement toutes les vues.

## 13. Recharger plus tard
1. Ouvrir ParaView.
2. File > Load State.
3. Selectionner `post/propeller_mrf_visual_state.pvsm`.
4. Si ParaView demande un remappage, pointer vers `cases/propeller_mrf/propeller_mrf.foam`.

## 14. Checklist de rendu minimal
- 1 figure vitesse globale (U Magnitude).
- 1 figure pression (p).
- 1 coupe du sillage.
- 1 visualisation streamline.
- 1 etat ParaView `.pvsm` sauvegarde.

## 15. Depannage rapide
### Je ne vois rien dans la vue
- Verifier que vous avez clique Apply.
- Cliquer Reset Camera.
- Verifier que vous etes sur un temps contenant des resultats.

### Le champ U ou p n'apparait pas
- Verifier que la source active est bien `propeller_mrf`.
- Verifier dans la liste des Arrays que les champs sont coches.

### Les images ne sont pas comparables
- Refixer manuellement la meme plage min/max sur les legends.
- Reutiliser le meme angle camera (eventuellement via Save State).
