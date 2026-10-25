import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, loopPhase} from './tokens';

type Bloom = {
  color: string;
  size: number; // fracción del lado mayor
  x: number; // centro en %
  y: number;
  ax: number; // amplitud en %
  ay: number;
  fx: number; // ciclos enteros por bucle
  fy: number;
  phase: number;
  alpha: number;
};

const BLOOMS: Bloom[] = [
  {color: C.bubblegum, size: 0.75, x: 28, y: 30, ax: 14, ay: 10, fx: 1, fy: 1, phase: 0, alpha: 0.42},
  {color: C.violet, size: 0.95, x: 72, y: 66, ax: 16, ay: 12, fx: 1, fy: 2, phase: 2.1, alpha: 0.55},
  {color: C.violet, size: 0.6, x: 20, y: 80, ax: 10, ay: 8, fx: 2, fy: 1, phase: 4.0, alpha: 0.35},
  {color: C.bubblegum, size: 0.5, x: 80, y: 18, ax: 9, ay: 12, fx: 1, fy: 1, phase: 1.2, alpha: 0.28},
  {color: C.iris, size: 0.45, x: 50, y: 50, ax: 18, ay: 14, fx: 1, fy: 1, phase: 3.3, alpha: 0.12},
];

const hexA = (hex: string, a: number) =>
  hex + Math.round(a * 255).toString(16).padStart(2, '0');

export const BgBloomDrift: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height, durationInFrames} = useVideoConfig();
  const p = loopPhase(frame, durationInFrames);
  const L = Math.max(width, height);

  return (
    <AbsoluteFill style={{backgroundColor: C.void}}>
      {BLOOMS.map((b, i) => {
        const cx = (b.x + b.ax * Math.sin(p * b.fx + b.phase)) / 100 * width;
        const cy = (b.y + b.ay * Math.cos(p * b.fy + b.phase)) / 100 * height;
        const breathe = 1 + 0.08 * Math.sin(p + b.phase * 1.7);
        const s = b.size * L * breathe;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: cx - s / 2,
              top: cy - s / 2,
              width: s,
              height: s,
              borderRadius: '50%',
              mixBlendMode: 'screen',
              background: `radial-gradient(circle closest-side, ${hexA(b.color, b.alpha)} 0%, ${hexA(b.color, b.alpha * 0.45)} 40%, ${hexA(b.color, 0)} 100%)`,
            }}
          />
        );
      })}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 90% 80% at 50% 50%, transparent 40%, ${hexA(C.void, 0.85)} 100%)`,
        }}
      />
    </AbsoluteFill>
  );
};
