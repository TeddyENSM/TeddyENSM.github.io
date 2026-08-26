TP propulseur - OpenFOAM ESI v2412
==================================

Structure creee par master_setup_propulseur_v2412.sh

- cases/propeller_mrf
  Copie locale du tutoriel officiel:
  incompressible/pimpleFoam/RAS/propeller

- cases/kp505_overset_template
  Squelette de travail pour la variante overset decrite dans le sujet.
  La geometrie reelle KP505 reste a fournir dans constant/triSurface/.

- docs/Tp_propulseur_eau_libre.md
  Copie du sujet de TP utilise pour la preparation.

Commandes utiles:

1. Lancer le cas MRF:
   ./scripts/run_propeller_mrf.sh

2. Nettoyer le cas MRF:
   ./scripts/clean_propeller_mrf.sh

3. Ouvrir dans ParaView:
   cd cases/propeller_mrf
   paraFoam
