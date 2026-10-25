import { cancelRender, continueRender, delayRender, staticFile } from 'remotion';

/**
 * Fuentes locales (public/fonts) para que el render no dependa de la red.
 * Anton (OFL) = display condensada · Space Grotesk (OFL) = UI ·
 * Permanent Marker (Apache 2.0) = acento manuscrito.
 */
const FACES: Array<[family: string, file: string, weight: string]> = [
  ['BarulloDisplay', 'Anton-Regular.ttf', '400'],
  ['BarulloUI', 'SpaceGrotesk.ttf', '300 700'],
  ['BarulloScribble', 'PermanentMarker.ttf', '400'],
];

let started = false;

export const loadFonts = () => {
  if (started || typeof document === 'undefined') return;
  started = true;
  const handle = delayRender('Cargando fuentes Barullo');
  Promise.all(
    FACES.map(([family, file, weight]) =>
      new FontFace(family, `url(${staticFile(`fonts/${file}`)})`, { weight })
        .load()
        .then((face) => document.fonts.add(face)),
    ),
  )
    .then(() => continueRender(handle))
    // Sin fuentes el wordmark sale con Impact: mejor fallar que renderizar mal.
    .catch((err) => cancelRender(err));
};
