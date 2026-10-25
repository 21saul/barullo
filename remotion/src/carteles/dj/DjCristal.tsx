import React from 'react';
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import { useJson } from '../Medalla';
import { C, easeInOut, FONT, Grain, kick, Kufi, phase } from '../ui';
import { Barra, Cabecera, cover, DIR, DjProps, Duotono, fit, foto, kufiW, octoPath, useFonts } from './comun';

// PLANTILLA B · CRISTAL (organización tipo Mondo: la foto manda, un bloque de texto compacto y centrado).
// Foto a sangre en duotono negro→acento→hueso con un velo de color translúcido; encima, un panel de cristal
// esmerilado (la misma foto pre-desenfocada por prep_foto.py) con fecha en Kufi, nombre y rol.

type Info = { w: number; h: number; bbox: number[] };

export const DjCristal: React.FC<DjProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const ready = useFonts();
  const story = H / W > 1.5;
  const pad = W * 0.06;
  const t = phase(f);
  const k = kick(f, 7);
  const info = useJson<Info>(`${DIR}fotos/${p.foto}.json`);

  // foto: empuje lento y deriva (un ciclo por bucle)
  const zoom = p.encuadre.zoom * (1.06 + 0.035 * (1 - Math.cos(2 * Math.PI * t)) / 2);
  const dx = W * 0.012 * Math.sin(2 * Math.PI * t);
  const box = info ? cover(info.w, info.h, W, H, p.encuadre.x, p.encuadre.y, zoom) : { left: 0, top: 0, width: W, height: H };
  const imgStyle = (src: string, extra?: React.CSSProperties): React.ReactNode => (
    <Img src={src} style={{ position: 'absolute', left: box.left + dx, top: box.top, width: box.width, height: box.height, filter: 'url(#duo)', ...extra }} />
  );

  // panel de cristal
  const barBottom = story ? H * 0.1 : pad * 0.9;
  const barTop = H - barBottom - W * 0.085;
  const PW = story ? W * 0.8 : W * 0.58;
  const PH = story ? W * 0.62 : W * 0.4;
  const PX = (W - PW) / 2;
  const PY = barTop - W * (story ? 0.05 : 0.04) - PH;
  const inner = PW - W * 0.1;
  const dateH = Math.min(W * (story ? 0.12 : 0.085), inner / (kufiW(p.fecha, 1)));
  const nameSize = ready ? fit(p.dj, "'Archivo'", 900, inner, W * (story ? 0.15 : 0.11), 'extra-condensed') : W * 0.1;

  // brillo que cruza el cristal (una vez por bucle) y velo que respira con el bombo
  const u = (t - 0.18) / 0.3;
  const sweep = u >= 0 && u <= 1 ? easeInOut(u) : -1;
  const veil = 0.3 + 0.06 * k;
  const shadow = `0 0 ${W * 0.012}px #0008`;

  return (
    <AbsoluteFill style={{ background: C.black, overflow: 'hidden' }}>
      <Duotono id="duo" sombra="#0B0B0B" medio={p.color} luz="#F2EFE8" contraste={1.15} />
      {imgStyle(foto(p))}
      {/* velo de color translúcido + viñeta */}
      <AbsoluteFill style={{ background: p.color2, opacity: veil, mixBlendMode: 'soft-light' }} />
      <AbsoluteFill style={{ background: `linear-gradient(180deg, #0B0B0Bb0 0%, transparent 22%, transparent 48%, #0B0B0B99 78%, #0B0B0Be6 100%)` }} />

      {/* panel de cristal: foto desenfocada recortada al panel */}
      <div style={{ position: 'absolute', left: PX, top: PY, width: PW, height: PH, overflow: 'hidden',
        border: `${W * 0.0018}px solid ${C.bone}66`, boxShadow: `0 ${W * 0.02}px ${W * 0.06}px #0007` }}>
        <div style={{ position: 'absolute', left: -PX, top: -PY, width: W, height: H }}>
          {imgStyle(foto(p, '-blur'))}
        </div>
        <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(160deg, ${p.color}AA 0%, ${p.color}66 55%, #0B0B0B88 100%)` }} />
        <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(180deg, #ffffff22 0%, transparent 30%)` }} />
        {/* trama de octogramas grabada en el cristal, se desplaza un módulo por bucle */}
        <svg width={PW} height={PH} style={{ position: 'absolute', inset: 0, opacity: 0.16 }}>
          {Array.from({ length: 6 }).map((_, row) => Array.from({ length: 6 }).map((__, col) => {
            const m = PW / 4.5;
            const x = col * m - m + t * m, y = row * m - m * 0.5;
            return <path key={`${row}-${col}`} d={octoPath(m * 0.42)} transform={`translate(${x} ${y})`} fill="none" stroke={C.bone} strokeWidth={W * 0.0012} />;
          }))}
        </svg>
        {sweep >= 0 && (
          <div style={{ position: 'absolute', inset: 0, mixBlendMode: 'screen',
            background: `linear-gradient(110deg, transparent ${sweep * 160 - 50}%, #ffffff30 ${sweep * 160 - 38}%, transparent ${sweep * 160 - 26}%)` }} />
        )}
        {/* contenido */}
        <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
          <div style={{ fontFamily: FONT.data, fontWeight: 700, fontSize: W * 0.02, letterSpacing: '0.42em', color: C.bone, marginBottom: W * 0.028, paddingLeft: '0.42em' }}>{p.dia}</div>
          <Kufi text={p.fecha} height={dateH} fill={C.bone} />
          <div style={{ fontFamily: FONT.lineup, fontWeight: 900, fontStretch: '62%', fontSize: nameSize, lineHeight: 0.9, color: C.bone, whiteSpace: 'nowrap',
            marginTop: W * 0.034, textShadow: `${W * 0.004}px ${W * 0.004}px 0 #E63B2E` }}>
            {p.dj}
          </div>
          <div style={{ fontFamily: FONT.data, fontSize: W * 0.0175, letterSpacing: '0.3em', color: C.bone, marginTop: W * 0.03, paddingLeft: '0.3em' }}>
            {p.rol} · {p.genero}
          </div>
        </div>
      </div>

      <Cabecera W={W} pad={pad} top={story ? H * 0.1 - W * 0.03 : pad * 0.8} pill={p.semana || p.rol} accent={C.bone} shadow={shadow} />
      <Barra p={p} W={W} pad={pad} bottom={barBottom} accent={p.color} dateInk={C.bone} />
      <Grain opacity={0.07} seed={f % 8} />
    </AbsoluteFill>
  );
};
