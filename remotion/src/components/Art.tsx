import React from 'react';
import { AbsoluteFill } from 'remotion';
import { C, osc, oscCos, pulse, rand, twinkle } from '../lib/tokens';
import { useSvgId } from '../lib/useSvgId';

/**
 * Piezas visuales compartidas. Todas reciben `t` (fase 0..1 del bucle) y sólo
 * usan osciladores con ciclos enteros, así que t=0 y t=1 dan el mismo frame.
 */

/** Fondo void con viñeta midnight: nunca negro puro. */
export const Backdrop: React.FC<{ cx?: number; cy?: number }> = ({
  cx = 50,
  cy = 45,
}) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(120% 80% at ${cx}% ${cy}%, ${C.midnight} 0%, ${C.void} 70%)`,
    }}
  />
);

/** Bloom: dos halos (bubblegum + violet) que orbitan alrededor de un punto. */
export const Bloom: React.FC<{
  t: number;
  x: number;
  y: number;
  radius: number;
  intensity?: number;
}> = ({ t, x, y, radius, intensity = 1 }) => {
  const orbit = radius * 0.18;
  const blobs = [
    { color: C.bubblegum, dx: osc(t) * orbit, dy: oscCos(t) * orbit * 0.6, r: radius, a: 0.55 },
    { color: C.violet, dx: -osc(t, 1, 0.3) * orbit, dy: -oscCos(t, 1, 0.3) * orbit, r: radius * 1.15, a: 0.6 },
    { color: C.blood, dx: oscCos(t, 2) * orbit * 0.5, dy: osc(t, 1) * orbit * 0.4, r: radius * 0.5, a: 0.18 },
  ];
  return (
    <AbsoluteFill style={{ mixBlendMode: 'screen' }}>
      {blobs.map((b, i) => {
        const r = b.r * (0.94 + 0.06 * pulse(t, 2, i * 0.25));
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x + b.dx - r,
              top: y + b.dy - r,
              width: r * 2,
              height: r * 2,
              borderRadius: '50%',
              opacity: b.a * intensity,
              background: `radial-gradient(circle, ${b.color} 0%, ${b.color}88 28%, ${b.color}00 68%)`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/**
 * Corona de pinchos cromados (ref-04). Gira exactamente 1/N de vuelta por
 * bucle: como todos los pinchos son iguales dos a dos, el último frame
 * coincide con el primero.
 */
export const SpikeCrown: React.FC<{
  t: number;
  cx: number;
  cy: number;
  inner: number;
  length: number;
  count?: number;
  width?: number;
}> = ({ t, cx, cy, inner, length, count = 14, width = 46 }) => {
  const id = useSvgId('spike');
  // Pares largo/corto: el periodo del patrón es 2 pinchos.
  const step = 360 / count;
  const rotation = t * step * 2;
  return (
    <svg style={{ position: 'absolute', inset: 0 }} width="100%" height="100%">
      <defs>
        <linearGradient id={id} x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#3A3150" />
          <stop offset="0.28" stopColor={C.chrome3} />
          <stop offset="0.46" stopColor={C.chrome1} />
          <stop offset="0.6" stopColor={C.chrome2} />
          <stop offset="0.82" stopColor="#5B4F78" />
          <stop offset="1" stopColor="#FFB8EE" />
        </linearGradient>
      </defs>
      <g transform={`translate(${cx} ${cy}) rotate(${rotation})`}>
        {Array.from({ length: count }, (_, i) => {
          const long = i % 2 === 0;
          const len = length * (long ? 1 : 0.68);
          const w = width * (long ? 1 : 0.8);
          return (
            <g key={i} transform={`rotate(${i * step})`}>
              <path
                d={`M ${-w / 2} ${-inner + 20} C ${-w * 0.42} ${-inner - len * 0.45} ${-w * 0.08} ${-inner - len * 0.85} 0 ${-inner - len} C ${w * 0.08} ${-inner - len * 0.85} ${w * 0.42} ${-inner - len * 0.45} ${w / 2} ${-inner + 20} Z`}
                stroke="#1A0C26"
                strokeWidth={3}
                fill={`url(#${id})`}
              />
            </g>
          );
        })}
      </g>
    </svg>
  );
};

/** Esfera glossy rosa chicle con brillo especular y reflejo de borde. */
export const GlossOrb: React.FC<{
  t: number;
  cx: number;
  cy: number;
  r: number;
  hue?: 'bubblegum' | 'violet' | 'chrome';
}> = ({ t, cx, cy, r, hue = 'bubblegum' }) => {
  const id = useSvgId('orb');
  const stops =
    hue === 'chrome'
      ? [C.chrome1, C.chrome2, C.chrome3, '#2B2140']
      : hue === 'violet'
        ? ['#E3D6FF', C.iris, C.violet, '#2A0D5C']
        : ['#FFE3F8', C.bubblegum, '#B21CA0', '#3B0A3A'];
  const hx = -0.32 + 0.05 * osc(t);
  const hy = -0.38 + 0.03 * oscCos(t);
  return (
    <svg
      style={{ position: 'absolute', left: cx - r, top: cy - r, overflow: 'visible' }}
      width={r * 2}
      height={r * 2}
      viewBox="-1 -1 2 2"
    >
      <defs>
        <radialGradient id={`${id}-body`} cx={0.38 + hx * 0.2} cy={0.32 + hy * 0.2} r="0.75">
          <stop offset="0" stopColor={stops[0]} />
          <stop offset="0.35" stopColor={stops[1]} />
          <stop offset="0.8" stopColor={stops[2]} />
          <stop offset="1" stopColor={stops[3]} />
        </radialGradient>
        <radialGradient id={`${id}-rim`} cx="0.5" cy="0.5" r="0.5">
          <stop offset="0.82" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.97" stopColor={C.iris} stopOpacity="0.55" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle r="1" fill={`url(#${id}-body)`} />
      <circle r="1" fill={`url(#${id}-rim)`} />
      <ellipse cx={hx} cy={hy} rx="0.3" ry="0.17" fill="#fff" opacity="0.92" transform={`rotate(-28 ${hx} ${hy})`} />
      <circle cx={hx + 0.32} cy={hy + 0.02} r="0.055" fill="#fff" opacity="0.85" />
      <ellipse cx="0.28" cy="0.62" rx="0.36" ry="0.1" fill="#fff" opacity="0.18" transform="rotate(-20 0.28 0.62)" />
    </svg>
  );
};

/** Gotas/burbujas glossy en órbitas cerradas (Lissajous con frecuencias enteras). */
export const Bubbles: React.FC<{
  t: number;
  width: number;
  height: number;
  count?: number;
  seed?: number;
  scale?: number;
}> = ({ t, width, height, count = 7, seed = 1, scale = 1 }) => (
  <>
    {Array.from({ length: count }, (_, i) => {
      const s = seed * 100 + i;
      const bx = rand(s) * width;
      const by = rand(s + 0.5) * height;
      const r = (18 + rand(s + 0.7) * 46) * scale;
      const ax = 20 + rand(s + 0.9) * 40;
      const ay = 30 + rand(s + 1.3) * 60;
      const ph = rand(s + 2.1);
      const hues = ['bubblegum', 'violet', 'chrome'] as const;
      return (
        <GlossOrb
          key={i}
          t={(t + ph) % 1}
          cx={bx + osc(t, 1, ph) * ax}
          cy={by + osc(t, 2, ph) * ay * 0.5 + oscCos(t, 1, ph) * ay * 0.5}
          r={r}
          hue={hues[i % 3]}
        />
      );
    })}
  </>
);

/** Destello ✦ de cuatro puntas con halo. */
export const Sparkle: React.FC<{
  x: number;
  y: number;
  size: number;
  power: number;
  color?: string;
  rotate?: number;
}> = ({ x, y, size, power, color = C.bubblegum, rotate = 0 }) => {
  if (power < 0.01) return null;
  const s = size * (0.35 + 0.65 * power);
  return (
    <svg
      style={{
        position: 'absolute',
        left: x - s,
        top: y - s,
        overflow: 'visible',
        opacity: Math.min(1, power * 1.4),
        filter: `drop-shadow(0 0 ${s * 0.25}px ${color})`,
      }}
      width={s * 2}
      height={s * 2}
      viewBox="-1 -1 2 2"
    >
      <path
        transform={`rotate(${rotate})`}
        d="M0,-1 C0.1,-0.1 0.1,-0.1 1,0 C0.1,0.1 0.1,0.1 0,1 C-0.1,0.1 -0.1,0.1 -1,0 C-0.1,-0.1 -0.1,-0.1 0,-1 Z"
        fill={C.milk}
      />
    </svg>
  );
};

/** Campo de destellos: con moderación, cada uno parpadea 1–2 veces por bucle. */
export const SparkleField: React.FC<{
  t: number;
  points: Array<[x: number, y: number, size: number]>;
  seed?: number;
  /** Halo blanco en vez de chicle/violeta (versión acromática). */
  mono?: boolean;
}> = ({ t, points, seed = 3, mono = false }) => (
  <>
    {points.map(([x, y, size], i) => {
      const cycles = 1 + Math.floor(rand(seed + i) * 2);
      const power = twinkle(t, cycles, rand(seed + i * 1.7), 4);
      return (
        <Sparkle
          key={i}
          x={x}
          y={y}
          size={size}
          power={power}
          rotate={power * 25}
          color={mono ? '#ffffff' : i % 2 ? C.violet : C.bubblegum}
        />
      );
    })}
  </>
);

/** Grano fino estático (mismo en todos los frames: barato de comprimir). */
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.06 }) => {
  const id = useSvgId('grain');
  return (
    <svg style={{ position: 'absolute', inset: 0, opacity, mixBlendMode: 'overlay' }} width="100%" height="100%">
      <filter id={id}>
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <rect width="100%" height="100%" filter={`url(#${id})`} />
    </svg>
  );
};
