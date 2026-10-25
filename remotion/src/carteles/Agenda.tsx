import React, { useLayoutEffect, useRef, useState } from 'react';
import { AbsoluteFill, CalculateMetadataFunction, Easing, Img, interpolate, Sequence, useCurrentFrame, useVideoConfig } from 'remotion';
import KUFI from './data/kufi.json';
import { LedCarpet } from './Medalla';
import { asset, C, FONT, Grain, kick, Kufi, loadFonts, phase, Star } from './ui';
import DATA from '../../../bocetos/animaciones/carteles/05-agenda-mes/agenda-2026-11.json';

loadFonts();

// AGENDA DEL MES de Barullo Clvb. Todo sale de los datos (bocetos/animaciones/carteles/05-agenda-mes/agenda-AAAA-MM.json):
//   Agenda-Story (1080x1920): intro con emblema y mes → una escena por semana → el mes entero → cierre.
//   Agenda-Feed  (1080x1350): el mes de un vistazo, bucle de 8 s (la fila activa recorre las noches).
// Render: bash bocetos/animaciones/carteles/05-agenda-mes/render.sh  (necesita serve.py en :8765).

// ---------- datos ----------
export type Venue = { name: string; address: string; city: string; hours: string };
export type AgendaEvent = {
  date: string; // AAAA-MM-DD
  title: string; // género real de la noche
  tag?: string;
  lineup: string[];
  venue: string; // clave de venues
  hours?: string;
  medal?: string;
  color?: string;
  placeholder?: boolean;
};
export type AgendaProps = {
  month: string; year: string; city: string; handle: string; cta: string;
  venues: Record<string, Venue>;
  events: AgendaEvent[];
  /** feed: sin fila activa (para el PNG fijo) */
  still?: boolean;
};
export const agendaDefaults = DATA as unknown as AgendaProps;

const INK = C.bone;
const BG = '#0B0B0B';
const RED = '#E63B2E';
const GOLD = '#D9A64E';
const MUTED = '#F2EFE8A6';

/** color de cada medalla del catálogo (bocetos/disenos/logo/estilos/) */
const MEDAL_COLOR: Record<string, string> = {
  'oro-turquesa': '#3FC9BC',
  'oro-girih-rubi': RED,
  'plata-joya-rubi': '#FF4A3D',
  'oro-esmeralda': '#3DBE78',
  'oro-perlas': GOLD,
  'oro-rosa-coral': '#FF8A74',
};
const accentOf = (e: AgendaEvent) => e.color ?? MEDAL_COLOR[e.medal ?? ''] ?? RED;
const medalOf = (e: AgendaEvent) => (e.medal && MEDAL_COLOR[e.medal] ? e.medal : 'oro-turquesa');

const DAYS = ['DOMINGO', 'LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO'];
const DAYS3 = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB'];
const parse = (d: string) => {
  const [y, m, dd] = d.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, dd));
  return { d: String(dd).padStart(2, '0'), m: String(m).padStart(2, '0'), wd: dt.getUTCDay(), t: dt.getTime() };
};
const venueOf = (p: AgendaProps, e: AgendaEvent): Venue =>
  p.venues[e.venue] ?? { name: e.venue.toUpperCase(), address: '', city: p.city, hours: '' };
const hoursOf = (p: AgendaProps, e: AgendaEvent) => e.hours ?? venueOf(p, e).hours;

/** agrupa por semana (lunes a domingo), máximo 3 noches por escena */
const weeks = (events: AgendaEvent[]) => {
  const sorted = [...events].sort((a, b) => parse(a.date).t - parse(b.date).t);
  const out: AgendaEvent[][] = [];
  let key = -1;
  for (const e of sorted) {
    const { t, wd } = parse(e.date);
    const monday = t - ((wd + 6) % 7) * 86400000;
    const last = out[out.length - 1];
    if (monday !== key || !last || last.length >= 3) out.push([e]);
    else last.push(e);
    key = monday;
  }
  return out;
};

// ---------- tiempos de la story ----------
const T_INTRO = 84;
const T_WEEK = 90;
const T_MONTH = 108;
const T_OUTRO = 60;
const storyTimeline = (p: AgendaProps) => {
  const w = weeks(p.events);
  const starts: number[] = [0];
  let t = T_INTRO;
  w.forEach(() => { starts.push(t); t += T_WEEK; });
  starts.push(t); t += T_MONTH;
  starts.push(t); t += T_OUTRO;
  return { w, starts, total: t };
};
export const agendaStoryMetadata: CalculateMetadataFunction<AgendaProps> = ({ props }) => ({
  durationInFrames: storyTimeline(props).total,
});

// ---------- utilidades ----------
const OUT = Easing.bezier(0.16, 1, 0.3, 1);
const IN = Easing.bezier(0.7, 0, 0.84, 0);
const prog = (f: number, start: number, len = 14) =>
  interpolate(f, [start, start + len], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: OUT });

const G = KUFI as unknown as Record<string, { w: number }>;
const ACC: Record<string, string> = { 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ñ': 'N' };
/** ancho en px del texto en Kufi a una altura dada (mismo cálculo que <Kufi>) */
const kufiW = (text: string, h: number) => {
  let w = 0;
  [...text].forEach((ch) => { w += (G[ACC[ch] ?? ch] ?? G[' ']).w + 1; });
  return ((w - 1) * h) / 5;
};

/** línea que sube desde detrás de una máscara */
const Reveal: React.FC<{ f: number; at: number; len?: number; children: React.ReactNode; style?: React.CSSProperties; from?: 'y' | 'x' }>
  = ({ f, at, len = 14, children, style, from = 'y' }) => {
    const u = prog(f, at, len);
    const tr = from === 'y' ? `translateY(${(1 - u) * 105}%)` : `translateX(${(u - 1) * 40}%)`;
    return (
      <div style={{ overflow: 'hidden', ...style }}>
        <div style={{ transform: tr, opacity: from === 'x' ? u : 1 }}>{children}</div>
      </div>
    );
  };

/** Kufi letra a letra: cada glifo sube con un pequeño desfase */
const KufiStagger: React.FC<{ text: string; h: number; f: number; at: number; fill?: string; step?: number }>
  = ({ text, h, f, at, fill = INK, step = 2 }) => (
    <div style={{ display: 'flex', overflow: 'hidden', paddingTop: h * 0.04, paddingBottom: h * 0.04 }}>
      {[...text].map((ch, i) => {
        const u = prog(f, at + i * step, 16);
        return (
          <div key={i} style={{ marginRight: i < text.length - 1 ? h / 5 : 0, transform: `translateY(${(1 - u) * 115}%)` }}>
            <Kufi text={ch} height={h} fill={fill} />
          </div>
        );
      })}
    </div>
  );

/** Medallón del catálogo: balanceo suave, brillo que lo cruza enmascarado por su alfa y halo que late. */
const Medal: React.FC<{ style: string; size: number; f: number; accent: string; enter?: number; sweepAt?: number }>
  = ({ style, size, f, accent, enter = 1, sweepAt = 0.35 }) => {
    const url = asset(`agenda/med-${style}.png`);
    const t = phase(f);
    const rot = Math.sin(2 * Math.PI * t) * 7 + (1 - enter) * -50;
    const u = (t - sweepAt) / 0.25;
    const pos = u < 0 || u > 1 ? -1 : u;
    const k = kick(f, 6);
    return (
      <div style={{ position: 'relative', width: size, height: size, transform: `scale(${0.55 + 0.45 * enter}) rotate(${rot}deg)`, opacity: Math.min(1, enter * 1.6) }}>
        <div style={{ position: 'absolute', inset: '-18%', borderRadius: '50%', background: `radial-gradient(circle, ${accent}${Math.round(46 + 30 * k).toString(16)} 0%, ${accent}14 40%, transparent 66%)` }} />
        <Img src={url} style={{ position: 'absolute', inset: 0, width: size, height: size, filter: `drop-shadow(0 ${size * 0.04}px ${size * 0.06}px #000d)` }} />
        {pos >= 0 && (
          <div style={{
            position: 'absolute', inset: 0, mixBlendMode: 'screen',
            WebkitMaskImage: `url(${url})`, WebkitMaskSize: '100% 100%', maskImage: `url(${url})`, maskSize: '100% 100%',
            background: `linear-gradient(115deg, transparent ${pos * 160 - 40}%, rgba(255,250,235,0.7) ${pos * 160 - 28}%, transparent ${pos * 160 - 16}%)`,
          }} />
        )}
      </div>
    );
  };

/** Emblema real (octograma rojo + ba/ru/llo), SVG de 01_LOGO/ORIGINAL_REDIBUJADO */
const Emblem: React.FC<{ size: number; style?: React.CSSProperties }> = ({ size, style }) => (
  <Img src={asset('agenda/emblema.svg')} style={{ width: size, height: size, display: 'block', ...style }} />
);

const mono = (size: number, extra: React.CSSProperties = {}): React.CSSProperties => ({
  fontFamily: FONT.data, fontSize: size, lineHeight: 1.25, letterSpacing: '0.12em', color: INK, whiteSpace: 'nowrap', ...extra,
});
const wide = (size: number, weight = 800, extra: React.CSSProperties = {}): React.CSSProperties => ({
  fontFamily: FONT.lineup, fontWeight: weight, fontStretch: '125%', fontSize: size, lineHeight: 1.02, letterSpacing: '-0.005em', color: INK, whiteSpace: 'nowrap', ...extra,
});

/** Una línea que nunca se corta: mide su ancho natural y se escala para caber en su caja (origen a la izquierda o derecha). */
const Fit: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; align?: 'left' | 'right'; box?: React.CSSProperties }>
  = ({ children, style, align = 'left', box }) => {
    const outer = useRef<HTMLDivElement>(null);
    const inner = useRef<HTMLSpanElement>(null);
    const [k, setK] = useState(1);
    const f = useCurrentFrame();
    useLayoutEffect(() => {
      if (!outer.current || !inner.current) return;
      const avail = outer.current.clientWidth;
      const nat = inner.current.offsetWidth;
      const nk = nat > avail && nat > 0 ? avail / nat : 1;
      if (Math.abs(nk - k) > 0.002) setK(nk);
    });
    void f;
    return (
      <div ref={outer} style={{ width: '100%', minWidth: 0, textAlign: align, ...box }}>
        <span ref={inner} style={{ display: 'inline-block', whiteSpace: 'nowrap', transform: `scale(${k})`, transformOrigin: `${align} center`, ...style }}>{children}</span>
      </div>
    );
  };

/** Cabecera común: emblema + BARULLO en Kufi a la izquierda, píldora AGENDA a la derecha */
const Header: React.FC<{ p: AgendaProps; u: number; right?: React.ReactNode }> = ({ p, u, right }) => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 18 * u }}>
      <Emblem size={78 * u} />
      <div>
        <Kufi text="BARULLO" height={30 * u} fill={INK} />
        <div style={mono(15 * u, { color: MUTED, letterSpacing: '0.3em', marginTop: 8 * u })}>CLVB · {p.city}</div>
      </div>
    </div>
    {right ?? (
      <div style={mono(19 * u, { color: RED, border: `${2 * u}px solid ${RED}`, padding: `${9 * u}px ${18 * u}px`, letterSpacing: '0.24em' })}>
        AGENDA · {p.year}
      </div>
    )}
  </div>
);

const Background: React.FC<{ story: boolean; f: number }> = ({ story, f }) => (
  <>
    <LedCarpet story={story} f={f} base={0.11} scanAmt={0.22} />
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 85% 60% at 50% 45%, transparent 0%, ${BG}cc 62%, ${BG} 100%)` }} />
  </>
);

/** Fila del mes (lista): franja de color · fecha Kufi · día · título + line-up · sala y horario */
const Row: React.FC<{ p: AgendaProps; e: AgendaEvent; u: number; h: number; width: number; active?: number; enter?: number; idx: number }>
  = ({ p, e, u, h, width, active = 0, enter = 1, idx }) => {
    const a = accentOf(e);
    const { d, wd } = parse(e.date);
    const v = venueOf(p, e);
    const dateW = kufiW('00', 58 * u);
    const rightW = 196 * u;
    const midW = width - 22 * u - dateW - 22 * u - 66 * u - 22 * u - rightW - 18 * u;
    const ln = e.lineup.join(' · ');
    return (
      <div style={{
        position: 'relative', height: h, display: 'flex', alignItems: 'center', borderBottom: `${1.5 * u}px solid ${INK}26`,
        opacity: enter, transform: `translateY(${(1 - enter) * 30 * u}px)`,
      }}>
        {/* barrido de la fila activa */}
        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${active * 100}%`, background: `linear-gradient(90deg, ${a}38, ${a}10)` }} />
        <div style={{ position: 'absolute', left: 0, top: h * 0.16, bottom: h * 0.16, width: (6 + 6 * active) * u, background: a }} />
        <div style={{ width: 22 * u }} />
        <div style={{ width: dateW, position: 'relative' }}><Kufi text={d} height={58 * u} fill={active > 0.5 ? INK : a} /></div>
        <div style={{ width: 22 * u }} />
        <div style={{ width: 66 * u, ...mono(22 * u, { fontWeight: 700, letterSpacing: '0.06em' }) }}>{DAYS3[wd]}</div>
        <div style={{ width: 22 * u }} />
        <div style={{ width: midW, overflow: 'hidden', position: 'relative' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 14 * u }}>
            <div style={{ flex: 'none', maxWidth: midW * 0.72, display: 'flex' }}><Fit style={wide(36 * u)}>{e.title}</Fit></div>
            {e.tag && <div style={{ flex: 1, minWidth: 0 }}><Fit style={mono(15 * u, { color: a, letterSpacing: '0.08em' })}>{e.tag}</Fit></div>}
          </div>
          <div style={{ marginTop: 8 * u }}><Fit style={{ ...wide(22 * u, 600), color: `${INK}D0` }}>{ln}</Fit></div>
        </div>
        <div style={{ width: 18 * u }} />
        <div style={{ width: rightW, textAlign: 'right' }}>
          <Fit align="right" style={mono(19 * u, { fontWeight: 700, letterSpacing: '0.04em' })}>{v.name}</Fit>
          <div style={mono(18 * u, { color: MUTED, letterSpacing: '0.04em', marginTop: 4 * u })}>{hoursOf(p, e)}</div>
        </div>
        <span style={{ display: 'none' }}>{idx}</span>
      </div>
    );
  };

/** cinta que corre en bucle: avanza exactamente un periodo por bucle de 240 frames */
const Ticker: React.FC<{ text: string; u: number; f: number; color?: string; bg?: string; len?: number }> = ({ text, u, f, color = BG, bg = RED, len = 240 }) => {
  const item = `${text}   ·   `;
  const charW = (0.612 + 0.1) * 20 * u; // Space Mono: avance 0,612 em + tracking 0,1 em (monoespaciada: el periodo es exacto)
  const period = item.length * charW;
  const x = -((f % len) / len) * period;
  return (
    <div style={{ background: bg, height: 44 * u, overflow: 'hidden', display: 'flex', alignItems: 'center' }}>
      <div style={{ transform: `translateX(${x}px)`, display: 'flex' }}>
        {Array.from({ length: 8 }).map((_, i) => (
          <span key={i} style={mono(20 * u, { color, fontWeight: 700, letterSpacing: '0.1em', width: period, display: 'inline-block', whiteSpace: 'pre' })}>{item}</span>
        ))}
      </div>
    </div>
  );
};

const venuesLine = (p: AgendaProps) => [...new Set(p.events.map((e) => venueOf(p, e).name))].join(' · ');

// ================= FEED =================
export const AgendaFeed: React.FC<AgendaProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = W / 1080;
  const pad = 56 * u;
  const ev = [...p.events].sort((a, b) => parse(a.date).t - parse(b.date).t);
  const n = ev.length;
  const slot = 240 / Math.max(n, 1);
  // desfase de medio tramo: el fotograma 0 (portada del vídeo) ya muestra la primera noche activa y la medalla de frente
  const ff = (f + slot / 2) % 240;
  const cur = Math.floor(ff / slot);
  const lf = ff - cur * slot;
  const act = (i: number) => {
    if (p.still || i !== cur) return 0;
    return interpolate(lf, [0, 8, slot - 6, slot], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  };
  const monthH = 84 * u;
  const listTop = 352 * u;
  const listBottom = H - 120 * u;
  const rowH = Math.min(118 * u, (listBottom - listTop) / n);
  const medalEv = p.still ? ev[0] : ev[cur] ?? ev[0];
  // la medalla cambia con la fila activa: se pone de canto (escala X a 0) justo en el cambio
  const dEdge = Math.min(lf, slot - lf);
  const flip = p.still ? 1 : Math.max(0.03, Math.sin(Math.min(1, dEdge / 5) * Math.PI / 2));
  return (
    <AbsoluteFill style={{ background: BG, overflow: 'hidden' }}>
      <Background story={false} f={f} />
      <div style={{ position: 'absolute', right: pad - 30 * u, top: 120 * u }}>
        <div style={{ transform: `scaleX(${flip})` }}>
          <Medal style={medalOf(medalEv)} size={260 * u} f={f} accent={accentOf(medalEv)} />
        </div>
      </div>
      <div style={{ position: 'absolute', left: pad, right: pad, top: pad }}>
        <Header p={p} u={u} right={<div />} />
        <div style={mono(20 * u, { color: RED, letterSpacing: '0.42em', marginTop: 44 * u })}>AGENDA · {p.year}</div>
        <div style={{ marginTop: 14 * u }}><Kufi text={p.month} height={monthH} fill={INK} /></div>
        <div style={mono(18 * u, { color: MUTED, letterSpacing: '0.26em', marginTop: 18 * u })}>{n} NOCHES · VIERNES Y SÁBADOS · {p.city}</div>
      </div>
      <div style={{ position: 'absolute', left: pad, right: pad, top: listTop, borderTop: `${1.5 * u}px solid ${INK}40` }}>
        {ev.map((e, i) => <Row key={i} idx={i} p={p} e={e} u={u} h={rowH} width={W - 2 * pad} active={act(i)} />)}
      </div>
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: pad * 0.9 }}>
        <Ticker text={`${p.handle}  ·  ${p.cta}  ·  ${venuesLine(p)}`} u={u} f={p.still ? 0 : f} />
      </div>
      <Grain opacity={0.05} seed={f % 8} />
    </AbsoluteFill>
  );
};

// ================= STORY =================
const SAFE_TOP = 0.1;

/** Cortinilla: panel rojo con el octograma que sube, tapa el corte y sale por arriba. */
const Shutter: React.FC<{ at: number[]; f: number; W: number; H: number }> = ({ at, f, W, H }) => {
  const T = 9;
  for (const b of at) {
    const lt = f - b;
    if (lt < -T || lt >= T) continue;
    const y = lt < 0
      ? H * (1 - interpolate(lt, [-T, 0], [0, 1], { easing: IN }))
      : -H * interpolate(lt, [0, T], [0, 1], { easing: OUT });
    const u = W / 1080;
    return (
      <div style={{ position: 'absolute', left: 0, top: y, width: W, height: H, background: RED, zIndex: 50 }}>
        <div style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 14 * u, background: INK }} />
        <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 14 * u, background: BG }} />
        <div style={{ position: 'absolute', left: W / 2 - 150 * u, top: H / 2 - 150 * u, transform: `rotate(${lt * 5}deg)` }}>
          <Star size={300 * u} fill={BG} />
        </div>
      </div>
    );
  }
  return null;
};

const Intro: React.FC<{ p: AgendaProps }> = ({ p }) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = W / 1080;
  const pad = 64 * u;
  const monthH = Math.min(150 * u, ((W - 2 * pad) / kufiW(p.month, 100)) * 100);
  const evs = [...p.events].sort((a, b) => parse(a.date).t - parse(b.date).t);
  const first = evs[0];
  // tira de fechas: cabe en una fila hasta ~9 noches; si hay más, salta a dos
  const perRow = Math.min(evs.length, 9);
  const stripH = Math.min(62 * u, ((W - 2 * pad - (perRow - 1) * 22 * u) / perRow / kufiW('00', 100)) * 100);
  const em = prog(f, 0, 18);
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', left: pad, right: pad, top: H * SAFE_TOP + 16 * u, opacity: em, transform: `translateY(${(1 - em) * -30 * u}px)` }}>
        <Header p={p} u={u} />
      </div>
      <div style={{ position: 'absolute', left: (W - 620 * u) / 2, top: 470 * u }}>
        <Medal style={medalOf(first)} size={620 * u} f={f + 60} accent={accentOf(first)} enter={prog(f, 4, 26)} sweepAt={0.0} />
      </div>
      <div style={{ position: 'absolute', left: pad, right: pad, top: 1170 * u }}>
        <Reveal f={f} at={14}><div style={mono(26 * u, { color: RED, letterSpacing: '0.5em' })}>AGENDA DEL MES</div></Reveal>
        <div style={{ marginTop: 24 * u }}><KufiStagger text={p.month} h={monthH} f={f} at={18} /></div>
        <div style={{ height: 3 * u, background: INK, marginTop: 30 * u, transformOrigin: 'left', transform: `scaleX(${prog(f, 30, 24)})` }} />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 22 * u }}>
          <Reveal f={f} at={36}><div style={mono(26 * u, { fontWeight: 700, letterSpacing: '0.2em' })}>{p.year} · {p.city}</div></Reveal>
          <Reveal f={f} at={40}><div style={mono(26 * u, { fontWeight: 700, letterSpacing: '0.2em', color: RED })}>{p.events.length} NOCHES</div></Reveal>
        </div>
        {/* el mes en fechas: cada noche con el color de su medalla */}
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', rowGap: 18 * u, marginTop: 70 * u }}>
          {evs.map((e, i) => {
            const q = prog(f, 44 + i * 2.5, 14);
            const { d, wd } = parse(e.date);
            return (
              <div key={i} style={{ opacity: q, transform: `translateY(${(1 - q) * 24 * u}px)`, textAlign: 'center' }}>
                <Kufi text={d} height={stripH} fill={accentOf(e)} />
                <div style={mono(17 * u, { marginTop: 10 * u, color: MUTED, letterSpacing: '0.14em' })}>{DAYS3[wd]}</div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const EventBlock: React.FC<{ p: AgendaProps; e: AgendaEvent; u: number; f: number; at: number; k: number; width: number }>
  = ({ p, e, u, f, at, k, width }) => {
    const a = accentOf(e);
    const { d, m, wd } = parse(e.date);
    const v = venueOf(p, e);
    const s = u * k;
    const dateH = 140 * s;
    const medalS = 186 * s;
    const lineup = e.lineup;
    const lnSize = lineup.length > 3 ? 44 * s : 54 * s;
    const barH = 78 * s;
    return (
      <div style={{ position: 'relative', width }}>
        <div style={{ position: 'absolute', right: -10 * s, top: -26 * s }}>
          <Medal style={medalOf(e)} size={medalS} f={f + at * 7} accent={a} enter={prog(f, at + 2, 22)} />
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 26 * s }}>
          <Reveal f={f} at={at} len={16}><Kufi text={d} height={dateH} fill={a} /></Reveal>
          <div style={{ paddingBottom: 8 * s }}>
            <Reveal f={f} at={at + 3}><div style={mono(34 * s, { fontWeight: 700, letterSpacing: '0.16em' })}>{DAYS[wd]}</div></Reveal>
            <Reveal f={f} at={at + 5}><div style={mono(24 * s, { color: MUTED, letterSpacing: '0.2em', marginTop: 6 * s })}>{d}.{m}.{p.year}</div></Reveal>
          </div>
        </div>
        <Reveal f={f} at={at + 5} style={{ marginTop: 26 * s }}>
          <Fit style={wide(104 * s)}>{e.title}</Fit>
        </Reveal>
        {e.tag && (
          <Reveal f={f} at={at + 8} from="x" style={{ marginTop: 12 * s }}>
            <div style={mono(24 * s, { color: a, letterSpacing: '0.26em', fontWeight: 700 })}>{e.tag}</div>
          </Reveal>
        )}
        <div style={{ marginTop: 26 * s }}>
          {lineup.map((name, j) => (
            <Reveal key={j} f={f} at={at + 10 + j * 3}>
              <Fit style={{ ...wide(lnSize, 700), lineHeight: 1.12 }}>{name}</Fit>
            </Reveal>
          ))}
        </div>
        {/* barra de datos en celdas */}
        <div style={{
          marginTop: 24 * s, height: barH, display: 'flex', border: `${2 * u}px solid ${INK}55`, background: `${BG}C8`,
          clipPath: `inset(0 ${(1 - prog(f, at + 14, 18)) * 100}% 0 0)`,
        }}>
          <div style={{ width: barH, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRight: `${2 * u}px solid ${INK}55` }}>
            <Star size={barH * 0.62} fill={a} />
          </div>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: `0 ${20 * s}px`, borderRight: `${2 * u}px solid ${INK}55` }}>
            <div style={mono(22 * s, { fontWeight: 700, letterSpacing: '0.08em' })}>{v.name}</div>
            <div style={mono(18 * s, { color: MUTED, letterSpacing: '0.06em' })}>{[v.address, v.city].filter((x, i, arr) => x && arr.indexOf(x) === i).join(' · ')}</div>
          </div>
          <div style={{ width: 230 * s, display: 'flex', alignItems: 'center', justifyContent: 'center', background: a }}>
            <div style={mono(24 * s, { fontWeight: 700, color: BG, letterSpacing: '0.04em' })}>{hoursOf(p, e)}</div>
          </div>
        </div>
      </div>
    );
  };

const WeekScene: React.FC<{ p: AgendaProps; evs: AgendaEvent[]; idx: number; count: number }> = ({ p, evs, idx, count }) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = W / 1080;
  const pad = 64 * u;
  const k = evs.length >= 3 ? 0.7 : 1;
  const top = H * SAFE_TOP + 16 * u;
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', left: pad, right: pad, top }}>
        <Header p={p} u={u} right={
          <div style={{ textAlign: 'right' }}>
            <div style={mono(20 * u, { color: RED, letterSpacing: '0.26em', fontWeight: 700 })}>{p.month}</div>
            <div style={mono(20 * u, { letterSpacing: '0.26em', marginTop: 6 * u })}>SEMANA {String(idx + 1).padStart(2, '0')}/{String(count).padStart(2, '0')}</div>
          </div>
        } />
        {/* progreso del mes: un segmento por semana */}
        <div style={{ display: 'flex', gap: 8 * u, marginTop: 26 * u }}>
          {Array.from({ length: count }).map((_, i) => (
            <div key={i} style={{ flex: 1, height: 6 * u, background: `${INK}30`, position: 'relative' }}>
              <div style={{ position: 'absolute', inset: 0, background: RED, transformOrigin: 'left', transform: `scaleX(${i < idx ? 1 : i > idx ? 0 : Math.min(1, f / (T_WEEK - 4))})` }} />
            </div>
          ))}
        </div>
      </div>
      <div style={{
        position: 'absolute', left: pad, right: pad, top: top + 170 * u, bottom: H * SAFE_TOP,
        display: 'flex', flexDirection: 'column', justifyContent: evs.length === 1 ? 'center' : 'space-evenly',
      }}>
        {evs.map((e, i) => (
          <React.Fragment key={i}>
            {i > 0 && <div style={{ height: 2 * u, background: `${INK}30`, transformOrigin: 'left', transform: `scaleX(${prog(f, 6 + i * 8, 20)})` }} />}
            <EventBlock p={p} e={e} u={u} f={f} at={4 + i * 9} k={k} width={W - 2 * pad} />
          </React.Fragment>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const MonthScene: React.FC<{ p: AgendaProps }> = ({ p }) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = W / 1080;
  const pad = 56 * u;
  const ev = [...p.events].sort((a, b) => parse(a.date).t - parse(b.date).t);
  const top = H * SAFE_TOP + 16 * u;
  const monthH = Math.min(104 * u, ((W - 2 * pad) / kufiW(p.month, 100)) * 100);
  const listTop = top + 330 * u;
  const rowH = Math.min(150 * u, (H * (1 - SAFE_TOP) - 30 * u - listTop) / ev.length);
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', left: pad, right: pad, top }}>
        <Header p={p} u={u} />
        <div style={{ marginTop: 50 * u }}><KufiStagger text={p.month} h={monthH} f={f} at={2} step={1} /></div>
        <Reveal f={f} at={10}><div style={mono(22 * u, { color: RED, letterSpacing: '0.34em', marginTop: 20 * u })}>EL MES ENTERO · {ev.length} NOCHES</div></Reveal>
      </div>
      <div style={{ position: 'absolute', left: pad, right: pad, top: listTop, borderTop: `${1.5 * u}px solid ${INK}40` }}>
        {ev.map((e, i) => (
          <Row key={i} idx={i} p={p} e={e} u={u} h={rowH} width={W - 2 * pad} enter={prog(f, 8 + i * 3, 16)}
            active={interpolate(f, [40 + i * 5, 48 + i * 5, 54 + i * 5], [0, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Outro: React.FC<{ p: AgendaProps }> = ({ p }) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = W / 1080;
  const em = prog(f, 0, 20);
  const letW = 900 * u;
  return (
    <AbsoluteFill style={{ alignItems: 'center' }}>
      <div style={{ position: 'absolute', top: 360 * u, transform: `scale(${0.7 + 0.3 * em}) rotate(${(1 - em) * -45}deg)`, opacity: em }}>
        <Emblem size={300 * u} />
      </div>
      <div style={{ position: 'absolute', top: 740 * u, width: letW, opacity: prog(f, 6, 16), transform: `translateY(${(1 - prog(f, 6, 20)) * 40 * u}px)` }}>
        <Img src={asset('agenda/lettering-oro-turquesa.png')} style={{ width: letW, display: 'block' }} />
      </div>
      <div style={{ position: 'absolute', top: 1220 * u, left: 64 * u, right: 64 * u, textAlign: 'center' }}>
        <Reveal f={f} at={12}><div style={wide(58 * u, 800)}>{p.cta.split('·')[0].trim()}</div></Reveal>
        <Reveal f={f} at={15}><div style={mono(28 * u, { color: RED, letterSpacing: '0.3em', marginTop: 14 * u })}>{(p.cta.split('·')[1] ?? '').trim()}</div></Reveal>
        <Reveal f={f} at={18}><div style={mono(28 * u, { fontWeight: 700, letterSpacing: '0.2em', marginTop: 40 * u })}>{p.handle}</div></Reveal>
        <Reveal f={f} at={20}><div style={mono(20 * u, { color: MUTED, letterSpacing: '0.16em', marginTop: 16 * u })}>{venuesLine(p)}</div></Reveal>
      </div>
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: H * SAFE_TOP, opacity: prog(f, 18, 12) }}>
        <Ticker text={`${p.month} ${p.year}  ·  ${p.events.length} NOCHES  ·  ${p.city}`} u={u} f={f} len={120} />
      </div>
    </AbsoluteFill>
  );
};

export const AgendaStory: React.FC<AgendaProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const { w, starts } = storyTimeline(p);
  const lens = starts.map((s, i) => (starts[i + 1] ?? s + T_OUTRO) - s);
  const nW = w.length;
  return (
    <AbsoluteFill style={{ background: BG, overflow: 'hidden' }}>
      <Background story f={f} />
      <Sequence from={starts[0]} durationInFrames={lens[0]}><Intro p={p} /></Sequence>
      {w.map((evs, i) => (
        <Sequence key={i} from={starts[i + 1]} durationInFrames={lens[i + 1]}>
          <WeekScene p={p} evs={evs} idx={i} count={nW} />
        </Sequence>
      ))}
      <Sequence from={starts[nW + 1]} durationInFrames={lens[nW + 1]}><MonthScene p={p} /></Sequence>
      <Sequence from={starts[nW + 2]} durationInFrames={lens[nW + 2]}><Outro p={p} /></Sequence>
      <Shutter at={starts.slice(1)} f={f} W={W} H={H} />
      <Grain opacity={0.05} seed={f % 8} />
    </AbsoluteFill>
  );
};
