import React, { useEffect, useState } from 'react';
import { AbsoluteFill, continueRender, delayRender, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import { asset, C, CartelProps, DataBar, DateBlock, Glint, Grain, kick, Lettering, Lineup, loadFonts, pad4, phase } from './ui';

loadFonts();

type Gem = Record<string, { x: number; y: number; vis: number }>;
export const useJson = <T,>(file: string): T | null => {
  const [data, setData] = useState<T | null>(null);
  const [h] = useState(() => delayRender(file));
  useEffect(() => {
    fetch(asset(file)).then((r) => r.json()).then((j) => { setData(j); continueRender(h); }).catch(() => continueRender(h));
  }, [file, h]);
  return data;
};

/** Alfombra LED (píxeles de nudo) muy tenue, con un barrido de luz que baja una vez por bucle y pulso de bombo. */
export const LedCarpet: React.FC<{ story: boolean; f: number; base?: number; scanAmt?: number }> = ({ story, f, base = 0.2, scanAmt = 0.4 }) => {
  const src = asset(story ? 'led-story.jpg' : 'led-feed.jpg');
  const y = -30 + 160 * phase(f); // % de alto: entra por arriba y sale por abajo
  const k = kick(f, 6);
  const mask = `linear-gradient(180deg, transparent ${y - 14}%, #000 ${y}%, transparent ${y + 14}%)`;
  return (
    <AbsoluteFill>
      <Img src={src} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: base + 0.035 * k }} />
      <Img src={src} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: scanAmt, WebkitMaskImage: mask, maskImage: mask }} />
    </AbsoluteFill>
  );
};

const MLOOP = 120; // la medalla da medio giro cada 4 s (idéntico al frame 0), se repite 2 veces en 8 s

export const Medalla: React.FC<CartelProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const story = H / W > 1.5;
  const pad = W * 0.06;
  const mf = p.seq ? f % MLOOP : 56;
  const dir = p.seq || 'f01key';
  const gems = useJson<Gem>(`${dir}/gem.json`);
  const g = gems?.[String(mf)];

  // caja de la medalla (frame cuadrado de Blender)
  const M = story ? { s: W * 0.74, cx: W * 0.54, cy: H * 0.35 } : { s: W * 0.58, cx: W * 0.66, cy: H * 0.33 };
  const k = kick(f, 7);
  const shadow = `0 0 ${W * 0.012}px ${C.black}`;
  const barBottom = story ? H * 0.1 : pad;
  const lineupBottom = barBottom + W * 0.082 + W * 0.045;
  const letW = story ? W * 0.76 : W * 0.52;

  return (
    <AbsoluteFill style={{ background: C.black, overflow: 'hidden' }}>
      <LedCarpet story={story} f={f} />
      {/* viñeta: el centro respira, los bordes caen a negro */}
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 70% 55% at 50% ${story ? 38 : 40}%, transparent 0%, ${C.black}aa 60%, ${C.black} 100%)` }} />
      {/* halo rojo detrás de la joya, late con el bombo */}
      <div style={{
        position: 'absolute', left: M.cx - M.s * 0.5, top: M.cy - M.s * 0.5, width: M.s, height: M.s, borderRadius: '50%',
        background: `radial-gradient(circle, ${C.red}${Math.round(40 + 30 * k).toString(16)} 0%, ${C.red}10 38%, transparent 62%)`,
      }} />
      <Img src={asset(p.seq ? `${dir}/m_${pad4(mf)}.png` : `${dir}/m_0056.png`)}
        style={{ position: 'absolute', left: M.cx - M.s / 2, top: M.cy - M.s / 2, width: M.s, height: M.s, filter: `drop-shadow(0 ${W * 0.02}px ${W * 0.04}px #000c)` }} />
      {g && <Glint x={M.cx - M.s / 2 + g.x * M.s - M.s * 0.03} y={M.cy - M.s / 2 + g.y * M.s - M.s * 0.07} size={W * 0.2} amount={k * g.vis * g.vis * 1.1} rot={(phase(f) * 90) % 90} />}

      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.black}cc 0%, transparent 18%, transparent 58%, ${C.black}e6 82%, ${C.black} 100%)` }} />

      <div style={{ position: 'absolute', left: pad, top: story ? 270 : pad }}>
        <DateBlock p={p} W={W} h={story ? W * 0.115 : W * 0.1} shadow={shadow} />
      </div>

      <Lettering src="lettering-plata-grabada.png" width={letW} f={f}
        style={{ position: 'absolute', left: story ? (W - letW) / 2 : pad * 0.8, bottom: lineupBottom + (story ? W * 0.27 : W * 0.215) }} />

      <div style={{ position: 'absolute', left: pad, bottom: lineupBottom }}>
        <Lineup p={p} W={W} size={story ? 0.075 : 0.06} shadow={shadow} />
      </div>
      <DataBar p={p} W={W} pad={pad} bottom={barBottom} />
      <Grain opacity={0.05} seed={f % 8} />
    </AbsoluteFill>
  );
};
