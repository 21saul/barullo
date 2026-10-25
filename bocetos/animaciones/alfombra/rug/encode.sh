#!/usr/bin/env bash
# Encode the flying-carpet PNG frames with Remotion's bundled ffmpeg.
#   encode.sh <frames_dir> <out_dir>
# Expects <frames_dir>/square_####.png and/or wide_####.png (one 180-frame loop each).
set -euo pipefail
FR=$1; OUT=$2; mkdir -p "$OUT"
cd "$(dirname "$0")/../../../../remotion"
ff() { npx remotion ffmpeg -hide_banner -loglevel error -y "$@"; }

if ls "$FR"/square_*.png >/dev/null 2>&1; then
  # Instagram: 1080x1080, 3 loops (18 s), high-quality H.264
  ff -framerate 30 -stream_loop 2 -i "$FR/square_%04d.png" -c:v libx264 -preset slow -crf 15 \
     -profile:v high -pix_fmt yuv420p -movflags +faststart "$OUT/barullo-alfombra-ig-1080.mp4"
  ff -i "$FR/square_0045.png" -q:v 2 "$OUT/barullo-alfombra-poster-1080.jpg"
fi
if ls "$FR"/wide_*.png >/dev/null 2>&1; then
  # Web hero: one seamless loop, the page loops it
  ff -framerate 30 -i "$FR/wide_%04d.png" -c:v libvpx-vp9 -b:v 2600k -row-mt 1 -deadline good -cpu-used 1 \
     -pix_fmt yuv420p -an "$OUT/barullo-alfombra-hero-1920.webm"
  ff -framerate 30 -i "$FR/wide_%04d.png" -c:v libx264 -preset slow -crf 19 -profile:v high \
     -pix_fmt yuv420p -movflags +faststart -an "$OUT/barullo-alfombra-hero-1920.mp4"
  ff -i "$FR/wide_0045.png" -q:v 2 "$OUT/barullo-alfombra-poster-1920.jpg"
fi
ls -la "$OUT"
