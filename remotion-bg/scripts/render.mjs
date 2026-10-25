// Renderiza todos los fondos a public/media/brand/ y garantiza < 800 KB por archivo
// subiendo el CRF hasta que quepa. Uso: npm run render [-- <id-composición>]
import {execFileSync} from 'node:child_process';
import {statSync, mkdirSync} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = resolve(root, '../public/media/brand');
const MAX = 800 * 1024;
mkdirSync(OUT, {recursive: true});

const JOBS = [
  {id: 'BgLiquidChrome-vertical', name: 'bg-liquid-chrome-vertical', formats: ['mp4', 'webm']},
  {id: 'BgLiquidChrome-wide', name: 'bg-liquid-chrome-wide', formats: ['mp4', 'webm']},
  {id: 'BgBloomDrift-vertical', name: 'bg-bloom-drift-vertical', formats: ['mp4', 'webm']},
  {id: 'BgBloomDrift-wide', name: 'bg-bloom-drift-wide', formats: ['mp4', 'webm']},
  // Cancelado (no hay alfa VP9 en Safari/iOS); se renderiza sólo con: npm run render -- BgSparkleField
  {id: 'BgSparkleField', name: 'bg-sparkle-field', manual: true, formats: ['webm-alpha'], posterProps: {background: '#0B0410'}},
];

const ENC = {
  mp4: {ext: 'mp4', crf: 28, max: 40, args: ['--codec=h264', '--pixel-format=yuv420p']},
  webm: {ext: 'webm', crf: 36, max: 52, args: ['--codec=vp9', '--pixel-format=yuv420p']},
  'webm-alpha': {ext: 'webm', crf: 34, max: 52, args: ['--codec=vp9', '--pixel-format=yuva420p', '--image-format=png']},
};

const remotion = (args) =>
  execFileSync('npx', ['remotion', ...args, '--log=error'], {cwd: root, stdio: 'inherit'});

const only = process.argv[2];
for (const job of JOBS.filter((j) => (only ? j.id === only : !j.manual))) {
  for (const f of job.formats) {
    const enc = ENC[f];
    const file = `${OUT}/${job.name}.${enc.ext}`;
    for (let crf = enc.crf; ; crf += 4) {
      remotion(['render', 'src/index.ts', job.id, file, ...enc.args, `--crf=${crf}`]);
      const size = statSync(file).size;
      console.log(`${job.name}.${enc.ext}  crf=${crf}  ${(size / 1024).toFixed(0)} KB`);
      if (size < MAX) break;
      if (crf + 4 > enc.max) throw new Error(`${file} no baja de 800 KB`);
    }
  }
  // Póster = primer frame. El de destellos lleva fondo void (un JPG no tiene alfa).
  const poster = `${OUT}/${job.name}-poster.jpg`;
  remotion(['still', 'src/index.ts', job.id, poster, '--frame=0', '--image-format=jpeg', '--jpeg-quality=82',
    ...(job.posterProps ? [`--props=${JSON.stringify(job.posterProps)}`] : [])]);
  console.log(`${job.name}-poster.jpg  ${(statSync(poster).size / 1024).toFixed(0)} KB`);
}
