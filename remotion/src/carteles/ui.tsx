import React from 'react';
import { cancelRender, continueRender, delayRender, Img, staticFile } from 'remotion';
import KUFI from './data/kufi.json';
import SHAPES from './data/shapes.json';

// Carteles de discoteca de Barullo Clvb (Vigo). Estructura de la plantilla R1 (fecha gigante, objeto 3D,
// logo, LINE UP, barra de datos en celdas) con el mundo nuevo: lettering kufi de la diseñadora,
// medalla «o», alfombra persa y cyborg. Los assets viven fuera del repo (--public-dir), ver README.

export const C = {
  black: '#070506',
  bone: '#F2EFE8',
  red: '#E2261C',
  orange: '#F6A43C',
  pink: '#FF4FA8',
  deep: '#B5160F',
};

/** Assets pesados (frames, texturas): servidos por bocetos/animaciones/carteles/comun/serve.py, fuera de --public-dir. */
export const ASSETS = 'http://127.0.0.1:8765/';
export const asset = (p: string) => ASSETS + p;

export const FPS = 30;
export const LOOP = 240; // 8 s
export const BPM = 120;

export type Venue = { name: string; address: string; city: string; hours: string };
export type CartelProps = {
  date: string; // '13.11'
  day: string; // 'VIERNES'
  year: string;
  genre: string;
  lineup: string[];
  venue: Venue;
  /** carpeta de frames dentro de public o '' para usar el fotograma clave fijo */
  seq?: string;
};

export const MONTHS = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'];
export const longDate = (p: CartelProps) => {
  const [d, m] = p.date.split('.');
  return `${p.day} ${+d} ${MONTHS[+m - 1]} ${p.year}`;
};

export const FONT = {
  lineup: "'Archivo', sans-serif",
  data: "'Space Mono', monospace",
  tag: "'Chakra Petch', sans-serif",
};

const FACES: [string, string, FontFaceDescriptors][] = [
  ['Archivo', 'fonts/Archivo.ttf', { weight: '100 900', stretch: '62% 125%' }],
  ['Space Mono', 'fonts/SpaceMono-Regular.ttf', { weight: '400' }],
  ['Space Mono', 'fonts/SpaceMono-Bold.ttf', { weight: '700' }],
  ['Chakra Petch', 'fonts/ChakraPetch-BoldItalic.ttf', { weight: '700', style: 'italic' }],
  ['Chakra Petch', 'fonts/ChakraPetch-SemiBoldItalic.ttf', { weight: '600', style: 'italic' }],
  ['Chakra Petch', 'fonts/ChakraPetch-Bold.ttf', { weight: '700' }],
];
let fontsStarted = false;
export const loadFonts = () => {
  if (fontsStarted || typeof document === 'undefined') return;
  fontsStarted = true;
  const h = delayRender('fuentes');
  Promise.all(FACES.map(async ([fam, file, desc]) => {
    const f = new FontFace(fam, `url(${staticFile(file)})`, desc);
    await f.load();
    document.fonts.add(f);
  })).then(() => continueRender(h)).catch((e) => cancelRender(e));
};

// ---------- ritmo ----------
/** Envolvente de bombo: subida instantánea y caída exponencial. 0..1 */
export const kick = (f: number, decay = 5) => {
  const beat = (f / FPS) * (BPM / 60);
  const ph = beat - Math.floor(beat);
  return Math.exp(-ph * decay);
};
/** fase 0..1 del bucle completo */
export const phase = (f: number, len = LOOP) => (((f % len) + len) % len) / len;
export const easeInOut = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
export const pad4 = (n: number) => String(n).padStart(4, '0');

// ---------- Kufi (fechas) ----------
const ACCENT: Record<string, string> = { 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ñ': 'N' };
type Glyph = { d?: string; w: number };
const G = KUFI as unknown as Record<string, Glyph>;
export const Kufi: React.FC<{ text: string; height: number; fill?: string; gap?: number; style?: React.CSSProperties }>
  = ({ text, height, fill = C.bone, gap = 1, style }) => {
    const u = height / 5;
    let x = 0;
    const parts: React.ReactNode[] = [];
    [...text].forEach((ch, i) => {
      const g = G[ACCENT[ch] ?? ch] ?? G[' '];
      if (g.d) parts.push(<path key={i} d={g.d} transform={`translate(${x} 0)`} />);
      x += g.w + gap;
    });
    const w = x - gap;
    return (
      <svg width={w * u} height={height} viewBox={`0 0 ${w} 5`} style={{ overflow: 'visible', display: 'block', ...style }}>
        <g fill={fill} fillRule="evenodd">{parts}</g>
      </svg>
    );
  };

// ---------- estrella de la «o» ----------
export const Star: React.FC<{ size: number; fill?: string; hole?: string | null; stroke?: string; strokeWidth?: number; style?: React.CSSProperties; children?: React.ReactNode }>
  = ({ size, fill = C.red, hole = null, stroke, strokeWidth = 0, style, children }) => (
    <div style={{ position: 'relative', width: size, height: size, flex: 'none', ...style }}>
      <svg width={size} height={size} viewBox="0 0 1000 1000" style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
        <path d={hole === null ? SHAPES.star + ' ' + SHAPES.hole : SHAPES.star} fill={fill} fillRule="evenodd" stroke={stroke} strokeWidth={strokeWidth} strokeLinejoin="round" />
        {hole && <path d={SHAPES.hole} fill={hole} />}
      </svg>
      {children && <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{children}</div>}
    </div>
  );

/** Estrella regular de 8 puntas (dos cuadrados): insignia de fecha de los carteles de la diseñadora. */
export const Octo: React.FC<{ size: number; fill: string; children?: React.ReactNode; style?: React.CSSProperties }> = ({ size, fill, children, style }) => (
  <div style={{ position: 'relative', width: size, height: size, flex: 'none', ...style }}>
    <svg width={size} height={size} viewBox="-50 -50 100 100" style={{ position: 'absolute', inset: 0 }}>
      <rect x={-35.4} y={-35.4} width={70.7} height={70.7} fill={fill} />
      <rect x={-35.4} y={-35.4} width={70.7} height={70.7} fill={fill} transform="rotate(45)" />
    </svg>
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>{children}</div>
  </div>
);

// ---------- piezas del cartel ----------
export const DateBlock: React.FC<{ p: CartelProps; W: number; h: number; ink?: string; accent?: string; shadow?: string }>
  = ({ p, W, h, ink = C.bone, accent = C.red, shadow }) => (
    <div>
      <Kufi text={p.date} height={h} fill={ink} style={shadow ? { filter: `drop-shadow(${shadow})` } : undefined} />
      <div style={{ fontFamily: FONT.data, fontWeight: 700, fontSize: W * 0.021, letterSpacing: '0.3em', color: ink, marginTop: W * 0.03, textShadow: shadow }}>{longDate(p)}</div>
      <div style={{ fontFamily: FONT.data, fontSize: W * 0.017, letterSpacing: '0.36em', color: accent, marginTop: W * 0.012, textShadow: shadow }}>{p.genre}</div>
    </div>
  );

export const Lineup: React.FC<{ p: CartelProps; W: number; size: number; ink?: string; accent?: string; shadow?: string }>
  = ({ p, W, size, ink = C.bone, accent = C.red, shadow }) => (
    <div>
      <div style={{ fontFamily: FONT.data, fontSize: W * 0.016, letterSpacing: '0.3em', color: accent, marginBottom: W * 0.014, textShadow: shadow }}>LINE UP</div>
      {p.lineup.map((n) => (
        <div key={n} style={{ fontFamily: FONT.lineup, fontWeight: 800, fontStretch: '125%', fontSize: W * size, lineHeight: 1.0, letterSpacing: '-0.01em', color: ink, whiteSpace: 'nowrap', textShadow: shadow }}>{n}</div>
      ))}
    </div>
  );

/** Barra de datos en celdas: estrella roja · sala y dirección · día y horario · fecha en bloque rojo. */
export const DataBar: React.FC<{ p: CartelProps; W: number; pad: number; bottom: number; bg?: string; ink?: string; accent?: string }>
  = ({ p, W, pad, bottom, bg = C.black, ink = C.bone, accent = C.red }) => {
    const line = `${W * 0.0016}px solid ${ink}55`;
    const cell: React.CSSProperties = { borderRight: line, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: `0 ${W * 0.018}px` };
    const mono: React.CSSProperties = { fontFamily: FONT.data, color: ink, fontSize: W * 0.0155, lineHeight: 1.35, letterSpacing: '0.06em' };
    return (
      <div style={{ position: 'absolute', left: pad, right: pad, bottom, height: W * 0.082, border: line, display: 'flex', background: `${bg}C8` }}>
        <div style={{ ...cell, width: W * 0.082, padding: 0 }}><Star size={W * 0.054} fill={accent} /></div>
        <div style={{ ...cell, flex: 1, justifyContent: 'flex-start' }}>
          <div style={mono}><b style={{ fontWeight: 700 }}>{p.venue.name}</b><br />{p.venue.address} · {p.venue.city}</div>
        </div>
        <div style={cell}><div style={{ ...mono, textAlign: 'center' }}>{p.day}<br />{p.venue.hours}</div></div>
        <div style={{ ...cell, borderRight: 'none', width: W * 0.2, background: accent }}>
          <Kufi text={p.date} height={W * 0.03} fill={bg} />
        </div>
      </div>
    );
  };

export const Grain: React.FC<{ opacity?: number; seed?: number }> = ({ opacity = 0.06, seed = 0 }) => (
  <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', mixBlendMode: 'overlay', opacity, pointerEvents: 'none' }}>
    <filter id={`g${seed}`}><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={seed} stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter>
    <rect width="100%" height="100%" filter={`url(#g${seed})`} />
  </svg>
);

/** Lettering 3D (PNG de Blender) con un brillo que lo recorre: banda diagonal enmascarada por su alfa. */
export const Lettering: React.FC<{ src: string; width: number; f: number; sweepAt?: number; sweepLen?: number; style?: React.CSSProperties }>
  = ({ src, width, f, sweepAt = 0.55, sweepLen = 0.22, style }) => {
    const u = (phase(f) - sweepAt) / sweepLen;
    const pos = u < 0 || u > 1 ? -1 : easeInOut(u);
    const url = asset(src);
    return (
      <div style={{ position: 'relative', width, ...style }}>
        <Img src={url} style={{ width, display: 'block' }} />
        {pos >= 0 && (
          <div style={{
            position: 'absolute', inset: 0, mixBlendMode: 'screen',
            WebkitMaskImage: `url(${url})`, WebkitMaskSize: '100% 100%', maskImage: `url(${url})`, maskSize: '100% 100%',
            background: `linear-gradient(105deg, transparent ${pos * 140 - 30}%, rgba(255,255,255,0.75) ${pos * 140 - 20}%, transparent ${pos * 140 - 10}%)`,
          }} />
        )}
      </div>
    );
  };

/** Destello de joya: cruz de 8 rayos finos con halo. */
export const Glint: React.FC<{ x: number; y: number; size: number; amount: number; color?: string; rot?: number }>
  = ({ x, y, size, amount, color = '#FF3B4E', rot = 0 }) => {
    if (amount < 0.01) return null;
    const s = size * (0.55 + 0.45 * amount);
    return (
      <div style={{ position: 'absolute', left: x - s / 2, top: y - s / 2, width: s, height: s, mixBlendMode: 'screen', opacity: Math.min(1, amount), pointerEvents: 'none' }}>
        <div style={{ position: 'absolute', inset: '30%', borderRadius: '50%', background: `radial-gradient(circle, ${color}cc 0%, ${color}44 40%, transparent 70%)` }} />
        <svg width={s} height={s} viewBox="-50 -50 100 100" style={{ position: 'absolute', inset: 0, transform: `rotate(${rot}deg)` }}>
          <defs>
            <radialGradient id="gl"><stop offset="0" stopColor="#fff" /><stop offset="0.25" stopColor="#FFD6DC" /><stop offset="1" stopColor={color} stopOpacity="0" /></radialGradient>
          </defs>
          {[0, 45, 90, 135].map((a, i) => (
            <path key={a} d={`M0 ${i % 2 ? -32 : -50} L1.3 0 L0 ${i % 2 ? 32 : 50} L-1.3 0 Z`} fill="url(#gl)" transform={`rotate(${a})`} />
          ))}
          <circle r={3.2} fill="#fff" />
        </svg>
      </div>
    );
  };
