import React from 'react';
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import { useJson } from '../Medalla';
import { C, FONT, Grain, kick, Kufi, Octo, phase } from '../ui';
import { Barra, Cabecera, DIR, DjProps, fit, foto, kufiW, octoPath, useFonts } from './comun';

// PLANTILLA C · RECORTE: el/la DJ recortado/a (prep_foto.py, rembg) en blanco y negro con borde de pegatina,
// delante de la chapa negra girando y de franjas con su nombre en Kufi Barullo que corren en bucle exacto.
// Fondo de color plano (rojo Barullo por defecto), sello de fecha octogonal que late con el bombo.

type Info = { w: number; h: number; bbox: number[] };

export const DjRecorte: React.FC<DjProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const ready = useFonts();
  const story = H / W > 1.5;
  const pad = W * 0.06;
  const t = phase(f);
  const k = kick(f, 8);
  const info = useJson<Info>(`${DIR}fotos/${p.foto}.json`);

  const barBottom = story ? H * 0.1 : pad * 0.9;
  const barH = W * 0.085;
  const bandH = W * (story ? 0.15 : 0.12);
  const bandBottom = barBottom + barH + W * 0.03;

  // franjas de nombre en Kufi: cada una avanza exactamente una repetición por bucle
  const rowH = W * (story ? 0.12 : 0.1);
  const word = `${p.dj.toUpperCase()} · `;
  const rep = kufiW(word, rowH, 1) + rowH * 0.2;
  const rows = story ? 9 : 7;
  const rowsTop = story ? H * 0.155 : H * 0.135;
  const rowGap = rowH * 1.38;

  // recorte: encaja la caja del recorte en el hueco entre cabecera y banda del nombre
  const areaTop = story ? H * 0.2 : H * 0.14;
  const areaBot = H - bandBottom - bandH * 0.35; // la banda tapa la base del recorte
  const bb = info?.bbox ?? [0, 0, 1, 1];
  const iw = info?.w ?? 1000, ih = info?.h ?? 1500;
  const cutW = (bb[2] - bb[0]) * iw, cutH = (bb[3] - bb[1]) * ih;
  const s = Math.min((areaBot - areaTop) / cutH, (W * (story ? 0.98 : 0.8)) / cutW) * p.encuadre.zoom;
  const bob = W * 0.004 * Math.sin(2 * Math.PI * t * 2);
  const sc = 1 + 0.008 * k;
  const imgW = iw * s, imgH = ih * s;
  const left = W / 2 - ((bb[0] + bb[2]) / 2) * imgW + (p.encuadre.x - 0.5) * W;
  const top = areaBot - bb[3] * imgH + bob;

  const nameSize = ready ? fit(p.dj, "'Archivo'", 800, W - pad * 2.6, bandH * 0.78, 'expanded') : bandH * 0.6;
  const R = W * (story ? 0.5 : 0.4);
  const cy = story ? H * 0.43 : H * 0.42;
  const badge = W * (story ? 0.25 : 0.2);
  const shadow = `0 0 ${W * 0.008}px #0006`;

  return (
    <AbsoluteFill style={{ background: p.color, overflow: 'hidden' }}>
      {/* franjas de nombre en Kufi */}
      {Array.from({ length: rows }).map((_, r) => {
        const dir = r % 2 ? 1 : -1;
        const off = ((dir * t * rep) % rep + rep) % rep;
        const n = Math.ceil(W / rep) + 2;
        const solid = r % 3 === 1;
        return (
          <div key={r} style={{ position: 'absolute', top: rowsTop + r * rowGap, left: -rep + off, display: 'flex', gap: rowH * 0.2, opacity: solid ? 0.2 : 0.32 }}>
            {Array.from({ length: n }).map((__, j) => (
              <Kufi key={j} text={word} height={rowH} fill={solid ? C.black : 'none'}
                style={{ flex: 'none', ...(solid ? {} : { stroke: C.black, strokeWidth: 0.06 }) }} />
            ))}
          </div>
        );
      })}
      {/* chapa negra gigante detrás del DJ: gira 45° por bucle */}
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        <g transform={`translate(${W / 2} ${cy}) rotate(${45 * t})`}>
          <path d={octoPath(R)} fill={C.black} />
          <path d={octoPath(R * 0.86)} fill="none" stroke={C.bone} strokeWidth={W * 0.003} />
          <path d={octoPath(R * 0.8)} fill="none" stroke={p.color} strokeOpacity={0.6} strokeWidth={W * 0.002} />
        </g>
      </svg>
      {/* DJ recortado: borde de pegatina + foto en B/N contrastada */}
      <div style={{ position: 'absolute', left, top, width: imgW, height: imgH, transform: `scale(${sc})`, transformOrigin: '50% 100%' }}>
        <Img src={foto(p, '-borde', 'png')} style={{ position: 'absolute', inset: 0, width: imgW, height: imgH, filter: `drop-shadow(${W * 0.012}px ${W * 0.014}px 0 #0B0B0B)` }} />
        <Img src={foto(p, '-cut', 'png')} style={{ position: 'absolute', inset: 0, width: imgW, height: imgH, filter: 'grayscale(1) contrast(1.35) brightness(1.06)' }} />
      </div>

      {/* sello de fecha */}
      <div style={{ position: 'absolute', right: pad * 0.8, top: story ? H * 0.2 : H * 0.15, transform: `rotate(${-8 + 3 * Math.sin(2 * Math.PI * t)}deg) scale(${1 + 0.03 * k})` }}>
        <Octo size={badge} fill={C.bone}>
          <div style={{ fontFamily: FONT.data, fontWeight: 700, fontSize: badge * 0.075, letterSpacing: '0.2em', color: C.black, marginBottom: badge * 0.04, paddingLeft: '0.2em' }}>{p.dia}</div>
          <Kufi text={p.fecha} height={Math.min(badge * 0.2, (badge * 0.62) / kufiW(p.fecha, 1))} fill={C.black} />
          <div style={{ fontFamily: FONT.data, fontWeight: 700, fontSize: badge * 0.065, letterSpacing: '0.12em', color: '#E63B2E', marginTop: badge * 0.05 }}>{p.sala.horario}</div>
        </Octo>
      </div>

      {/* banda con el nombre */}
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: bandBottom, height: bandH, background: C.black, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontFamily: FONT.lineup, fontWeight: 800, fontStretch: '125%', fontSize: nameSize, lineHeight: 1, color: C.bone, whiteSpace: 'nowrap' }}>{p.dj}</div>
      </div>
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: bandBottom + bandH, height: W * 0.05, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontFamily: FONT.data, fontWeight: 700, fontSize: W * 0.017, letterSpacing: '0.32em', color: C.bone, background: C.black, padding: `${W * 0.008}px ${W * 0.02}px ${W * 0.008}px ${W * 0.026}px` }}>
          {p.rol} · {p.genero}
        </div>
      </div>

      <Cabecera W={W} pad={pad} top={story ? H * 0.1 - W * 0.03 : pad * 0.8} pill={p.semana || p.rol} accent={C.black} shadow={shadow} />
      <Barra p={p} W={W} pad={pad} bottom={barBottom} accent={C.bone} dateInk={C.black} />
      <Grain opacity={0.08} seed={f % 8} />
    </AbsoluteFill>
  );
};
