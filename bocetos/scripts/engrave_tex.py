"""Engraving masks in wordmark space: <name>-lines.png (niello), <name>-fill.png (enamel), <name>-col.png (enamel colour)."""
import sys, os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

MASK, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
m = np.asarray(Image.open(MASK)) > 127
H, W = m.shape
d = ndimage.distance_transform_edt(m)
Y, X = np.mgrid[0:H, 0:W].astype(float)
LW = 1.7  # half line width in px

def band(v, w=LW):
    return np.abs(v) < w

def star_g(x, y):
    return np.minimum(np.maximum(abs(x), abs(y)), (abs(x) + abs(y)) / 1.414)

def border():
    """double guard line + bead chain following each letter's contour"""
    L = band(d - 7) | band(d - 19)
    beads = (abs(d - 13) < 3.2) & (np.sin(X / 4.2) * np.sin(Y / 4.2) > 0.25)
    return L | beads, d > 24

def rosettes(p=58):
    u = ((X + Y) % p) - p / 2; v = ((X - Y) % p) - p / 2
    lines = band(u, 1.3) | band(v, 1.3)
    cx = (X % p) - p / 2; cy = (Y % p) - p / 2
    r = np.hypot(cx, cy); th = np.arctan2(cy, cx)
    R = p * 0.3 * (0.62 + 0.38 * np.abs(np.cos(4 * th)))
    inside = r < R
    lines = (lines & ~inside) | band(r - R) | (r < 3.2)
    fill = (r < R - 3) & (r > 6)
    return lines, fill, (np.floor(X / p) + np.floor(Y / p)) % 2

def girih(p=66):
    cx = (X % p) - p / 2; cy = (Y % p) - p / 2
    g = star_g(cx, cy); s = p * 0.36
    o = np.maximum(np.maximum(abs(cx), abs(cy)), (abs(cx) + abs(cy)) / 1.414)
    lines = band(g - s) | band(o - s * 0.55)
    lines |= (band(cx, 1.2) | band(cy, 1.2)) & (g > s)
    fill = (g < s - 3) & (o > s * 0.55 + 3)
    return lines, fill, ((np.floor(X / p) * 3 + np.floor(Y / p)) % 3)

def vines(p=62, lam=96):
    row = np.floor(Y / p)
    v = (Y % p) - p / 2 - 10 * np.sin(2 * np.pi * X / lam + row * 1.3)
    lines = band(v)
    k = np.floor(X / (lam / 2)); lx = (X % (lam / 2)) - lam / 4
    side = np.where(k % 2 == 0, 1, -1)
    ly = v - side * 11
    a = np.radians(35) * side
    rx = lx * np.cos(a) + ly * np.sin(a); ry = -lx * np.sin(a) + ly * np.cos(a)
    e = (rx / 15) ** 2 + (ry / 6.5) ** 2
    lines |= band(e - 1, 0.18)
    # tendril curls
    tx = (X % (lam / 2)) - lam / 4 + 14; ty = v + side * 12
    rr = np.hypot(tx, ty); tt = np.arctan2(ty, tx)
    lines |= band(rr - (3 + 1.6 * ((tt + np.pi) % (2 * np.pi))), 1.1) & (rr < 13)
    fill = e < 0.75
    return lines, fill, k % 3

def scales(p=40):
    row = np.floor(Y / (p / 2))
    cx = ((X + (row % 2) * p / 2) % p) - p / 2
    cy = (Y % (p / 2))
    r = np.hypot(cx, cy)
    lines = band(r - p / 2) & (cy >= 0) | band(r - p / 2 + 6, 1.1)
    fill = r < p / 2 - 8
    return lines, fill, row % 3

def guilloche():
    w = np.sin(d * 2 * np.pi / 7 + 2.2 * np.sin(X / 26) * np.sin(Y / 31))
    lines = w > 0.86
    return lines, np.zeros_like(lines), np.zeros_like(X)

PAL = np.array([[226, 38, 28], [246, 164, 60], [255, 79, 168]], float)

def save(name, lines, fill, idx, enamel=None):
    bl, inner = border()
    L = (bl | (lines & inner)) & m
    F = fill & inner & m & ~L
    def w(a, fn, blur=0.7):
        Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur)).save(os.path.join(OUT, fn))
    w(L, f'{name}-lines.png'); w(F, f'{name}-fill.png')
    if enamel is None:
        col = PAL[idx.astype(int) % 3]
    else:
        col = np.zeros((H, W, 3)); col[:] = enamel
    Image.fromarray(col.astype(np.uint8)).save(os.path.join(OUT, f'{name}-col.png'))
    print(name)

for name, fn in (('rosetas', rosettes), ('girih', girih), ('arabesco', vines), ('escamas', scales), ('guilloche', guilloche)):
    save(name, *fn())
# a "todo" pattern: guilloché band + rosettes
gl, _, _ = guilloche(); rl, rf, ri = rosettes(70)
band_zone = (d > 24) & (d < 40)
save('todo', (gl & band_zone) | (rl & (d >= 40)), rf & (d >= 46), ri)
