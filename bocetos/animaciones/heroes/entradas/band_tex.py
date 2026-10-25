"""Cinta jacquard de las pulseras de tela (héroe de /entradas).

Tejido a máquina: hilos de urdimbre a lo largo, el wordmark kufi repetido y
estrellas de ocho puntas entre medias, con orillos de colores. Saca, por
variante, albedo + normal + rugosidad para Blender.

    python3 band_tex.py <wordmark.json> <salida>
"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

WM, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

L, H = 4096, 288            # largo x ancho en px (cinta de ~22 cm x 15 mm)
PIT = 4                     # px por hilo
REP = 5                     # wordmarks a lo largo

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255

VARIANTES = {
    # fondo, dibujo, orillo exterior, orillo interior
    'roja': ('#D9221A', '#F2EBDD', '#141010', '#F6A43C'),
    'negra': ('#141010', '#E2261C', '#E2261C', '#FF4FA8'),
    'hueso': ('#EFE6D6', '#C91E16', '#C91E16', '#141010'),
}

wm = json.load(open(WM))

def motif_mask():
    """Máscara (H, L) con el wordmark repetido y una estrella entre cada dos."""
    im = Image.new('L', (L, H), 0)
    d = ImageDraw.Draw(im)
    band = H * 0.64                      # alto del wordmark dentro de la cinta
    s = band / wm['h']
    cell = L / REP
    ww = wm['w'] * s
    for k in range(REP):
        x0 = k * cell + (cell - ww) / 2 + cell * 0.12
        y0 = (H - wm['h'] * s) / 2
        for poly in wm['polys']:
            d.polygon([(x0 + x * s, y0 + y * s) for x, y in poly], fill=255)
        # estrella de ocho puntas (dos cuadrados girados) entre wordmarks
        cx, cy, r = k * cell + cell * 0.07, H / 2, H * 0.17
        for a0 in (0, 45):
            pts = [(cx + r * np.cos(np.radians(a0 + 45 + 90 * i)), cy + r * np.sin(np.radians(a0 + 45 + 90 * i)))
                   for i in range(4)]
            d.polygon(pts, fill=255)
    m = np.array(im, float) / 255
    # al tejerse, el dibujo se cuantiza a la rejilla de hilos
    m = m.reshape(H // PIT, PIT, L // PIT, PIT).mean((1, 3)) > 0.5
    return np.kron(m, np.ones((PIT, PIT))).astype(bool)

M = motif_mask()
y, x = np.mgrid[0:H, 0:L]
edge = np.minimum(y, H - 1 - y)

# relieve: urdimbre a lo largo (líneas en x) y, donde hay dibujo, trama flotante
warp = 0.5 + 0.5 * np.cos(2 * np.pi * (y % PIT) / PIT)
weft = 0.5 + 0.5 * np.cos(2 * np.pi * (x % (PIT * 2)) / (PIT * 2))
height = np.where(M, 0.55 + 0.35 * weft * 0.6 + 0.2 * warp, 0.35 * warp + 0.15 * weft)
height[edge < 14] = 0.25 + 0.4 * warp[edge < 14]          # orillos más planos
height = ndimage.gaussian_filter(height, 0.7)
gy, gx = np.gradient(height * 3.0)
n = np.dstack([-gx, -gy, np.ones_like(height)])
n /= np.linalg.norm(n, axis=2, keepdims=True)
Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(OUT, 'band_normal.png'))
rough = np.where(M, 0.62, 0.78) - 0.08 * warp
Image.fromarray((np.clip(rough, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, 'band_rough.png'))

rng = np.random.default_rng(3)
noise = ndimage.gaussian_filter(rng.normal(0, 1, (H, L)), (0.6, 3))   # fibra
for name, (bgc, fgc, e1, e2) in VARIANTES.items():
    col = np.where(M[..., None], hexc(fgc), hexc(bgc))
    col[(edge < 7)] = hexc(e1)
    col[(edge >= 7) & (edge < 13)] = hexc(e2)
    shade = 0.84 + 0.16 * warp[..., None] + 0.035 * noise[..., None]
    out = np.clip(col * shade, 0, 1)
    Image.fromarray((out * 255).astype(np.uint8)).save(os.path.join(OUT, f'band_{name}.png'))
    print(name)
