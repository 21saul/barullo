"""Foto del cartel Grillz: gradación rojo/negro, encuadre a la boca y grills de Blender compuestos en los dientes.

python compose.py <foto.jpg> <grill-logo-dir> <grill-fecha-dir> <out_dir>

Sale en <out_dir>:
  base.jpg     1080×1920, foto graduada con las sombras de contacto de los grills (sin los grills)
  still.jpg    base + grills (cartel fijo / póster)
  top.png, bottom.png  capas de los grills al doble de resolución (se dibujan a la mitad)
  grillz.json  cajas de las capas en px del cartel y destellos (gemas) en px del cartel
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

SRC, GTOP, GBOT, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
W_OUT, H_OUT = 1080, 1920
SC, X0, Y0 = 2.5, 152, 256           # px de la foto → px del cartel: (p - X0) * SC

im = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32) / 255
H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
mx, mn = im.max(-1), im.min(-1)
sat = (mx - mn) / (mx + 1e-6)
yy, xx = np.mgrid[0:H, 0:W]

# fondo rojo liso
face = (((xx - W * 0.5) / (W * 0.24)) ** 2 + ((yy - H * 0.55) / (H * 0.17)) ** 2) < 1
redish = (r == mx) & (sat > 0.6) & (g < 0.4 * r + 0.05) & (np.abs(g - b) < 0.12) & (mx > 0.12) & ~face
lab, _ = ndimage.label(redish)
seeds = set(np.unique(lab[0, :])) | set(np.unique(lab[: H // 2, 0])) | set(np.unique(lab[: H // 2, -1]))
seeds.discard(0)
bgm = ndimage.binary_dilation(ndimage.binary_closing(np.isin(lab, list(seeds)), iterations=3), iterations=1) & ~face
bgm = np.asarray(Image.fromarray((bgm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255

# metal de la boca (dientes y colmillos): se queda en plata
mouth = (((xx - 368) / 115) ** 2 + ((yy - 610) / 140) ** 2) < 1
metal = ndimage.binary_opening(mouth & (sat < 0.32) & (mx > 0.42), iterations=1)
metal = np.asarray(Image.fromarray((metal * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255

L = np.clip((0.55 * r + 0.35 * g + 0.10 * b - 0.04) / 0.9, 0, 1) ** 1.15


def gmap(t, stops):
    xs = np.array([s[0] for s in stops]); cs = np.array([s[1] for s in stops], np.float32) / 255
    return np.stack([np.interp(t, xs, cs[:, k]) for k in range(3)], -1)


fig = gmap(L, [(0, (5, 3, 4)), (0.22, (34, 4, 4)), (0.45, (120, 12, 8)), (0.66, (214, 32, 22)), (0.84, (255, 104, 74)), (1, (255, 232, 222))])
silver = gmap(np.clip(L * 1.1, 0, 1), [(0, (20, 20, 24)), (0.5, (150, 154, 162)), (0.8, (226, 229, 235)), (1, (255, 255, 255))])
fig = fig * (1 - metal[..., None]) + silver * metal[..., None]
glow = np.exp(-(((xx - W * 0.5) / (W * 0.5)) ** 2 + ((yy - H * 0.33) / (H * 0.33)) ** 2))
bg = np.array([7, 5, 6], np.float32) / 255 * (1 - glow[..., None]) + np.array([150, 14, 8], np.float32) / 255 * glow[..., None]
res = fig * (1 - bgm[..., None]) + bg * bgm[..., None]

src = Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8))
cw, ch = W_OUT / SC, H_OUT / SC
canvas = Image.new('RGB', (round(cw), round(ch)), (7, 5, 6))
canvas.paste(src.crop((X0, Y0, min(W, X0 + round(cw)), min(H, Y0 + round(ch)))), (0, 0))
base = canvas.resize((W_OUT, H_OUT), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.4, percent=80, threshold=2))
base = np.asarray(base).astype(np.float32) / 255

# ---------- grills
P = lambda x, y: ((x - X0) * SC, (y - Y0) * SC)


def layer(path, width_px, cx, top=None, baseline=None, base_frac=None, cy=None):
    """Recorta el render a su alfa y lo escala a `width_px` px de cartel (la capa se guarda al doble)."""
    g_ = Image.open(path).convert('RGBA')
    bbox = g_.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    g_ = g_.crop(bbox)
    h_px = width_px * g_.height / g_.width
    if baseline is not None:
        top = baseline - base_frac * h_px
    if cy is not None:
        top = cy - h_px / 2
    left = cx - width_px / 2
    big = g_.resize((round(width_px * 2), round(h_px * 2)), Image.LANCZOS)
    # un pelo de tinte rojo en las sombras del metal: el mismo aire que la foto
    a = np.asarray(big).astype(np.float32) / 255
    rgb = a[..., :3]
    shade = 1 - rgb.mean(-1, keepdims=True)
    rgb = np.clip(rgb * 1.18, 0, 1) ** 0.88                    # el metal, más vivo que el render a este tamaño
    rgb = rgb * (1 - 0.12 * shade) + np.array([0.35, 0.03, 0.02]) * 0.12 * shade
    big = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), a[..., 3:]]) * 255).astype(np.uint8), 'RGBA')
    return big, dict(left=round(left, 2), top=round(top, 2), width=round(width_px, 2), height=round(h_px, 2)), bbox, g_.size


def shadow(img, box, dy, blur, k):
    """Sombra de contacto: el alfa desenfocado oscurece la foto bajo el grill."""
    global base
    a = img.getchannel('A').resize((round(box['width']), round(box['height'])), Image.LANCZOS)
    m = Image.new('L', (W_OUT, H_OUT), 0)
    m.paste(a, (round(box['left']), round(box['top'] + dy)))
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32)[..., None] / 255
    base = base * (1 - k * m)


# logo arriba: las fundas (812 u. del SVG de alto, 2906 de ancho) van de la encía (y 496) al borde de los dientes (y 541)
GUM, EDGE = 496, 541
tw = 2906 * (EDGE - GUM) / 812
tx0, tty = P(371 - tw / 2, GUM); tx1, _ = P(371 + tw / 2, GUM)
top, top_box, top_bbox, top_size = layer(os.path.join(GTOP, 'grill.png'), tx1 - tx0, (tx0 + tx1) / 2, top=tty - 4)
# fecha abajo: tapa la placa «logan» (x 326–409, y 689–722)
bx0, by0 = P(324, 689); bx1, by1 = P(411, 722)
bot, bot_box, bot_bbox, bot_size = layer(os.path.join(GBOT, 'grill.png'), bx1 - bx0, (bx0 + bx1) / 2, cy=(by0 + by1) / 2)

shadow(top, top_box, 7, 7, 0.75)
shadow(bot, bot_box, 5, 5, 0.7)
base_img = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8))
base_img.save(os.path.join(OUT, 'base.jpg'), quality=93)

# encía: la foto por encima del borde de la encía, con un fundido corto, va por delante del grill
gy = tty + 3
gx0, gx1 = round(top_box['left'] - 30), round(top_box['left'] + top_box['width'] + 30)
gt = round(top_box['top'] - 30)
gum = base_img.crop((gx0, gt, gx1, round(gy + 6))).convert('RGBA')
ga = np.zeros((gum.height, gum.width), np.float32)
rows = np.arange(gum.height) + gt
ga[:] = np.clip((gy + 6 - rows) / 9, 0, 1)[:, None]
cols = np.arange(gum.width) + gx0
side = np.clip(np.minimum(cols - gx0, gx1 - cols) / 24, 0, 1)
ga *= side[None, :]
gum.putalpha(Image.fromarray((ga * 255).astype(np.uint8)))
gum.save(os.path.join(OUT, 'gum.png'))
gum_box = dict(left=gx0, top=gt, width=gum.width, height=gum.height)

still = base_img.convert('RGBA')
for img, box in ((top, top_box), (bot, bot_box)):
    still.alpha_composite(img.resize((round(box['width']), round(box['height'])), Image.LANCZOS), (round(box['left']), round(box['top'])))
still.alpha_composite(gum, (gx0, gt))
still.convert('RGB').save(os.path.join(OUT, 'still.jpg'), quality=93)
top.save(os.path.join(OUT, 'top.png'), optimize=True)
bot.save(os.path.join(OUT, 'bottom.png'), optimize=True)


def glints(gdir, bbox, size, box):
    """Gemas del render (fracciones de la imagen completa) → px del cartel."""
    j = json.load(open(os.path.join(gdir, 'grill.json')))
    pts = j['gems'] + ([j['ruby']] if not j.get('text') else [])
    out = []
    for fx, fy in pts:
        x = (fx * j['w'] - bbox[0]) / size[0] * box['width'] + box['left']
        y = (fy * j['h'] - bbox[1]) / size[1] * box['height'] + box['top']
        out.append([round(x, 1), round(y, 1)])
    return out


meta = {
    'top': top_box, 'bottom': bot_box, 'gum': gum_box,
    'glintsTop': glints(GTOP, top_bbox, top_size, top_box),
    'glintsBottom': glints(GBOT, bot_bbox, bot_size, bot_box)[:-1],
}
json.dump(meta, open(os.path.join(OUT, 'grillz.json'), 'w'), indent=1)
print(json.dumps({k: meta[k] for k in ('top', 'bottom')}))
