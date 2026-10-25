// Paleta de bocetos/DIRECCION-VISUAL.md
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

export const FPS = 30;

// Fase normalizada 0..2π del bucle. Todo movimiento usa sin/cos de múltiplos
// enteros de esta fase, así el último frame encadena exacto con el primero.
export const loopPhase = (frame: number, durationInFrames: number) =>
  (frame / durationInFrames) * Math.PI * 2;
