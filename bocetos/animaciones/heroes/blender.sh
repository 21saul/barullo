#!/usr/bin/env bash
# Lanza Blender de Windows en modo headless desde WSL.
#   blender.sh <script.py relativo a bocetos/animaciones/heroes> -- <args del script>
# Las variables de entorno que el script lea (CAM, TGT...) se pasan con WSLENV.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$1"; shift
WIN='\\wsl.localhost\DDEV'"$(echo "$HERE/$SCRIPT" | sed 's#/#\\#g')"
export WSLENV="${WSLENV:-}:CAM:TGT:LENS:YAW:RUG_FUZZ:RUGHIDE:EMBERS:DRY:SKIP"
exec "/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python "$WIN" "$@"
