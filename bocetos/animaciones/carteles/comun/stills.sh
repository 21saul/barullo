#!/bin/bash
# Fotogramas fijos de los carteles para revisar: bash stills.sh <frame> Comp1 Comp2 ...
# Necesita serve.py corriendo sobre barullo-render/carteles/assets (puerto 8765).
set -e
R=/mnt/c/Users/Veintiuno/barullo-render/carteles
REM=/home/ddev/www/barullo/remotion
BUNDLE=${BUNDLE:-/tmp/barullo-carteles-bundle}
FRAME=$1; shift
cd "$REM"
npx remotion bundle src/carteles/index.ts --public-dir="$R/public" --out-dir="$BUNDLE" --log=error >/dev/null
mkdir -p "$R/out"
for c in "$@"; do
  npx remotion still "$BUNDLE" "$c" "$R/out/$c.png" --frame="$FRAME" ${PROPS:+--props="$PROPS"} --log=error
  echo "$R/out/$c.png"
done
