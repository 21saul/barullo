"""Hand-knotted Persian rug (Heriz layout) with the Barullo kufi wordmark as the medallion.

Builds the design on a knot grid, then renders wool textures for Blender:
albedo, height (pile + knot domes + fibres), normal, roughness and a pile mask.
Run: python3 rug_tex.py <wordmark.json|none> <out_dir> [px_per_knot]   (none = medallón sin logo, cartel 02)
"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

WM, OUT = sys.argv[1], sys.argv[2]
K = int(sys.argv[3]) if len(sys.argv) > 3 else 8
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)

# palette: designer riso + wool-ish neutrals
RED, DRED, ORA, PINK, BONE, BLACK, KILIM, DORA = range(8)
PAL = np.array([hexc(c) for c in ('#E2261C', '#9E1510', '#F6A43C', '#FF4FA8', '#F2EBDD', '#141010', '#E9DFCC', '#D9741F')])

# knot grid: W columns along the length (warp), H rows across
W, H = 420, 200
KIL = 10                      # flat-woven kilim rows at each short end (no pile)
y, x = np.mgrid[0:H, 0:W]
rug = np.full((H, W), RED, int)

# distance to the knotted area's edge (kilim ends excluded)
xi = x - KIL
WI = W - 2 * KIL
e = np.minimum.reduce([xi, y, WI - 1 - xi, H - 1 - y])
inside = (xi >= 0) & (xi < WI)

def star8(dx, dy, s):
    return (np.maximum(abs(dx), abs(dy)) <= s) | ((abs(dx) + abs(dy)) <= s * 1.42)

def along(e0):
    """Coordinate running along the band at depth e0 and the band's local depth."""
    top = (y <= x - KIL) & (y <= WI - 1 - (x - KIL)) & (y < H / 2)
    bot = (H - 1 - y <= x - KIL) & (H - 1 - y <= WI - 1 - (x - KIL)) & ~top
    t = np.where(top | bot, xi, y).astype(float)
    return t

# ---------- borders (from outside in) ----------
T = along(0)
# 0: binding line
rug[inside & (e == 0)] = BLACK
# 1-4: outer guard, reciprocal teeth (orange into red)
d = e - 1
g = inside & (e >= 1) & (e <= 4)
tooth = (abs(((T + 3) % 6) - 3) + d) <= 3.2
rug[g] = np.where(tooth, ORA, DRED)[g]
rug[inside & (e == 5)] = BLACK
rug[inside & (e == 6)] = BONE
rug[inside & (e == 7)] = BLACK

# 8-29: main border, black ground, rosettes + palmettes linked by an angular vine
B0, B1 = 8, 29
mb = inside & (e >= B0) & (e <= B1)
bd = (e - B0).astype(float) - (B1 - B0) / 2           # -10.5..10.5 across band
band = np.full((H, W), BLACK, int)
# lay motifs along each side with spacing that lands rosettes on the corners
def side_phase(length, P=46):
    n = max(1, round(length / P)); return length / n
cx_len = WI - 2 * B0 - (B1 - B0)
cy_len = H - 2 * B0 - (B1 - B0)
Px, Py = side_phase(cx_len), side_phase(cy_len)
horiz = (np.minimum(y, H - 1 - y) <= np.minimum(xi, WI - 1 - xi))
off = B0 + (B1 - B0) / 2
u = np.where(horiz, xi - off, y - off).astype(float)
P = np.where(horiz, Px, Py)
k = np.round(u / (P / 2))
uu = u - k * (P / 2)                                  # local coord to nearest half-step
ros = (k % 2 == 0)
# vine: angular zig-zag between motifs
vine_y = 6.0 * np.sign(np.sin(np.pi * u / (P / 2) + 0.0001)) * np.minimum(1, abs(np.sin(np.pi * u / (P / 2))) * 3)
vine = abs(bd - vine_y * 0.0 - 5.5 * np.sin(2 * np.pi * u / P)) < 0.9
band[vine] = PINK
leaf = (abs(bd - 5.5 * np.sin(2 * np.pi * u / P) - 2.2 * np.sign(np.cos(2 * np.pi * u / P))) < 1.3) & (abs((u % (P / 4)) - P / 8) < 1.6)
band[leaf & ~vine] = DORA
# rosette: stepped 8-point star, orange petals, pink ring, bone eye, red pupil
r = np.hypot(uu, bd); th = np.arctan2(bd, uu)
rs = ros & star8(uu, bd, 8.2)
band[rs] = ORA
band[rs & star8(uu, bd, 7.0)] = RED
band[ros & (r <= 5.2)] = PINK
band[ros & (r <= 5.2) & (abs(np.cos(4 * th)) > 0.8) & (r > 3.2)] = DRED
band[ros & star8(uu, bd, 2.7)] = BONE
band[ros & star8(uu, bd, 1.0)] = RED
# palmette (Heriz "crab"): stepped lozenge with hooked arms
pal = ~ros
lz = (abs(uu) / 8.5 + abs(bd) / 8.0) <= 1
arms = (abs(abs(uu) - abs(bd)) < 0.9) & (np.maximum(abs(uu), abs(bd)) < 9.5) & (np.maximum(abs(uu), abs(bd)) > 5)
band[pal & arms] = DORA
band[pal & lz] = PINK
band[pal & ((abs(uu) / 7.0 + abs(bd) / 6.5) <= 1)] = BLACK
band[pal & ((abs(uu) / 5.6 + abs(bd) / 5.2) <= 1)] = BONE
band[pal & ((abs(uu) / 3.0 + abs(bd) / 2.8) <= 1)] = ORA
band[pal & (abs(uu) <= 0.5) & (abs(bd) <= 0.5)] = RED
rug[mb] = band[mb]
# corner rosettes overwrite (clean mitre)
for cx in (KIL + off, KIL + WI - 1 - off):
    for cy in (off, H - 1 - off):
        dx, dy = x - cx, y - cy
        cr = star8(dx, dy, 9.6) & mb
        rug[cr] = ORA
        rug[cr & star8(dx, dy, 8.4)] = RED
        rr = np.hypot(dx, dy)
        rug[mb & (rr <= 6.2)] = PINK
        rug[mb & star8(dx, dy, 3.4)] = BONE
        rug[mb & star8(dx, dy, 1.4)] = RED

rug[inside & (e == 30)] = BLACK
rug[inside & (e == 31)] = ORA
# 32-36: inner guard, running small flowers (pink/bone) on dark red
gi = inside & (e >= 32) & (e <= 36)
dg = (e - 34).astype(float)
Ti = along(0) % 8 - 4
fl = (abs(Ti) + abs(dg)) <= 2
inner = np.full((H, W), DRED, int)
inner[fl] = PINK
inner[(abs(Ti) + abs(dg)) <= 0.5] = BONE
inner[(abs(abs(Ti) - 4) <= 0.5) & (abs(dg) <= 0.5)] = ORA
rug[gi] = inner[gi]
rug[inside & (e == 37)] = BLACK
F0 = 38                                          # field starts

# ---------- field ----------
fld = inside & (e >= F0)
fx0, fx1, fy0, fy1 = KIL + F0, KIL + WI - 1 - F0, F0, H - 1 - F0
fcx, fcy = (fx0 + fx1) / 2, (fy0 + fy1) / 2
# tonal herati lattice (dark red) with small accents
px, py = 16, 12
lx = ((x - fcx) % px) - px / 2; ly = ((y - fcy) % py) - py / 2
cell = ((np.floor((x - fcx) / px) + np.floor((y - fcy) / py)) % 2 == 0)
lattice = abs(abs(lx) / (px / 2) + abs(ly) / (py / 2) - 1) < 0.11
herati = np.full((H, W), RED, int)
herati[lattice] = DRED
herati[star8(lx, ly, 1.6)] = DRED
herati[star8(lx, ly, 0.6) & cell] = ORA
herati[star8(lx, ly, 0.6) & ~cell] = PINK
# lancet leaves on lattice midpoints
mx = ((x - fcx - px / 4) % (px / 2)) - px / 4
my = ((y - fcy - py / 4) % (py / 2)) - py / 4
herati[(abs(mx) + abs(my) * 1.6 <= 1.6)] = DRED
rug[fld] = herati[fld]

# corner spandrels: stepped quarter medallions on black
def stepped(dx, dy, a, b, step=3):
    return (np.floor(abs(dx) / step) * step / a + np.floor(abs(dy) / step) * step / b) <= 1
SA, SB = 74, 40
for cx in (fx0, fx1):
    for cy in (fy0, fy1):
        dx, dy = x - cx, y - cy
        sp = fld & stepped(dx, dy, SA, SB)
        rug[fld & stepped(dx, dy, SA + 3, SB + 3)] = ORA
        rug[fld & stepped(dx, dy, SA + 1.5, SB + 1.5)] = PINK
        rug[sp] = BLACK
        # inner motifs: quarter rosette at the corner + scattered blossoms
        rr = np.hypot(dx, dy)
        rug[sp & star8(dx, dy, 16)] = ORA
        rug[sp & star8(dx, dy, 16) & ~star8(dx, dy, 14.8)] = DORA
        rug[sp & (rr <= 11)] = PINK
        rug[sp & star8(dx, dy, 6)] = BONE
        rug[sp & star8(dx, dy, 2.5)] = RED
        for (ox, oy) in ((30, 6), (46, 10), (12, 24), (26, 22), (58, 4)):
            bx, by = dx - np.sign(fcx - cx) * ox, dy - np.sign(fcy - cy) * oy
            bl = sp & star8(bx, by, 2.4) & stepped(dx, dy, SA - 6, SB - 6)
            rug[bl] = ORA if ox % 4 == 2 else PINK
            rug[sp & star8(bx, by, 0.6) & stepped(dx, dy, SA - 6, SB - 6)] = BONE
        # vine tendrils inside spandrel
        tend = sp & (abs(np.hypot(dx * 0.62, dy) - 25) < 0.7) & ~star8(dx, dy, 16)
        rug[tend] = DORA

# side pendants: small 8-point stars on the long axis, echoing the wordmark's "o"
for cx in (fx0 + 14, fx1 - 14):
    dx, dy = x - cx, y - fcy
    rug[fld & star8(dx, dy, 7.4)] = BLACK
    rug[fld & star8(dx, dy, 6.2)] = ORA
    rug[fld & (np.hypot(dx, dy) <= 3.8)] = PINK
    rug[fld & star8(dx, dy, 1.6)] = BONE

# ---------- medallion ----------
if WM == 'none':
    # cartel 02: el logo 3D flota encima, así que el centro lleva un medallón de lóbulos escalonados
    dx, dy = x - fcx, y - fcy
    rug[fld & stepped(dx, dy, 112, 52)] = ORA
    rug[fld & stepped(dx, dy, 109, 49.5)] = PINK
    med = fld & stepped(dx, dy, 106, 47)
    rug[med] = BLACK
    # herati negro: rombos naranja y rosa
    lx2 = ((dx) % 12) - 6; ly2 = ((dy) % 12) - 6
    rug[med & star8(lx2, ly2, 1.2) & ((np.floor(dx / 12) + np.floor(dy / 12)) % 2 == 0)] = DORA
    rug[med & star8(lx2, ly2, 1.2) & ((np.floor(dx / 12) + np.floor(dy / 12)) % 2 == 1)] = PINK
    rug[med & (abs(np.hypot(dx * 0.46, dy) - 30) < 0.8)] = DORA
    rug[med & star8(dx * 0.8, dy, 27)] = RED
    rug[med & star8(dx * 0.8, dy, 25)] = ORA
    rug[med & star8(dx * 0.8, dy, 22)] = BLACK
    rug[med & star8(dx * 0.8, dy, 19.5)] = PINK
    rug[med & star8(dx * 0.8, dy, 15)] = RED
    rug[med & star8(dx, dy, 9)] = BONE
    rug[med & star8(dx, dy, 6)] = RED
    rug[med & star8(dx, dy, 2.2)] = ORA
    for sx in (-1, 1):  # remates en punta a los lados
        ex = dx - sx * 92
        rug[med & star8(ex, dy, 6)] = ORA
        rug[med & star8(ex, dy, 3.5)] = PINK
        rug[med & star8(ex, dy, 1.2)] = BONE
else:
    data = json.load(open(WM))
    IW, IH = data['w'], data['h']
    LW = 288
    LH = int(round(LW * IH / IW))
    SS = 8
    im = Image.new('L', (LW * SS, LH * SS), 0)
    dr = ImageDraw.Draw(im)
    acc = np.zeros((LH * SS, LW * SS), bool)
    for poly in data['polys']:
        tmp = Image.new('1', im.size, 0)
        ImageDraw.Draw(tmp).polygon([(px_ * LW * SS / IW, py_ * LH * SS / IH) for px_, py_ in poly], fill=1)
        acc ^= np.asarray(tmp, bool)
    lm = np.asarray(Image.fromarray((acc * 255).astype(np.uint8)).resize((LW, LH), Image.BOX)) > 120
    oy, ox = int(round(fcy - LH / 2)), int(round(fcx - LW / 2))
    L = np.zeros((H, W), bool); L[oy:oy + LH, ox:ox + LW] = lm
    halo2 = ndimage.binary_dilation(L, structure=np.ones((3, 3)), iterations=3) & ~L
    halo1 = ndimage.binary_dilation(L, structure=np.ones((3, 3)), iterations=1) & ~L
    rug[halo2] = RED
    rug[halo1] = BLACK
    rug[L] = BONE
    # a pink pinstripe inside the letters' counters keeps them woven, not printed
    dL = ndimage.distance_transform_edt(L)
    rug[L & (dL > 3) & (dL <= 4)] = KILIM


# ---------- kilim ends (flat weave, no pile) ----------
kil = ~inside
kb = np.where((np.minimum(x, W - 1 - x) % 5 == 2), RED, KILIM)
rug[kil] = kb[kil]
pile = inside.astype(float)

# ---------- render textures ----------
Image.fromarray(PAL[rug].astype(np.uint8)).resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(OUT, 'design.png'))

HH, WW = H * K, W * K
big = np.kron(rug, np.ones((K, K), int))
col = PAL[big].astype(float)
# per-knot jitter + abrash (dye-lot bands running across the rug)
kj = rng.normal(0, 0.035, (H, W))
abr = np.cumsum(rng.normal(0, 0.012, W)); abr -= abr.mean()
abr = ndimage.gaussian_filter1d(abr, 6)
shade = 1 + np.kron(kj + abr[None, :], np.ones((K, K)))
# sub-knot coords
sy, sx = np.mgrid[0:HH, 0:WW]
fu = (sx % K + 0.5) / K - 0.5; fv = (sy % K + 0.5) / K - 0.5
# knot dome: slightly elongated across the row; fibre streaks along the pile
dome = np.clip(1 - (fu / 0.56) ** 2 - (fv / 0.5) ** 2, 0, 1) ** 0.6
fib = ndimage.gaussian_filter(rng.random((HH, WW)), (0.6, 2.2))
fib = (fib - fib.mean()) / fib.std()
fine = rng.random((HH, WW))
pileK = np.kron(pile, np.ones((K, K)))
height = pileK * (0.55 + 0.32 * dome + 0.07 * fib + 0.06 * (fine - 0.5))
# kilim: weft ribs
weft = 0.5 + 0.5 * np.sin(sy * np.pi * 2 / (K / 2))
warp = 0.5 + 0.5 * np.sin(sx * np.pi * 2 / (K / 2) + np.pi * (sy // (K // 2) % 2))
height = np.where(pileK > 0, height, 0.18 + 0.1 * weft * warp + 0.04 * fib)
ao = 0.78 + 0.22 * dome
col *= (shade * np.where(pileK > 0, ao * (1 + 0.05 * fib), 0.9 + 0.1 * weft * warp))[..., None]
# halo of fibres bleeding between knots
col = ndimage.gaussian_filter(col, (0.7, 0.7, 0))
Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'albedo.png'))
h16 = (np.clip(height, 0, 1) * 65535).astype(np.uint16)
Image.fromarray(h16).save(os.path.join(OUT, 'height.png'))
# normal map (OpenGL, +Y up in image space = -row)
hs = ndimage.gaussian_filter(height, 0.6)
gx = ndimage.sobel(hs, 1) / 8.0; gy = ndimage.sobel(hs, 0) / 8.0
st = 3.2
n = np.dstack([-gx * st, gy * st, np.ones_like(hs)])
n /= np.linalg.norm(n, axis=2, keepdims=True)
Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(OUT, 'normal.png'))
rough = np.where(pileK > 0, 0.82 + 0.1 * (1 - dome), 0.9)
Image.fromarray((rough * 255).astype(np.uint8)).save(os.path.join(OUT, 'rough.png'))
json.dump({'knots_w': W, 'knots_h': H, 'kilim': KIL, 'px_per_knot': K}, open(os.path.join(OUT, 'rug.json'), 'w'))
print('ok', W, H, WW, HH)
