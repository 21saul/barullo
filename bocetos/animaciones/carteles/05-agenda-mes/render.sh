#!/bin/bash
# Agenda del mes de Barullo: story animada, feed en bucle y PNG fijo, todo a partir de un JSON de datos.
#
#   bash render.sh [datos.json] [check]
#
# datos.json: por defecto agenda-2026-11.json (al lado de este script). Para otro mes, copia el JSON,
# cambia mes y noches y pásalo aquí. Con "check" solo saca fotogramas de revisión (rápido).
# Necesita el servidor de assets: python3 ../comun/serve.py C:/Users/Veintiuno/barullo-render/carteles/assets
# (en WSL: /mnt/c/Users/Veintiuno/barullo-render/carteles/assets) en el puerto 8765.
#
# Salida: C:/Users/Veintiuno/barullo-render/carteles/agenda-mes/<AAAA-MM>/ y copia en el escritorio
# (REBRANDING BARULLO/04_CARTELES/AGENDA_MES/).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
DATA=$(realpath "${1:-$HERE/agenda-2026-11.json}")
MODE=${2:-full}
R=/mnt/c/Users/Veintiuno/barullo-render/carteles
REM=/home/ddev/www/barullo/remotion
DESK="/mnt/c/Users/Veintiuno/Desktop/REBRANDING BARULLO/04_CARTELES/AGENDA_MES"
BUNDLE=${BUNDLE:-/tmp/barullo-agenda-bundle}

TAG=$(python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
m=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'].index(d['month'])+1
print(f\"{d['year']}-{m:02d}_{d['month']}\")" "$DATA")
OUT=$R/agenda-mes/$TAG
mkdir -p "$OUT"
curl -sf -o /dev/null http://127.0.0.1:8765/agenda/emblema.svg || { echo "Arranca antes: python3 $HERE/../comun/serve.py $R/assets"; exit 1; }

cd "$REM"
npx remotion bundle src/carteles/index.ts --public-dir="$R/public" --out-dir="$BUNDLE" --log=error >/dev/null
STILL=$(mktemp --suffix=.json)
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); d['still']=True; json.dump(d,open(sys.argv[2],'w'))" "$DATA" "$STILL"

if [ "$MODE" = check ]; then
  mkdir -p "$OUT/check"
  for fr in 40 70 130 200 300 420 470 540 580; do
    npx remotion still "$BUNDLE" Agenda-Story "$OUT/check/story_$fr.png" --props="$DATA" --frame=$fr --log=error
  done
  for fr in 0 45 89; do
    npx remotion still "$BUNDLE" Agenda-Feed "$OUT/check/feed_$fr.png" --props="$DATA" --frame=$fr --log=error
  done
  echo "Revisión en $OUT/check"; exit 0
fi

# vídeos 1080 nativos, H.264 30 fps
npx remotion render "$BUNDLE" Agenda-Story "$OUT/${TAG}_agenda_story.mp4" --props="$DATA" --codec=h264 --crf=16 \
  --pixel-format=yuv420p --concurrency=${CONC:-4} --log=error
npx remotion render "$BUNDLE" Agenda-Feed "$OUT/${TAG}_agenda_feed.mp4" --props="$DATA" --codec=h264 --crf=16 \
  --pixel-format=yuv420p --concurrency=${CONC:-4} --log=error
# PNG fijos a 2x (2160 de ancho): el mes entero en feed y la lista de la story
npx remotion still "$BUNDLE" Agenda-Feed "$OUT/${TAG}_agenda_feed.png" --props="$STILL" --frame=0 --scale=2 --log=error
LIST=$(python3 -c "
import json,sys,datetime
d=json.load(open(sys.argv[1]))
ds=sorted(datetime.date.fromisoformat(e['date']) for e in d['events'])
w=[];k=None
for x in ds:
    mon=x-datetime.timedelta(days=x.weekday())
    if mon!=k or len(w[-1])>=3: w.append([x])
    else: w[-1].append(x)
    k=mon
print(84+90*len(w)+96)" "$DATA")
npx remotion still "$BUNDLE" Agenda-Story "$OUT/${TAG}_agenda_story.png" --props="$DATA" --frame="$LIST" --scale=2 --log=error
rm -f "$STILL"
for f in "$OUT"/*.png; do npx remotion ffmpeg -hide_banner -loglevel error -y -i "$f" -q:v 2 "${f%.png}.jpg"; done
mkdir -p "$DESK"
cp "$OUT"/*.mp4 "$OUT"/*.png "$OUT"/*.jpg "$DESK/"
echo "OK $OUT  →  $DESK"
