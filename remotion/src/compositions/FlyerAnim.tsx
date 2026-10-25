import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { Backdrop, Bloom, Grain, SparkleField } from '../components/Art';
import { ChromeText } from '../components/ChromeText';
import { ChromeHeading, FlyerCard, Lineup, Pill, PriceBadge, Scribble, useEnter } from '../components/EventBits';
import { EventProps, formatDate } from '../lib/event';
import { loadFonts } from '../lib/fonts';
import { C } from '../lib/tokens';

loadFonts();

export const FLYER_SECONDS = 8;

const sweepAt = (frame: number, start: number, every: number, length: number) =>
  frame < start ? 0 : Math.min(1, ((frame - start) % every) / length);

/** Post cuadrado para el feed: flyer a la izquierda, información a la derecha. */
export const FlyerAnim: React.FC<EventProps> = ({ title, date, lineup, room, priceFrom, flyerSrc }) => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const t = frame / durationInFrames;

  const M = 64;
  const cardW = 440;
  const cardH = 600;
  const colX = M + cardW + 56;
  const colW = width - colX - M;

  const titleSize = title.length <= 16 ? 96 : title.length <= 30 ? 80 : 64;
  const lineupSize = lineup.length <= 2 ? 40 : lineup.length <= 4 ? 34 : 28;

  const fade = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const head = useEnter(2);
  const card = useEnter(6, 11);
  const badge = useEnter(18, 9);
  const heading = useEnter(16);
  const pills = useEnter(26);

  return (
    <AbsoluteFill style={{ background: C.void, overflow: 'hidden' }}>
      <Backdrop cx={30} cy={55} />
      <AbsoluteFill style={{ opacity: fade }}>
        <Bloom t={t} x={M + cardW / 2} y={height * 0.58} radius={520} />
      </AbsoluteFill>

      <div
        style={{
          position: 'absolute',
          left: M - 34,
          top: 30,
          opacity: head,
          transform: `translateY(${interpolate(head, [0, 1], [-30, 0])}px)`,
        }}
      >
        <ChromeText text="BARULLO" width={360} fontSize={132} t={t} liquid={0.6} />
      </div>
      <Scribble text="vigo ✦" fontSize={50} style={{ position: 'absolute', right: M, top: 90, opacity: head }} />

      <div style={{ position: 'absolute', left: M, top: 250 }}>
        <FlyerCard
          src={flyerSrc}
          width={cardW}
          height={cardH}
          t={t}
          sweep={sweepAt(frame, 24, 120, 40)}
          style={{
            opacity: Math.min(1, card * 1.5),
            transform: `scale(${interpolate(card, [0, 1], [0.85, 1])}) rotate(${interpolate(card, [0, 1], [-10, -3])}deg)`,
          }}
        />
        <div
          style={{
            position: 'absolute',
            left: -50,
            bottom: -70,
            transform: `scale(${badge}) rotate(${interpolate(badge, [0, 1], [-120, 0])}deg)`,
          }}
        >
          <PriceBadge price={priceFrom} size={230} t={t} />
        </div>
      </div>

      <div
        style={{
          position: 'absolute',
          left: colX,
          top: 230,
          width: colW,
          bottom: M,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          gap: 30,
        }}
      >
        <div style={{ opacity: heading, transform: `translateY(${interpolate(heading, [0, 1], [40, 0])}px)` }}>
          <ChromeHeading text={title} fontSize={titleSize} sweep={sweepAt(frame, 34, 120, 45)} />
        </div>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            gap: 14,
            opacity: pills,
            transform: `translateY(${interpolate(pills, [0, 1], [24, 0])}px)`,
          }}
        >
          <Pill fontSize={30}>{formatDate(date)}</Pill>
          {room ? (
            <Pill fontSize={26} tone="ghost">
              {room.toUpperCase()}
            </Pill>
          ) : null}
        </div>
        <Lineup lineup={lineup} fontSize={lineupSize} delay={32} />
      </div>

      <SparkleField
        t={t}
        seed={21}
        points={[
          [990, 110, 40],
          [560, 210, 28],
          [80, 930, 36],
          [1000, 990, 30],
        ]}
      />
      <Grain opacity={0.05} />
    </AbsoluteFill>
  );
};
