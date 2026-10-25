import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { Backdrop, Bloom, Bubbles, GlossOrb, Grain, SparkleField, SpikeCrown } from '../components/Art';
import { ChromeText, Drip } from '../components/ChromeText';
import { loadFonts } from '../lib/fonts';
import { C, FONT_UI, osc } from '../lib/tokens';

loadFonts();

export const HERO_SECONDS = 6;

const DRIPS: Drip[] = [
  { at: 0.075, width: 40, length: 120, phase: 0 },
  { at: 0.35, width: 30, length: 70, phase: 0.35 },
  { at: 0.535, width: 46, length: 160, phase: 0.6 },
  { at: 0.84, width: 34, length: 95, phase: 0.15 },
];

/**
 * Hero en bucle perfecto. Todo depende de t = frame / duración y de
 * osciladores con ciclos enteros, así que el frame N enlaza con el 0.
 * Un solo componente para vertical y horizontal: la maqueta sale de
 * width/height.
 */
export const HeroLoop: React.FC<{ grain?: boolean }> = ({ grain = true }) => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const t = frame / durationInFrames;

  const vertical = height > width;
  const unit = Math.min(width, height) / 1080;
  const cx = width / 2;
  const cy = vertical ? height * 0.46 : height * 0.47;

  const textWidth = vertical ? width * 0.86 : width * 0.62;
  const fontSize = vertical ? textWidth * 0.36 : textWidth * 0.27;
  const dripScale = fontSize / 350;

  const orbR = (vertical ? 250 : 230) * unit;
  const float = osc(t, 1) * 14 * unit;

  const sparkles: Array<[number, number, number]> = vertical
    ? [
        [0.16, 0.24, 46], [0.82, 0.3, 60], [0.88, 0.58, 38], [0.12, 0.63, 52],
        [0.7, 0.16, 30], [0.3, 0.76, 34], [0.62, 0.72, 44], [0.5, 0.12, 28],
      ].map(([x, y, s]) => [x * width, y * height, s * unit])
    : [
        [0.14, 0.22, 44], [0.86, 0.26, 56], [0.9, 0.72, 40], [0.1, 0.74, 50],
        [0.32, 0.12, 30], [0.66, 0.86, 36], [0.72, 0.12, 30],
      ].map(([x, y, s]) => [x * width, y * height, s * unit]);

  return (
    <AbsoluteFill style={{ background: C.void, overflow: 'hidden' }}>
      <Backdrop cy={(cy / height) * 100} />
      <Bloom t={t} x={cx} y={cy} radius={(vertical ? 620 : 560) * unit} />

      <SpikeCrown
        t={t}
        cx={cx}
        cy={cy + float}
        inner={orbR * 0.82}
        length={(vertical ? 300 : 240) * unit}
        width={120 * unit}
      />
      <GlossOrb t={t} cx={cx} cy={cy + float} r={orbR} />

      <Bubbles t={t} width={width} height={height} count={vertical ? 7 : 8} seed={vertical ? 2 : 5} scale={unit} />

      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          transform: `translateY(${cy - height / 2 + float * 0.6}px) rotate(${-4 + osc(t) * 1.2}deg)`,
        }}
      >
        <ChromeText
          text="BARULLO"
          width={textWidth}
          fontSize={fontSize}
          t={t}
          drips={DRIPS.map((d) => ({ ...d, width: d.width * dripScale, length: d.length * dripScale }))}
          style={{ marginTop: fontSize * 0.35 }}
        />
      </AbsoluteFill>

      <SparkleField t={t} points={sparkles} />

      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: vertical ? height * 0.12 : height * 0.08,
          textAlign: 'center',
          fontFamily: FONT_UI,
          fontWeight: 600,
          fontSize: (vertical ? 40 : 34) * unit,
          letterSpacing: '0.42em',
          color: C.iris,
          textShadow: `0 0 ${24 * unit}px ${C.violet}`,
          paddingLeft: '0.42em',
        }}
      >
        CLUB · VIGO
      </div>

      {grain ? <Grain opacity={0.05} /> : null}
    </AbsoluteFill>
  );
};
