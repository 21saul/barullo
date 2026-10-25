#!/bin/bash
# Renderiza un anuncio de DJ (story + feed) con un JSON de props:
#   bash render_dj.sh <DjMedallon|DjCristal|DjRecorte> <props.json> [frame_png=40]
#   p. ej.: bash render_dj.sh DjCristal djs/b-cristal-conguchu.json
# Salta los mp4 que ya existen (FORCE=1 para rehacerlos). Necesita: servidor de assets (python3 ../comun/serve.py /mnt/c/Users/Veintiuno/barullo-render/carteles/assets) y la foto
# preparada con prep_foto.py. Salida en barullo-render/carteles/dj-plantillas/<nombre del json>/:
#   story.mp4 (2160×3840) · feed.mp4 (2160×2700) · story-1080.mp4 (1080×1920) · feed-1080.mp4 (1080×1350) · story.png · feed.png
set -e
COMP=$1; PROPS=$(realpath "$2"); STILL=${3:-40}
NAME=$(basename "$PROPS" .json)
R=/mnt/c/Users/Veintiuno/barullo-render/carteles
OUT=$R/dj-plantillas/$NAME
BUNDLE=${BUNDLE:-/tmp/barullo-dj-bundle}
mkdir -p "$OUT"
curl -sf -o /dev/null http://127.0.0.1:8765/shapes.json || { echo "Arranca antes: python3 comun/serve.py $R/assets"; exit 1; }
cd /home/ddev/www/barullo/remotion
[ -n "$NOBUNDLE" ] || npx remotion bundle src/carteles/index.ts --public-dir="$R/public" --out-dir="$BUNDLE" --log=error >/dev/null
for v in Story Feed; do
  lo=$(echo $v | tr A-Z a-z)
  [ -f "$OUT/$lo.mp4" ] && [ -z "$FORCE" ] || npx remotion render "$BUNDLE" "$COMP-$v" "$OUT/$lo.mp4" --props="$PROPS" --codec=h264 --crf=16 --pixel-format=yuv420p \
    --concurrency=${CONC:-3} --log=error
  npx remotion still "$BUNDLE" "$COMP-$v" "$OUT/$lo.png" --props="$PROPS" --frame="$STILL" --log=error
  # versión 1080 de ancho para Instagram
  npx remotion ffmpeg -hide_banner -loglevel error -y -i "$OUT/$lo.mp4" -vf "scale=1080:-2:flags=lanczos" \
    -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart "$OUT/$lo-1080.mp4"
  echo "OK $OUT/$lo.mp4"
done
