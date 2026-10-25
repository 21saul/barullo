import React from 'react';
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import { asset, C, CartelProps, FONT, Grain, kick, Kufi, Lettering, loadFonts, longDate, Octo, pad4, phase, Star } from './ui';

loadFonts();

// Mundo riso de la diseñadora: rojo, naranja y rosa, textos en etiquetas, fechas en estrella de 8 puntas.
// La alfombra es un render de Blender (banda 2160x1500 transparente, bucle de 240 frames).

const Tag: React.FC<{ W: number; bg?: string; ink?: string; size: number; children: React.ReactNode; style?: React.CSSProperties }>
  = ({ W, bg = C.orange, ink = C.red, size, children, style }) => (
    <div style={{
      display: 'inline-block', background: bg, color: ink, fontFamily: FONT.tag, fontWeight: 700, fontStyle: 'italic',
      fontSize: W * size, lineHeight: 1, letterSpacing: '0.04em', padding: `${W * size * 0.22}px ${W * size * 0.42}px ${W * size * 0.18}px`,
      whiteSpace: 'nowrap', ...style,
    }}>{children}</div>
  );

export const Alfombra: React.FC<CartelProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const story = H / W > 1.5;
  const pad = W * 0.06;
  const k = kick(f, 8);
  const t = phase(f);
  const rugSrc = asset(p.seq ? `${p.seq}/band_${pad4(f)}.png` : 'f02key/band_0060.png');
  const starS = story ? W * 0.4 : W * 0.3;
  const bandTop = story ? H * 0.37 : H * 0.29;
  const bandW = story ? W : W * 0.8;
  // el logo flota: dos armónicos del bucle, sin linealidad
  const bob = Math.sin(2 * Math.PI * t) * W * 0.012 + Math.sin(4 * Math.PI * t + 1) * W * 0.004;
  const tilt = Math.sin(2 * Math.PI * t + 0.6) * 1.2;
  const letW = story ? W * 0.8 : W * 0.62;
  const letTop = story ? H * 0.315 : H * 0.235;
  // registro riso: la capa rosa se desplaza un pelo en cada bombo
  const mis = W * 0.0025 * k;
  const barBottom = story ? H * 0.1 : pad;
  const barH = W * 0.082;

  return (
    <AbsoluteFill style={{ background: C.red, overflow: 'hidden' }}>
      {/* fondo: alfombra riso a baja dosis sobre rojo, con viñeta rojo oscuro para ordenar */}
      <Img src={asset(story ? 'riso-story.jpg' : 'riso-feed.jpg')} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.28, mixBlendMode: 'luminosity' }} />
      <Img src={asset(story ? 'riso-story.jpg' : 'riso-feed.jpg')} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.12, transform: `translate(${mis}px, ${-mis}px)`, mixBlendMode: 'screen' }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 80% 45% at 50% ${story ? 52 : 50}%, ${C.orange}55 0%, transparent 60%), linear-gradient(180deg, ${C.deep}cc 0%, transparent 30%, transparent 70%, ${C.deep}ee 100%)` }} />

      {/* sombra de la alfombra sobre el fondo */}
      <div style={{ position: 'absolute', left: (W - bandW * 0.72) / 2, width: bandW * 0.72, top: bandTop + bandW * 0.62 + bob * 0.3, height: W * 0.08, borderRadius: '50%', background: '#5A0806', filter: `blur(${W * 0.03}px)`, opacity: 0.55 }} />
      <Img src={rugSrc} style={{ position: 'absolute', left: (W - bandW) / 2, top: bandTop, width: bandW, height: bandW * 1500 / 2160 }} />

      {/* logo flotando sobre la alfombra */}
      <div style={{ position: 'absolute', left: (W - letW) / 2, top: letTop + bob, transform: `rotate(${tilt}deg)`, filter: `drop-shadow(0 ${W * 0.03}px ${W * 0.025}px #4A0503aa)` }}>
        <Lettering src="lettering-oro-perlas.png" width={letW} f={f} sweepAt={0.4} sweepLen={0.25} />
      </div>

      {/* cabecera: la fecha gigante va en la estrella de 8 puntas (gira 45° por bucle: cierra limpio) */}
      <div style={{ position: 'absolute', left: pad * 0.55, top: story ? 230 : pad * 0.45 }}>
        <div style={{ position: 'relative', width: starS, height: starS }}>
          <div style={{ position: 'absolute', inset: 0, transform: `rotate(${45 * t}deg)` }}><Octo size={starS} fill={C.orange} /></div>
          <div style={{ position: 'absolute', inset: 0, transform: `rotate(${45 * t}deg) scale(0.9)` }}><Octo size={starS} fill={C.deep} /></div>
          <div style={{ position: 'absolute', inset: 0, transform: `rotate(${45 * t}deg) scale(0.84)` }}><Octo size={starS} fill={C.orange} /></div>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: starS * 0.03 }}>
            <div style={{ color: C.red, fontFamily: FONT.tag, fontStyle: 'italic', fontWeight: 700, fontSize: starS * 0.1, lineHeight: 1 }}>{p.day.toLowerCase()}</div>
            <Kufi text={p.date} height={starS * 0.145} fill={C.red} />
          </div>
        </div>
      </div>
      <div style={{ position: 'absolute', left: pad * 0.55 + starS + W * 0.02, top: (story ? 230 : pad * 0.45) + starS * 0.3, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: W * 0.014 }}>
        <Tag W={W} size={story ? 0.036 : 0.028}>{longDate(p).replace(/^\S+ /, '')}</Tag>
        <Tag W={W} size={story ? 0.027 : 0.022} bg={C.pink} ink={C.bone}>{p.genre}</Tag>
        <Tag W={W} size={story ? 0.027 : 0.022} bg={C.deep} ink={C.orange}>{p.venue.name} · {p.venue.hours}</Tag>
      </div>

      {/* line up en etiquetas */}
      <div style={{ position: 'absolute', left: pad, bottom: barBottom + barH + W * 0.045 }}>
        <Tag W={W} size={0.017} bg={C.deep} ink={C.orange} style={{ letterSpacing: '0.3em', marginBottom: W * 0.016 }}>LINE UP</Tag>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: W * 0.012 }}>
          {p.lineup.map((n) => (
            <div key={n} style={{ background: C.orange, color: C.red, fontFamily: FONT.lineup, fontWeight: 800, fontStretch: '125%', fontSize: W * (story ? 0.068 : 0.05), lineHeight: 1, padding: `${W * 0.012}px ${W * 0.022}px ${W * 0.008}px`, whiteSpace: 'nowrap' }}>{n}</div>
          ))}
        </div>
      </div>

      {/* barra de datos en etiquetas */}
      <div style={{ position: 'absolute', left: pad, right: pad, bottom: barBottom, height: barH, display: 'flex', gap: W * 0.01, alignItems: 'stretch' }}>
        <div style={{ width: barH, background: C.deep, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Star size={W * 0.054} fill={C.orange} /></div>
        <div style={{ flex: 1, background: C.deep, color: C.bone, fontFamily: FONT.tag, fontWeight: 700, fontStyle: 'italic', fontSize: W * 0.019, lineHeight: 1.3, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: `0 ${W * 0.02}px`, letterSpacing: '0.03em' }}>
          <span style={{ color: C.orange }}>{p.venue.name}</span><span>{p.venue.address} · {p.venue.city}</span>
        </div>
        <div style={{ background: C.deep, color: C.bone, fontFamily: FONT.tag, fontWeight: 700, fontStyle: 'italic', fontSize: W * 0.019, lineHeight: 1.3, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: `0 ${W * 0.024}px` }}>
          <span>{p.day}</span><span>{p.venue.hours}</span>
        </div>
        <div style={{ width: W * 0.2, background: C.orange, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Kufi text={p.date} height={W * 0.03} fill={C.red} />
        </div>
      </div>
      <Grain opacity={0.09} seed={f % 8} />
    </AbsoluteFill>
  );
};
