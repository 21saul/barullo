#!/bin/bash
# Lettering de los 5 estilos al 200% (3600x1728) para que la cabecera no se reescale en 4K.
B="/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
W='C:/Users/Veintiuno/barullo-render/logo-alfombra'
O=/mnt/c/Users/Veintiuno/barullo-render/carteles/assets/med/lettering
mkdir -p $O
for s in ${@:-oro-turquesa oro-perlas oro-girih-rubi oro-esmeralda oro-rosa-coral}; do
  [ -f $O/$s.png ] || WSLENV=RES_PCT RES_PCT=200 "$B" -b --factory-startup --python "$W/engr.py" -- "$W" "$s" "C:/Users/Veintiuno/barullo-render/carteles/assets/med/lettering/$s.png" 2>&1 | grep -E "RENDERED|Error|Traceback"
done
echo ALLDONE
