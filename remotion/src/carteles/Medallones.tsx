import React from 'react';
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import { useJson } from './Medalla';
import { asset, C, CartelProps, easeInOut, FONT, Glint, Grain, Kufi, loadFonts, MONTHS, pad4, phase, Star } from './ui';

loadFonts();

// Serie MEDALLONES: cinco flyers, cada uno con un medallón del catálogo de estilos (bocetos/disenos/logo/estilos/)
// girando despacio en el centro. Estructura de la plantilla R2 URBANO (cabecera, título, etiquetas de
// género y fecha, objeto central, line up, barra de datos), con el lettering 3D a juego como título
// y un fondo del color de la gema: degradado, rayos, celosía de estrellas en hilo de oro y polvo de oro.

export type Theme = {
  name: string; // nombre del medallón, en la píldora
  bg0: string; // fondo, bordes
  bg1: string; // fondo, centro
  glow: string; // halo detrás de la medalla y destello de la gema
  accent: string; // etiqueta de género, bloque de fecha
  accentInk: string; // texto sobre accent
  gold: string; // hilo de la celosía, polvo
};

export const THEMES: Record<string, Theme> = {
  'oro-turquesa': { name: 'ORO VIEJO · TURQUESA', bg0: '#021416', bg1: '#0B5A5B', glow: '#3FE0D0', accent: '#35D2C3', accentInk: '#03211F', gold: '#E6BE78' },
  'oro-perlas': { name: 'ORO · PERLAS', bg0: '#04060E', bg1: '#173262', glow: '#9FE6EE', accent: '#9FE3EA', accentInk: '#081633', gold: '#E9C47E' },
  'oro-girih-rubi': { name: 'ORO · RUBÍ', bg0: '#160203', bg1: '#860D0A', glow: '#FF3B2E', accent: C.red, accentInk: '#1A0202', gold: '#F0BE72' },
  'oro-esmeralda': { name: 'ORO · ESMERALDA', bg0: '#02120A', bg1: '#0B5233', glow: '#35F096', accent: '#2CD487', accentInk: '#02170D', gold: '#E8C178' },
  'oro-rosa-coral': { name: 'ORO ROSA · CORAL', bg0: '#1B0311', bg1: '#8E1252', glow: '#FF6FB4', accent: C.pink, accentInk: '#2A0418', gold: '#F4B9A0' },
};

export type MedallonProps = CartelProps & { style: string; num: number; frames: boolean };

type Pts = Record<string, { gem: [number, number]; tips: [number, number][]; vis: number; sweep: number }>;

/** Caja de la letra en el PNG de engr.py (1800x864, igual en todos los estilos). */
const LBOX = { x0: 248 / 1800, x1: 1630 / 1800, y0: 194 / 864, y1: 636 / 864 };
/** Caja de la medalla en el PNG de medalla (1400x1400). */

const DAYS = (p: CartelProps) => {
  const [d, m] = p.date.split('.');
  return `${p.day} ${+d} ${MONTHS[+m - 1]}`;
};

// ---------- fondo ----------
const STAR8 = (cx: number, cy: number, r: number) => {
  const pts: string[] = [];
  for (let i = 0; i < 16; i++) {
    const a = (i * Math.PI) / 8 - Math.PI / 2;
    const rr = i % 2 ? r * 0.72 : r;
    pts.push(`${(cx + rr * Math.cos(a)).toFixed(2)},${(cy + rr * Math.sin(a)).toFixed(2)}`);
  }
  return `M${pts.join('L')}Z`;
};

/** Celosía de estrellas de 8 puntas en hilo de oro, que baja una baldosa por bucle (sin salto). */
const Lattice: React.FC<{ W: number; H: number; t: number; color: string; cy: number }> = ({ W, H, t, color, cy }) => {
  const tile = W / 7;
  const off = t * tile;
  const mask = `radial-gradient(ellipse 70% 42% at 50% ${(cy / H) * 100}%, transparent 30%, #000 75%)`;
  return (
    <svg width={W} height={H} style={{ position: 'absolute', inset: 0, opacity: 0.16, WebkitMaskImage: mask, maskImage: mask }}>
      <defs>
        <pattern id="lat" width={tile} height={tile} patternUnits="userSpaceOnUse" patternTransform={`translate(${W / 2 - tile / 2} ${off})`}>
          <path d={STAR8(tile / 2, tile / 2, tile * 0.42)} fill="none" stroke={color} strokeWidth={W * 0.0011} />
          <path d={STAR8(0, 0, tile * 0.18)} fill="none" stroke={color} strokeWidth={W * 0.0009} />
          <path d={STAR8(tile, 0, tile * 0.18)} fill="none" stroke={color} strokeWidth={W * 0.0009} />
          <path d={STAR8(0, tile, tile * 0.18)} fill="none" stroke={color} strokeWidth={W * 0.0009} />
          <path d={STAR8(tile, tile, tile * 0.18)} fill="none" stroke={color} strokeWidth={W * 0.0009} />
        </pattern>
      </defs>
      <rect width={W} height={H} fill="url(#lat)" />
    </svg>
  );
};

/** Rayos de luz detrás de la medalla: 16 rayos que giran 22.5° por bucle (vuelve a la misma imagen). */
const Rays: React.FC<{ cx: number; cy: number; R: number; t: number; color: string }> = ({ cx, cy, R, t, color }) => {
  const rot = 22.5 * t;
  const mask = 'radial-gradient(circle, #000 18%, transparent 68%)';
  return (
    <div style={{
      position: 'absolute', left: cx - R, top: cy - R, width: 2 * R, height: 2 * R, opacity: 0.2, mixBlendMode: 'screen',
      background: `repeating-conic-gradient(from ${rot}deg, ${color} 0deg 3deg, transparent 7deg 18.5deg, ${color}00 22.5deg)`,
      WebkitMaskImage: mask, maskImage: mask, filter: `blur(${R * 0.012}px)`,
    }} />
  );
};

/** Polvo de oro: motas fijas con deriva circular y parpadeo, periodo del bucle. */
const Dust: React.FC<{ W: number; H: number; t: number; color: string; n?: number }> = ({ W, H, t, color, n = 46 }) => {
  let seed = 11;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const dots = Array.from({ length: n }, () => ({ x: rnd(), y: rnd(), r: 0.4 + rnd() * 1.6, ph: rnd(), k: 1 + Math.floor(rnd() * 3), a: rnd() }));
  return (
    <svg width={W} height={H} style={{ position: 'absolute', inset: 0, mixBlendMode: 'screen' }}>
      {dots.map((d, i) => {
        const ang = 2 * Math.PI * (t + d.ph);
        const tw = Math.pow(0.5 + 0.5 * Math.sin(2 * Math.PI * (d.k * t + d.ph)), 3);
        return <circle key={i} cx={d.x * W + Math.cos(ang) * W * 0.008} cy={d.y * H + Math.sin(ang) * W * 0.012} r={d.r * W * 0.0016} fill={color} opacity={0.15 + 0.7 * tw * d.a} />;
      })}
    </svg>
  );
};

/** Destello de 4 rayos para las puntas del medallón (más fino que Glint). */
const Twinkle: React.FC<{ x: number; y: number; size: number; amount: number; color: string }> = ({ x, y, size, amount, color }) => {
  if (amount < 0.02) return null;
  const s = size * (0.5 + 0.5 * amount);
  return (
    <svg width={s} height={s} viewBox="-50 -50 100 100" style={{ position: 'absolute', left: x - s / 2, top: y - s / 2, mixBlendMode: 'screen', opacity: amount, overflow: 'visible' }}>
      <defs><radialGradient id="tw"><stop offset="0" stopColor="#fff" /><stop offset="0.3" stopColor={color} /><stop offset="1" stopColor={color} stopOpacity="0" /></radialGradient></defs>
      <circle r={14} fill="url(#tw)" opacity={0.7} />
      <path d="M0 -50 L2 0 L0 50 L-2 0 Z" fill="url(#tw)" />
      <path d="M-50 0 L0 2 L50 0 L0 -2 Z" fill="url(#tw)" />
      <path d="M0 -26 L1.2 0 L0 26 L-1.2 0 Z" fill="url(#tw)" transform="rotate(45)" />
      <path d="M0 -26 L1.2 0 L0 26 L-1.2 0 Z" fill="url(#tw)" transform="rotate(-45)" />
      <circle r={2.4} fill="#fff" />
    </svg>
  );
};

// ---------- piezas ----------
const Tag: React.FC<{ text: string; bg: string; ink: string; size: number; W: number }> = ({ text, bg, ink, size, W }) => (
  <div style={{ display: 'inline-block', background: bg, transform: 'skewX(-12deg)', padding: `${size * 0.16}px ${size * 0.7}px` }}>
    <div style={{ transform: 'skewX(12deg)', fontFamily: FONT.lineup, fontWeight: 800, fontStretch: '125%', fontSize: size, lineHeight: 1.08, color: ink, whiteSpace: 'nowrap', letterSpacing: '0.01em' }}>{text}</div>
  </div>
);

const Bar: React.FC<{ p: MedallonProps; th: Theme; W: number; pad: number; bottom: number }> = ({ p, th, W, pad, bottom }) => {
  const ink = C.bone;
  const line = `${W * 0.0016}px solid ${ink}50`;
  const h = W * 0.088;
  const cell: React.CSSProperties = { borderRight: line, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: `0 ${W * 0.018}px` };
  const mono: React.CSSProperties = { fontFamily: FONT.data, color: ink, fontSize: W * 0.0148, lineHeight: 1.4, letterSpacing: '0.05em', whiteSpace: 'nowrap' };
  return (
    <div style={{ position: 'absolute', left: pad, right: pad, bottom, height: h, border: line, display: 'flex', background: `${th.bg0}D0` }}>
      <div style={{ ...cell, width: h, padding: 0 }}><Star size={W * 0.054} fill={C.red} /></div>
      <div style={{ ...cell, width: h, padding: 0 }}>
        <Star size={W * 0.062} fill="none" hole="transparent" stroke={th.accent} strokeWidth={30}>
          <Kufi text={String(p.num).padStart(2, '0')} height={W * 0.021} fill={th.accent} />
        </Star>
      </div>
      <div style={{ ...cell, flex: 1, justifyContent: 'flex-start' }}>
        <div style={mono}><b style={{ fontWeight: 700 }}>{p.venue.name}</b><br />{p.venue.address} · {p.venue.city}</div>
      </div>
      <div style={cell}><div style={{ ...mono, textAlign: 'center' }}>{p.day}<br />{p.venue.hours}</div></div>
      <div style={{ ...cell, borderRight: 'none', width: W * 0.19, background: th.accent }}>
        <Kufi text={p.date} height={W * 0.032} fill={th.accentInk} />
      </div>
    </div>
  );
};

/** Lettering 3D recortado a su caja, con un brillo que lo recorre y flotación suave. */
const Title: React.FC<{ src: string; width: number; f: number; t: number }> = ({ src, width, f, t }) => {
  const full = width / (LBOX.x1 - LBOX.x0);
  const fullH = full * (864 / 1800);
  const h = fullH * (LBOX.y1 - LBOX.y0);
  const u = (phase(f) - 0.58) / 0.2;
  const pos = u < 0 || u > 1 ? -1 : easeInOut(u);
  const url = asset(src);
  const bob = Math.sin(2 * Math.PI * t) * width * 0.004;
  return (
    <div style={{ position: 'relative', width, height: h, transform: `translateY(${bob}px)` }}>
      <div style={{ position: 'absolute', left: -LBOX.x0 * full, top: -LBOX.y0 * fullH, width: full, height: fullH }}>
        <Img src={url} style={{ width: full, height: fullH, display: 'block' }} />
        {pos >= 0 && (
          <div style={{
            position: 'absolute', inset: 0, mixBlendMode: 'screen',
            WebkitMaskImage: `url(${url})`, WebkitMaskSize: '100% 100%', maskImage: `url(${url})`, maskSize: '100% 100%',
            background: `linear-gradient(105deg, transparent ${pos * 140 - 30}%, rgba(255,250,235,0.7) ${pos * 140 - 20}%, transparent ${pos * 140 - 10}%)`,
          }} />
        )}
      </div>
    </div>
  );
};

export const Medallon: React.FC<MedallonProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const story = H / W > 1.5;
  const th = THEMES[p.style];
  const t = phase(f);
  const pad = W * 0.06;
  const top = story ? 250 : W * 0.05;
  const bottom = story ? 250 : W * 0.05;

  // medalla
  const box = story ? W * 0.8 : W * 0.6;
  const cx = W / 2;
  const cy = story ? H * 0.5 : H * 0.505;
  const dir = `med/${p.style}`;
  const pts = useJson<Pts>(p.frames ? `${dir}/pts.json` : `med/key/pts.json`);
  const pt = p.frames ? pts?.[String(f)] : undefined;
  const medSrc = p.frames ? `${dir}/m_${pad4(f)}.png` : `med/key/${p.style}.png`;
  const mx = (v: number) => cx - box / 2 + v * box;
  const my = (v: number) => cy - box / 2 + v * box;

  // destellos: cada punta brilla una vez por bucle, escalonadas; la gema en cada compás (2 s)
  const tw = (i: number) => {
    const u = ((t - i / 8 - 0.03) % 1 + 1) % 1 / 0.07;
    return u > 1 ? 0 : Math.sin(Math.PI * u) ** 2;
  };
  const bar = (f % 60) / 60;
  const gemAmt = Math.exp(-bar * 7) * 0.9;

  const letW = story ? W * 0.72 : W * 0.5;
  const lineSize = story ? 0.08 : 0.064;

  return (
    <AbsoluteFill style={{ background: th.bg0, overflow: 'hidden' }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 85% ${story ? 48 : 62}% at 50% ${(cy / H) * 100}%, ${th.bg1} 0%, ${th.bg0} 78%)` }} />
      <Lattice W={W} H={H} t={t} color={th.gold} cy={cy} />
      <Rays cx={cx} cy={cy} R={box * 0.95} t={t} color={th.glow} />
      <div style={{ position: 'absolute', left: cx - box * 0.42, top: cy - box * 0.42, width: box * 0.84, height: box * 0.84, borderRadius: '50%', background: `radial-gradient(circle, ${th.glow}55 0%, ${th.glow}18 45%, transparent 70%)`, opacity: 0.8 + 0.2 * Math.cos(2 * Math.PI * t * 4) }} />
      <Dust W={W} H={H} t={t} color={th.gold} />

      {/* medalla */}
      <div style={{ position: 'absolute', left: cx - box / 2, top: cy - box / 2, width: box, height: box, filter: `drop-shadow(0 ${W * 0.02}px ${W * 0.03}px ${th.bg0}cc)` }}>
        <Img src={asset(medSrc)} style={{ width: box, height: box, display: 'block' }} />
      </div>
      {pt && pt.tips.map(([x, y], i) => <Twinkle key={i} x={mx(x)} y={my(y)} size={W * 0.13} amount={tw(i) * (0.4 + 0.6 * pt.vis)} color={th.gold} />)}
      {pt && pt.vis > 0.35 && <Glint x={mx(pt.gem[0])} y={my(pt.gem[1])} size={W * 0.2} amount={gemAmt * pt.vis} color={th.glow} rot={22.5} />}

      {/* viñeta */}
      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${th.bg0}cc 0%, transparent 14%, transparent 70%, ${th.bg0}ee 100%)` }} />

      {/* cabecera */}
      <div style={{ position: 'absolute', left: pad, right: pad, top, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: W * 0.018 }}>
          <Star size={W * 0.052} fill={C.red} />
          <Kufi text="BARULLO" height={W * 0.03} fill={C.bone} />
        </div>
        <div style={{ border: `${W * 0.0018}px solid ${th.accent}`, borderRadius: 999, padding: `${W * 0.01}px ${W * 0.026}px`, fontFamily: FONT.data, fontWeight: 700, fontSize: W * 0.017, letterSpacing: '0.18em', color: th.accent }}>
          B/{String(p.num).padStart(2, '0')} · {th.name}
        </div>
      </div>

      {/* título + etiquetas */}
      <div style={{ position: 'absolute', left: 0, right: 0, top: top + W * (story ? 0.095 : 0.07), display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Title src={p.frames ? `med/lettering/${p.style}.png` : `med/key/lettering-${p.style}.png`} width={letW} f={f} t={t} />
        <div style={{ marginTop: W * (story ? 0.04 : 0.025), display: 'flex', flexDirection: 'column', alignItems: 'center', gap: W * 0.012 }}>
          <Tag text={p.genre} bg={th.accent} ink={th.accentInk} size={W * (story ? 0.029 : 0.025)} W={W} />
          <Tag text={DAYS(p)} bg={C.bone} ink={C.black} size={W * (story ? 0.036 : 0.03)} W={W} />
        </div>
      </div>

      {/* line up */}
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: bottom + W * 0.088 + W * (story ? 0.07 : 0.035), display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {p.lineup.map((n) => (
          <div key={n} style={{ fontFamily: FONT.lineup, fontWeight: 800, fontStretch: '125%', fontSize: W * lineSize, lineHeight: 1.02, letterSpacing: '-0.005em', color: C.bone, whiteSpace: 'nowrap', textShadow: `0 ${W * 0.004}px ${W * 0.02}px ${th.bg0}` }}>{n}</div>
        ))}
      </div>

      <Bar p={p} th={th} W={W} pad={pad} bottom={bottom} />
      <Grain opacity={0.05} seed={f % 8} />
    </AbsoluteFill>
  );
};
