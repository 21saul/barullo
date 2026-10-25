#!/bin/bash
# full loop, EEVEE on the iGPU; skips frames that already exist so it can be resumed
cd /mnt/c/Users/Veintiuno/barullo-render/colgante
for i in 1 2 3; do
  ./multi.sh frames=0-209 engine=eevee samples=64 mr=2 grid=700 out=C:/Users/Veintiuno/barullo-render/colgante/frames/f_ save=C:/Users/Veintiuno/barullo-render/colgante/colgante.blend >> frames/render.log
  n=$(ls frames/f_*.png 2>/dev/null | wc -l); [ "$n" -ge 210 ] && break
done
echo ALLDONE $(ls frames/f_*.png | wc -l)
