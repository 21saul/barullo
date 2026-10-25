/**
 * Renderiza un bucle (hero o personaje) y lo comprime hasta su presupuesto.
 *
 *   node scripts/render-loop.mjs hero [vertical|wide] [--reuse-master]
 *   node scripts/render-loop.mjs character [3x2|wide] [--reuse-master]
 *   node scripts/render-loop.mjs blender|cyber|v4|v5 [3x2|wide]   (frames PNG ya renderizados en Blender)
 *
 * 1. Máster casi sin pérdidas (H.264 CRF 10) con Remotion.
 * 2. Con el ffmpeg de Remotion, VP9 (.webm) y H.264 (.mp4) a dos pasadas con
 *    bitrate objetivo. Si el archivo se pasa del presupuesto, se baja el
 *    bitrate en proporción y se repite (el peso manda sobre la fidelidad).
 * 3. Póster JPEG del frame 0, que es también el último del bucle.
 */
import { existsSync } from 'node:fs';
import { basename, join } from 'node:path';
import { BRAND, OUT, ffmpeg, mb, run, size } from './lib.mjs';

const MB = 1024 * 1024;
/** Donde Blender (Windows) deja los PNG: una carpeta por variante. */
const BLENDER_FRAMES = process.env.BLENDER_FRAMES ?? '/mnt/c/Users/Veintiuno/barullo-render';

const GROUPS = {
  hero: [
    { id: 'HeroLoop', name: 'hero-loop-vertical', poster: 'hero-poster.jpg', budget: 1.45 * MB, seconds: 6 },
    { id: 'HeroLoopWide', name: 'hero-loop-wide', poster: 'hero-poster-wide.jpg', budget: 1.9 * MB, seconds: 6 },
  ],
  // Encargo: < 1,2 MB por vídeo. 1,1 MiB = 1,15 MB, con margen en ambas unidades.
  // Mascota 3D en cromo negro (three.js, render por software con supersampling ×2: tarda).
  // Móvil 1080x1080 aunque el archivo se llame 3x2 (la web mantiene esa ruta).
  character: [
    { id: 'HeroCharacter', name: 'hero-character-3x2', poster: 'hero-character-3x2-poster.jpg', budget: 1.1 * MB, seconds: 8 },
    { id: 'HeroCharacterWide', name: 'hero-character-wide', poster: 'hero-character-wide-poster.jpg', budget: 1.1 * MB, seconds: 8 },
  ],
  // Mascota v2 hecha en Blender (blender/barullo_mascot.py). Sustituye a `character`
  // en las mismas rutas de la web; los frames PNG los deja Blender en BLENDER_FRAMES.
  blender: [
    { frames: 'square', name: 'hero-character-3x2', poster: 'hero-character-3x2-poster.jpg', budget: 1.1 * MB, seconds: 8 },
    { frames: 'wide', name: 'hero-character-wide', poster: 'hero-character-wide-poster.jpg', budget: 1.1 * MB, seconds: 8 },
  ],
  // Mascota v3 "cyber" (blender/barullo_cyber.py): busto de porcelana lila. Nombres
  // propios hasta que se apruebe y sustituya a hero-character-*.
  cyber: [
    { frames: 'cyber-square', name: 'hero-character-cyber-3x2', poster: 'hero-character-cyber-3x2-poster.jpg', budget: 1.1 * MB, seconds: 8 },
    { frames: 'cyber-wide', name: 'hero-character-cyber-wide', poster: 'hero-character-cyber-wide-poster.jpg', budget: 1.1 * MB, seconds: 8 },
  ],
  // Mascota v4 (blender/barullo_v4.py): busto de porcelana con pinchos y auriculares.
  // Si aún no hay frames de v4-wide, esa variante se salta.
  v4: [
    { frames: 'v4-square', name: 'hero-character-v4-3x2', poster: 'hero-character-v4-3x2-poster.jpg', budget: 1.1 * MB, seconds: 8 },
    { frames: 'v4-wide', name: 'hero-character-v4-wide', poster: 'hero-character-v4-wide-poster.jpg', budget: 1.1 * MB, seconds: 8 },
  ],
  // Mascota v5 (blender/barullo_v5.py): sin cigarro ni grillz, labios realistas,
  // cascos y corona más detallados. Bucle de 10 s, gestos lentos.
  v5: [
    { frames: 'v5-square', name: 'hero-character-v5-3x2', poster: 'hero-character-v5-3x2-poster.jpg', budget: 1.1 * MB, seconds: 10 },
    { frames: 'v5-wide', name: 'hero-character-v5-wide', poster: 'hero-character-v5-wide-poster.jpg', budget: 1.1 * MB, seconds: 10 },
  ],
  // Retrato 3D rosa anterior, de respaldo.
  pink: [
    { id: 'HeroCharacterPink', name: 'hero-character-pink-3x2', poster: 'hero-character-pink-3x2-poster.jpg', budget: 1.1 * MB, seconds: 8 },
    { id: 'HeroCharacterPinkWide', name: 'hero-character-pink-wide', poster: 'hero-character-pink-wide-poster.jpg', budget: 1.1 * MB, seconds: 8 },
  ],
  // Personaje vectorial (SVG), de respaldo.
  vector: [
    { id: 'HeroCharacterVector', name: 'hero-character-vector-3x2', poster: 'hero-character-vector-3x2-poster.jpg', budget: 1.1 * MB, seconds: 8 },
    { id: 'HeroCharacterVectorWide', name: 'hero-character-vector-wide', poster: 'hero-character-vector-wide-poster.jpg', budget: 1.1 * MB, seconds: 8 },
  ],
};

const args = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const TARGETS = GROUPS[args[0]];
if (!TARGETS) {
  console.error(`Uso: node scripts/render-loop.mjs <${Object.keys(GROUPS).join('|')}> [variante] [--reuse-master]`);
  process.exit(1);
}

const encode = (master, file, codec, kbps) => {
  const log = join(OUT, `${basename(file)}.passlog`);
  const common =
    codec === 'vp9'
      ? ['-c:v', 'libvpx-vp9', '-b:v', `${kbps}k`, '-row-mt', '1', '-tile-columns', '2', '-deadline', 'good', '-cpu-used', '1', '-auto-alt-ref', '1', '-lag-in-frames', '25', '-g', '180']
      : ['-c:v', 'libx264', '-b:v', `${kbps}k`, '-preset', 'veryslow', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-g', '180'];
  ffmpeg(['-i', master, ...common, '-pass', '1', '-passlogfile', log, '-an', '-f', codec === 'vp9' ? 'webm' : 'mp4', '/dev/null']);
  ffmpeg([
    '-i', master, ...common, '-pass', '2', '-passlogfile', log, '-an',
    ...(codec === 'vp9' ? [] : ['-movflags', '+faststart']),
    file,
  ]);
  return size(file);
};

/** Ajusta el bitrate hasta que el archivo cabe en el presupuesto. */
const fit = (master, file, codec, budget, seconds) => {
  let kbps = Math.floor(((budget * 8) / seconds / 1000) * 0.9);
  for (let attempt = 1; attempt <= 6; attempt++) {
    const bytes = encode(master, file, codec, kbps);
    console.log(`  ${codec} @ ${kbps} kbps → ${mb(bytes)}`);
    if (bytes <= budget) return { bytes, kbps };
    kbps = Math.floor(kbps * (budget / bytes) * 0.97);
  }
  throw new Error(`${file} no cabe en ${mb(budget)} tras 6 intentos`);
};

const only = args[1]; // opcional: variante (vertical, wide, 3x2)
// --reuse-master: salta el render y solo recomprime (útil al ajustar pesos).
const reuse = process.argv.includes('--reuse-master');

const results = [];
for (const target of TARGETS) {
  if (only && !target.name.endsWith(only)) continue;
  const master = join(OUT, `${target.name}-master.mp4`);
  if (target.frames) {
    const seq = join(BLENDER_FRAMES, target.frames);
    if (!existsSync(join(seq, '0001.png'))) {
      console.log(`Sin frames en ${seq}: se salta ${target.name}`);
      continue;
    }
    ffmpeg(['-framerate', '30', '-i', join(seq, '%04d.png'), '-c:v', 'libx264', '-crf', '10', '-pix_fmt', 'yuv420p', master]);
    ffmpeg(['-i', join(seq, '0001.png'), '-q:v', '3', join(BRAND, target.poster)]);
  } else {
    if (!(reuse && existsSync(master))) {
      run(['remotion', 'render', target.id, master, '--codec=h264', '--crf=10', '--pixel-format=yuv420p']);
    }
    run(['remotion', 'still', target.id, join(BRAND, target.poster), '--frame=0', '--image-format=jpeg', '--jpeg-quality=82']);
  }

  console.log(`\nComprimiendo ${target.name} (presupuesto ${mb(target.budget)})`);
  for (const codec of ['vp9', 'h264']) {
    const file = join(BRAND, `${target.name}.${codec === 'vp9' ? 'webm' : 'mp4'}`);
    const { bytes, kbps } = fit(master, file, codec, target.budget, target.seconds);
    results.push({ file, bytes, kbps });
  }
  results.push({ file: join(BRAND, target.poster), bytes: size(join(BRAND, target.poster)) });
}

console.log('\nResultado:');
for (const r of results) console.log(`  ${mb(r.bytes).padStart(9)}  ${r.file}${r.kbps ? `  (${r.kbps} kbps)` : ''}`);
