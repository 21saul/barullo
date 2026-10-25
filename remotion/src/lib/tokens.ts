/**
 * Tokens de marca Barullo.
 * Fuente de verdad: bocetos/DIRECCION-VISUAL.md
 */
export const C = {
  void: '#0B0410',
  midnight: '#160A22',
  bubblegum: '#FF4FD8',
  blood: '#E6003C',
  violet: '#7B2BFF',
  iris: '#B9A8FF',
  milk: '#FFF1F7',
  chrome1: '#FFFFFF',
  chrome2: '#C8CCE0',
  chrome3: '#7E849E',
} as const;

export const FONT_DISPLAY = 'BarulloDisplay, Impact, sans-serif';
export const FONT_UI = 'BarulloUI, "DejaVu Sans", sans-serif';
export const FONT_SCRIBBLE = 'BarulloScribble, cursive';

/** Radio squircle (24–40 px segun la direccion visual). */
export const SQUIRCLE = 36;

const TAU = Math.PI * 2;

/**
 * Oscilador con periodo exacto = `cycles` vueltas por bucle.
 * `t` es la fase 0..1 del bucle; con `cycles` entero, t=0 y t=1 coinciden,
 * que es lo que garantiza el bucle perfecto.
 */
export const osc = (t: number, cycles = 1, phase = 0) =>
  Math.sin(TAU * (cycles * t + phase));

export const oscCos = (t: number, cycles = 1, phase = 0) =>
  Math.cos(TAU * (cycles * t + phase));

/** 0..1 suave, mismo periodo que `osc`. */
export const pulse = (t: number, cycles = 1, phase = 0) =>
  0.5 + 0.5 * osc(t, cycles, phase);

/** Destello: pico corto y el resto apagado (sin^n recortado). */
export const twinkle = (t: number, cycles = 1, phase = 0, sharpness = 6) =>
  Math.pow(Math.max(0, osc(t, cycles, phase)), sharpness);

/** Pseudo-aleatorio determinista: mismo resultado en cada frame/render. */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
