import React from 'react';
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from 'remotion';
import { LedCarpet, useJson } from './Medalla';
import { asset, C, CartelProps, DataBar, DateBlock, Glint, Grain, kick, Lettering, Lineup, loadFonts, pad4 } from './ui';

loadFonts();

type Gem = Record<string, { x: number; y: number; vis: number }>;

/** CYBORG: la mascota en cromo negro con la medalla al pecho, sobre la alfombra LED.
 *  El render de Blender ya viene a tamaño de cartel (story o feed) con fondo transparente; frames 1..240. */
export const Cyborg: React.FC<CartelProps> = (p) => {
  const f = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const story = H / W > 1.5;
  const view = story ? 'story' : 'feed';
  const pad = W * 0.06;
  const bf = p.seq ? f + 1 : 1;
  const dir = p.seq || 'f03key';
  const gems = useJson<Gem>(`${dir}/gem_${view}.json`);
  const g = gems?.[String(bf)];
  const k = kick(f, 7);
  const shadow = `0 0 ${W * 0.012}px ${C.black}`;
  const barBottom = story ? H * 0.1 : pad;
  const lineupBottom = barBottom + W * 0.082 + W * 0.045;
  const letW = story ? W * 0.62 : W * 0.44;

  return (
    <AbsoluteFill style={{ background: C.black, overflow: 'hidden' }}>
      <LedCarpet story={story} f={f} base={0.3} scanAmt={0.5} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 55% 40% at 50% 40%, ${C.red}${Math.round(26 + 18 * k).toString(16)} 0%, transparent 70%), radial-gradient(ellipse 90% 70% at 50% 42%, transparent 30%, ${C.black}dd 85%)` }} />
      <Img src={asset(`${dir}/${view}_${pad4(bf)}.png`)} style={{ position: 'absolute', inset: 0, width: W, height: H }} />
      {g && <Glint x={g.x * W} y={g.y * H} size={W * 0.16} amount={k * 1.1} rot={22.5} />}
      <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.black}aa 0%, transparent 16%, transparent ${story ? 54 : 55}%, ${C.black}ee ${story ? 74 : 78}%, ${C.black} 100%)` }} />

      <div style={{ position: 'absolute', left: pad, top: story ? 270 : pad }}>
        <DateBlock p={p} W={W} h={story ? W * 0.115 : W * 0.1} shadow={shadow} />
      </div>
      <Lettering src="lettering-plata-grabada.png" width={letW} f={f} sweepAt={0.7}
        style={{ position: 'absolute', left: story ? (W - letW) / 2 : pad * 0.8, ...(story ? { top: H * 0.572 } : { top: H * 0.33 }) }} />
      <div style={{ position: 'absolute', left: pad, bottom: lineupBottom }}>
        <Lineup p={p} W={W} size={story ? 0.068 : 0.056} shadow={shadow} />
      </div>
      <DataBar p={p} W={W} pad={pad} bottom={barBottom} />
      <Grain opacity={0.05} seed={f % 8} />
    </AbsoluteFill>
  );
};
