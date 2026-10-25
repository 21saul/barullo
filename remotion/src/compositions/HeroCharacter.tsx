import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { Backdrop, Bloom, SparkleField } from '../components/Art';
import { CHARACTER_VIEWBOX, Character } from '../components/Character';
import { C } from '../lib/tokens';

export const CHARACTER_SECONDS = 8;

/** Franja del lienzo del personaje que se ve: de la punta de los pinchos a la gargantilla. */
const CROP: [number, number] = [-40, 1060];

/**
 * Héroe con personaje, bucle perfecto. La cabeza está quieta: solo se mueven
 * el reflejo cromado, el parpadeo, las gotas, los destellos y el bloom, todo
 * lento. Un componente para 3:2 (móvil) y 16:9 (escritorio).
 */
export const HeroCharacter: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const t = frame / durationInFrames;

  const charH = height;
  const charW = (charH * CHARACTER_VIEWBOX.width) / CROP[1];
  const cx = width / 2;
  const unit = height / 720;

  const sparkles: Array<[number, number, number]> = [
    [cx - charW * 0.62, height * 0.22, 30],
    [cx + charW * 0.6, height * 0.3, 40],
    [cx - charW * 0.55, height * 0.72, 26],
    [cx + charW * 0.66, height * 0.78, 30],
    [cx + charW * 0.95, height * 0.12, 22],
    [cx - charW * 0.95, height * 0.5, 22],
  ].map(([x, y, s]) => [x, y, s * unit]);

  return (
    <AbsoluteFill style={{ background: C.void, overflow: 'hidden' }}>
      <Backdrop cy={45} />
      <Bloom t={t} x={cx} y={height * 0.42} radius={charW * 0.75} intensity={0.85} />
      <AbsoluteFill style={{ alignItems: 'center' }}>
        <Character t={t} width={charW} height={charH} crop={CROP} />
      </AbsoluteFill>
      <SparkleField t={t} points={sparkles} seed={31} />
    </AbsoluteFill>
  );
};
