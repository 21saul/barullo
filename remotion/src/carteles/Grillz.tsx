import React from 'react';
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import G from './data/grillz.json';
import type { DjProps } from './Dj';
import { asset, C, DataBar, easeInOut, FONT, Glint, Grain, kick, loadFonts, phase } from './ui';

loadFonts();

// Cartel GRILLZ: primer plano de Lobezno en rojo y negro con un grill de Blender en la boca.
// Arriba el lettering kufi iced sobre fundas de oro, abajo la fecha en una placa de ónix (bocetos/animaciones/carteles/06-grillz/).
// La foto, los grills y la encía se dibujan en px de un cartel de 1080 de ancho (grillz.json) y se escalan con W.

const fit = (text: string, width: number, max: number, em = 0.9) => Math.min(max, width / (Math.max(text.length, 1) * em));

type Box = { left: number; top: number; width: number; height: number };

/** Capa de grill: brillo que la recorre (enmascarado por su alfa) y golpe de luz en cada bombo. */
const GrillLayer: React.FC<{ src: string; box: Box; u: number; f: number; k: number; sweepAt: number[] }> = ({ src, box, u, f, k, sweepAt }) => {
  const url = asset(src);
  const t = phase(f);
  const pos = sweepAt.map((a) => (t - a) / 0.14).find((v) => v >= 0 && v <= 1);
  const style: React.CSSProperties = { position: 'absolute', left: box.left * u, top: box.top * u, width: box.width * u, height: box.height * u };
  return (
    <>
      <Img src={url} style={{ ...style, filter: `brightness(${1 + 0.22 * k}) contrast(${1 + 0.06 * k})` }} />
      {pos !== undefined && (
        <div style={{
          ...style, mixBlendMode: 'screen',
          WebkitMaskImage: `url(${url})`, WebkitMaskSize: '100% 100%', maskImage: `url(${url})`, maskSize: '100% 100%',
          background: `linear-gradient(100deg, transparent ${easeInOut(pos) * 160 - 40}%, rgba(255,250,240,0.95) ${easeInOut(pos) * 160 - 26}%, transparent ${easeInOut(pos) * 160 - 12}%)`,
        }} />
      )}
    </>
  );
};

/** Destellos sobre gemas reales del render: en cada bombo se encienden unas pocas, sin repetir el patrón. */
const Sparkles: React.FC<{ pts: number[][]; u: number; f: number; per: number; size: number; seed: number }> = ({ pts, u, f, per, size, seed }) => {
  const beat = Math.floor((f / 30) * 2);
  const ph = (f / 30) * 2 - beat;
  const out: React.ReactNode[] = [];
  for (let i = 0; i < per; i++) {
    const idx = Math.abs((beat * 7919 + i * 104729 + seed * 31) % pts.length);
    const delay = i * 0.12;
    const x = ph - delay;
    const amt = x < 0 ? 0 : Math.sin(Math.min(1, x / 0.55) * Math.PI);
    const [px, py] = pts[idx];
    out.push(<Glint key={i} x={px * u} y={py * u} size={size * u} amount={amt} color="#FFFFFF" rot={(beat * 23 + i * 40) % 90} />);
  }
  return <>{out}</>;
};

export const Grillz: React.FC<DjProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const u = W / 1080;
  const pad = W * 0.06;
  const k = kick(f, 6);
  const t = phase(f);
  // empuje lento hacia la boca a lo largo del bucle + sacudida corta en cada bombo; todo lo pegado a la foto va en la misma caja
  const zoom = 1.0 + 0.035 * (0.5 - 0.5 * Math.cos(2 * Math.PI * t)) + 0.008 * k;
  const nameSize = fit(p.dj, W - pad * 2, W * 0.15);
  const line = `${W * 0.0016}px solid ${C.bone}4d`;
  const mono = (size: number, color: string = C.bone): React.CSSProperties => ({
    fontFamily: FONT.data, fontSize: W * size, letterSpacing: '0.26em', color, whiteSpace: 'nowrap', lineHeight: 1,
  });

  return (
    <AbsoluteFill style={{ background: C.black, overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, transform: `scale(${zoom})`, transformOrigin: `50% ${(G.top.top / 1920) * 100 + 6}%` }}>
        <Img src={asset('grillz/base.jpg')} style={{ position: 'absolute', left: 0, top: 0, width: W, height: H }} />
        <GrillLayer src="grillz/bottom.png" box={G.bottom} u={u} f={f} k={k} sweepAt={[0.3, 0.8]} />
        <GrillLayer src="grillz/top.png" box={G.top} u={u} f={f} k={k} sweepAt={[0.05, 0.55]} />
        <Img src={asset('grillz/gum.png')} style={{ position: 'absolute', left: G.gum.left * u, top: G.gum.top * u, width: G.gum.width * u, height: G.gum.height * u }} />
        <Sparkles pts={G.glintsTop} u={u} f={f} per={4} size={46} seed={1} />
        <Sparkles pts={G.glintsBottom} u={u} f={f} per={2} size={36} seed={2} />
      </div>

      {/* luz: viñeta y golpe rojo con el bombo */}
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 70% 42% at 50% 40%, transparent 40%, ${C.black}b3 100%)` }} />
      <AbsoluteFill style={{ background: C.red, mixBlendMode: 'soft-light', opacity: 0.18 * k }} />
      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.black}d9 0%, transparent 13%, transparent 62%, ${C.black}e6 74%, ${C.black} 84%)` }} />

      {/* cabecera */}
      <div style={{ position: 'absolute', left: pad, right: pad, top: W * 0.06, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <svg viewBox="0 0 2906 980" style={{ width: W * 0.26 }}>
          <image href={asset('wordmark.svg')} width={2906} height={980} />
        </svg>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: W * 0.009, paddingTop: W * 0.006 }}>
          {p.genre.split(' · ').map((g, i, a) => <div key={g} style={mono(0.015, i === a.length - 1 ? C.red : C.bone)}>{g}</div>)}
        </div>
      </div>

      {/* laterales */}
      <div style={{ ...mono(0.0125, `${C.bone}99`), position: 'absolute', right: W * 0.022, top: H * 0.3, writingMode: 'vertical-rl', letterSpacing: '0.45em' }}>BARULLO CLVB — {p.venue.city}</div>
      <div style={{ ...mono(0.0125, `${C.bone}99`), position: 'absolute', left: W * 0.022, top: H * 0.3, writingMode: 'vertical-rl', transform: 'rotate(180deg)', letterSpacing: '0.45em' }}>{p.venue.name} — {p.venue.hours}</div>

      {/* bloque del DJ */}
      <div style={{ position: 'absolute', left: pad, right: pad, top: H * 0.695 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', paddingBottom: W * 0.014, borderBottom: line }}>
          <div style={{ ...mono(0.0165, C.red), fontWeight: 700 }}>DJ SET · CABEZA DE CARTEL</div>
          <div style={mono(0.0165, `${C.bone}b3`)}>LINE UP</div>
        </div>
        <div style={{ position: 'relative', marginTop: W * 0.03 }}>
          {/* copia roja desplazada: tiembla con el bombo */}
          <div style={{ position: 'absolute', left: W * 0.006 * k, top: 0, fontFamily: FONT.lineup, fontWeight: 900, fontStretch: '125%', fontSize: nameSize, lineHeight: 0.86, letterSpacing: '-0.03em', color: C.red, whiteSpace: 'nowrap', opacity: 0.85 * k }}>{p.dj}</div>
          <div style={{ position: 'relative', fontFamily: FONT.lineup, fontWeight: 900, fontStretch: '125%', fontSize: nameSize, lineHeight: 0.86, letterSpacing: '-0.03em', color: C.bone, whiteSpace: 'nowrap' }}>{p.dj}</div>
        </div>
        <div style={{ ...mono(0.0165, `${C.bone}b3`), marginTop: W * 0.02 }}>{p.from}</div>
        <div style={{ ...mono(0.0145, C.red), fontWeight: 700, marginTop: W * 0.045 }}>+ RESIDENTES</div>
        <div style={{ fontFamily: FONT.lineup, fontWeight: 800, fontStretch: '125%', fontSize: W * 0.042, lineHeight: 1, letterSpacing: '-0.01em', color: C.bone, marginTop: W * 0.012, whiteSpace: 'nowrap' }}>{p.support.join(' / ')}</div>
      </div>

      <DataBar p={p} W={W} pad={W * 0.037} bottom={W * 0.045} />
      <Grain opacity={0.11} seed={f % 8} />
    </AbsoluteFill>
  );
};
