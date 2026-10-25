"""High-res engraving masks for the star 'o' as a medal, plus coin and ribbon textures."""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

WJ, OUT, FONT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
data = json.load(open(WJ))
polys = data['polys']

def info(p):
    xs = [q[0] for q in p]; ys = [q[1] for q in p]
    a = 0.5 * abs(sum(p[i][0] * p[i + 1][1] - p[i + 1][0] * p[i][1] for i in range(len(p) - 1)))
    return sum(xs) / len(xs), a, min(xs), max(xs), min(ys), max(ys)

right = [p for p in polys if info(p)[0] > data['w'] * 0.85]
outer = max(right, key=lambda p: info(p)[1]); hole = min(right, key=lambda p: info(p)[1])
_, _, x0, x1, y0, y1 = info(outer)
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
hs = max(x1 - x0, y1 - y0) / 2 * 1.06
N = 2048
k = N / (2 * hs)
def tr(p): return [((x - cx + hs) * k, (y - cy + hs) * k) for x, y in p]
im = Image.new('L', (N, N), 0); dr = ImageDraw.Draw(im)
dr.polygon(tr(outer), fill=255); dr.polygon(tr(hole), fill=0)
m = np.asarray(im.filter(ImageFilter.GaussianBlur(2))) > 127
d = ndimage.distance_transform_edt(m)
Y, X = np.mgrid[0:N, 0:N].astype(float)
dx, dy = X - N / 2, Y - N / 2
r = np.hypot(dx, dy); th = np.arctan2(dy, dx)
LW = 4.5
band = lambda v, w=LW: np.abs(v) < w
json.dump({'cx': cx, 'cy': cy, 'hs': hs, 'outer': outer, 'hole': hole}, open(os.path.join(OUT, 'frame.json'), 'w'))

PAL = np.array([[226, 38, 28], [246, 164, 60], [255, 79, 168]], float)

def border():
    L = band(d - 22) | band(d - 64)
    beads = (np.abs(d - 43) < 11) & (np.sin(X / 11) * np.sin(Y / 11) > 0.3)
    return L | beads, d > 84

def petals():
    R = 430 + 250 * np.abs(np.cos(8 * th)) ** 0.8
    lines = band(r - R) | band(r - 400) | (band(np.sin(16 * th), 0.03) & (r > 400) & (r < R))
    fill = (r > 410) & (r < R - 10)
    idx = (np.floor((th + np.pi) / (2 * np.pi) * 16 + 0.5) % 3)
    for kk in range(8):
        a = kk * np.pi / 4
        tx, ty = 840 * np.cos(a), 840 * np.sin(a)
        rr = np.hypot(dx - tx, dy - ty); tt = np.arctan2(dy - ty, dx - tx)
        RR = 70 * (0.6 + 0.4 * np.abs(np.cos(4 * tt)))
        lines |= band(rr - RR) | (rr < 10)
        fill |= (rr < RR - 8) & (rr > 18)
    return lines, fill, idx

def girih(p=170):
    gx = (X % p) - p / 2; gy = (Y % p) - p / 2
    g = np.minimum(np.maximum(abs(gx), abs(gy)), (abs(gx) + abs(gy)) / 1.414); s = p * 0.36
    o = np.maximum(np.maximum(abs(gx), abs(gy)), (abs(gx) + abs(gy)) / 1.414)
    lines = band(g - s) | band(o - s * 0.55) | ((band(gx, 3.5) | band(gy, 3.5)) & (g > s))
    fill = (g < s - 8) & (o > s * 0.55 + 8)
    return lines, fill, (np.floor(X / p) + np.floor(Y / p)) % 3

def sunburst():
    lines = (np.sin(th * 72 + 0.002 * r) > 0.82) | (np.sin(r * 2 * np.pi / 90) > 0.94)
    return lines, np.zeros_like(lines), np.zeros_like(X)

def save(name, lines, fill, idx, raised_border=False):
    bl, inner = border()
    L = (bl | (lines & inner)) & m
    F = fill & inner & m & ~L
    def w(a, fn): Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)).save(os.path.join(OUT, fn))
    w(L, f'{name}-lines.png'); w(F, f'{name}-fill.png')
    Image.fromarray(PAL[idx.astype(int) % 3].astype(np.uint8)).save(os.path.join(OUT, f'{name}-col.png'))
    print(name)

save('rosa', *petals())
save('girih', *girih())
save('sol', *sunburst())


# wordmark patterns, scaled up for the medal
F = 3.4
def m_rosetas(p=58 * F):
    u = ((X + Y) % p) - p / 2; v = ((X - Y) % p) - p / 2
    lines = band(u, 3.5) | band(v, 3.5)
    cx_ = (X % p) - p / 2; cy_ = (Y % p) - p / 2
    rr = np.hypot(cx_, cy_); tt = np.arctan2(cy_, cx_)
    R = p * 0.3 * (0.62 + 0.38 * np.abs(np.cos(4 * tt)))
    lines = (lines & ~(rr < R)) | band(rr - R) | (rr < 9)
    fill = (rr < R - 8) & (rr > 16)
    return lines, fill, (np.floor(X / p) + np.floor(Y / p)) % 2

def m_arabesco(p=62 * F, lam=96 * F):
    row = np.floor(Y / p)
    v = (Y % p) - p / 2 - 10 * F * np.sin(2 * np.pi * X / lam + row * 1.3)
    lines = band(v)
    kk = np.floor(X / (lam / 2)); lx = (X % (lam / 2)) - lam / 4
    side = np.where(kk % 2 == 0, 1, -1); ly = v - side * 11 * F
    a = np.radians(35) * side
    rx = lx * np.cos(a) + ly * np.sin(a); ry = -lx * np.sin(a) + ly * np.cos(a)
    e = (rx / (15 * F)) ** 2 + (ry / (6.5 * F)) ** 2
    lines |= band(e - 1, 0.07)
    return lines, e < 0.75, kk % 3

def m_escamas(p=40 * F):
    row = np.floor(Y / (p / 2))
    cx_ = ((X + (row % 2) * p / 2) % p) - p / 2; cy_ = (Y % (p / 2))
    rr = np.hypot(cx_, cy_)
    lines = (band(rr - p / 2) & (cy_ >= 0)) | band(rr - p / 2 + 6 * F, 3)
    return lines, rr < p / 2 - 8 * F, row % 3

save('rosetas', *m_rosetas())
save('arabesco', *m_arabesco())
save('escamas', *m_escamas())

# coin face (disc of radius 1 mapped to the full texture)
C = 2048
Yc, Xc = np.mgrid[0:C, 0:C].astype(float)
rc = np.hypot(Xc - C / 2, Yc - C / 2) / (C / 2); tc = np.arctan2(Yc - C / 2, Xc - C / 2)
L = band(rc - 0.975, 0.005) | band(rc - 0.905, 0.004) | band(rc - 0.66, 0.004) | band(rc - 0.635, 0.003)
L |= (np.abs(rc - 0.94) < 0.014) & (np.sin(tc * 90) > 0.2)
L |= (rc < 0.63) & (np.sin(tc * 96) > 0.86)
txt = Image.new('L', (C, C), 0); td = ImageDraw.Draw(txt)
font = ImageFont.truetype(FONT, 120)
s = 'BARULLO CLVB  ✦  VIGO  ✦  BARULLO CLVB  ✦  VIGO  ✦  '
s = s.replace('✦', '*')
n = len(s); rad = C / 2 * 0.775
for i, ch in enumerate(s):
    a = -np.pi / 2 + 2 * np.pi * i / n
    g = Image.new('L', (200, 200), 0); gd = ImageDraw.Draw(g)
    if ch == '*':
        pts = []
        for j in range(16):
            rr = 34 if j % 2 == 0 else 14
            aa = j * np.pi / 8
            pts.append((100 + rr * np.cos(aa), 100 + rr * np.sin(aa)))
        gd.polygon(pts, fill=255)
    else:
        gd.text((100, 100), ch, font=font, fill=255, anchor='mm')
    g = g.rotate(-np.degrees(a + np.pi / 2), resample=Image.BICUBIC)
    px, py = C / 2 + rad * np.cos(a), C / 2 + rad * np.sin(a)
    txt.paste(255, (int(px - 100), int(py - 100)), g)
T = np.asarray(txt) > 127
Lc = (L | T) & (rc < 1)
Image.fromarray((Lc * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)).save(os.path.join(OUT, 'coin-lines.png'))
print('coin')

# ribbon stripes (u across, v along)
rw = np.zeros((1024, 512, 3))
stripes = [(0.00, '#0B0B0B'), (0.08, '#F6A43C'), (0.12, '#0B0B0B'), (0.15, '#E2261C'), (0.42, '#FF4FA8'), (0.47, '#FFF1E2'), (0.53, '#FF4FA8'), (0.58, '#E2261C'), (0.85, '#0B0B0B'), (0.88, '#F6A43C'), (0.92, '#0B0B0B')]
u = np.linspace(0, 1, 512)
for i, (s0, c) in enumerate(stripes):
    s1 = stripes[i + 1][0] if i + 1 < len(stripes) else 1.01
    col = [int(c[j:j + 2], 16) for j in (1, 3, 5)]
    rw[:, (u >= s0) & (u < s1)] = col
rw *= (0.9 + 0.1 * np.sin(np.arange(1024)[:, None, None] * 1.7))  # rib weave
Image.fromarray(np.clip(rw, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'ribbon.png'))
print('ribbon')
