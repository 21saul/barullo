import React from 'react';
import { Composition } from 'remotion';
import { CHARACTER_SECONDS, HeroCharacter } from './compositions/HeroCharacter';
import { CHARACTER3D_SECONDS, HeroCharacter3D } from './compositions/HeroCharacter3D';
import { HeroMascot, MASCOT_SECONDS } from './compositions/HeroMascot';
import { FLYER_SECONDS, FlyerAnim } from './compositions/FlyerAnim';
import { HERO_SECONDS, HeroLoop } from './compositions/HeroLoop';
import { STORY_SECONDS, StoryEvent } from './compositions/StoryEvent';
import { DEMO_EVENT, eventSchema } from './lib/event';

const FPS = 30;

export const RemotionRoot: React.FC = () => (
  <>
    {/* Hero: bucle perfecto de 6 s. Vertical es el principal (móvil). */}
    <Composition
      id="HeroLoop"
      component={HeroLoop}
      durationInFrames={HERO_SECONDS * FPS}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={{ grain: true }}
    />
    <Composition
      id="HeroLoopWide"
      component={HeroLoop}
      durationInFrames={HERO_SECONDS * FPS}
      fps={FPS}
      width={1920}
      height={1080}
      defaultProps={{ grain: true }}
    />

    {/* Héroe con la mascota de Barullo (3D, cromo negro): bucle perfecto de 8 s, a sangre.
        Cuadrado para móvil y 21:9 para escritorio (824 de alto: H.264 4:2:0 exige pares). */}
    <Composition id="HeroCharacter" component={HeroMascot} durationInFrames={MASCOT_SECONDS * FPS} fps={FPS} width={1080} height={1080} />
    <Composition id="HeroCharacterWide" component={HeroMascot} durationInFrames={MASCOT_SECONDS * FPS} fps={FPS} width={1920} height={824} />

    {/* Personaje 3D anterior (retrato): rosa hyperpop y la prueba en cromo negro. */}
    {(
      [
        ['HeroCharacterPink', 'pink', 1080, 720],
        ['HeroCharacterPinkWide', 'pink', 1920, 1080],
        ['HeroCharacterHeadBlack', 'black', 1080, 720],
      ] as const
    ).map(([id, variant, width, height]) => (
      <Composition
        key={id}
        id={id}
        component={HeroCharacter3D}
        durationInFrames={CHARACTER3D_SECONDS * FPS}
        fps={FPS}
        width={width}
        height={height}
        defaultProps={{ variant }}
      />
    ))}

    {/* Versión vectorial (SVG) del personaje, de respaldo. */}
    <Composition
      id="HeroCharacterVector"
      component={HeroCharacter}
      durationInFrames={CHARACTER_SECONDS * FPS}
      fps={FPS}
      width={1080}
      height={720}
    />
    <Composition
      id="HeroCharacterVectorWide"
      component={HeroCharacter}
      durationInFrames={CHARACTER_SECONDS * FPS}
      fps={FPS}
      width={1920}
      height={1080}
    />

    {/* Plantillas de Instagram, parametrizadas por evento. */}
    <Composition
      id="StoryEvent"
      component={StoryEvent}
      schema={eventSchema}
      durationInFrames={STORY_SECONDS * FPS}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={DEMO_EVENT}
    />
    <Composition
      id="FlyerAnim"
      component={FlyerAnim}
      schema={eventSchema}
      durationInFrames={FLYER_SECONDS * FPS}
      fps={FPS}
      width={1080}
      height={1080}
      defaultProps={DEMO_EVENT}
    />
  </>
);
