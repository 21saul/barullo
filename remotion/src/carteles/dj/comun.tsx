import React, { useEffect, useState } from 'react';
import { continueRender, delayRender, Img } from 'remotion';
import KUFI from '../data/kufi.json';
import { asset, C, FONT, Kufi, loadFonts, MONTHS } from '../ui';

// Plantillas de ANUNCIO DE DJ (bocetos/animaciones/carteles/04-dj-plantillas/). Todo sale de las props (DjProps):
// cambiar de DJ = otra foto preparada con prep_foto.py + otro JSON (--props=dj.json).

export type Sala = { nombre: string; direccion: string; ciudad: string; horario: string };
export type DjProps = {
  dj: string; // nombre tal cual se escribe: 'CARAMELORARØ'
  rol: string; // 'DJ SET' · 'LIVE' · 'B2B' · 'ALL NIGHT LONG'
  genero: string; // 'TECHNO · HARDGROOVE'
  /** nombre base de la foto preparada en assets/dj-plantillas/fotos (sin extensión) */
  foto: string;
  /** punto de la foto que queda en el centro del encuadre (0..1) y zoom extra */
  encuadre: { x: number; y: number; zoom: number };
  fecha: string; // '13.11'
  dia: string; // 'VIERNES'
  anio: string;
  semana: string; // 'NOVIEMBRE · SEMANA 02' ('' para ocultar)
  sala: Sala;
  /** color de acento de la pieza (tinte, celdas) y segundo color (luces) */
  color: string;
  color2: string;
  /** plantilla A: carpeta del marco renderizado (assets/dj-plantillas/marco-<estilo>) y nº de variantes de luz */
  medalla: string;
  variantes: number;
};

export const DIR = 'dj-plantillas/';
export const foto = (p: DjProps, suf = '', ext = 'jpg') => asset(`${DIR}fotos/${p.foto}${suf}.${ext}`);
export const LOGO = asset(`${DIR}logo/BARULLO_logo_original_rojo_negro.svg`);
export const LOGO_ROJO = asset(`${DIR}logo/BARULLO_logo_original_rojo_transparente.svg`);

export const fechaLarga = (p: DjProps) => {
  const [d, m] = p.fecha.split('.');
  return `${p.dia} ${+d} ${MONTHS[+m - 1]} ${p.anio}`;
};

// ---------- fuentes y medida de texto ----------
let fontsP: Promise<unknown> | null = null;
const fontsReady = () => {
  if (!fontsP) {
    loadFonts();
    fontsP = new Promise<void>((res) => {
      const tick = () => (document.fonts.check(`800 100px 'Archivo'`) && document.fonts.check(`700 100px 'Space Mono'`) ? res() : setTimeout(tick, 30));
      tick();
    }).then(() => document.fonts.ready);
  }
  return fontsP;
};
/** true cuando las fuentes están cargadas; retiene el render hasta entonces (para medir texto). */
export const useFonts = () => {
  const [ready, setReady] = useState(false);
  const [h] = useState(() => delayRender('dj-fuentes'));
  useEffect(() => { fontsReady().then(() => setReady(true)); }, []);
  useEffect(() => { if (ready) continueRender(h); }, [ready, h]);
  return ready;
};

let cv: HTMLCanvasElement | null = null;
/** Tamaño de letra para que `text` ocupe `maxW` px (sin pasar de `maxSize`). stretch: palabra clave CSS de canvas. */
export const fit = (text: string, family: string, weight: number, maxW: number, maxSize: number, stretch: CanvasFontStretch = 'normal', tracking = 0) => {
  if (typeof document === 'undefined') return maxSize;
  cv = cv || document.createElement('canvas');
  const ctx = cv.getContext('2d')!;
  ctx.font = `${weight} 100px ${family}`;
  ctx.fontStretch = stretch;
  const w = ctx.measureText(text).width + tracking * 100 * Math.max(0, [...text].length - 1);
  return Math.min(maxSize, (maxW / w) * 100);
};

type Glyph = { d?: string; w: number };
const G = KUFI as unknown as Record<string, Glyph>;
const ACC: Record<string, string> = { 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ñ': 'N', 'Ü': 'U' };
/** Ancho en px del texto en Kufi Barullo a la altura dada (mismo cálculo que <Kufi>). */
export const kufiW = (text: string, height: number, gap = 1) => {
  let x = 0;
  [...text.toUpperCase()].forEach((ch) => { x += (G[ACC[ch] ?? ch] ?? G[' ']).w + gap; });
  return (x - gap) * (height / 5);
};

// ---------- piezas ----------
/** Cabecera de la marca: chapa + BARULLO en Kufi a la izquierda, píldora a la derecha. */
export const Cabecera: React.FC<{ W: number; pad: number; top: number; pill: string; ink?: string; accent?: string; shadow?: string }>
  = ({ W, pad, top, pill, ink = C.bone, accent = '#E63B2E', shadow }) => {
    const e = W * 0.068;
    return (
      <div style={{ position: 'absolute', left: pad, right: pad, top, height: e, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: W * 0.018 }}>
          <Img src={LOGO} style={{ width: e, height: e, filter: shadow ? `drop-shadow(${shadow})` : undefined }} />
          <Kufi text="BARULLO" height={W * 0.03} fill={ink} style={shadow ? { filter: `drop-shadow(${shadow})` } : undefined} />
        </div>
        <div style={{
          fontFamily: FONT.data, fontWeight: 700, fontSize: W * 0.0165, letterSpacing: '0.24em', color: ink,
          border: `${W * 0.0018}px solid ${accent}`, borderRadius: W, padding: `${W * 0.009}px ${W * 0.022}px ${W * 0.009}px ${W * 0.026}px`,
          background: `${C.black}55`,
        }}>{pill}</div>
      </div>
    );
  };

/** Barra de datos en celdas: chapa · sala y dirección · día y horario · fecha en Kufi sobre el acento. */
export const Barra: React.FC<{ p: DjProps; W: number; pad: number; bottom: number; bg?: string; ink?: string; accent?: string; dateInk?: string }>
  = ({ p, W, pad, bottom, bg = C.black, ink = C.bone, accent = '#E63B2E', dateInk = C.black }) => {
    const h = W * 0.085;
    const line = `${W * 0.0016}px solid ${ink}55`;
    const cell: React.CSSProperties = { borderRight: line, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: `0 ${W * 0.02}px` };
    const mono: React.CSSProperties = { fontFamily: FONT.data, color: ink, fontSize: W * 0.0158, lineHeight: 1.4, letterSpacing: '0.06em', whiteSpace: 'nowrap' };
    return (
      <div style={{ position: 'absolute', left: pad, right: pad, bottom, height: h, border: line, display: 'flex', background: `${bg}D9` }}>
        <div style={{ ...cell, width: h, padding: 0 }}><Img src={LOGO} style={{ width: h * 0.7, height: h * 0.7 }} /></div>
        <div style={{ ...cell, flex: 1, justifyContent: 'flex-start', overflow: 'hidden' }}>
          <div style={mono}><b style={{ fontWeight: 700 }}>{p.sala.nombre}</b><br />{p.sala.direccion} · {p.sala.ciudad}</div>
        </div>
        <div style={cell}><div style={{ ...mono, textAlign: 'center' }}>{p.dia}<br />{p.sala.horario}</div></div>
        <div style={{ ...cell, borderRight: 'none', width: W * 0.2, background: accent }}>
          <Kufi text={p.fecha} height={W * 0.031} fill={dateInk} />
        </div>
      </div>
    );
  };

/** Octograma de dos cuadrados (anillo), centrado en (0,0), radio r. */
export const octoPath = (r: number, rot = 0) => {
  const pts: string[] = [];
  for (let i = 0; i < 16; i++) {
    // estrella {8/2}: alterna punta (r) y valle (r·cos45/cos22.5... aproximado con la intersección de los cuadrados)
    const a = (i * Math.PI) / 8 + rot - Math.PI / 2;
    const rr = i % 2 === 0 ? r : r * 0.7654; // valle de dos cuadrados: r·cos(45°)/cos(22.5°)
    pts.push(`${(Math.cos(a) * rr).toFixed(2)} ${(Math.sin(a) * rr).toFixed(2)}`);
  }
  return `M${pts.join(' L')} Z`;
};

/** Filtro SVG de duotono/tritono: luminancia -> sombra, medio, luz. Úsalo con filter: url(#id). */
export const Duotono: React.FC<{ id: string; sombra: string; medio: string; luz: string; contraste?: number }>
  = ({ id, sombra, medio, luz, contraste = 1 }) => {
    const rgb = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
    const [a, b, c] = [rgb(sombra), rgb(medio), rgb(luz)];
    const ch = (k: number) => `${a[k].toFixed(3)} ${b[k].toFixed(3)} ${c[k].toFixed(3)}`;
    const s = contraste; const o = (1 - s) / 2;
    return (
      <svg width={0} height={0} style={{ position: 'absolute' }}>
        <filter id={id} colorInterpolationFilters="sRGB">
          <feColorMatrix type="matrix" values={`0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0 0 0 1 0`} />
          <feComponentTransfer>
            <feFuncR type="linear" slope={s} intercept={o} /><feFuncG type="linear" slope={s} intercept={o} /><feFuncB type="linear" slope={s} intercept={o} />
          </feComponentTransfer>
          <feComponentTransfer>
            <feFuncR type="table" tableValues={ch(0)} /><feFuncG type="table" tableValues={ch(1)} /><feFuncB type="table" tableValues={ch(2)} />
          </feComponentTransfer>
        </filter>
      </svg>
    );
  };

/** Encaja una foto (w×h) en una caja (bw×bh) tipo cover, con el punto focal (fx,fy) lo más centrado posible. */
export const cover = (w: number, h: number, bw: number, bh: number, fx: number, fy: number, zoom = 1) => {
  const s = Math.max(bw / w, bh / h) * zoom;
  const iw = w * s, ih = h * s;
  const left = Math.min(0, Math.max(bw - iw, bw / 2 - fx * iw));
  const top = Math.min(0, Math.max(bh - ih, bh / 2 - fy * ih));
  return { left, top, width: iw, height: ih };
};
