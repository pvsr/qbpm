#!/bin/sh
PYTHON=$1
nix-shell --quiet -p $PYTHON ${PYTHON}Packages.pyxdg ${PYTHON}Packages.pytest \
  --run "python -m pytest"
