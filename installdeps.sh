#!/bin/bash
set -o nounset -o errexit -o xtrace

LIBS="libs"

npm install
rm -rf "$LIBS"
pip install --target "$LIBS" --requirement requirements.txt
pip install --no-deps --requirement requirements-dev.txt
