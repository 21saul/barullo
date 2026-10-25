"""Prepara la foto de un/a DJ para las plantillas (se hace una vez por foto, tarda ~20 s).

  PYTHONPATH=~/.local/rembg-lib python3 prep_foto.py <foto.jpg> [<carpeta salida>=barullo-render/carteles/assets/dj-plantillas/fotos]

Escribe, con el nombre de la foto como base:
  <n>.jpg          copia a máx. 2400 px (la usan las tres plantillas)
  <n>-blur.jpg     desenfocada (el panel de cristal de la plantilla B)
  <n>-cut.png      DJ recortado/a sin fondo (rembg, modelo local gratuito; plantilla C)
  <n>-borde.png    silueta dilatada en blanco (el borde de pegatina de la plantilla C)
  <n>.json         caja del recorte (0..1) para encuadrar
rembg: pip install --target ~/.local/rembg-lib "rembg[cpu]" (descarga el modelo la primera vez, gratis).
"""
import json, os, sys
from PIL import Image, ImageFilter

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else '/mnt/c/Users/Veintiuno/barullo-render/carteles/assets/dj-plantillas/fotos'
os.makedirs(out, exist_ok=True)
n = os.path.splitext(os.path.basename(src))[0]
im = Image.open(src).convert('RGB')
im.thumbnail((2400, 2400), Image.LANCZOS)
im.save(os.path.join(out, n + '.jpg'), quality=92)

bl = im.resize((im.width // 4, im.height // 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(im.width / 4 * 0.025))
bl.resize(im.size, Image.BICUBIC).save(os.path.join(out, n + '-blur.jpg'), quality=90)

from rembg import new_session, remove  # noqa: E402
sess = new_session(os.environ.get('REMBG_MODEL', 'isnet-general-use'))
cut = remove(im, session=sess, post_process_mask=True)
a = cut.getchannel('A')
# limpia el halo: umbral suave del alfa
a = a.point(lambda v: 0 if v < 24 else (255 if v > 200 else int((v - 24) * 255 / 176)))
cut.putalpha(a)
cut.save(os.path.join(out, n + '-cut.png'))

r = max(4, im.width // 110)  # grosor del borde de pegatina
dil = a.point(lambda v: 255 if v > 90 else 0).filter(ImageFilter.MaxFilter(3))
for _ in range(r // 2):
    dil = dil.filter(ImageFilter.MaxFilter(5))
dil = dil.filter(ImageFilter.GaussianBlur(1.2))
borde = Image.new('RGBA', im.size, (255, 255, 255, 0)); borde.putalpha(dil)
borde.save(os.path.join(out, n + '-borde.png'))

bb = a.point(lambda v: 255 if v > 128 else 0).getbbox() or (0, 0, im.width, im.height)
json.dump(dict(w=im.width, h=im.height, bbox=[bb[0] / im.width, bb[1] / im.height, bb[2] / im.width, bb[3] / im.height]),
          open(os.path.join(out, n + '.json'), 'w'))
print('OK', n, bb)
