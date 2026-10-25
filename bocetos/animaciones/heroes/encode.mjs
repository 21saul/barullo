/**
 * Codifica los fotogramas de un héroe de sección a los entregables de la web.
 *
 *   node bocetos/animaciones/heroes/encode.mjs <nombre> <carpeta_fotogramas> <segundos> [fotograma_póster]
 *
 * Espera <carpeta>/wide_####.png (1920x1080) y <carpeta>/narrow_####.png
 * (1080x1920), un bucle cada uno, y escribe en public/media/heroes/:
 *   <nombre>-{wide,narrow}.{webm,mp4} y <nombre>-{wide,narrow}-poster.jpg
 *
 * Antes pasa los fotogramas por bocetos/animaciones/colgante/lift.py (grano, viñeta y el
 * negro subido a #0B0B0B, para que el vídeo se funda con el fondo de la web).
 * VP9 y H.264 a dos pasadas, bajando la tasa hasta que cada fichero cabe en
 * su presupuesto.
 */
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readdirSync } from 'node:fs';
import { basename, join, resolve } from 'node:path';
import { OUT, ffmpeg, mb, size } from '../../../remotion/scripts/lib.mjs';

const MB = 1024 * 1024;
const [name, RAW, secs, posterArg] = process.argv.slice(2);
if (!name || !RAW || !secs) throw new Error('uso: encode.mjs <nombre> <fotogramas> <segundos> [póster]');
const SECONDS = Number(secs);
const DEST = resolve(import.meta.dirname, '../../../public/media/heroes');
mkdirSync(DEST, { recursive: true });
const BUDGET = { wide: 2.4 * MB, narrow: 2.2 * MB };

const encode = (master, file, codec, kbps) => {
  const log = join(OUT, `${basename(file)}.passlog`);
  const gop = String(Math.round(SECONDS * 30));
  const common =
    codec === 'vp9'
      ? ['-c:v', 'libvpx-vp9', '-b:v', `${kbps}k`, '-row-mt', '1', '-tile-columns', '2', '-deadline', 'good', '-cpu-used', '1', '-auto-alt-ref', '1', '-lag-in-frames', '25', '-g', gop]
      : ['-c:v', 'libx264', '-b:v', `${kbps}k`, '-preset', 'veryslow', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-g', gop];
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
  throw new Error(`${file} no cabe en ${mb(budget)}`);
};

for (const view of ['wide', 'narrow']) {
  const frames = readdirSync(RAW).filter((f) => f.startsWith(`${view}_`) && f.endsWith('.png')).sort();
  if (!frames.length) {
    console.log(`(sin fotogramas ${view})`);
    continue;
  }
  const lifted = join(RAW, `lifted-${view}`);
  execFileSync(
    `${process.env.HOME}/.local/bin/uv`,
    ['run', '-q', '--no-project', '--with', 'pillow', '--with', 'numpy', 'python', '-I',
      resolve(import.meta.dirname, '../colgante/lift.py'), RAW, lifted, `${view}_`],
    { stdio: 'inherit' },
  );
  const first = frames[0].slice(view.length + 1, -4);
  const target = `${name}-${view}`;
  const master = join(OUT, `${target}-master.mp4`);
  ffmpeg(['-framerate', '30', '-start_number', String(Number(first)), '-i', join(lifted, 'f_%04d.png'),
    '-c:v', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', master]);
  const poster = join(lifted, `f_${String(posterArg ?? first).padStart(4, '0')}.png`);
  if (!existsSync(poster)) throw new Error(`no existe el póster ${poster}`);
  ffmpeg(['-i', poster, '-q:v', '3', join(DEST, `${target}-poster.jpg`)]);
  console.log(`\n${target}`);
  for (const codec of ['vp9', 'h264']) fit(master, join(DEST, `${target}.${codec === 'vp9' ? 'webm' : 'mp4'}`), codec, BUDGET[view]);
  console.log(`  póster ${mb(size(join(DEST, `${target}-poster.jpg`)))}`);
}
