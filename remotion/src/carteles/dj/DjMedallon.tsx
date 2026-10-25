import React from 'react';
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import { useJson } from '../Medalla';
import { asset, C, easeInOut, FONT, Glint, Grain, kick, LOOP, phase } from '../ui';
import { Barra, Cabecera, cover, DIR, DjProps, fechaLarga, fit, foto, octoPath, useFonts } from './comun';

// PLANTILLA A · MEDALLÓN: la foto del/de la DJ dentro del hueco de la medalla «o» (render de Blender de frente,
// medallon_marco.py). El brillo del oro se mueve fundiendo N variantes de luz; el conjunto se mece en 3D (CSS),
// foto y medalla juntas, y las puntas destellan con el bombo.

type Marco = { hole: [number, number][]; tips: [number, number][]; n: number };
type Info = { w: number; h: number; bbox: number[] };

export const DjMedallon: React.FC<DjProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const ready = useFonts();
  const story = H / W > 1.5;
  const pad = W * 0.06;
  const dir = `${DIR}marco-${p.medalla}`;
  const marco = useJson<Marco>(`${dir}/marco.json`);
  const info = useJson<Info>(`${DIR}fotos/${p.foto}.json`);
  const t = phase(f);
  const k = kick(f, 6);

  // medalla
  const S = story ? W * 1.0 : W * 0.7;
  const cx = W / 2;
  const cy = story ? H * 0.415 : H * 0.4;
  const n = Math.max(1, p.variantes || marco?.n || 1);
  const lv = t * n; // variante de luz continua (cíclica)
  const i0 = Math.floor(lv) % n, i1 = (i0 + 1) % n;
  const mixv = easeInOut(lv - Math.floor(lv));

  // hueco: polígono para recortar la foto (ligeramente crecido: el filete de oro tapa el borde)
  const hole = marco?.hole ?? [];
  const hc = hole.reduce((a, [x, y]) => [a[0] + x / hole.length, a[1] + y / hole.length], [0, 0]);
  const grow = 1.035;
  const clip = hole.length ? `polygon(${hole.map(([x, y]) => `${((hc[0] + (x - hc[0]) * grow) * 100).toFixed(2)}% ${((hc[1] + (y - hc[1]) * grow) * 100).toFixed(2)}%`).join(',')})` : 'none';
  const xs = hole.map((q) => q[0]), ys = hole.map((q) => q[1]);
  const hb = hole.length ? { x0: Math.min(...xs), y0: Math.min(...ys), x1: Math.max(...xs), y1: Math.max(...ys) } : { x0: 0.25, y0: 0.25, x1: 0.75, y1: 0.75 };
  const bw = (hb.x1 - hb.x0) * S, bh = (hb.y1 - hb.y0) * S;
  const zoom = p.encuadre.zoom * (1.04 + 0.03 * Math.sin(2 * Math.PI * t));
  const ph = info ? cover(info.w, info.h, bw, bh, p.encuadre.x, p.encuadre.y, zoom) : { left: 0, top: 0, width: bw, height: bh };

  // vaivén 3D de todo el medallón (un ciclo por bucle)
  const ry = 5 * Math.sin(2 * Math.PI * t);
  const rx = 3 * Math.cos(2 * Math.PI * t);
  const bob = W * 0.006 * Math.sin(4 * Math.PI * t);

  // barrido de brillo sobre el metal (2 por bucle)
  const sweep = (a: number) => { const u = ((t - a + 1) % 1) / 0.22; return u <= 1 ? easeInOut(u) : -1; };
  const sw = Math.max(sweep(0.1), sweep(0.6));
  const medalUrl = (i: number) => asset(`${dir}/l_${i}.png`);

  // texto
  const nameW = W - pad * 2;
  const nameSize = ready ? fit(p.dj, "'Archivo'", 800, nameW, W * (story ? 0.13 : 0.1), 'expanded') : W * 0.1;
  const barBottom = story ? H * 0.1 : pad * 0.9;
  const barH = W * 0.085;
  const glow = p.color2;
  const shadow = `0 0 ${W * 0.01}px ${C.black}`;

  return (
    <AbsoluteFill style={{ background: '#0B0B0B', overflow: 'hidden' }}>
      {/* halo de color detrás de la medalla, late con el bombo */}
      <div style={{ position: 'absolute', left: cx - S * 0.75, top: cy - S * 0.75, width: S * 1.5, height: S * 1.5, borderRadius: '50%',
        background: `radial-gradient(circle, ${glow}${Math.round(70 + 40 * k).toString(16)} 0%, ${glow}22 35%, transparent 62%)` }} />
      {/* anillos de octograma que giran 45° por bucle (simetría 8: bucle exacto) */}
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        <g transform={`translate(${cx} ${cy})`} fill="none" stroke={p.color} strokeOpacity={0.35} strokeWidth={W * 0.0014}>
          {[0.55, 0.62, 0.69].map((r, j) => (
            <path key={j} d={octoPath(S * r, (j % 2 ? -1 : 1) * (Math.PI / 4) * t + j * (Math.PI / 8))} strokeOpacity={0.36 - j * 0.1} />
          ))}
        </g>
      </svg>

      {/* medallón: foto + medalla en el mismo plano 3D */}
      <div style={{ position: 'absolute', left: cx - S / 2, top: cy - S / 2 + bob, width: S, height: S, perspective: S * 3 }}>
        <div style={{ position: 'absolute', inset: 0, transform: `rotateY(${ry}deg) rotateX(${rx}deg)`, transformStyle: 'preserve-3d' }}>
          <div style={{ position: 'absolute', inset: 0, clipPath: clip }}>
            <div style={{ position: 'absolute', left: hb.x0 * S, top: hb.y0 * S, width: bw, height: bh, overflow: 'hidden', background: '#111' }}>
              <Img src={foto(p)} style={{ position: 'absolute', ...ph, filter: 'contrast(1.06) saturate(0.95)' }} />
              {/* sombra interior: la foto queda "dentro" del metal */}
              <div style={{ position: 'absolute', inset: 0, boxShadow: `inset 0 ${S * 0.02}px ${S * 0.06}px #000c` }} />
            </div>
          </div>
          <Img src={medalUrl(i0)} style={{ position: 'absolute', inset: 0, width: S, height: S, filter: `drop-shadow(0 ${W * 0.02}px ${W * 0.035}px #000d)` }} />
          <Img src={medalUrl(i1)} style={{ position: 'absolute', inset: 0, width: S, height: S, opacity: mixv }} />
          {sw >= 0 && (
            <div style={{
              position: 'absolute', inset: 0, mixBlendMode: 'screen',
              WebkitMaskImage: `url(${medalUrl(i0)})`, WebkitMaskSize: '100% 100%', maskImage: `url(${medalUrl(i0)})`, maskSize: '100% 100%',
              background: `linear-gradient(115deg, transparent ${sw * 150 - 40}%, rgba(255,240,215,0.55) ${sw * 150 - 30}%, transparent ${sw * 150 - 20}%)`,
            }} />
          )}
        </div>
      </div>
      {/* destellos en las puntas, uno por tiempo de compás */}
      {(marco?.tips ?? []).map(([x, y], j) => {
        const beat = (t * 16 - j * 2 + 16) % 16;
        const a = beat < 1.2 ? Math.sin((beat / 1.2) * Math.PI) : 0;
        return <Glint key={j} x={cx - S / 2 + x * S} y={cy - S / 2 + y * S + bob} size={W * 0.12} amount={a * 0.9} color={glow} rot={45 * t} />;
      })}

      {/* sombreado para el texto */}
      <AbsoluteFill style={{ background: `linear-gradient(180deg, #0B0B0Bcc 0%, transparent 14%, transparent 62%, #0B0B0Be0 80%, #0B0B0B 100%)` }} />

      <Cabecera W={W} pad={pad} top={story ? H * 0.1 - W * 0.03 : pad * 0.8} pill={p.rol} accent={p.color} shadow={shadow} />
      {p.semana && (
        <div style={{ position: 'absolute', left: pad, top: (story ? H * 0.1 - W * 0.03 : pad * 0.8) + W * 0.09, fontFamily: FONT.data, fontSize: W * 0.016, letterSpacing: '0.32em', color: C.bone, opacity: 0.8, textShadow: shadow }}>
          {p.semana}
        </div>
      )}

      {/* nombre y datos */}
      <div style={{ position: 'absolute', left: pad, right: pad, bottom: barBottom + barH + W * (story ? 0.06 : 0.035), textAlign: 'center' }}>
        <div style={{ fontFamily: FONT.data, fontSize: W * 0.0175, letterSpacing: '0.34em', color: p.color, marginBottom: W * 0.018, textShadow: shadow }}>
          {p.rol} · {p.genero}
        </div>
        <div style={{ fontFamily: FONT.lineup, fontWeight: 800, fontStretch: '125%', fontSize: nameSize, lineHeight: 0.95, color: C.bone, whiteSpace: 'nowrap', textShadow: `0 ${W * 0.006}px ${W * 0.02}px #000` }}>
          {p.dj}
        </div>
        <div style={{ fontFamily: FONT.data, fontWeight: 700, fontSize: W * 0.021, letterSpacing: '0.3em', color: C.bone, marginTop: W * 0.024, textShadow: shadow }}>
          {fechaLarga(p)}
        </div>
      </div>
      <Barra p={p} W={W} pad={pad} bottom={barBottom} accent="#E63B2E" />
      <Grain opacity={0.05} seed={f % 8} />
    </AbsoluteFill>
  );
};

export const DJ_LOOP = LOOP;
