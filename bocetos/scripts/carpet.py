"""Procedural Persian carpet on a knot grid -> riso / cyborg-LED / ember textures."""
import sys, os
import numpy as np
from PIL import Image, ImageFilter

OUT = sys.argv[1]
SRC = sys.argv[2]  # repo root
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

# index: 0 ground, 1 deep, 2 orange, 3 pink, 4 bone
def star8(x, y, s):
    return (np.maximum(abs(x), abs(y)) <= s) | ((abs(x) + abs(y)) <= s * 1.41)

def border_band(t, d, depth=12, unit=14):
    """t along the band, d depth 0..depth-1"""
    idx = np.full(t.shape, 1)
    u = (t % unit) - unit / 2
    mid = (depth - 1) / 2
    vine = abs(d - (mid + 3.2 * np.sin(2 * np.pi * t / unit))) < 0.8
    idx[vine] = 3
    st = star8(u, d - mid, 3.2)
    idx[st] = 2
    idx[star8(u, d - mid, 1.4)] = 3
    idx[(abs(u) < 0.6) & (abs(d - mid) < 0.6)] = 4
    # tiny bone dots between stars
    idx[(abs(abs(u) - unit / 2) < 0.6) & (abs(d - mid) < 0.6)] = 4
    idx[(d == 0) | (d == depth - 1)] = 2
    return idx

def guard(t):
    return np.where((t // 2) % 2 == 0, 2, 3)

def carpet(W=120, H=168):
    y, x = np.mgrid[0:H, 0:W]
    idx = np.zeros((H, W), int)
    # distance to edge
    e = np.minimum.reduce([x, y, W - 1 - x, H - 1 - y])
    G, B = 2, 12
    # guards
    g1 = e < G
    idx[g1] = guard(np.where((y < G) | (y >= H - G), x, y))[g1]
    idx[e == G] = 1
    band = (e > G) & (e <= G + B)
    d = e - G - 1
    horiz = np.minimum(y, H - 1 - y) <= np.minimum(x, W - 1 - x)
    t = np.where(horiz, x, y)
    bb = border_band(t, d, B)
    idx[band] = bb[band]
    idx[e == G + B + 1] = 1
    g2 = (e > G + B + 1) & (e <= G + B + 3)
    idx[g2] = guard(t + 1)[g2]
    field = e > G + B + 3
    cx, cy = (W - 1) / 2, (H - 1) / 2
    dx, dy = x - cx, y - cy
    # field lattice (herati-ish)
    lat = ((np.round(dx + dy) % 10 == 0) | (np.round(dx - dy) % 10 == 0))
    f = np.zeros_like(idx)
    f[lat] = 1
    # flowers at lattice nodes
    nx = ((dx + 0.5) % 10) - 5
    ny = ((dy + 0.5) % 10) - 5
    node = (abs(nx) + abs(ny) < 2.2)
    alt = ((np.floor((dx + 0.5) / 10) + np.floor((dy + 0.5) / 10)) % 2 == 0)
    f[node & alt] = 2
    f[node & ~alt] = 3
    f[(abs(nx) < 0.6) & (abs(ny) < 0.6)] = 4
    # medallion
    r = np.hypot(dx, dy * 0.82)
    th = np.arctan2(dy, dx)
    R = 24 + 3.5 * np.cos(8 * th) + 1.5 * np.cos(16 * th)
    med = r < R
    f[med] = 1
    f[med & (r > R - 2.2)] = 2
    f[med & (r > R - 3.4) & (r <= R - 2.2)] = 3
    inner = r < R - 6
    f[inner] = 0
    ring = (abs(r - 12) < 0.8)
    f[ring & inner] = 3
    f[star8(dx, dy, 9)] = 2
    f[star8(dx, dy, 7)] = 1
    f[star8(dx, dy, 5)] = 3
    f[star8(dx, dy, 2.2)] = 4
    # petals on medallion ring
    pet = (abs(r - 17.5) < 2.4) & (np.cos(8 * th) > 0.55)
    f[pet] = 3
    # pendants on vertical axis
    for s in (-1, 1):
        py = dy - s * 33
        f[(abs(dx) + abs(py) * 1.2 < 5)] = 2
        f[(abs(dx) + abs(py) * 1.2 < 2.5)] = 3
        f[(abs(dx) < 0.6) & (abs(dy) > 24) & (abs(dy) < 30)] = 2
    # corner quarter medallions
    fx0, fy0 = G + B + 4, G + B + 4
    qx = np.minimum(x - fx0, W - 1 - fx0 - x)
    qy = np.minimum(y - fy0, H - 1 - fy0 - y)
    qr = np.hypot(qx, qy)
    qth = np.arctan2(qy, qx)
    QR = 14 + 2.5 * np.cos(8 * qth)
    q = qr < QR
    f[q] = 1
    f[q & (qr > QR - 2)] = 2
    f[q & (qr < 7)] = 3
    f[q & (qr < 3)] = 2
    idx[field] = f[field]
    return idx

def band_strip(L=480, B=12):
    t, d = np.mgrid[0:L, 0:B + 6].astype(float)
    t, d = t.T, d.T
    idx = np.ones(d.shape, int)
    gt = (d < 2) | (d >= B + 4)
    idx[gt] = guard(t.astype(int))[gt]
    inb = (d >= 3) & (d < B + 3)
    bb = border_band(t, d - 3, B)
    idx[inb] = bb[inb]
    return idx

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)

RISO = [hexc(c) for c in ('#E2261C', '#B5160F', '#F6A43C', '#FF4FA8', '#FFE9D2')]
LED = [hexc(c) for c in ('#15181E', '#3A1216', '#F6A43C', '#FF4FA8', '#FFE9D2')]
EMBER = [hexc(c) for c in ('#140D10', '#1E1014', '#3B1A1E', '#4A1A2C', '#5A2A24')]

def render_riso(idx, k=7):
    big = np.kron(idx, np.ones((k, k), int))
    pal = np.array(RISO)
    img = pal[big]
    H, W = big.shape
    # risograph speckle: knock motif pixels back to ground/deep randomly
    n = rng.random((H, W))
    motif = big >= 2
    img[motif & (n < 0.10)] = RISO[0]
    img[(big == 0) & (n < 0.06)] = RISO[1]
    img[(big == 0) & (n > 0.985)] = RISO[3]
    # misregistered pink layer
    pink = (big == 3)
    sh = np.roll(np.roll(pink, 2, 0), 2, 1) & ~pink & (big <= 1)
    img[sh & (n < 0.5)] = img[sh & (n < 0.5)] * 0.55 + RISO[3] * 0.45
    img += rng.normal(0, 9, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

def render_led(idx, k=8, dim=0.62, scan=None):
    H0, W0 = idx.shape
    pal = np.array(LED)
    col = pal[idx]
    # dim motifs, keep a scan band brighter
    yy = np.arange(H0)[:, None] * np.ones((1, W0))
    bright = np.full((H0, W0), dim)
    if scan is not None:
        bright = dim + (1 - dim) * np.exp(-((yy - scan) / 5.0) ** 2)
    bg = pal[0]
    col = bg + (col - bg) * bright[..., None]
    # glitch rows: shift a few knot rows sideways
    for row in rng.choice(H0, 6, replace=False):
        col[row] = np.roll(col[row], rng.integers(-6, 7), 0)
    # LED dots
    yk, xk = np.mgrid[0:k, 0:k]
    c = (k - 1) / 2
    dot = np.clip(1.25 - np.hypot(yk - c, xk - c) / (k * 0.42), 0, 1)
    big = np.kron(col, np.ones((k, k, 1)))
    m = np.tile(dot, (H0, W0))[..., None]
    img = big * m + np.array([9, 10, 13]) * (1 - m)
    # scanlines
    img[1::3] *= 0.86
    img += rng.normal(0, 3, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

def render_ember(idx, k=7):
    big = np.kron(idx, np.ones((k, k), int))
    img = np.array(EMBER)[big]
    img += rng.normal(0, 4, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

def save(im, name, q=82):
    im.save(os.path.join(OUT, name), quality=q, optimize=True)
    print(name, im.size, os.path.getsize(os.path.join(OUT, name)) // 1024, 'KB')

C = carpet()
save(render_riso(C), 'carpet-riso.jpg')
save(render_led(C, scan=60), 'carpet-led.jpg')
save(render_ember(C), 'carpet-ember.jpg')
S = band_strip()
save(render_riso(S, 6), 'band-riso.jpg')
save(render_led(S, 6, dim=0.8), 'band-led.jpg')

# --- cyborg portrait gradient-mapped onto the designer palette, over LED carpet
por = Image.open(os.path.join(SRC, 'public/media/brand/hero-character-cyber-3x2-poster.jpg')).convert('RGB')
por = por.resize((960, 960), Image.LANCZOS)
a = np.asarray(por, float) / 255
lum = a @ np.array([0.299, 0.587, 0.114])
stops = [(0, '#0B0D11'), (0.28, '#5A0E0C'), (0.5, '#E2261C'), (0.72, '#FF4FA8'), (0.88, '#F6A43C'), (1, '#FFF4E6')]
xs = [s for s, _ in stops]; cs = np.array([hexc(c) for _, c in stops])
gm = np.stack([np.interp(lum, xs, cs[:, i]) for i in range(3)], -1)
# blend a bit of original chroma so chrome keeps its sheen
gm = gm * 0.88 + a * 255 * 0.12
bgc = np.asarray(render_led(carpet(120, 120), k=8, dim=0.5, scan=200).resize((960, 960)), float)
mask = np.clip((lum - 0.04) / 0.10, 0, 1)
mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), float)[..., None] / 255
comp = gm * mask + bgc * (1 - mask)
save(Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8)), 'cyborg-carpet.jpg', 84)
save(Image.fromarray(np.clip(gm, 0, 255).astype(np.uint8)), 'cyborg-riso.jpg', 84)

# --- kufi wordmark from the designer's sheet -> white + red on transparent
wm = Image.open(sys.argv[3]).convert('RGB')
w = np.asarray(wm, float)
white = (w.min(-1) > 200)
from collections import deque
H, W = white.shape
outside = np.zeros_like(white)
dq = deque([(0, 0), (0, W - 1), (H - 1, 0), (H - 1, W - 1)])
while dq:
    yy, xx = dq.popleft()
    if 0 <= yy < H and 0 <= xx < W and white[yy, xx] and not outside[yy, xx]:
        outside[yy, xx] = True
        dq.extend([(yy + 1, xx), (yy - 1, xx), (yy, xx + 1), (yy, xx - 1)])
letters = white & ~outside
alpha = np.asarray(Image.fromarray((letters * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
ys, xs_ = np.where(letters)
box = (xs_.min() - 2, ys.min() - 2, xs_.max() + 3, ys.max() + 3)
for name, col in (('wordmark-white.png', (255, 244, 230)), ('wordmark-red.png', (226, 38, 28))):
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., :3] = col; rgba[..., 3] = alpha
    im = Image.fromarray(rgba).crop(box)
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    im.save(os.path.join(OUT, name), optimize=True); print(name, im.size)

# medal: black -> transparent
md = Image.open(os.path.join(SRC, 'bocetos/disenos/logo/medalla-puas/A.png')).convert('RGB').resize((600, 600), Image.LANCZOS)
m = np.asarray(md, float)
al = np.clip((m.max(-1) - 14) / 30, 0, 1)
rgba = np.dstack([m, al * 255]).astype(np.uint8)
Image.fromarray(rgba).save(os.path.join(OUT, 'medal.png'), optimize=True); print('medal.png')
