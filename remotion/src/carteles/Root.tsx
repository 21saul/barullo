import { AgendaFeed, agendaDefaults, AgendaStory, agendaStoryMetadata } from './Agenda';
import React from 'react';
import { Composition } from 'remotion';
import { Alfombra } from './Alfombra';
import { Cyborg } from './Cyborg';
import { DjFoto, DjMedalla, DjProps, DjRiso } from './Dj';
import { Medalla } from './Medalla';
import { Medallon, MedallonProps } from './Medallones';
import { CartelProps, FPS, LOOP } from './ui';
import { DjCristal } from './dj/DjCristal';
import { DjMedallon } from './dj/DjMedallon';
import { DjRecorte } from './dj/DjRecorte';
import { EJ_CRISTAL, EJ_MEDALLON, EJ_RECORTE } from './dj/ejemplos';

const DJ_PLANTILLAS = [
  ['DjMedallon', DjMedallon, EJ_MEDALLON],
  ['DjCristal', DjCristal, EJ_CRISTAL],
  ['DjRecorte', DjRecorte, EJ_RECORTE],
] as const;

// Entrada propia de los carteles (bocetos/animaciones/carteles/). Render:
//   npx remotion render src/carteles/index.ts Medalla-Story out.mp4 --public-dir=<barullo-render/carteles/public>
const STORY = { width: 2160, height: 3840 };
const FEED = { width: 2160, height: 2700 };

const base = (date: string): CartelProps => ({
  date, day: 'VIERNES', year: '2026', genre: 'CLUB · ELECTRÓNICA · VIGO',
  lineup: ['CARAMELORARØ', 'CONGUCHU', 'BOUZAS'],
  venue: { name: 'KINGSTON CLUB', address: 'RÚA ROGELIO ABALDE 18', city: 'VIGO', hours: '1:00 — 4:30' },
  seq: '',
});

const POSTERS = [
  ['Medalla', Medalla, '13.11'],
  ['Alfombra', Alfombra, '20.11'],
  ['Cyborg', Cyborg, '27.11'],
] as const;

// Serie MEDALLONES (bocetos/animaciones/carteles/medallones/): un medallón del catálogo por viernes.
const MEDALLONES = [
  ['oro-turquesa', '06.11'],
  ['oro-perlas', '13.11'],
  ['oro-girih-rubi', '20.11'],
  ['oro-esmeralda', '27.11'],
  ['oro-rosa-coral', '04.12'],
] as const;
const med = (i: number): MedallonProps => ({
  ...base(MEDALLONES[i][1]), genre: 'TRAP · REGGAETON · URBANO · DEMBOW', style: MEDALLONES[i][0], num: i + 1, frames: false,
});

// Plantillas de DJ invitado: los datos y la foto son de ejemplo (fotos CC de Wikimedia Commons, ver assets/dj/CREDITOS.txt).
const dj = (date: string, name: string, photo: string, crop: DjProps['crop'], cropStory?: DjProps['crop']): DjProps => ({
  ...base(date), dj: name, from: 'BERLÍN · DJ SET', photo, crop, cropStory, support: ['CONGUCHU', 'BOUZAS'],
});
const DJS = [
  ['DjMedalla', DjMedalla, dj('06.11', 'GRIZLI', 'grizli', { s: 1, x: 0, y: 0 })],
  ['DjFoto', DjFoto, dj('13.11', 'COIL', 'coil', { s: 1.05, x: -0.03, y: -0.15 }, { s: 1.4, x: -0.3, y: 0.0 })],
  ['DjRiso', DjRiso, dj('20.11', 'DJ GRIZLI', 'grizli', { s: 1, x: 0.06, y: 0 })],
] as const;

export const CartelesRoot: React.FC = () => (
  <>
    {DJS.map(([id, Comp, props]) => (
      <React.Fragment key={id}>
        <Composition id={`${id}-Story`} component={Comp} durationInFrames={LOOP} fps={FPS} {...STORY} defaultProps={props} />
        <Composition id={`${id}-Feed`} component={Comp} durationInFrames={LOOP} fps={FPS} {...FEED} defaultProps={props} />
      </React.Fragment>
    ))}
    {MEDALLONES.map(([style], i) => (
      <React.Fragment key={style}>
        <Composition id={`Medallon${i + 1}-Story`} component={Medallon} durationInFrames={LOOP} fps={FPS} {...STORY} defaultProps={med(i)} />
        <Composition id={`Medallon${i + 1}-Feed`} component={Medallon} durationInFrames={LOOP} fps={FPS} {...FEED} defaultProps={med(i)} />
      </React.Fragment>
    ))}
    {POSTERS.map(([id, Comp, date]) => (
      <React.Fragment key={id}>
        <Composition id={`${id}-Story`} component={Comp} durationInFrames={LOOP} fps={FPS} {...STORY} defaultProps={base(date)} />
        <Composition id={`${id}-Feed`} component={Comp} durationInFrames={LOOP} fps={FPS} {...FEED} defaultProps={base(date)} />
      </React.Fragment>
    ))}
    {/* Agenda del mes (bocetos/animaciones/carteles/05-agenda-mes/): 1080 de ancho, los datos en agenda-AAAA-MM.json */}
    <Composition id="Agenda-Story" component={AgendaStory} durationInFrames={600} fps={30} width={1080} height={1920} defaultProps={agendaDefaults} calculateMetadata={agendaStoryMetadata} />
    <Composition id="Agenda-Feed" component={AgendaFeed} durationInFrames={240} fps={30} width={1080} height={1350} defaultProps={agendaDefaults} />
    {/* Plantillas de anuncio de DJ A/B/C (bocetos/animaciones/carteles/04-dj-plantillas/, código en ./dj/) */}
    {DJ_PLANTILLAS.map(([id, Comp, props]) => (
      <React.Fragment key={id}>
        <Composition id={`${id}-Story`} component={Comp} durationInFrames={LOOP} fps={FPS} {...STORY} defaultProps={props} />
        <Composition id={`${id}-Feed`} component={Comp} durationInFrames={LOOP} fps={FPS} {...FEED} defaultProps={props} />
      </React.Fragment>
    ))}
  </>
);
