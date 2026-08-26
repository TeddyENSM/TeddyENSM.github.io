# Installation OpenFOAM v2412 ESI — WSL2/Ubuntu

## Prérequis

- Windows 10/11 avec WSL2 activé
- Ubuntu 22.04 LTS (recommandé) dans WSL2

```bash
wsl --install -d Ubuntu-22.04
```

---

## 1. Installation OpenFOAM v2412

Ajouter le dépôt ESI-OpenCFD :

```bash
sudo sh -c "wget -O - https://dl.openfoam.com/add-debian-repo.sh | bash"
sudo apt-get update
sudo apt-get install openfoam2412
```

Vérifier l'installation :

```bash
ls /usr/lib/openfoam/openfoam2412/
```

---

## 2. Configuration du shell

Ajouter à `~/.bashrc` :

```bash
echo 'source /usr/lib/openfoam/openfoam2412/etc/bashrc' >> ~/.bashrc
source ~/.bashrc
```

Vérifier :

```bash
foamVersion
# → 2412
simpleFoam -help | head -2
```

---

## 3. Installation ParaView

```bash
sudo apt-get install paraview
```

Lancement depuis WSL (avec serveur X ou WSLg) :

```bash
paraview &
```

Ou utiliser `paraFoam` depuis le répertoire d'un cas :

```bash
paraFoam &
```

---

## 4. Outils complémentaires

```bash
# Python + bibliothèques pour post-traitement
sudo apt-get install python3 python3-pip python3-scipy python3-matplotlib

# gnuplot
sudo apt-get install gnuplot
```

---

## 5. Test rapide

```bash
mkdir -p $FOAM_RUN
cd $FOAM_RUN
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity .
cd cavity
blockMesh
icoFoam
paraFoam &
```

---

## 6. Structure des TDs

| Répertoire       | Solveur     | Physique                         |
|------------------|-------------|----------------------------------|
| `TD1_Poiseuille/` | icoFoam     | Écoulement laminaire entre plaques |
| `TD2_NACA_Profil/` | simpleFoam / pimpleFoam | Profil NACA-0012, k-ω SST |
| `TD3_Voilier/`   | interFoam   | Résistance navire, surface libre |
| `Devoir_Final/`  | simpleFoam  | Profil NACA-0012 à 4° d'incidence |

---

## 7. Commandes utiles v2412

```bash
# Source (si pas dans .bashrc)
source /usr/lib/openfoam/openfoam2412/etc/bashrc

# Lancer un cas
blockMesh
foamRun -solver icoFoam      # équivalent à icoFoam
foamRun -solver simpleFoam   # équivalent à simpleFoam

# Monitorer la convergence
foamMonitor -f postProcessing/residuals/0/residuals.dat &

# Reconstruire après calcul parallèle
reconstructPar -latestTime

# Nettoyer un cas
foamListTimes -rm            # supprime tous les timesteps sauf 0 et constant
```

---

## 8. Remarques WSL2

- Les fichiers de cas sont dans le système de fichiers Linux (`~/`) — **ne pas** travailler depuis `/mnt/c/` (performances très dégradées).
- Pour transférer des fichiers depuis Windows : `cp /mnt/c/Users/<nom>/Downloads/fichier.zip ~/`.
- WSLg (Windows 11) permet d'afficher ParaView directement sans serveur X externe.
- Sur Windows 10 : installer VcXsrv ou Xming, puis `export DISPLAY=:0`.
