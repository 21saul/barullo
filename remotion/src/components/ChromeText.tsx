import React from 'react';
import { C, FONT_DISPLAY, osc, oscCos, pulse } from '../lib/tokens';
import { useSvgId } from '../lib/useSvgId';

/** Altura de mayúsculas de Anton en em (medida en render). */
const CAP = 0.72;

export type Drip = { at: number; width: number; length: number; phase: number };

/**
 * Texto en cromo líquido, todo en SVG (sin WebGL):
 *  - extrusión violeta + contorno oscuro → volumen "inflado"
 *  - gradiente plata con horizonte oscuro y reflejo rosa (cromo hyperpop)
 *  - feSpecularLighting con una luz que orbita → brillo de relieve
 *  - reflejo diagonal que barre una vez por bucle
 *  - feDisplacementMap con el ruido desplazado en círculo → ondulación
 *    líquida que cierra el bucle (el offset vuelve a su origen)
 *  - gotas cromadas que cuelgan de las letras
 *
 * `t` = fase 0..1. Sin `t` (plantillas) se puede pasar una fase cualquiera.
 */
export const ChromeText: React.FC<{
  text: string;
  /** Ancho final del texto en px (se fuerza con textLength). */
  width: number;
  fontSize: number;
  t: number;
  liquid?: number;
  /** Progreso 0..1 del barrido de brillo; por defecto pasa una vez por bucle y descansa. */
  sweep?: number;
  drips?: Drip[];
  extrude?: number;
  style?: React.CSSProperties;
}> = ({ text, width, fontSize, t, liquid = 1, sweep, drips = [], extrude, style }) => {
  const id = useSvgId('chrome');
  const pad = fontSize * 0.25;
  const cap = fontSize * CAP;
  const depth = extrude ?? fontSize * 0.055;
  const maxDrip = drips.reduce((m, d) => Math.max(m, d.length), 0);
  const W = width + pad * 2;
  const H = cap + pad * 2 + depth + maxDrip;
  const x = W / 2;
  const top = pad;
  const base = pad + cap;

  // Luz rasante que da una vuelta completa por bucle: sólo brillan los cantos.
  const lightAz = 225 + 360 * t;

  // Barrido: de fuera a fuera; en t=0 y t=1 la banda está fuera de cuadro.
  const s = sweep ?? Math.min(1, Math.max(0, (t - 0.12) / 0.45));
  const band = width * 0.35;
  const sweepX = -band * 2 + s * (W + band * 4);

  // Ruido desplazado en círculo: mismo campo en t=0 y t=1.
  const r = fontSize * 0.5;
  const ndx = oscCos(t) * r - r;
  const ndy = osc(t) * r;
  const dispScale = fontSize * 0.05 * liquid * (0.7 + 0.3 * pulse(t, 2));

  const textProps = {
    x,
    y: base,
    textAnchor: 'middle' as const,
    fontFamily: FONT_DISPLAY,
    fontSize,
    textLength: width,
    lengthAdjust: 'spacingAndGlyphs' as const,
  };

  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ overflow: 'visible', ...style }}>
      <defs>
        <linearGradient id={`${id}-fill`} gradientUnits="userSpaceOnUse" x1="0" x2="0" y1={top} y2={base}>
          <stop offset="0" stopColor={C.chrome1} />
          <stop offset="0.3" stopColor={C.chrome2} />
          <stop offset="0.47" stopColor={C.chrome3} />
          <stop offset="0.5" stopColor="#2E2145" />
          <stop offset="0.56" stopColor="#8E5AD9" />
          <stop offset="0.68" stopColor="#FF9BE6" />
          <stop offset="0.86" stopColor={C.milk} />
          <stop offset="1" stopColor={C.iris} />
        </linearGradient>
        <linearGradient id={`${id}-side`} gradientUnits="userSpaceOnUse" x1="0" x2="0" y1={top} y2={base + depth}>
          <stop offset="0" stopColor={C.violet} />
          <stop offset="1" stopColor="#1E0838" />
        </linearGradient>
        <linearGradient
          id={`${id}-sweep`}
          gradientUnits="userSpaceOnUse"
          x1={sweepX - band}
          y1={top}
          x2={sweepX + band}
          y2={base}
        >
          <stop offset="0" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.45" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.5" stopColor="#fff" stopOpacity="0.95" />
          <stop offset="0.56" stopColor={C.bubblegum} stopOpacity="0.25" />
          <stop offset="0.62" stopColor="#fff" stopOpacity="0" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
        <linearGradient id={`${id}-drip`} x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#3A2A55" />
          <stop offset="0.3" stopColor={C.chrome2} />
          <stop offset="0.45" stopColor={C.chrome1} />
          <stop offset="0.75" stopColor="#B07BE8" />
          <stop offset="1" stopColor="#2E2145" />
        </linearGradient>

        <filter id={`${id}-puff`} x="-5%" y="-20%" width="110%" height="140%">
          <feGaussianBlur in="SourceAlpha" stdDeviation={fontSize * 0.035} result="blur" />
          <feSpecularLighting
            in="blur"
            surfaceScale={fontSize * 0.04}
            specularConstant="1.3"
            specularExponent="30"
            lightingColor="#ffffff"
            result="spec"
          >
            <feDistantLight azimuth={lightAz} elevation="38" />
          </feSpecularLighting>
          <feComposite in="spec" in2="SourceAlpha" operator="in" result="specIn" />
          <feComposite in="SourceGraphic" in2="specIn" operator="arithmetic" k1="0" k2="1" k3="0.85" k4="0" />
        </filter>

        <filter
          id={`${id}-liquid`}
          filterUnits="userSpaceOnUse"
          x={-r * 3}
          y={-r * 3}
          width={W + r * 6}
          height={H + r * 6}
        >
          <feTurbulence type="fractalNoise" baseFrequency={0.55 / fontSize} numOctaves="1" seed="3" result="noise" />
          <feOffset in="noise" dx={ndx} dy={ndy} result="moved" />
          <feDisplacementMap in="SourceGraphic" in2="moved" scale={dispScale} xChannelSelector="R" yChannelSelector="G" />
        </filter>
      </defs>

      <g filter={liquid > 0 ? `url(#${id}-liquid)` : undefined}>
        {/* Gotas detrás del texto, cuelgan de la línea base. */}
        {drips.map((d, i) => {
          const len = d.length * (0.55 + 0.45 * pulse(t, 1, d.phase));
          const dx = pad + d.at * width;
          const w = d.width;
          const y0 = base - cap * 0.2;
          const y1 = base + depth + len;
          return (
            <path
              key={i}
              d={`M ${dx - w * 1.2} ${y0} C ${dx - w * 0.5} ${y0 + cap * 0.1} ${dx - w * 0.3} ${y1 - w * 1.6} ${dx - w * 0.62} ${y1 - w * 0.2} A ${w * 0.62} ${w * 0.62} 0 1 0 ${dx + w * 0.62} ${y1 - w * 0.2} C ${dx + w * 0.3} ${y1 - w * 1.6} ${dx + w * 0.5} ${y0 + cap * 0.1} ${dx + w * 1.2} ${y0} Z`}
              fill={`url(#${id}-drip)`}
              stroke="#1A0C26"
              strokeWidth={fontSize * 0.012}
            />
          );
        })}

        {/* Extrusión: copias desplazadas hacia abajo. */}
        {Array.from({ length: 6 }, (_, i) => (
          <text key={i} {...textProps} y={base + (depth * (6 - i)) / 6} fill={`url(#${id}-side)`}>
            {text}
          </text>
        ))}
        <text {...textProps} y={base + depth} fill="none" stroke="#12061C" strokeWidth={fontSize * 0.05} strokeLinejoin="round">
          {text}
        </text>

        <text {...textProps} fill="none" stroke="#1A0C26" strokeWidth={fontSize * 0.045} strokeLinejoin="round">
          {text}
        </text>
        <g filter={`url(#${id}-puff)`}>
          <text {...textProps} fill={`url(#${id}-fill)`}>
            {text}
          </text>
        </g>
        <text {...textProps} fill={`url(#${id}-sweep)`} style={{ mixBlendMode: 'screen' }}>
          {text}
        </text>
      </g>
    </svg>
  );
};
