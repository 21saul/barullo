"""Photographic finish + black lift for the pendant frames.

Blender writes pure black and a perfectly clean (denoised) image, which reads as CG. Each frame gets:
- a mild unsharp mask (the knit and skin texture survive the denoiser better),
- fine luminance grain that changes every frame, like a real sensor,
- a gentle vignette,
- black lifted to Barullo #0B0B0B (Remotion's ffmpeg has no lutrgb).

  uv run --no-project --with pillow --with numpy python -I lift.py <src_dir> <dst_dir> [prefix]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
prefix = sys.argv[3] if len(sys.argv) > 3 else "f_"
GRAIN, SHARP, VIGNETTE = 2.6, 60, 0.18
dst.mkdir(parents=True, exist_ok=True)
vig = None
n = 0
for f in sorted(src.glob(f"{prefix}*.png")):
    out = dst / f"f_{f.stem[len(prefix):]}.png"
    if out.exists() and out.stat().st_mtime >= f.stat().st_mtime:
        continue
    im = Image.open(f).convert("RGB")
    a = np.asarray(im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=SHARP, threshold=1)), np.float32)
    h, w, _ = a.shape
    if vig is None:
        yy, xx = np.mgrid[0:h, 0:w]
        vig = (1 - VIGNETTE * 0.5 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)).astype(np.float32)
    rng = np.random.default_rng(int(f.stem[len(prefix):]))
    g = Image.fromarray((rng.normal(0, 40, (h, w)) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    g = (np.asarray(g, np.float32) - 128) / 40 * GRAIN
    # grain fades out in the black background so the video still melts into the page
    a = a * vig[..., None] + g[..., None] * np.sqrt(a / 255)
    a = 11 + a.clip(0, 255) * 244 / 255
    Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(out, compress_level=1)
    n += 1
print("finished", n)
