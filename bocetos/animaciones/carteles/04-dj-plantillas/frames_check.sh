#!/bin/bash
# Extrae los frames 0, 100 y 239 de un mp4 y los pone en una tira (revisión de bucle y legibilidad):
#   bash frames_check.sh <video.mp4> <salida.jpg>
set -e
V=$1; O=$2; T=$(mktemp -d)
cd /home/ddev/www/barullo/remotion
for n in 0 100 239; do
  npx remotion ffmpeg -hide_banner -loglevel error -y -i "$V" -ss $(python3 -c "print(max(0,$n/30-0.005))") -frames:v 1 "$T/f$n.png"
done
python3 -c "
from PIL import Image
ims=[Image.open('$T/f%d.png'%n).convert('RGB') for n in (0,100,239)]
w=540; ims=[i.resize((w,int(i.height*w/i.width))) for i in ims]
c=Image.new('RGB',(w*3+20,ims[0].height),(128,128,128))
for k,i in enumerate(ims): c.paste(i,(k*(w+10),0))
c.save('$O',quality=88)"
rm -rf "$T"; echo "$O"
