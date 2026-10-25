"""Prepara la carpeta public de Remotion para los carteles.

  python3 prep.py <public_dir> <repo_root> [estilos_dir]

- Alfombra LED y riso a tamaño de cartel (story 120x213 nudos, feed 120x150) con el
  generador de bocetos/animaciones/alfombra/carpet.py (se ejecuta solo su parte de funciones).
- shapes.json: estrella de 8 puntas de la «o» (contorno + hueco) como path SVG en 0..1000.
- lettering-<estilo>.png: los PNG de Blender recortados a su caja.
"""
import json, os, sys
import numpy as np
from PIL import Image

PUB, REPO = sys.argv[1], sys.argv[2]
EST = sys.argv[3] if len(sys.argv) > 3 else '/mnt/c/Users/Veintiuno/barullo-render/estilos'
TEX = '/mnt/c/Users/Veintiuno/barullo-render/logo-alfombra/tex/medal/frame.json'
os.makedirs(PUB, exist_ok=True)

src = open(os.path.join(REPO, 'bocetos/animaciones/alfombra/carpet.py')).read()
src = src[:src.index('\nC = carpet()')]
g = {'__name__': 'carpet', 'sys': sys}
sys.argv = ['carpet.py', PUB, REPO]
exec(src, g)

for name, (w, h) in {'story': (120, 213), 'feed': (120, 150)}.items():
    idx = g['carpet'](w, h)
    # LED a plena luz: el atenuado y el barrido se animan en Remotion
    g['render_led'](idx, k=18, dim=1.0).save(os.path.join(PUB, f'led-{name}.jpg'), quality=90)
    g['render_riso'](idx, k=18).save(os.path.join(PUB, f'riso-{name}.jpg'), quality=90)
    print('carpet', name, idx.shape)

fr = json.load(open(TEX))
cx, cy, hs = fr['cx'], fr['cy'], fr['hs']
def path(poly):
    pts = [((x - cx) / hs * 500 + 500, (y - cy) / hs * 500 + 500) for x, y in poly]
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'
json.dump({'star': path(fr['outer']), 'hole': path(fr['hole'])}, open(os.path.join(PUB, 'shapes.json'), 'w'))

for st in sorted(os.listdir(EST)):
    p = os.path.join(EST, st, 'lettering.png')
    if not os.path.exists(p):
        continue
    im = Image.open(p).convert('RGBA')
    x0, y0, x1, y1 = im.getbbox()
    m = 6
    im.crop((x0 - m, y0 - m, x1 + m, y1 + m)).save(os.path.join(PUB, f'lettering-{st}.png'))
    print('lettering', st, x1 - x0, y1 - y0)
