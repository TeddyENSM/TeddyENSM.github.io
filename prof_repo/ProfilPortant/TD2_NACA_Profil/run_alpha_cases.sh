#!/bin/bash
set -e
cd "$(dirname "$0")"
source /usr/lib/openfoam/openfoam2412/etc/bashrc

cases=(simpleFoam_alpha5 simpleFoam_alpha15)
for case in "${cases[@]}"; do
  if [ ! -d "$case" ]; then
    echo "Case $case not found, skipping"
    continue
  fi
  echo "=== Running $case ==="
  cd "$case"
  if [ -f log.simpleFoam ]; then
    echo "Existing log.simpleFoam found for $case"
  fi
  simpleFoam 2>&1 | tee log.simpleFoam
  cd ..
done
