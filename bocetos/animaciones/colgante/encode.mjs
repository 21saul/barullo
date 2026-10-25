/**
 * Encodes the pendant loop frames (Blender, 2520x1080) into the web deliverables.
 *
 *   node bocetos/animaciones/colgante/encode.mjs
 *
 * square = centred 1080x1080 crop, wide = 21:9 scaled to 2240x960.
 * VP9 + H.264 two-pass, bitrate lowered until each file fits its budget.
 */
import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { basename, join } from 'node:path';
import { BRAND, OUT, ffmpeg, mb, size } from '../../../remotion/scripts/lib.mjs';

const MB = 1024 * 1024;
const DEST = process.env.PENDANT_DEST ?? BRAND; // staging dir for review before it goes live
const RAW = process.env.PENDANT_FRAMES ?? '/mnt/c/Users/Veintiuno/barullo-render/colgante/frames';
const FRAMES = join(RAW, 'lifted');
const SECONDS = 7;
const TARGETS = [
  { name: 'hero-pendant-square', vf: 'crop=1080:1080:720:0', budget: 2.4 * MB },
  { name: 'hero-pendant-wide', vf: 'scale=2240:960:flags=lanczos', budget: 2.4 * MB },
];

const encode = (master, file, codec, kbps) => {
  const log = join(OUT, `${basename(file)}.passlog`);
  const common =
    codec === 'vp9'
      ? ['-c:v', 'libvpx-vp9', '-b:v', `${kbps}k`, '-row-mt', '1', '-tile-columns', '2', '-deadline', 'good', '-cpu-used', '1', '-auto-alt-ref', '1', '-lag-in-frames', '25', '-g', '210']
      : ['-c:v', 'libx264', '-b:v', `${kbps}k`, '-preset', 'veryslow', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-g', '210'];
  ffmpeg(['-i', master, ...common, '-pass', '1', '-passlogfile', log, '-an', '-f', codec === 'vp9' ? 'webm' : 'mp4', '/dev/null']);
  ffmpeg(['-i', master, ...common, '-pass', '2', '-passlogfile', log, '-an', ...(codec === 'vp9' ? [] : ['-movflags', '+faststart']), file]);
  return size(file);
};

const fit = (master, file, codec, budget) => {
  let kbps = Math.floor(((budget * 8) / SECONDS / 1000) * 0.92);
  for (let attempt = 1; attempt <= 6; attempt++) {
    const bytes = encode(master, file, codec, kbps);
    console.log(`  ${codec} @ ${kbps} kbps → ${mb(bytes)}`);
    if (bytes <= budget) return bytes;
    kbps = Math.floor(kbps * (budget / bytes) * 0.97);
  }
  throw new Error(`${file} does not fit ${mb(budget)}`);
};

if (!existsSync(join(RAW, 'f_0209.png'))) throw new Error(`frames incomplete in ${RAW}`);
// Blender writes pure black; lift it to Barullo #0B0B0B so the video melts into the page
// (Remotion's ffmpeg has no lutrgb, so lift.py does it).
execFileSync(
  `${process.env.HOME}/.local/bin/uv`,
  ['run', '-q', '--no-project', '--with', 'pillow', '--with', 'numpy', 'python', '-I', join(import.meta.dirname, 'lift.py'), RAW, FRAMES],
  { stdio: 'inherit' },
);
for (const t of TARGETS) {
  const master = join(OUT, `${t.name}-master.mp4`);
  ffmpeg(['-framerate', '30', '-start_number', '0', '-i', join(FRAMES, 'f_%04d.png'), '-vf', t.vf, '-c:v', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', master]);
  ffmpeg(['-i', join(FRAMES, 'f_0000.png'), '-vf', t.vf, '-q:v', '3', join(DEST, `${t.name}-poster.jpg`)]);
  console.log(`\n${t.name}`);
  for (const codec of ['vp9', 'h264']) fit(master, join(DEST, `${t.name}.${codec === 'vp9' ? 'webm' : 'mp4'}`), codec, t.budget);
  console.log(`  poster ${mb(size(join(DEST, `${t.name}-poster.jpg`)))}`);
}
