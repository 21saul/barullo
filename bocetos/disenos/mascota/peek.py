"""peek.py salida.jpg a.png b.png ... — pega PNGs RGBA sobre el negro de la web, en fila."""
import sys
from PIL import Image
out, *ins = sys.argv[1:]
ims = [Image.open(p).convert("RGBA") for p in ins]
h = max(i.height for i in ims)
canvas = Image.new("RGB", (sum(i.width for i in ims), h), (11, 13, 17))
x = 0
for im in ims:
    bg = Image.new("RGBA", im.size, (11, 13, 17, 255)); bg.alpha_composite(im)
    canvas.paste(bg.convert("RGB"), (x, 0)); x += im.width
canvas.save(out, quality=92)
