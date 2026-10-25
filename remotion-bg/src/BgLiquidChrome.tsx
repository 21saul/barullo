import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, loopPhase} from './tokens';

// Cromo de horizonte (como el wordmark de hero-poster.jpg) en bandas que
// bajan despacio: suelo noche → violeta → chicle → leche, cielo plata que se
// oscurece hacia el siguiente horizonte, filo duro con brillo especular.
// Los horizontes son paths vectoriales (filo nítido). Su ondulación depende
// sólo de (x, posición vertical, fase del bucle), así que cuando cada banda
// baja un periodo ocupa exactamente la forma de la siguiente: bucle perfecto.
const SAMPLES = 96;

// Suelo (bajo el horizonte) → cielo (hasta el siguiente horizonte)
const STOPS: [number, string][] = [
  [0.12, C.violet],
  [0.28, C.bubblegum],
  [0.4, C.iris],
  [0.48, C.milk],
  [0.56, C.chrome1],
  [0.72, C.chrome2],
  [0.88, C.chrome3],
];

const wave = (x: number, base: number, p: number, L: number, P: number) => {
  const u = (x / L) * Math.PI * 2;
  const v = (base / P) * 1.7;
  return (
    P * 0.085 * Math.sin(u * 1.0 + v + p) +
    P * 0.05 * Math.sin(u * 2.3 - v * 1.3 + p * 2 + 1.1) +
    P * 0.025 * Math.sin(u * 4.1 + v * 0.7 - p * 3 + 2.4)
  );
};

const edge = (base: number, p: number, w: number, L: number, P: number) =>
  Array.from({length: SAMPLES + 1}, (_, i) => {
    const x = -40 + ((w + 80) * i) / SAMPLES;
    return [x, base + wave(x, base, p, L, P)] as const;
  });

const pts = (e: ReadonlyArray<readonly [number, number]>) =>
  e.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' L');

export const BgLiquidChrome: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height, durationInFrames} = useVideoConfig();
  const p = loopPhase(frame, durationInFrames);
  const t = frame / durationInFrames;
  const L = Math.max(width, height);
  const P = Math.round(L * 0.4);
  const first = -2;
  const count = Math.ceil(height / P) + 3;

  const bands = Array.from({length: count}, (_, k) => {
    const i = first + k;
    const base = (i + t) * P;
    return {i, top: edge(base, p, width, L, P), bottom: edge(base + P, p, width, L, P)};
  });

  return (
    <AbsoluteFill style={{backgroundColor: C.void}}>
      <svg width={width} height={height} style={{position: 'absolute'}}>
        <defs>
          <filter id="melt" x="-10%" y="-10%" width="120%" height="120%">
            <feGaussianBlur stdDeviation={P * 0.06} />
          </filter>
          <filter id="glint" x="-10%" y="-50%" width="120%" height="200%">
            <feGaussianBlur stdDeviation={1.2} />
          </filter>
        </defs>
        {bands.map(({i, top, bottom}) => {
          // Contornos interiores: interpolan entre este horizonte y el
          // siguiente, así el color fluye con la onda en vez de ir en franjas.
          const lerp = (f: number) => top.map(([x, y], j) => [x, y + (bottom[j][1] - y) * f] as const);
          const floor = bottom.map(([x, y]) => [x, y + P * 0.4] as const);
          const outline = `M${pts(top)} L${pts([...bottom].reverse())} Z`;
          return (
            <g key={i}>
              <clipPath id={`clip${i}`}>
                <path d={outline} />
              </clipPath>
              <g clipPath={`url(#clip${i})`}>
                <path d={outline} fill={C.midnight} />
                <g filter="url(#melt)">
                  {STOPS.map(([f, color]) => (
                    <path key={f} d={`M${pts(lerp(f))} L${pts([...floor].reverse())} Z`} fill={color} />
                  ))}
                </g>
              </g>
              {/* brillo especular duro justo encima del siguiente horizonte */}
              <path
                d={`M${pts(bottom.map(([x, y]) => [x, y - 3] as const))}`}
                fill="none"
                stroke={C.chrome1}
                strokeWidth={2.5}
                filter="url(#glint)"
              />
            </g>
          );
        })}
      </svg>

      {/* Tinte violeta/chicle para que la plata no quede gris */}
      <AbsoluteFill
        style={{
          mixBlendMode: 'soft-light',
          opacity: 0.6,
          background: `linear-gradient(160deg, ${C.violet}, ${C.bubblegum} 55%, ${C.violet})`,
        }}
      />
      {/* Contraste bajo en origen: velo void; conserva el filo especular
          pero deja los blancos en torno al 40 % para que el texto mande. */}
      <AbsoluteFill style={{backgroundColor: C.void, opacity: 0.66}} />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 90% 80% at 50% 50%, transparent 40%, ${C.void}d9 100%)`,
        }}
      />
    </AbsoluteFill>
  );
};
