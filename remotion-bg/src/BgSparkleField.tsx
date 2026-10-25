import React from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, loopPhase} from './tokens';

// ✦ de 4 puntas con curvas cóncavas
const STAR = 'M0,-1 C0.03,-0.12 0.12,-0.03 1,0 C0.12,0.03 0.03,0.12 0,1 C-0.03,0.12 -0.12,0.03 -1,0 C-0.12,-0.03 -0.03,-0.12 0,-1 Z';
const COUNT = 16;
const COLORS = [C.milk, C.milk, C.iris, C.bubblegum];

// Repartidos en rejilla 4x4 con jitter, para que no se amontonen.
const SPARKS = Array.from({length: COUNT}, (_, i) => ({
  x: ((i % 4) + 0.15 + random(`x${i}`) * 0.7) / 4,
  y: (Math.floor(i / 4) + 0.15 + random(`y${i}`) * 0.7) / 4,
  r: 9 + random(`r${i}`) * 14,
  phase: random(`p${i}`) * Math.PI * 2,
  color: Math.floor(random(`k${i}`) * COLORS.length),
  flare: random(`f${i}`) < 0.4, // algunos llevan rayos largos de lente
}));

// `background` sólo se usa para el póster JPG (que no admite alfa).
export const BgSparkleField: React.FC<{background?: string}> = ({background = 'transparent'}) => {
  const frame = useCurrentFrame();
  const {width, height, durationInFrames} = useVideoConfig();
  const p = loopPhase(frame, durationInFrames);

  return (
    <AbsoluteFill style={{backgroundColor: background}}>
      <svg width={width} height={height}>
        <defs>
          {COLORS.map((c, i) => (
            <radialGradient key={i} id={`halo${i}`}>
              <stop offset="0" stopColor={c} stopOpacity={0.45} />
              <stop offset="1" stopColor={c} stopOpacity={0} />
            </radialGradient>
          ))}
          <linearGradient id="ray" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0" stopColor={C.milk} stopOpacity={0} />
            <stop offset="0.5" stopColor={C.milk} stopOpacity={0.7} />
            <stop offset="1" stopColor={C.milk} stopOpacity={0} />
          </linearGradient>
        </defs>
        {SPARKS.map((s, i) => {
          // un destello por bucle: casi siempre apagado, aparece y se va
          const w = 0.5 + 0.5 * Math.sin(p + s.phase);
          const t = Math.pow(w, 5);
          if (t < 0.01) return null;
          const scale = s.r * (0.3 + 0.7 * t);
          return (
            <g
              key={i}
              transform={`translate(${s.x * width},${s.y * height})`}
              opacity={0.55 * t}
            >
              {s.flare && (
                <g transform={`scale(${scale})`}>
                  <rect x={-4.5} y={-0.025} width={9} height={0.05} fill="url(#ray)" />
                  <rect x={-2.2} y={-0.02} width={4.4} height={0.04} fill="url(#ray)" transform="rotate(90)" />
                </g>
              )}
              <g transform={`rotate(${30 * t}) scale(${scale})`}>
                <circle r={0.8} fill={`url(#halo${s.color})`} />
                <path d={STAR} fill={COLORS[s.color]} />
              </g>
            </g>
          );
        })}
      </svg>
    </AbsoluteFill>
  );
};
