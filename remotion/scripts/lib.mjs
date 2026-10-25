import { spawnSync } from 'node:child_process';
import { mkdirSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
/** Las salidas aterrizan en la carpeta pública de la web Next. */
export const BRAND = resolve(ROOT, '../public/media/brand');
export const OUT = join(ROOT, 'out');

mkdirSync(BRAND, { recursive: true });
mkdirSync(OUT, { recursive: true });

export const run = (args, { quiet = false } = {}) => {
  if (!quiet) console.log(`\n$ npx ${args.join(' ')}`);
  const res = spawnSync('npx', args, { cwd: ROOT, stdio: quiet ? 'pipe' : 'inherit' });
  if (res.status !== 0) {
    if (quiet) process.stderr.write(res.stderr ?? '');
    throw new Error(`Falló: npx ${args.join(' ')}`);
  }
};

/** ffmpeg que trae Remotion (no hace falta tenerlo instalado en el sistema). */
export const ffmpeg = (args) => run(['remotion', 'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', ...args], { quiet: true });

export const size = (file) => statSync(file).size;
export const mb = (bytes) => `${(bytes / 1024 / 1024).toFixed(2)} MB`;

/** Pasa por la CLI los argumentos extra (p. ej. --props=evento.json). */
export const extraArgs = process.argv.slice(2).filter((a) => a.startsWith('--'));
