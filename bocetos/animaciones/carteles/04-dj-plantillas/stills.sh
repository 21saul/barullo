#!/bin/bash
# Fotogramas fijos de revisión de las plantillas DJ (a media escala): bash stills.sh <frame> [Comp-Story ...]
# Necesita el servidor de assets (comun/serve.py sobre barullo-render/carteles/assets, puerto 8765).
set -e
R=/mnt/c/Users/Veintiuno/barullo-render/carteles
BUNDLE=${BUNDLE:-/tmp/barullo-dj-bundle}
OUT=${OUT:-$R/dj-plantillas/stills}
FRAME=${1:-40}; shift || true
COMPS=${@:-DjMedallon-Story DjMedallon-Feed DjCristal-Story DjCristal-Feed DjRecorte-Story DjRecorte-Feed}
mkdir -p "$OUT"
cd /home/ddev/www/barullo/remotion
npx remotion bundle src/carteles/index.ts --public-dir="$R/public" --out-dir="$BUNDLE" --log=error >/dev/null
for c in $COMPS; do
  npx remotion still "$BUNDLE" "$c" "$OUT/$c-$FRAME.png" --frame="$FRAME" --scale=${SCALE:-0.5} ${PROPS:+--props="$PROPS"} --log=error
  echo "$OUT/$c-$FRAME.png"
done
