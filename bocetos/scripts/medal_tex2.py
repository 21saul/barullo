"""Patrones de grabado nuevos para la medalla (llamas, rayos, contorno, rombos, mandala, granulado).
Mismo encuadre que medal_tex.py (lee frame.json). Además de lines/fill/col escribe {pat}-idx.png
(0/127/255 = tono 1/2/3) para el esmalte en paleta de estilos.json.
  python medal_tex2.py <tex/medal>"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

OUT = sys.argv[1]
fr = json.load(open(os.path.join(OUT, 'frame.json')))
cx, cy, hs = fr['cx'], fr['cy'], fr['hs']
N = 2048; k = N / (2 * hs)
def tr(p): return [((x - cx + hs) * k, (y - cy + hs) * k) for x, y in p]
im = Image.new('L', (N, N), 0); dr = ImageDraw.Draw(im)
dr.polygon(tr(fr['outer']), fill=255); dr.polygon(tr(fr['hole']), fill=0)
m = np.asarray(im.filter(ImageFilter.GaussianBlur(2))) > 127
d = ndimage.distance_transform_edt(m)
Y, X = np.mgrid[0:N, 0:N].astype(float)
dx, dy = X - N / 2, Y - N / 2
r = np.hypot(dx, dy); th = np.arctan2(dy, dx)
LW = 4.5
band = lambda v, w=LW: np.abs(v) < w
PAL = np.array([[226, 38, 28], [246, 164, 60], [255, 79, 168]], float)

def border():
    L = band(d - 22) | band(d - 64)
    beads = (np.abs(d - 43) < 11) & (np.sin(X / 11) * np.sin(Y / 11) > 0.3)
    return L | beads, d > 84

def save(name, lines, fill, idx):
    bl, inner = border()
    L = (bl | (lines & inner)) & m
    F = fill & inner & m & ~L
    def w(a, fn): Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)).save(os.path.join(OUT, fn))
    w(L, f'{name}-lines.png'); w(F, f'{name}-fill.png')
    idx = idx.astype(int) % 3
    Image.fromarray(PAL[idx].astype(np.uint8)).save(os.path.join(OUT, f'{name}-col.png'))
    Image.fromarray((idx * 127.5).astype(np.uint8)).save(os.path.join(OUT, f'{name}-idx.png'))
    print(name)

# radio del agujero central, en píxeles de la textura
hole_r = np.sqrt(((~m) & (r < N * 0.3)).sum() / np.pi)

def llamas(n=12):
    r0, r1 = hole_r + 40, 960
    t = (r - r0) / (r1 - r0)
    u = (th * n / (2 * np.pi)) % 1 - 0.5
    sec = np.floor(th * n / (2 * np.pi) + 0.5) % n
    uu = u - 0.16 * np.sin(np.clip(t, 0, 1) * 3.4)
    w = 0.55 * np.clip(1 - t, 0, 1) ** 0.75 * (1 + 0.12 * np.sin(t * 11))
    inside = (np.abs(uu) < w) & (t > 0) & (t < 1)
    core = (np.abs(uu) < w * 0.45) & (t > 0.02) & (t < 0.75)
    arc = 2 * np.pi * r / n
    lines = (band((np.abs(uu) - w) * arc) & (t > 0) & (t < 1)) | (band((np.abs(uu) - w * 0.45) * arc, 3) & (t > 0.02) & (t < 0.75))
    lines |= band(r - r0)
    idx = np.where(core, 1, np.where(sec % 2 == 0, 0, 2))
    return lines, inside, idx

def rayos(n=16):
    r0 = hole_r + 40
    s = np.floor((th + np.pi) / (2 * np.pi) * n)
    edge = np.abs(((th + np.pi) / (2 * np.pi) * n + 0.5) % 1 - 0.5) * 2 * np.pi * r / n
    lines = (band(edge) & (r > r0)) | band(r - r0) | band(r - 700, 3)
    fine = (np.sin(th * 144) > 0.9) & (s % 2 == 1) & (r > r0)
    lines |= fine
    fill = (s % 2 == 0) & (r > r0)
    idx = np.where(r < 700, (s // 2) % 2, 2)
    return lines, fill, idx

def contorno(step=40):
    q = np.floor(d / step)
    lines = band(d % step - step / 2, 3.5) & (d > 84)
    fill = (q % 2 == 1)
    idx = (q // 2) % 3
    return lines, fill, idx

def rombos(p=150):
    u = (X + Y) / p; v = (X - Y) / p
    fu, fv = u % 1, v % 1
    e = np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv)) * p / 1.414
    lines = band(e, 3.5)
    c = (np.floor(u) + np.floor(v)) % 3
    return lines, c != 2, c

def mandala():
    a, b, c_, e_ = 560, 600, 770, 910
    lines = band(r - a) | band(r - b) | band(r - c_) | band(r - e_)
    # anillo 1: pétalos
    R1 = a + (b - a) * (0.25 + 0.7 * np.abs(np.cos(16 * th)))
    p1 = (r > a) & (r < R1); lines |= band(r - R1) & (r > a) & (r < b)
    # anillo 2: círculos
    n2 = 24; ang = np.round(th * n2 / (2 * np.pi)) * 2 * np.pi / n2; rm = (b + c_) / 2
    rr = np.hypot(dx - rm * np.cos(ang), dy - rm * np.sin(ang)); cr = (c_ - b) * 0.36
    p2 = rr < cr; lines |= band(rr - cr) & (r > b) & (r < c_)
    # anillo 3: dientes
    n3 = 40; f3 = np.abs(((th + np.pi) / (2 * np.pi) * n3) % 1 - 0.5) * 2
    R3 = c_ + (e_ - c_) * (1 - f3)
    p3 = (r > c_) & (r < R3); lines |= band(r - R3, 3.5) & (r > c_) & (r < e_)
    # exterior: aguas finas
    lines |= (r > e_) & (np.sin(th * 120) > 0.88)
    fill = p1 | p2 | p3
    idx = np.where(p1, 0, np.where(p2, 1, 2))
    return lines, fill, idx

def granulado(p=72, rad=25):
    row = np.floor(Y / (p * 0.866))
    gx = ((X + (row % 2) * p / 2) % p) - p / 2; gy = (Y % (p * 0.866)) - p * 0.433
    rr = np.hypot(gx, gy)
    lines = band(rr - rad, 3)
    fill = rr < rad - 4
    idx = np.floor(r / 110) % 3
    return lines, fill, idx

for name, fn in [('llamas', llamas), ('rayos', rayos), ('contorno', contorno), ('rombos', rombos), ('mandala', mandala), ('granulado', granulado)]:
    save(name, *fn())
