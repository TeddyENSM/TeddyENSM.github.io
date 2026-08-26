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
