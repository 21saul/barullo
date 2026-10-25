"""Texturas del corredor (alfombra larga) para el héroe de «Propón una noche».

Se corta la alfombra voladora (bocetos/animaciones/alfombra/rug) por dos columnas
simétricas: [A, W-A) en nudos. Como el diseño es simétrico en espejo, la
última columna del trozo es igual a la primera, y al repetirlo a lo largo el
corredor no tiene costura: borde con borde, enjutas con enjutas.

    python3 runner_tex.py <tex_alfombra> <salida> [A]
"""
import sys, os
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
A = int(sys.argv[3]) if len(sys.argv) > 3 else 38          # en nudos
K = 8                                                      # px por nudo
os.makedirs(OUT, exist_ok=True)
for name in ('albedo', 'normal', 'rough'):
    im = Image.open(os.path.join(SRC, f'{name}.png'))
    W = im.width // K
    # la columna W-A-1 es espejo de la A: se quita una para no duplicarla
    tile = im.crop((A * K, 0, (W - A - 1) * K, im.height))
    tile.save(os.path.join(OUT, f'runner_{name}.png'))
    print(name, tile.size)
