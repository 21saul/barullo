import React from 'react';
import { Composition, registerRoot } from 'remotion';
import { Grillz } from './Grillz';
import { FPS, LOOP } from './ui';
import type { DjProps } from './Dj';

// Entrada propia del cartel GRILLZ (bocetos/animaciones/carteles/06-grillz/). Render:
//   npx remotion render src/carteles/GrillzRoot.tsx Grillz-Story out.mp4 --public-dir=<barullo-render/carteles/public>
// La foto manda la resolución: 1080 de ancho.
const props: DjProps = {
  date: '13.11', day: 'VIERNES', year: '2026', genre: 'CLUB · ELECTRÓNICA · VIGO',
  lineup: ['NOMBRE DJ', 'CONGUCHU', 'BOUZAS'],
  venue: { name: 'KINGSTON CLUB', address: 'RÚA ROGELIO ABALDE 18', city: 'VIGO', hours: '1:00 — 4:30' },
  seq: '',
  dj: 'NOMBRE DJ', from: '[CIUDAD] · EXTENDED SET', photo: '', support: ['CONGUCHU', 'BOUZAS'],
};

const GrillzRoot: React.FC = () => (
  <Composition id="Grillz-Story" component={Grillz} durationInFrames={LOOP} fps={FPS} width={1080} height={1920} defaultProps={props} />
);

registerRoot(GrillzRoot);
