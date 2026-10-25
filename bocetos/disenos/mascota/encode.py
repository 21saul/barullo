"""
Codifica el bucle del diablillo para la web, con transparencia.

  uv run --no-project --with pillow --with numpy python -I encode.py <carpeta_frames> [--size 720] [--dest public/media/brand/diablillo]

Lee <carpeta>/f_####.png (RGBA, 16 bits) y escribe en --dest:
  loop.webm   VP9 con canal alfa (Chrome, Firefox, Edge)
  loop.webp   WebP animado con alfa (Safari, que no lee el alfa del VP9)
  poster.png / poster.webp  primer fotograma (el .webp es el que usa la web)
  preview.mp4 sobre el negro de la web, sólo para revisar (no se publica)
"""
import argparse, os, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("frames")
ap.add_argument("--size", type=int, default=720)
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--dest", default=str(ROOT / "public/media/brand/diablillo"))
ap.add_argument("--webp-size", type=int, default=480)
ap.add_argument("--webp-quality", type=int, default=70)
ap.add_argument("--crf", type=int, default=40)
ap.add_argument("--webp-step", type=int, default=2, help="WebP: uno de cada N fotogramas (pesa la mitad a 15 fps)")
a = ap.parse_args()

src = sorted(Path(a.frames).glob("f_*.png"))
if not src:
    sys.exit("sin fotogramas")
dest = Path(a.dest)
dest.mkdir(parents=True, exist_ok=True)
tmp = Path(tempfile.mkdtemp(prefix="diablillo-"))


def ffmpeg(*args):
    subprocess.run(["npx", "remotion", "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                   cwd=ROOT / "remotion", check=True)


frames = []
for i, p in enumerate(src):
    im = Image.open(p)
    if im.mode not in ("RGBA", "RGB"):
        im = im.convert("RGBA")
    im = im.convert("RGBA").resize((a.size, a.size), Image.LANCZOS)
    im.save(tmp / f"f_{i:04d}.png")
    frames.append(im)

ffmpeg("-framerate", str(a.fps), "-i", str(tmp / "f_%04d.png"),
       "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", str(a.crf),
       "-deadline", "good", "-cpu-used", "1", "-row-mt", "1", "-auto-alt-ref", "0", "-an",
       str(dest / "loop.webm"))

small = [f.resize((a.webp_size, a.webp_size), Image.LANCZOS) for f in frames[::a.webp_step]]
small[0].save(dest / "loop.webp", save_all=True, append_images=small[1:], duration=round(1000 * a.webp_step / a.fps),
              loop=0, quality=a.webp_quality, alpha_quality=60, method=4)

frames[0].save(dest / "poster.png", optimize=True)
frames[0].save(dest / "poster.webp", quality=85, alpha_quality=90, method=6)

# revisión: sobre el negro de la web
for i, f in enumerate(frames):
    bg = Image.new("RGBA", f.size, (11, 13, 17, 255))
    bg.alpha_composite(f)
    bg.convert("RGB").save(tmp / f"b_{i:04d}.png")
ffmpeg("-framerate", str(a.fps), "-i", str(tmp / "b_%04d.png"), "-c:v", "libx264", "-crf", "18",
       "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(Path(a.frames) / "preview.mp4"))

for f in ("loop.webm", "loop.webp", "poster.png", "poster.webp"):
    print(f, f"{os.path.getsize(dest / f) / 1024:.0f} KB")
