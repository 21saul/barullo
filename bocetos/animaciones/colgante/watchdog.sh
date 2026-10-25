#!/bin/bash
# Keeps the pendant render alive until all 210 frames exist:
# - if no new frame appears for STALL seconds, kills the hung colgante Blender (only that one) so the
#   render loop resumes from the next missing frame;
# - if the render loop itself has exited early, starts it again.
# Prints one line per intervention and DONE at the end.
DIR=/mnt/c/Users/Veintiuno/barullo-render/colgante
STALL=${STALL:-600}
count() { ls "$DIR"/frames/f_*.png 2>/dev/null | wc -l; }
colgante_pid() {
  powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name='blender.exe'\" | Where-Object { \$_.CommandLine -like '*colgante.py*' } | ForEach-Object { \$_.ProcessId }" 2>/dev/null | tr -d '\r' | head -1
}
last=$(count); since=$(date +%s)
while [ "$(count)" -lt 210 ]; do
  sleep 20
  n=$(count)
  if [ "$n" -gt "$last" ]; then last=$n; since=$(date +%s); continue; fi
  if ! pgrep -f "render_all.sh|render_cycles.sh" >/dev/null; then
    echo "$(date +%H:%M) render loop not running at $n frames: restarting"
    (cd "$DIR" && nohup ./render_cycles.sh >/dev/null 2>&1 &)
    since=$(date +%s); continue
  fi
  if [ $(( $(date +%s) - since )) -gt "$STALL" ]; then
    pid=$(colgante_pid)
    echo "$(date +%H:%M) stalled at $n frames for ${STALL}s: killing Blender $pid"
    [ -n "$pid" ] && taskkill.exe /PID "$pid" /F >/dev/null
    since=$(date +%s)
  fi
done
echo "$(date +%H:%M) DONE $(count) frames"
