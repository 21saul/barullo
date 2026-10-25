import React from 'react';
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import SHAPES from './data/shapes.json';
import { LedCarpet } from './Medalla';
import { asset, C, CartelProps, DataBar, FONT, Grain, kick, Kufi, Lettering, loadFonts, longDate, Octo, phase } from './ui';

loadFonts();

// Plantillas para anunciar a un DJ invitado. Tres direcciones con los mismos datos:
//   DjMedalla: el DJ dentro de la estrella de la «o» y saliéndose por arriba.
//   DjFoto:    foto a sangre tintada en rojo, nombre gigante por detrás del DJ (estilo cartel de club).
//   DjRiso:    pegatina riso sobre la alfombra de la diseñadora, nombre en etiquetas.
// La foto va en assets/dj/: `<id>.jpg` y el recorte `<id>-cut.png` (rembg, u2net_human_seg).

export type DjProps = CartelProps & {
  dj: string;
  /** subtítulo bajo el nombre: ciudad, sello, tipo de set */
  from: string;
  /** id de la foto en assets/dj */
  photo: string;
  /** encuadre del recorte: escala respecto al ancho y desplazamiento en fracciones de W */
  crop?: { s: number; x: number; y: number };
  /** encuadre propio para story (9:16); si falta, se usa `crop` */
  cropStory?: { s: number; x: number; y: number };
  /** teloneros / residentes */
  support: string[];
};

const starMask = (fill = '#000') =>
  `url("data:image/svg+xml;utf8,${encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 1000'><path fill='${fill}' d='${SHAPES.star}'/></svg>`)}")`;

/** Tamaño de letra para que `text` llene `width` (Archivo 800 al 125 %: ~0.78 em por carácter). */
const fit = (text: string, width: number, max: number, em = 0.78) => Math.min(max, width / (Math.max(text.length, 1) * em));

const Name: React.FC<{ text: string; size: number; color?: string; style?: React.CSSProperties }> = ({ text, size, color = C.bone, style }) => (
  <div style={{ fontFamily: FONT.lineup, fontWeight: 800, fontStretch: '125%', fontSize: size, lineHeight: 0.86, letterSpacing: '-0.02em', color, whiteSpace: 'nowrap', ...style }}>{text}</div>
);

const Mono: React.FC<{ W: number; size?: number; color?: string; children: React.ReactNode; style?: React.CSSProperties }> = ({ W, size = 0.017, color = C.bone, children, style }) => (
  <div style={{ fontFamily: FONT.data, fontSize: W * size, letterSpacing: '0.3em', color, whiteSpace: 'nowrap', ...style }}>{children}</div>
);

// ───────────────────────── 1 · MEDALLA ─────────────────────────

export const DjMedalla: React.FC<DjProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const story = H / W > 1.5;
  const pad = W * 0.06;
  const k = kick(f, 7);
  const t = phase(f);
  const S = story ? W * 0.92 : W * 0.72; // lado de la estrella
  const sx = (W - S) / 2;
  const sy = story ? H * 0.2 : H * 0.15;
  const crop = (story && p.cropStory) || p.crop || { s: 1, x: 0, y: 0 };
  const cutW = S * 0.8 * crop.s;
  const cutL = sx + (S - cutW) / 2 + crop.x * W;
  const cutT = sy - S * 0.1 + crop.y * W;
  // por encima de esta línea el DJ se sale de la medalla (cabeza y brazo); por debajo queda dentro
  const popY = sy + S * 0.42;
  const breathe = 1 + 0.012 * k;
  const cut = asset(`dj/${p.photo}-cut.png`);
  const shadow = `0 0 ${W * 0.012}px ${C.black}`;
  const barBottom = story ? H * 0.1 : pad;
  const nameSize = fit(p.dj, W - pad * 2, W * 0.16);

  return (
    <AbsoluteFill style={{ background: C.black, overflow: 'hidden' }}>
      <LedCarpet story={story} f={f} base={0.16} scanAmt={0.3} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 75% 50% at 50% 40%, ${C.red}44 0%, ${C.black}cc 55%, ${C.black} 100%)` }} />

      {/* la medalla: aro de plata + fondo rojo con estrellas concéntricas, girando 45° por bucle */}
      <div style={{ position: 'absolute', left: sx, top: sy, width: S, height: S, transform: `scale(${breathe})`, filter: `drop-shadow(0 ${W * 0.03}px ${W * 0.05}px #000)` }}>
        <svg width={S} height={S} viewBox="0 0 1000 1000" style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
          <defs>
            <linearGradient id="silver" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#FFFFFF" /><stop offset="0.25" stopColor="#8E8B92" /><stop offset="0.45" stopColor="#F4F2F6" />
              <stop offset="0.6" stopColor="#5D5A62" /><stop offset="0.8" stopColor="#E6E3EA" /><stop offset="1" stopColor="#77737C" />
            </linearGradient>
            <radialGradient id="rojo" cx="0.5" cy="0.45" r="0.6">
              <stop offset="0" stopColor="#FF4A3A" /><stop offset="0.6" stopColor={C.red} /><stop offset="1" stopColor="#7A0A06" />
            </radialGradient>
            <clipPath id="sc"><path d={SHAPES.star} /></clipPath>
          </defs>
          <path d={SHAPES.star} fill="url(#rojo)" />
          <g clipPath="url(#sc)" opacity={0.55}>
            {[0.82, 0.62, 0.42].map((s, i) => (
              <path key={s} d={SHAPES.star} fill="none" stroke={i % 2 ? C.pink : C.orange} strokeWidth={6}
                transform={`translate(500 500) rotate(${(i % 2 ? -1 : 1) * 45 * t}) scale(${s}) translate(-500 -500)`} />
            ))}
          </g>
        </svg>
        {/* DJ dentro de la estrella */}
        <Img src={cut} style={{
          position: 'absolute', left: cutL - sx, top: cutT - sy, width: cutW,
          WebkitMaskImage: starMask(), WebkitMaskSize: `${S}px ${S}px`, WebkitMaskPosition: `${sx - cutL}px ${sy - cutT}px`, WebkitMaskRepeat: 'no-repeat',
        }} />
        <svg width={S} height={S} viewBox="0 0 1000 1000" style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
          <path d={SHAPES.star} fill="none" stroke="url(#silver)" strokeWidth={34} strokeLinejoin="round" />
          <path d={SHAPES.star} fill="none" stroke="#2A2730" strokeWidth={4} strokeLinejoin="round" transform="translate(500 500) scale(0.955) translate(-500 -500)" />
        </svg>
        {/* lo que sobresale: el mismo recorte por encima del aro, solo de popY hacia arriba */}
        <Img src={cut} style={{
          position: 'absolute', left: cutL - sx, top: cutT - sy, width: cutW,
          WebkitMaskImage: `linear-gradient(180deg, #000 ${popY - cutT}px, transparent ${popY - cutT + 2}px)`,
          filter: `drop-shadow(0 ${W * 0.01}px ${W * 0.012}px #000a)`,
        }} />
      </div>

      {/* cabecera */}
      <div style={{ position: 'absolute', left: pad, top: story ? 250 : pad, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', right: pad }}>
        <div>
          <Kufi text={p.date} height={W * 0.075} fill={C.bone} style={{ filter: `drop-shadow(${shadow})` }} />
          <Mono W={W} size={0.016} style={{ marginTop: W * 0.022, textShadow: shadow }}>{longDate(p)}</Mono>
        </div>
        <Lettering src="lettering-plata-grabada.png" width={W * 0.3} f={f} style={{ marginTop: W * 0.005 }} />
      </div>

      {/* nombre */}
      <div style={{ position: 'absolute', left: pad, right: pad, bottom: barBottom + W * 0.082 + W * 0.045 }}>
        <Mono W={W} color={C.red} style={{ marginBottom: W * 0.018 }}>BARULLO PRESENTA</Mono>
        <Name text={p.dj} size={nameSize} style={{ textShadow: shadow }} />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: W * 0.026 }}>
          <Mono W={W} size={0.019} color={C.orange}>{p.from}</Mono>
          <Mono W={W} size={0.019} color="#bdb8b0">+ {p.support.join(' · ')}</Mono>
        </div>
      </div>
      <DataBar p={p} W={W} pad={pad} bottom={barBottom} />
      <Grain opacity={0.05} seed={f % 8} />
    </AbsoluteFill>
  );
};

/** Duotono de la foto: negro → granate, medios → rojo Barullo, luces → rosa crema. */
const DuoFilter: React.FC<{ id: string }> = ({ id }) => (
  <svg width={0} height={0} style={{ position: 'absolute' }}>
    <filter id={id} colorInterpolationFilters="sRGB">
      <feColorMatrix type="saturate" values="0" />
      <feComponentTransfer>
        <feFuncR type="table" tableValues="0.16 0.6 0.89 1 1" />
        <feFuncG type="table" tableValues="0.01 0.04 0.15 0.45 0.9" />
        <feFuncB type="table" tableValues="0.03 0.04 0.11 0.5 0.86" />
      </feComponentTransfer>
    </filter>
  </svg>
);

// ───────────────────────── 2 · FOTO ─────────────────────────

export const DjFoto: React.FC<DjProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const story = H / W > 1.5;
  const pad = W * 0.06;
  const k = kick(f, 6);
  const t = phase(f);
  // lento push-in de la foto a lo largo del bucle (vuelve al inicio con coseno: cierra limpio)
  const zoom = 1.06 + 0.03 * (0.5 - 0.5 * Math.cos(2 * Math.PI * t));
  const crop = (story && p.cropStory) || p.crop || { s: 1, x: 0, y: 0 };
  const photo: React.CSSProperties = {
    position: 'absolute', left: crop.x * W, top: crop.y * W, width: W * crop.s, height: 'auto',
    transform: `scale(${zoom})`, transformOrigin: '50% 30%',
  };
  const nameSize = fit(p.dj, W * 1.04, W * 0.3, 0.74);
  const nameTop = story ? H * 0.19 : H * 0.2;
  const panelH = story ? H * 0.28 : H * 0.3;
  const shadow = `0 0 ${W * 0.01}px #0006`;
  // la foto y el recorte comparten caja y transformación: el recorte cae exacto encima
  const Layer: React.FC<{ src: string }> = ({ src }) => (
    <Img src={asset(src)} style={{ ...photo, filter: 'url(#duo)' }} />
  );

  return (
    <AbsoluteFill style={{ background: C.red, overflow: 'hidden' }}>
      <DuoFilter id="duo" />
      <Layer src={`dj/${p.photo}.jpg`} />
      <AbsoluteFill style={{ background: `linear-gradient(200deg, ${C.pink}66 0%, transparent 40%)`, mixBlendMode: 'screen' }} />
      {/* nombre gigante entre la foto y el recorte: el DJ queda por delante */}
      <div style={{ position: 'absolute', left: -W * 0.02, right: -W * 0.02, top: nameTop, display: 'flex', justifyContent: 'center' }}>
        <Name text={p.dj} size={nameSize} color={C.bone} style={{ letterSpacing: '-0.04em' }} />
      </div>
      <Layer src={`dj/${p.photo}-cut.png`} />

      {/* cabecera */}
      <div style={{ position: 'absolute', left: pad, right: pad, top: story ? 230 : pad, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <svg viewBox="0 0 2906 980" style={{ width: W * 0.3, filter: `drop-shadow(${shadow})` }}>
          <image href={asset('wordmark.svg')} width={2906} height={980} />
        </svg>
        <Mono W={W} size={0.016} style={{ textAlign: 'right', lineHeight: 1.7, textShadow: shadow }}>{p.genre.split(' · ').map((g) => <div key={g}>{g}</div>)}</Mono>
      </div>

      {/* panel translúcido con los datos: vidrio rojo con desenfoque */}
      <div style={{
        position: 'absolute', left: pad, right: pad, bottom: story ? H * 0.09 : pad, height: panelH,
        background: `${C.red}9a`, backdropFilter: `blur(${W * 0.018}px) saturate(1.4)`, WebkitBackdropFilter: `blur(${W * 0.018}px) saturate(1.4)`,
        border: `${W * 0.0016}px solid ${C.bone}66`, display: 'flex',
      }}>
        <div style={{ flex: 1, padding: W * 0.04, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <Mono W={W} size={0.017} color={C.bone}>{p.from}</Mono>
            <Name text={p.dj} size={fit(p.dj, W * 0.55, W * 0.08)} style={{ marginTop: W * 0.02 }} />
          </div>
          <div>
            <Mono W={W} size={0.015} color={`${C.bone}bb`} style={{ marginBottom: W * 0.01 }}>+ RESIDENTES</Mono>
            <div style={{ fontFamily: FONT.lineup, fontWeight: 700, fontStretch: '110%', fontSize: W * 0.032, color: C.bone, lineHeight: 1.15 }}>{p.support.join(' / ')}</div>
          </div>
        </div>
        <div style={{ width: W * 0.3, borderLeft: `${W * 0.0016}px solid ${C.bone}66`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: W * 0.02 }}>
          <Octo size={W * 0.2} fill={C.bone} style={{ transform: `rotate(${45 * t}deg) scale(${1 + 0.02 * k})` }} />
          <div style={{ position: 'absolute', width: W * 0.3, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: W * 0.008, marginTop: -W * 0.075 }}>
            <Mono W={W} size={0.014} color={C.red} style={{ letterSpacing: '0.2em' }}>{p.day}</Mono>
            <Kufi text={p.date} height={W * 0.045} fill={C.red} />
          </div>
          <Mono W={W} size={0.014} style={{ textAlign: 'center', lineHeight: 1.5, letterSpacing: '0.12em' }}>{p.venue.name}<br />{p.venue.hours}</Mono>
        </div>
      </div>
      <Grain opacity={0.1} seed={f % 8} />
    </AbsoluteFill>
  );
};

// ───────────────────────── 3 · RISO ─────────────────────────

const Tag: React.FC<{ W: number; bg?: string; ink?: string; size: number; children: React.ReactNode; style?: React.CSSProperties }>
  = ({ W, bg = C.orange, ink = C.red, size, children, style }) => (
    <div style={{
      display: 'inline-block', background: bg, color: ink, fontFamily: FONT.tag, fontWeight: 700, fontStyle: 'italic',
      fontSize: W * size, lineHeight: 1, letterSpacing: '0.03em', padding: `${W * size * 0.2}px ${W * size * 0.38}px ${W * size * 0.14}px`,
      whiteSpace: 'nowrap', ...style,
    }}>{children}</div>
  );

/** Mapa de degradado riso: sombras rojo oscuro → rojo → rosa → crema. */
const RisoFilter: React.FC<{ id: string }> = ({ id }) => (
  <svg width={0} height={0} style={{ position: 'absolute' }}>
    <filter id={id} colorInterpolationFilters="sRGB">
      <feColorMatrix type="saturate" values="0" />
      <feComponentTransfer>
        <feFuncR type="table" tableValues="0.36 0.89 1 1 0.99" />
        <feFuncG type="table" tableValues="0.02 0.15 0.31 0.64 0.93" />
        <feFuncB type="table" tableValues="0.02 0.11 0.66 0.24 0.85" />
      </feComponentTransfer>
    </filter>
  </svg>
);

export const DjRiso: React.FC<DjProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const story = H / W > 1.5;
  const pad = W * 0.06;
  const k = kick(f, 8);
  const t = phase(f);
  const crop = (story && p.cropStory) || p.crop || { s: 1, x: 0, y: 0 };
  const cutW = W * 0.9 * crop.s;
  const cutL = (W - cutW) / 2 + crop.x * W;
  const cutT = (story ? H * 0.2 : H * 0.17) + crop.y * W;
  const bob = Math.sin(2 * Math.PI * t) * W * 0.008;
  const mis = W * 0.004 * k; // registro riso que se descuadra con el bombo
  const outline = W * 0.007;
  const sticker = [0, 45, 90, 135, 180, 225, 270, 315].map((a) => {
    const r = (a * Math.PI) / 180;
    return `drop-shadow(${(Math.cos(r) * outline).toFixed(1)}px ${(Math.sin(r) * outline).toFixed(1)}px 0 ${C.bone})`;
  }).join(' ');
  const starS = W * 0.3;
  const words = p.dj.split(' ');

  return (
    <AbsoluteFill style={{ background: C.red, overflow: 'hidden' }}>
      <RisoFilter id="riso" />
      <Img src={asset(story ? 'riso-story.jpg' : 'riso-feed.jpg')} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.85 }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 60% 45% at 50% 45%, ${C.deep}dd 0%, ${C.deep}88 50%, transparent 80%)` }} />

      {/* pegatina: DJ en riso con contorno crema; detrás, la capa rosa descuadrada */}
      <Img src={asset(`dj/${p.photo}-cut.png`)} style={{
        position: 'absolute', left: cutL + mis + W * 0.012, top: cutT + bob - mis + W * 0.012, width: cutW,
        filter: 'brightness(0) invert(1)', opacity: 0.9, mixBlendMode: 'screen',
        WebkitMaskImage: 'linear-gradient(180deg, #000 70%, transparent 92%)',
      }} />
      <div style={{ position: 'absolute', left: cutL, top: cutT + bob, width: cutW, filter: sticker, WebkitMaskImage: 'linear-gradient(180deg, #000 72%, transparent 90%)' }}>
        <Img src={asset(`dj/${p.photo}-cut.png`)} style={{ width: cutW, display: 'block', filter: 'url(#riso) contrast(1.1)' }} />
      </div>

      {/* fecha en estrella de 8 puntas, como en los carteles de la diseñadora */}
      <div style={{ position: 'absolute', right: pad * 0.6, top: story ? 230 : pad * 0.6, width: starS, height: starS }}>
        <div style={{ position: 'absolute', inset: 0, transform: `rotate(${45 * t}deg)` }}><Octo size={starS} fill={C.orange} /></div>
        <div style={{ position: 'absolute', inset: 0, transform: `rotate(${45 * t}deg) scale(0.86)` }}><Octo size={starS} fill={C.pink} /></div>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: starS * 0.03 }}>
          <div style={{ color: C.bone, fontFamily: FONT.tag, fontStyle: 'italic', fontWeight: 700, fontSize: starS * 0.11, lineHeight: 1 }}>{p.day.toLowerCase()}</div>
          <Kufi text={p.date} height={starS * 0.15} fill={C.bone} />
        </div>
      </div>
      <div style={{ position: 'absolute', left: pad, top: story ? 250 : pad, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: W * 0.016 }}>
        <svg viewBox="0 0 2906 980" style={{ width: W * 0.4, filter: `drop-shadow(${W * 0.008}px ${W * 0.008}px 0 ${C.deep})` }}>
          <image href={asset('wordmark.svg')} width={2906} height={980} />
        </svg>
        <Tag W={W} size={0.024} bg={C.deep} ink={C.orange}>presenta</Tag>
      </div>

      {/* nombre en etiquetas apiladas, ligeramente inclinadas */}
      <div style={{ position: 'absolute', left: pad, right: pad, bottom: story ? H * 0.2 : H * 0.17, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: W * 0.012, transform: 'rotate(-3deg)', transformOrigin: 'left bottom' }}>
        {words.map((w, i) => (
          <Tag key={w + i} W={W} size={Math.min(0.15, 0.9 / Math.max(w.length, 4))} bg={i % 2 ? C.pink : C.orange} ink={i % 2 ? C.bone : C.red}
            style={{ marginLeft: i * W * 0.05, boxShadow: `${W * 0.008}px ${W * 0.008}px 0 ${C.deep}` }}>{w.toLowerCase()}</Tag>
        ))}
        <Tag W={W} size={0.024} bg={C.deep} ink={C.bone} style={{ marginTop: W * 0.01 }}>{p.from.toLowerCase()} · + {p.support.join(' · ').toLowerCase()}</Tag>
      </div>

      {/* pie: género + sala */}
      <div style={{ position: 'absolute', left: pad, right: pad, bottom: story ? H * 0.08 : pad, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <Tag W={W} size={0.022} bg={C.pink} ink={C.bone}>{p.genre.toLowerCase()}</Tag>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: W * 0.01 }}>
          <Tag W={W} size={0.024} bg={C.orange} ink={C.red}>{p.venue.name.toLowerCase()}</Tag>
          <Tag W={W} size={0.02} bg={C.deep} ink={C.bone}>{p.venue.hours} · {p.venue.city.toLowerCase()}</Tag>
        </div>
      </div>
      <Grain opacity={0.12} seed={f % 8} />
    </AbsoluteFill>
  );
};
