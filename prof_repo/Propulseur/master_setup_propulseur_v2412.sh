#!/bin/bash

###############################################################################
# master_setup_propulseur_v2412.sh
#
# Prepare un TP OpenFOAM ESI v2412 pour le cas propeller en eau libre.
# - detecte et source OpenFOAM v2412 si besoin
# - copie le tutoriel officiel incompressible/pimpleFoam/RAS/propeller
# - cree une arborescence de TP exploitable localement
# - ajoute un squelette overset conforme au sujet Markdown
###############################################################################

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TP_DOC="$SCRIPT_DIR/Tp_propulseur_eau_libre.md"

DEFAULT_TARGET="$SCRIPT_DIR/tp_propulseur_eau_libre_v2412"
TARGET_DIR="$DEFAULT_TARGET"
FORCE=0
DRY_RUN=0

usage() {
    cat <<EOF
Usage: $(basename "$0") [options] [target_dir]

Options:
  --force      Supprime le dossier cible s'il existe deja.
  --dry-run    Affiche les actions sans creer de fichiers.
  -h, --help   Affiche cette aide.

Sans argument, le TP est cree dans:
  $DEFAULT_TARGET
EOF
}

run_cmd() {
    if [ "$DRY_RUN" -eq 1 ]; then
        printf '[dry-run]'
        printf ' %q' "$@"
        printf '\n'
        return 0
    fi
    "$@"
}

source_openfoam() {
    local root

    if [ -n "${FOAM_TUTORIALS:-}" ] && [ -d "$FOAM_TUTORIALS" ]; then
        return 0
    fi

    for root in \
        /usr/lib/openfoam/openfoam2412 \
        /opt/openfoam2412 \
        "$HOME/OpenFOAM/OpenFOAM-v2412"
    do
        if [ -d "$root/tutorials" ]; then
            export WM_PROJECT_DIR="$root"
            export FOAM_TUTORIALS="$root/tutorials"
            return 0
        fi
    done

    fail "OpenFOAM v2412 introuvable. Verifie l'installation (ex: /usr/lib/openfoam/openfoam2412)."
}

find_propeller_tutorial() {
    local candidate

    for candidate in \
        "${FOAM_TUTORIALS:-}/incompressible/pimpleFoam/RAS/propeller" \
        "${WM_PROJECT_DIR:-}/tutorials/incompressible/pimpleFoam/RAS/propeller"
    do
        if [ -n "$candidate" ] && [ -d "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done

    candidate="$(find "${FOAM_TUTORIALS:-/usr/lib/openfoam/openfoam2412/tutorials}" \
        -type d -path '*/incompressible/pimpleFoam/RAS/propeller' 2>/dev/null | head -n 1 || true)"

    [ -n "$candidate" ] || fail "Tutoriel propeller introuvable dans OpenFOAM."
    printf '%s\n' "$candidate"
}

prepare_target_dir() {
    if [ -e "$TARGET_DIR" ] && [ "$FORCE" -eq 0 ]; then
        fail "Le dossier cible existe deja: $TARGET_DIR (utilise --force pour l'ecraser)."
    fi

    if [ -e "$TARGET_DIR" ] && [ "$FORCE" -eq 1 ]; then
        run_cmd rm -rf "$TARGET_DIR"
    fi

    run_cmd mkdir -p "$TARGET_DIR/cases" "$TARGET_DIR/docs" "$TARGET_DIR/logs" "$TARGET_DIR/post" "$TARGET_DIR/scripts"
}

copy_mrf_case() {
    local tutorial_dir="$1"
    local case_dir="$TARGET_DIR/cases/propeller_mrf"

    run_cmd cp -a "$tutorial_dir" "$case_dir"

    if [ "$DRY_RUN" -eq 0 ]; then
        if [ -d "$case_dir/0.orig" ] && [ ! -d "$case_dir/0" ]; then
            cp -a "$case_dir/0.orig" "$case_dir/0"
        fi

        if [ -d "${FOAM_TUTORIALS:-}/resources/geometry/propeller" ] && [ ! -d "$case_dir/constant/triSurface" ]; then
            cp -a "${FOAM_TUTORIALS}/resources/geometry/propeller" "$case_dir/constant/triSurface"
        fi

        if [ -f "$case_dir/Allrun.pre" ]; then
            # Prevent renumberMesh from touching field files before patches are recreated.
            sed -i 's/runApplication renumberMesh -overwrite/runApplication renumberMesh -overwrite -noFields/' "$case_dir/Allrun.pre"
        fi

        chmod +x "$case_dir/Allrun" "$case_dir/Allrun.pre" "$case_dir/Allclean"
        : > "$case_dir/propeller_mrf.foam"
    fi

    ok "Cas MRF copie depuis le tutoriel officiel"
}

write_top_readme() {
    if [ "$DRY_RUN" -eq 1 ]; then
        info "Generation de README_SETUP.txt"
        return 0
    fi

    cat > "$TARGET_DIR/README_SETUP.txt" <<EOF
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
EOF
}

write_helper_scripts() {
    if [ "$DRY_RUN" -eq 1 ]; then
        info "Generation des scripts d'aide"
        return 0
    fi

    cat > "$TARGET_DIR/scripts/run_propeller_mrf.sh" <<'EOF'
#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$ROOT_DIR/cases/propeller_mrf"

if ! command -v foamVersion >/dev/null 2>&1; then
    if [ -f /usr/lib/openfoam/openfoam2412/etc/bashrc ]; then
        # shellcheck disable=SC1091
        set +u
        . /usr/lib/openfoam/openfoam2412/etc/bashrc
        set -u
    else
        echo "OpenFOAM v2412 introuvable" >&2
        exit 1
    fi
fi

cd "$CASE_DIR"
chmod +x Allrun Allrun.pre Allclean
./Allrun
EOF

    cat > "$TARGET_DIR/scripts/clean_propeller_mrf.sh" <<'EOF'
#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$ROOT_DIR/cases/propeller_mrf"

if ! command -v foamVersion >/dev/null 2>&1; then
    if [ -f /usr/lib/openfoam/openfoam2412/etc/bashrc ]; then
        # shellcheck disable=SC1091
        set +u
        . /usr/lib/openfoam/openfoam2412/etc/bashrc
        set -u
    fi
fi

cd "$CASE_DIR"
chmod +x Allclean
./Allclean
rm -rf 0 constant/triSurface postProcessing processor* log.* propeller_mrf.foam
cp -a 0.orig 0
cp -a "${FOAM_TUTORIALS:-/usr/lib/openfoam/openfoam2412/tutorials}/resources/geometry/propeller" constant/triSurface
: > propeller_mrf.foam
EOF

    chmod +x "$TARGET_DIR/scripts/run_propeller_mrf.sh" "$TARGET_DIR/scripts/clean_propeller_mrf.sh"
}

write_overset_template() {
    local case_dir="$TARGET_DIR/cases/kp505_overset_template"

    run_cmd mkdir -p "$case_dir/0" "$case_dir/constant/triSurface" "$case_dir/system"

    if [ "$DRY_RUN" -eq 1 ]; then
        info "Generation du squelette overset"
        return 0
    fi

    cat > "$case_dir/README.md" <<'EOF'
# KP505 overset template

Ce dossier est un squelette de depart pour la variante avancee du TP.

- Geometrie a fournir dans `constant/triSurface/`
- Solveur vise: `overPimpleDyMFoam`
- Les dictionnaires ci-dessous viennent du sujet Markdown du TP
EOF

    cat > "$case_dir/constant/dynamicMeshDict" <<'EOF'
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      dynamicMeshDict;
}

dynamicFvMesh       dynamicOversetFvMesh;

solver              solidBody;

solidBodyMotionFunctions
{
    propellerRotation
    {
        solidBodyMotionFunction  rotatingMotion;
        rotatingMotionCoeffs
        {
            origin      (0 0 0);
            axis        (1 0 0);
            omega       100;
        }
    }
}
EOF

    cat > "$case_dir/system/topoSetDict" <<'EOF'
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}

actions
(
    {
        name    overset;
        type    cellSet;
        action  new;
        source  cylinderToCell;
        sourceInfo
        {
            p1      (-0.1 0 0);
            p2      (0.3 0 0);
            radius  0.2;
        }
    }
    {
        name    overset;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        sourceInfo { set overset; }
    }
);
EOF

    cat > "$case_dir/0/U" <<'EOF'
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (1 0 0);

boundaryField
{
    overset
    {
        type            overset;
        value           uniform (0 0 0);
    }
}
EOF
}

copy_tp_doc() {
    if [ ! -f "$TP_DOC" ]; then
        warn "Sujet Markdown introuvable, copie docs ignoree: $TP_DOC"
        return 0
    fi

    run_cmd cp -a "$TP_DOC" "$TARGET_DIR/docs/Tp_propulseur_eau_libre.md"
}

parse_args() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            --force)
                FORCE=1
                ;;
            --dry-run)
                DRY_RUN=1
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -*)
                fail "Option inconnue: $1"
                ;;
            *)
                TARGET_DIR="$1"
                ;;
        esac
        shift
    done
}

main() {
    local tutorial_dir

    parse_args "$@"

    info "Cible TP: $TARGET_DIR"
    source_openfoam
    if command -v foamVersion >/dev/null 2>&1; then
        info "OpenFOAM detecte: $(foamVersion 2>/dev/null || echo OpenFOAM-v2412)"
    else
        info "OpenFOAM detecte via chemins: ${WM_PROJECT_DIR:-inconnu}"
    fi

    tutorial_dir="$(find_propeller_tutorial)"
    info "Tutoriel source: $tutorial_dir"

    prepare_target_dir
    copy_mrf_case "$tutorial_dir"
    write_overset_template
    copy_tp_doc
    write_helper_scripts
    write_top_readme

    ok "TP propulseur cree dans: $TARGET_DIR"
    if [ "$DRY_RUN" -eq 0 ]; then
        info "Prochaine etape: cd '$TARGET_DIR' && ./scripts/run_propeller_mrf.sh"
    fi
}

main "$@"