"""Trace the designer's kufi wordmark mask into clean polygons (SVG + JSON for Blender)."""
import sys, json
import numpy as np
from PIL import Image, ImageFilter
from skimage import measure

src, out_svg, out_json, out_png = sys.argv[1:5]
im = Image.open(src).convert('RGBA')
a = np.asarray(im)[..., 3].astype(float)
# wordmark-white.png is already 3x; upscale 2x more, soften, threshold
S = 2
big = Image.fromarray(a.astype(np.uint8)).resize((im.width * S, im.height * S), Image.LANCZOS)
big = big.filter(ImageFilter.GaussianBlur(6))
m = (np.asarray(big) > 127)
m = np.pad(m, 4)
H, W = m.shape
Image.fromarray((m * 255).astype(np.uint8)).save(out_png)
contours = measure.find_contours(m.astype(float), 0.5)
polys = []
for c in contours:
    p = measure.approximate_polygon(c, tolerance=3.2)
    if len(p) < 4:
        continue
    area = 0.5 * np.sum(p[:-1, 1] * p[1:, 0] - p[1:, 1] * p[:-1, 0])
    if abs(area) < 60:
        continue
    polys.append(p[:, ::-1].tolist())  # x,y
d = ' '.join('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in p) + ' Z' for p in polys)
open(out_svg, 'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><path fill-rule="evenodd" fill="#F2EFE8" d="{d}"/></svg>')
json.dump({'w': W, 'h': H, 'polys': polys}, open(out_json, 'w'))
print(len(polys), 'polys', W, H)
