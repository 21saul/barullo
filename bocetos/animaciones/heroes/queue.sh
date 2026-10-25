#!/usr/bin/env bash
# Cola de renders de los héroes. Lanza un trabajo detrás de otro y, antes de
# cada uno, espera a que no haya otro blender.exe en marcha: dos renders a la
# vez en la iGPU dan fotogramas negros (ver memoria «blender-headless-setup»).
#
#   setsid nohup bocetos/animaciones/heroes/queue.sh jobs.txt > cola.log 2>&1 &
#
# Cada línea de jobs.txt: VAR=valor ... -- <script relativo> -- <args del script>
# (al menos una variable, aunque sea Q=1). Para poder reanudar, conviene partir
# los bucles largos en tramos de fotogramas, una línea por tramo.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
JOBS="$1"

# Renders que van sólo en CPU (Cycles device=CPU) y no tocan la GPU: no bloquean.
CPU_ONLY=${CPU_ONLY:-diablillo|device=CPU}

busy() {
  # Sólo cuentan los render en segundo plano (-b): un Blender abierto con
  # interfaz no ocupa la GPU y no debe bloquear la cola.
  powershell.exe -NoProfile -Command \
    "(Get-CimInstance Win32_Process -Filter \"name='blender.exe'\" | Where-Object { \$_.CommandLine -match ' -b ' -and \$_.CommandLine -notmatch '$CPU_ONLY' } | Measure-Object).Count" < /dev/null 2>/dev/null | tr -d '\r'
}

# Permiso explícito: la GPU la reparte otra sesión. Hasta que exista este
# fichero (lo crea quien coordina, o se crea a mano) la cola no arranca.
GO="/mnt/c/Users/Veintiuno/barullo-render/heroes/GO"
QUIET=${QUIET:-600}   # segundos seguidos sin ningún blender.exe antes de empezar

wait_gpu() {
  while [[ ! -e "$GO" ]]; do echo "$(date +%T) sin GO — espero"; sleep 120; done
  local since=""
  while :; do
    n="$(busy)"
    # CIM a veces devuelve vacío: eso NO significa libre
    if [[ "$n" == "0" ]]; then
      since=${since:-$(date +%s)}
      (( $(date +%s) - since >= QUIET )) && return
    else
      since=""; echo "$(date +%T) GPU ocupada (${n:-?} blender) — espero"
    fi
    sleep 30
  done
}

# La lista se lee por el descriptor 3: powershell.exe y blender.exe leen la
# entrada estándar y, si no, se comen el resto de líneas.
while IFS= read -r line <&3; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  envs="${line%% -- *}"; cmd="${line#* -- }"
  QUIET=${FIRST_QUIET:-$QUIET} wait_gpu; FIRST_QUIET=20   # entre trabajos propios basta un respiro
  echo "$(date +%T) START $line"
  # < /dev/null: si no, blender.exe se come la entrada del bucle (el resto de la lista)
  env $envs "$HERE/blender.sh" $cmd < /dev/null 2>&1 | grep -E "FRAME|Error|Traceback|GLARE"
  echo "$(date +%T) END $line"
done 3< "$JOBS"
echo "$(date +%T) COLA TERMINADA"
