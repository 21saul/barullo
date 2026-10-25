#!/bin/bash
# Monta los 5 flyers en Remotion con las secuencias ya renderizadas: story y feed en mp4 (H.264 CRF 16,
# yuv420p), jpg del frame STILL y versiones 1080. Solo monta un estilo si tiene sus 240 frames y pts.json.
#   bash render_flyers.sh [1 2 3 4 5]
set -e
R=/mnt/c/Users/Veintiuno/barullo-render/carteles
REM=/home/ddev/www/barullo/remotion
DEST=/home/ddev/www/barullo/bocetos/animaciones/carteles/medallones
BUNDLE=${BUNDLE:-/tmp/barullo-carteles-bundle}
STILL=${STILL:-0}
STYLES=(x oro-turquesa oro-perlas oro-girih-rubi oro-esmeralda oro-rosa-coral)
curl -sf -o /dev/null http://127.0.0.1:8765/shapes.json || { echo "Arranca antes: python3 comun/serve.py $R/assets"; exit 1; }
cd "$REM"
npx remotion bundle src/carteles/index.ts --public-dir="$R/public" --out-dir="$BUNDLE" --log=error >/dev/null
for i in ${@:-1 2 3 4 5}; do
  s=${STYLES[$i]}
  n=$(ls $R/assets/med/$s/m_*.png 2>/dev/null | wc -l)
  if [ "$n" -lt 240 ] || [ ! -f $R/assets/med/$s/pts.json ] || [ ! -f $R/assets/med/lettering/$s.png ]; then
    echo "SALTO $s: $n/240 frames"; continue
  fi
  OUT=$DEST/0$i-$s; mkdir -p "$OUT"
  for v in Story Feed; do
    lo=$(echo $v | tr A-Z a-z)
    npx remotion render "$BUNDLE" "Medallon$i-$v" "$OUT/$lo.mp4" --props='{"frames":true}' --codec=h264 --crf=16 \
      --pixel-format=yuv420p --concurrency=${CONC:-6} --log=error
    npx remotion still "$BUNDLE" "Medallon$i-$v" "$OUT/$lo.png" --props='{"frames":true}' --frame="$STILL" --log=error
    npx remotion ffmpeg -hide_banner -loglevel error -y -i "$OUT/$lo.png" -q:v 2 "$OUT/$lo.jpg"
    rm "$OUT/$lo.png"
    npx remotion ffmpeg -hide_banner -loglevel error -y -i "$OUT/$lo.mp4" -vf "scale=1080:-2:flags=lanczos" \
      -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart "$OUT/$lo-1080.mp4"
    echo "OK $OUT/$lo.mp4"
  done
done
