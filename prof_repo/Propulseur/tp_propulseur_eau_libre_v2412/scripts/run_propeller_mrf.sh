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
