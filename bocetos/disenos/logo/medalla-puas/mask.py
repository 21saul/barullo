from PIL import Image, ImageFilter
import numpy as np, sys
from collections import deque
im = Image.open(sys.argv[1]).convert("RGB")
a = np.asarray(im).astype(int); h, w, _ = a.shape
r, g, b = a[..., 0], a[..., 1], a[..., 2]
red = (r > 150) & (g < 120) & (b < 120)
bg = np.zeros((h, w), bool); q = deque()
for x in range(w): q += [(0, x), (h - 1, x)]
for y in range(h): q += [(y, 0), (y, w - 1)]
while q:
    y, x = q.popleft()
    if 0 <= y < h and 0 <= x < w and not bg[y, x] and not red[y, x]:
        bg[y, x] = True; q += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
letters = ~bg & ~red
cols = np.where(letters.any(0))[0]; rows = np.where(letters.any(1))[0]
print(h, w, "x", cols.min(), cols.max(), "y", rows.min(), rows.max())
m = Image.fromarray(np.where(letters, 0, 255).astype(np.uint8))
m = m.resize((w * 8, h * 8), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6)).point(lambda v: 0 if v < 128 else 255)
m.save(sys.argv[2])
