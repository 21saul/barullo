import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { formatPrice, resolveFlyer, splitArtist } from '../lib/event';
import { C, FONT_DISPLAY, FONT_SCRIBBLE, FONT_UI, SQUIRCLE, osc } from '../lib/tokens';
import { GlossOrb, SpikeCrown } from './Art';

/** Entrada con muelle a partir de `delay` frames (0..1, con un pelín de rebote). */
export const useEnter = (delay: number, damping = 13) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping, mass: 0.8 } });
};

const CHROME_GRADIENT = `linear-gradient(180deg, ${C.chrome1} 0%, ${C.chrome2} 30%, ${C.chrome3} 47%, #2E2145 50%, #8E5AD9 56%, #FF9BE6 68%, ${C.milk} 86%, ${C.iris} 100%)`;

/**
 * Titular cromado en HTML (background-clip:text), para textos largos que
 * tienen que partir línea. `box-decoration-break: clone` repite el gradiente
 * en cada línea, así cada una tiene su propio horizonte cromado.
 */
export const ChromeHeading: React.FC<{
  text: string;
  fontSize: number;
  /** 0..1, posición del reflejo que barre. */
  sweep: number;
  align?: 'left' | 'center';
  style?: React.CSSProperties;
}> = ({ text, fontSize, sweep, align = 'left', style }) => {
  const p = -30 + sweep * 160;
  return (
    <div
      style={{
        fontFamily: FONT_DISPLAY,
        fontSize,
        lineHeight: 1.04,
        textTransform: 'uppercase',
        textAlign: align,
        filter: `drop-shadow(0 ${fontSize * 0.055}px 0 #1E0838) drop-shadow(0 0 ${fontSize * 0.28}px ${C.bubblegum}70)`,
        ...style,
      }}
    >
      <span
        style={{
          backgroundImage: `linear-gradient(105deg, transparent ${p - 7}%, rgba(255,255,255,0.95) ${p}%, ${C.bubblegum}40 ${p + 3}%, transparent ${p + 8}%), ${CHROME_GRADIENT}`,
          WebkitBackgroundClip: 'text',
          backgroundClip: 'text',
          color: 'transparent',
          WebkitBoxDecorationBreak: 'clone',
          boxDecorationBreak: 'clone',
          padding: '0 0.03em',
        }}
      >
        {text}
      </span>
    </div>
  );
};

/** Píldora squircle (fecha, sala). */
export const Pill: React.FC<{
  children: React.ReactNode;
  fontSize: number;
  tone?: 'bubblegum' | 'ghost' | 'blood';
  style?: React.CSSProperties;
}> = ({ children, fontSize, tone = 'bubblegum', style }) => {
  const solid = tone !== 'ghost';
  const bg = tone === 'blood' ? C.blood : C.bubblegum;
  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: fontSize * 0.4,
        padding: `${fontSize * 0.42}px ${fontSize * 0.8}px`,
        borderRadius: SQUIRCLE,
        fontFamily: FONT_UI,
        fontWeight: 700,
        fontSize,
        letterSpacing: '0.06em',
        color: solid ? C.void : C.milk,
        background: solid
          ? `linear-gradient(180deg, #FFB3EE 0%, ${bg} 45%, ${tone === 'blood' ? '#9E0029' : '#C2189F'} 100%)`
          : `${C.midnight}CC`,
        border: solid ? 'none' : `2px solid ${C.iris}66`,
        boxShadow: solid
          ? `0 0 ${fontSize * 1.2}px ${bg}88, inset 0 ${fontSize * 0.12}px 0 rgba(255,255,255,0.55), inset 0 -${fontSize * 0.1}px 0 rgba(60,0,50,0.35)`
          : `0 0 ${fontSize}px ${C.violet}55`,
        whiteSpace: 'nowrap',
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Insignia de precio: orbe chicle con corona de pinchos cromados (cute-agresivo). */
export const PriceBadge: React.FC<{ price: number; size: number; t: number }> = ({ price, size, t }) => {
  const label = formatPrice(price);
  const free = price <= 0;
  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <SpikeCrown t={t} cx={size / 2} cy={size / 2} inner={size * 0.3} length={size * 0.2} width={size * 0.13} count={12} />
      <GlossOrb t={t} cx={size / 2} cy={size / 2} r={size * 0.33} />
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          fontFamily: FONT_DISPLAY,
          color: C.void,
          textAlign: 'center',
          lineHeight: 0.95,
          transform: `rotate(${-8 + osc(t) * 3}deg)`,
        }}
      >
        {free ? null : <div style={{ fontFamily: FONT_UI, fontWeight: 700, fontSize: size * 0.085, letterSpacing: '0.12em' }}>DESDE</div>}
        <div style={{ fontSize: size * (label.length > 5 ? 0.15 : 0.19) }}>{label}</div>
      </AbsoluteFill>
    </div>
  );
};

/** Flyer en tarjeta squircle con marco cromado, zoom lento y reflejo que barre. */
export const FlyerCard: React.FC<{
  src: string;
  width: number;
  height: number;
  t: number;
  sweep: number;
  style?: React.CSSProperties;
}> = ({ src, width, height, t, sweep, style }) => {
  const url = resolveFlyer(src);
  const border = 7;
  const p = -30 + sweep * 160;
  return (
    <div
      style={{
        width,
        height,
        padding: border,
        borderRadius: SQUIRCLE + border,
        background: `linear-gradient(160deg, ${C.chrome1}, ${C.chrome2} 35%, ${C.chrome3} 50%, #FF9BE6 70%, ${C.iris})`,
        boxShadow: `0 30px 80px ${C.void}, 0 0 90px ${C.violet}66`,
        ...style,
      }}
    >
      <div style={{ position: 'relative', width: '100%', height: '100%', borderRadius: SQUIRCLE, overflow: 'hidden', background: C.midnight }}>
        {url ? (
          <Img
            src={url}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transform: `scale(${1.04 + t * 0.08})`,
            }}
          />
        ) : (
          <GenerativeFlyer t={t} width={width - border * 2} height={height - border * 2} />
        )}
        {/* Tinte de marca para que cualquier foto case con la paleta. */}
        <AbsoluteFill
          style={{
            background: `linear-gradient(180deg, ${C.violet}22 0%, transparent 40%, ${C.void}AA 100%)`,
            mixBlendMode: 'multiply',
          }}
        />
        <AbsoluteFill style={{ background: `${C.bubblegum}14`, mixBlendMode: 'screen' }} />
        <AbsoluteFill
          style={{
            background: `linear-gradient(115deg, transparent ${p - 10}%, rgba(255,255,255,0.35) ${p}%, transparent ${p + 10}%)`,
          }}
        />
      </div>
    </div>
  );
};

/** Sin flyer: orbe con pinchos sobre bloom, para que la plantilla nunca salga vacía. */
const GenerativeFlyer: React.FC<{ t: number; width: number; height: number }> = ({ t, width, height }) => {
  const r = Math.min(width, height) * 0.24;
  return (
    <AbsoluteFill
      style={{ background: `radial-gradient(circle at 50% 50%, ${C.violet} 0%, ${C.midnight} 55%, ${C.void} 100%)` }}
    >
      <SpikeCrown t={t} cx={width / 2} cy={height / 2} inner={r * 0.8} length={r * 0.9} width={r * 0.42} />
      <GlossOrb t={t} cx={width / 2} cy={height / 2} r={r} />
    </AbsoluteFill>
  );
};

/** Lineup con entrada escalonada; el rol va en iris y pequeño. */
export const Lineup: React.FC<{
  lineup: string[];
  fontSize: number;
  delay: number;
  align?: 'left' | 'center';
}> = ({ lineup, fontSize, delay, align = 'left' }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: fontSize * 0.18, alignItems: align === 'center' ? 'center' : 'flex-start' }}>
      {lineup.map((line, i) => {
        const { name, role } = splitArtist(line);
        const enter = spring({ frame: frame - delay - i * 5, fps, config: { damping: 14 } });
        return (
          <div
            key={i}
            style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: fontSize * 0.35,
              flexWrap: 'wrap',
              justifyContent: align === 'center' ? 'center' : 'flex-start',
              opacity: enter,
              transform: `translateX(${interpolate(enter, [0, 1], [align === 'center' ? 0 : -60, 0])}px) translateY(${interpolate(enter, [0, 1], [24, 0])}px)`,
            }}
          >
            <span
              style={{
                fontFamily: FONT_UI,
                fontWeight: 700,
                fontSize,
                color: C.milk,
                letterSpacing: '-0.01em',
                textShadow: `0 0 ${fontSize * 0.5}px ${C.violet}`,
              }}
            >
              {name}
            </span>
            {role ? (
              <span style={{ fontFamily: FONT_UI, fontWeight: 500, fontSize: fontSize * 0.5, color: C.iris, letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                {role}
              </span>
            ) : null}
          </div>
        );
      })}
    </div>
  );
};

/** Anotación manuscrita: sólo marca, nunca se usa para leer información. */
export const Scribble: React.FC<{ text: string; fontSize: number; rotate?: number; style?: React.CSSProperties }> = ({
  text,
  fontSize,
  rotate = -8,
  style,
}) => (
  <div
    style={{
      fontFamily: FONT_SCRIBBLE,
      fontSize,
      color: C.bubblegum,
      transform: `rotate(${rotate}deg)`,
      textShadow: `0 0 ${fontSize * 0.4}px ${C.bubblegum}AA`,
      ...style,
    }}
  >
    {text}
  </div>
);
