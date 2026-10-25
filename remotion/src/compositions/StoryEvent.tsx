import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { Backdrop, Bloom, Grain, SparkleField } from '../components/Art';
import { ChromeText } from '../components/ChromeText';
import { ChromeHeading, FlyerCard, Lineup, Pill, PriceBadge, Scribble, useEnter } from '../components/EventBits';
import { EventProps, formatDate } from '../lib/event';
import { loadFonts } from '../lib/fonts';
import { C } from '../lib/tokens';

loadFonts();

export const STORY_SECONDS = 10;

// Zonas que tapa la interfaz de Instagram Stories (cabecera y caja de respuesta).
const SAFE_TOP = 220;
const SAFE_BOTTOM = 330;
const SIDE = 80;

/** Reflejo que barre cada `every` frames a partir de `start`. */
const sweepAt = (frame: number, start: number, every: number, length: number) =>
  frame < start ? 0 : Math.min(1, ((frame - start) % every) / length);

export const StoryEvent: React.FC<EventProps> = ({ title, date, lineup, room, priceFrom, flyerSrc }) => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const t = frame / durationInFrames;
  const inner = width - SIDE * 2;

  // Medidas que dependen del contenido: el flyer se queda con lo que sobre.
  const titleSize = title.length <= 16 ? 132 : title.length <= 30 ? 112 : 92;
  const titleLines = Math.ceil((title.length * titleSize * 0.47) / inner);
  const lineupSize = lineup.length <= 2 ? 54 : lineup.length <= 4 ? 44 : 36;
  const gap = 34;
  const used =
    120 + // cabecera
    titleLines * titleSize * 1.04 +
    96 + // píldoras
    lineup.length * lineupSize * 1.3 +
    gap * 4;
  const cardH = Math.max(380, Math.min(760, height - SAFE_TOP - SAFE_BOTTOM - used));

  const fade = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const head = useEnter(4);
  const card = useEnter(8, 11);
  const badge = useEnter(20, 9);
  const heading = useEnter(24);
  const pills = useEnter(32);

  return (
    <AbsoluteFill style={{ background: C.void, overflow: 'hidden' }}>
      <Backdrop cy={40} />
      <AbsoluteFill style={{ opacity: fade }}>
        <Bloom t={t} x={width / 2} y={SAFE_TOP + 120 + cardH / 2} radius={640} />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          padding: `${SAFE_TOP}px ${SIDE}px ${SAFE_BOTTOM}px`,
          display: 'flex',
          flexDirection: 'column',
          gap,
        }}
      >
        <div
          style={{
            height: 120,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            opacity: head,
            transform: `translateY(${interpolate(head, [0, 1], [-40, 0])}px)`,
          }}
        >
          <ChromeText text="BARULLO" width={400} fontSize={150} t={t} liquid={0.6} style={{ marginLeft: -40 }} />
          <Scribble text="vigo ✦" fontSize={56} />
        </div>

        <div style={{ position: 'relative', alignSelf: 'center' }}>
          <FlyerCard
            src={flyerSrc}
            width={inner}
            height={cardH}
            t={t}
            sweep={sweepAt(frame, 30, 120, 40)}
            style={{
              opacity: Math.min(1, card * 1.5),
              transform: `scale(${interpolate(card, [0, 1], [0.85, 1])}) rotate(${interpolate(card, [0, 1], [-9, -2.5])}deg)`,
            }}
          />
          <div
            style={{
              position: 'absolute',
              right: -60,
              top: -40,
              transform: `scale(${badge}) rotate(${interpolate(badge, [0, 1], [-120, 0])}deg)`,
            }}
          >
            <PriceBadge price={priceFrom} size={270} t={t} />
          </div>
        </div>

        <div style={{ opacity: heading, transform: `translateY(${interpolate(heading, [0, 1], [50, 0])}px)` }}>
          <ChromeHeading text={title} fontSize={titleSize} sweep={sweepAt(frame, 40, 120, 45)} />
        </div>

        <div
          style={{
            display: 'flex',
            gap: 18,
            flexWrap: 'wrap',
            opacity: pills,
            transform: `translateY(${interpolate(pills, [0, 1], [30, 0])}px)`,
          }}
        >
          <Pill fontSize={38}>{formatDate(date)}</Pill>
          {room ? (
            <Pill fontSize={38} tone="ghost">
              {room.toUpperCase()}
            </Pill>
          ) : null}
        </div>

        <Lineup lineup={lineup} fontSize={lineupSize} delay={38} />
      </AbsoluteFill>

      <SparkleField
        t={t}
        seed={11}
        points={[
          [120, 300, 40],
          [960, 760, 52],
          [140, 1180, 34],
          [930, 1420, 44],
          [600, 250, 26],
        ]}
      />
      <Grain opacity={0.05} />
    </AbsoluteFill>
  );
};
