"""Carpet textures in wordmark space: letters woven as carpet, rug with woven logo, LED knot colors."""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage

MASK, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(3)
m = np.asarray(Image.open(MASK)) > 127
H, W = m.shape

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
RISO = np.array([hexc(c) for c in ('#E2261C', '#A8140F', '#F6A43C', '#FF4FA8', '#FFF1E2', '#0B0B0B')])

def down(mask, cols):
    rows = int(round(cols * mask.shape[0] / mask.shape[1]))
    im = Image.fromarray((mask * 255).astype(np.uint8)).resize((cols, rows), Image.BOX)
    return np.asarray(im) > 127

def star8(x, y, s):
    return (np.maximum(abs(x), abs(y)) <= s) | ((abs(x) + abs(y)) <= s * 1.41)

def riso(idx, k, speck=0.09):
    big = np.kron(idx, np.ones((k, k), int))
    img = RISO[big].copy()
    n = rng.random(big.shape)
    img[(big >= 2) & (big <= 4) & (n < speck)] = RISO[0]
    img[(big == 0) & (n < 0.05)] = RISO[1]
    img += rng.normal(0, 8, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)

def woven_letters(cols, period, edge=(1.5, 2.5, 3.5)):
    km = down(m, cols)
    d = ndimage.distance_transform_edt(km)
    h, w = km.shape
    y, x = np.mgrid[0:h, 0:w]
    idx = np.zeros((h, w), int)
    lat = ((x + y) % period == 0) | ((x - y) % period == 0)
    idx[lat] = 1
    nx = (x % period) - period / 2; ny = (y % period) - period / 2
    alt = ((x // period + y // period) % 2 == 0)
    fl = star8(nx, ny, period * 0.22)
    idx[fl & alt] = 2; idx[fl & ~alt] = 3
    idx[(abs(nx) < 0.6) & (abs(ny) < 0.6)] = 4
    e1, e2, e3 = edge
    idx[d <= e3] = 3
    idx[d <= e2] = 1
    idx[d <= e1] = 2
    return km, idx

# 1) letters texture for the 3D wordmark (aligned to the mask canvas)
km, idx = woven_letters(415, 8)
k = 7
img = riso(idx, k)
Image.fromarray(img).resize((W, H), Image.NEAREST).save(os.path.join(OUT, 'letters-riso.png'))

# 2) LED knots: positions + colour index per knot (letters only)
km2, idx2 = woven_letters(150, 4, edge=(1.0, 1.0, 1.0))
ys, xs = np.where(km2)
json.dump({'cols': km2.shape[1], 'rows': km2.shape[0],
           'knots': [[int(a), int(b), int(idx2[a, b])] for a, b in zip(ys, xs)]},
          open(os.path.join(OUT, 'knots.json'), 'w'))
print('knots', len(ys))

# 3) rug with the logo woven into the field
RW, RH = 240, 104
y, x = np.mgrid[0:RH, 0:RW]
e = np.minimum.reduce([x, y, RW - 1 - x, RH - 1 - y])
rug = np.zeros((RH, RW), int)
rug[e < 2] = np.where(((np.where(np.minimum(y, RH - 1 - y) <= np.minimum(x, RW - 1 - x), x, y)) // 2) % 2 == 0, 2, 3)[e < 2]
rug[e == 2] = 1
band = (e > 2) & (e <= 12)
t = np.where(np.minimum(y, RH - 1 - y) <= np.minimum(x, RW - 1 - x), x, y).astype(float)
dd = (e - 3).astype(float)
u = (t % 12) - 6
bb = np.ones_like(rug)
vine = abs(dd - (4.5 + 2.6 * np.sin(2 * np.pi * t / 12))) < 0.8
bb[vine] = 3
bb[star8(u, dd - 4.5, 2.8)] = 2
bb[star8(u, dd - 4.5, 1.1)] = 4
bb[(dd == 0) | (dd == 9)] = 2
rug[band] = bb[band]
rug[e == 13] = 1
fld = e > 13
p = 7
lat = ((x + y) % p == 0) | ((x - y) % p == 0)
f = np.zeros_like(rug); f[lat] = 1
nx = (x % p) - p / 2; ny = (y % p) - p / 2
fl = star8(nx, ny, 1.4)
f[fl & ((x // p + y // p) % 2 == 0)] = 2; f[fl & ((x // p + y // p) % 2 == 1)] = 3
rug[fld] = f[fld]
lm = down(m, 196)
lh, lw = lm.shape
oy, ox = (RH - lh) // 2, (RW - lw) // 2
d = ndimage.distance_transform_edt(lm)
halo = ndimage.binary_dilation(lm, iterations=2) & ~lm
sub = rug[oy:oy + lh, ox:ox + lw]
sub[halo] = 0
sub[lm] = 4
sub[lm & (d <= 1.0)] = 2
rug[oy:oy + lh, ox:ox + lw] = sub
Image.fromarray(riso(rug, 10, 0.07)).save(os.path.join(OUT, 'rug-riso.png'))

# 4) flat riso stamp (2D): letters woven, black outline, pink misregistration, on red
km3, idx3 = woven_letters(415, 8)
k3 = 7
big_m = np.kron(km3, np.ones((k3, k3), bool))
pad = 80
canvas_h, canvas_w = big_m.shape[0] + 2 * pad, big_m.shape[1] + 2 * pad
M = np.zeros((canvas_h, canvas_w), bool); M[pad:-pad, pad:-pad] = big_m
outline = ndimage.binary_dilation(M, iterations=18)
pinkshadow = np.roll(np.roll(outline, 22, 0), 22, 1)
img = np.zeros((canvas_h, canvas_w, 3)); img[:] = hexc('#E2261C')
n = rng.random((canvas_h, canvas_w))
img[pinkshadow & (n > 0.08)] = hexc('#FF4FA8')
img[outline] = hexc('#0B0B0B')
let = np.zeros((canvas_h, canvas_w, 3), np.uint8); let[pad:-pad, pad:-pad] = riso(idx3, k3)
img[M] = let[M]
img += rng.normal(0, 7, img.shape)
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'stamp-riso.png'))
print('done')
