/**
 * Renderiza StoryEvent o FlyerAnim en H.264 (lo que mejor digiere Instagram).
 *
 *   npm run render:story
 *   npm run render:story -- --props=eventos/mi-evento.json --name=story-mi-evento
 *
 * Sin --props usa los defaultProps (evento demo).
 */
import { join } from 'node:path';
import { BRAND, extraArgs, mb, run, size } from './lib.mjs';

const DEFAULT_NAME = { StoryEvent: 'story-event-demo', FlyerAnim: 'flyer-anim-demo' };

const id = process.argv[2];
if (!DEFAULT_NAME[id]) {
  console.error(`Uso: node scripts/render-template.mjs <${Object.keys(DEFAULT_NAME).join('|')}> [--props=archivo.json] [--name=salida]`);
  process.exit(1);
}

const nameArg = extraArgs.find((a) => a.startsWith('--name='));
const name = nameArg ? nameArg.slice('--name='.length) : DEFAULT_NAME[id];
const passthrough = extraArgs.filter((a) => !a.startsWith('--name='));

const file = join(BRAND, `${name}.mp4`);
run([
  'remotion', 'render', id, file,
  '--codec=h264', '--crf=20', '--pixel-format=yuv420p', '--x264-preset=slow',
  ...passthrough,
]);
console.log(`\n${mb(size(file)).padStart(9)}  ${file}`);
