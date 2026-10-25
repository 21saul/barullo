#!/bin/bash
# Monta un cartel en Remotion (story + feed) a partir de los frames de Blender ya renderizados.
#   bash render_cartel.sh <Comp> <seq> <frame_jpg> <carpeta_entrega>
#   p. ej.: bash render_cartel.sh Medalla f01 56 01-medalla
# <seq> es la carpeta de frames dentro de barullo-render/carteles/assets (la sirve serve.py en :8765).
# Salida: story.mp4/jpg, feed.mp4/jpg (2160 de ancho, H.264 CRF 16, yuv420p) y story-1080.mp4/feed-1080.mp4.
set -e
COMP=$1; SEQ=$2; STILL=$3; DEST=$4
R=/mnt/c/Users/Veintiuno/barullo-render/carteles
REM=/home/ddev/www/barullo/remotion
OUT=$R/final/$DEST
BUNDLE=${BUNDLE:-/tmp/barullo-carteles-bundle}
mkdir -p "$OUT"
curl -sf -o /dev/null http://127.0.0.1:8765/shapes.json || { echo "Arranca antes: python3 serve.py $R/assets"; exit 1; }
cd "$REM"
npx remotion bundle src/carteles/index.ts --public-dir="$R/public" --out-dir="$BUNDLE" --log=error >/dev/null
PROPS="{\"seq\":\"$SEQ\"}"
for v in Story Feed; do
  lo=$(echo $v | tr A-Z a-z)
  npx remotion render "$BUNDLE" "$COMP-$v" "$OUT/$lo.mp4" --props="$PROPS" --codec=h264 --crf=16 --pixel-format=yuv420p \
    --concurrency=${CONC:-4} --log=error
  npx remotion still "$BUNDLE" "$COMP-$v" "$OUT/$lo.png" --props="$PROPS" --frame="$STILL" --log=error
  npx remotion ffmpeg -hide_banner -loglevel error -y -i "$OUT/$lo.png" -q:v 2 "$OUT/$lo.jpg"
  rm "$OUT/$lo.png"
  # versión ligera para subir rápido a Instagram
  npx remotion ffmpeg -hide_banner -loglevel error -y -i "$OUT/$lo.mp4" -vf "scale=1080:-2:flags=lanczos" \
    -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart "$OUT/$lo-1080.mp4"
  echo "OK $OUT/$lo.mp4"
done
