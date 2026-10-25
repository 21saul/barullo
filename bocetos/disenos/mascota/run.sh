#!/usr/bin/env bash
# run.sh <args del script> — lanza diablillo.py en el Blender de Windows (CPU, 6 hilos)
HERE="$(cd "$(dirname "$0")" && pwd)"
WIN='\\wsl.localhost\DDEV'"$(echo "$HERE/diablillo.py" | sed 's#/#\\#g')"
exec "/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -t "${THREADS:-6}" --python "$WIN" -- "$@"
