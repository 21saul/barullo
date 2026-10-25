#!/bin/bash
# Renders every style in estilos.json as lettering + medal, then the medal formats.
B="/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
W='C:/Users/Veintiuno/barullo-render/logo-alfombra'
O=/mnt/c/Users/Veintiuno/barullo-render/estilos
cd /mnt/c/Users/Veintiuno/barullo-render/logo-alfombra
for s in $(python3 -c "import json;print(' '.join(k for k in json.load(open('estilos.json')) if not k.startswith('_')))"); do
  mkdir -p "$O/$s"
  [ -f "$O/$s/medalla.png" ] || "$B" -b --factory-startup --python "$W/medal.py" -- "$W" "$s" "C:/Users/Veintiuno/barullo-render/estilos/$s/medalla.png" 2>&1 | grep -E "RENDERED|Error|Traceback"
  [ -f "$O/$s/lettering.png" ] || "$B" -b --factory-startup --python "$W/engr.py" -- "$W" "$s" "C:/Users/Veintiuno/barullo-render/estilos/$s/lettering.png" 2>&1 | grep -E "RENDERED|Error|Traceback"
done
mkdir -p "$O/_formatos-medalla"
for f in med-cinta med-moneda med-puas med-pin; do
  [ -f "$O/_formatos-medalla/$f.png" ] || "$B" -b --factory-startup --python "$W/medal.py" -- "$W" "$f" "C:/Users/Veintiuno/barullo-render/estilos/_formatos-medalla/$f.png" 2>&1 | grep -E "RENDERED|Error|Traceback"
done
echo ALLDONE
