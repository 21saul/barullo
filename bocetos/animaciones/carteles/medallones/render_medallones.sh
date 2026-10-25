#!/bin/bash
# Renderiza los 5 medallones (240 frames cada uno) por tramos de 30 frames, un Blender por tramo:
# si uno muere, el siguiente sigue y medallon_anim.py salta los PNG que ya existen.
# Al final de cada estilo comprueba que estén los 240 frames, repite los que falten y une los pts_*.json.
#   setsid nohup bash render_medallones.sh [estilos...] > log 2>&1 &
B="/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
S='\\wsl.localhost\DDEV\home\ddev\www\barullo\design\carteles\medallones\medallon_anim.py'
D=C:/Users/Veintiuno/barullo-render/logo-alfombra
OUTW=C:/Users/Veintiuno/barullo-render/carteles/assets/med
OUTL=/mnt/c/Users/Veintiuno/barullo-render/carteles/assets/med
STYLES=${@:-oro-turquesa oro-perlas oro-girih-rubi oro-esmeralda oro-rosa-coral}
SAMPLES=${SAMPLES:-24}; RES=${RES:-1400}
for s in $STYLES; do
  for pass in 1 2 3; do
    for a in $(seq 0 30 239); do
      b=$((a + 29))
      "$B" -b --factory-startup --python "$S" -- $D $s $OUTW/$s $a-$b $SAMPLES $RES 2>&1 | grep -E "Error|Traceback|DONE"
    done
    n=$(ls $OUTL/$s/m_*.png 2>/dev/null | wc -l)
    echo "$(date +%H:%M) $s pasada $pass: $n/240"
    [ "$n" -ge 240 ] && break
  done
  python3 -c "
import json,glob,sys
d={}
for p in sorted(glob.glob('$OUTL/$s/pts_*.json')): d.update(json.load(open(p)))
json.dump(d,open('$OUTL/$s/pts.json','w')); print('pts', len(d))"
done
echo ALLDONE
