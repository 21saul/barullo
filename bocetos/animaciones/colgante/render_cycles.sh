#!/bin/bash
# full loop in Cycles on the Radeon iGPU (HIP); skips frames that already exist so it can be resumed
cd /mnt/c/Users/Veintiuno/barullo-render/colgante
for i in 1 2 3 4 5 6; do
  ./multi.sh frames=0-209 engine=cycles samples=16 mr=3 grid=700 out=C:/Users/Veintiuno/barullo-render/colgante/frames/f_ >> frames/render.log
  n=$(ls frames/f_*.png 2>/dev/null | wc -l); [ "$n" -ge 210 ] && break
done
echo ALLDONE $(ls frames/f_*.png | wc -l)
