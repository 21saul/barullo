# Héroes de sección

Cada página interior abre con un héroe a sangre: la animación es el fondo y el
título (h1 de verdad, en HTML) va dentro, abajo a la izquierda. Es la idea de
rehojo.com, donde cada sección tiene su propia escena, traída al mundo Barullo:
alfombra, kufi, plata, pavés y neón.

Componente: `src/components/ui/PageHero.tsx` (+ `HeroVideo.tsx`).
Datos de los vídeos: `src/content/heroes.ts`. Mientras un render no exista,
su entrada lleva `animated: false` y sólo se pinta el póster.

Estado (22-10-2026): los seis héroes están renderizados e integrados; vídeos
en `public/media/heroes/<sección>-{wide,narrow}.{webm,mp4}` (≤2,4 MB).

En móvil el motivo va **detrás/encima del título, como en escritorio** (lo
pidió el usuario: nada de «arriba la animación y abajo el texto»). Criterio
de encuadre: el motivo entero entre el ~25 y el ~55 % del alto, terminando
justo por encima del badge. Los teléfonos son más estrechos que 9:16 y el
máster entra por altura, así que `focus` no mueve nada en vertical: para eso
está `shift` (club -18px, propón -15svh, entradas -16svh). El vídeo se funde
por abajo (`--mask-n`) para que su borde no deje escalón.

| Página | Fondo | Tipo |
|---|---|---|
| /club | Alfombra voladora con el logo tejido, sola (sin brasas: `EMBERS=0`, lo pidió el usuario) | Blender · `club/rug_hero.py` |
| /agenda | Pantalla de salidas split-flap con las noches reales | DOM · `components/events/DepartureBoard.tsx` |
| /galeria | Muro inclinado de fotos reales, viradas al rojo, con flash | CSS · `components/gallery/GalleryScene.tsx` |
| /entradas | Tres pulseras de tela jacquard con engarce de plata | Blender · `entradas/bands.py` (+ `band_tex.py`) |
| /eventos-privados | «Te extendemos la alfombra»: corredor persa que se desenrolla sin fin | Blender · `propon/runner.py` (+ `runner_tex.py`) |
| /contacto | El neón rojo de Barullo sobre el pavés con contraluz, como en el club | Blender · `contacto/neon.py` |

Las escenas DOM se alimentan de datos (agenda, álbumes), así que nunca se
quedan desfasadas como pasaría con un vídeo.

## Másteres

Dos por héroe, renderizados por separado (no recortados):
- `wide` 1920×1080: motivo a la derecha y hueco abajo a la izquierda para el texto.
- `narrow` 1080×1920: motivo arriba y hueco abajo.

Todos son bucles exactos: los movimientos usan frecuencias enteras del bucle
(o, en el corredor, el rollo avanza exactamente un periodo del dibujo).

## Flujo

```bash
# 1. pruebas de encuadre (un fotograma, al 50 %): CAM / TGT / LENS mueven la cámara sin tocar el script
bocetos/animaciones/heroes/blender.sh propon/runner.py -- C:/Users/Veintiuno/barullo-render/heroes/propon/tex C:/Users/Veintiuno/barullo-render/heroes/propon/test wide 0 16 50

# 2. render final en cola. Espera a que exista barullo-render/heroes/GO y a que
#    no haya otro blender.exe con -b (ignora los de CPU: CPU_ONLY). Líneas con
#    SKIP=1 reanudan sin repetir fotogramas ya hechos.
QUIET=1 setsid nohup bocetos/animaciones/heroes/queue.sh bocetos/animaciones/heroes/jobs-run7.txt > /mnt/c/Users/Veintiuno/barullo-render/heroes/cola.log 2>&1 &

# 3. codificar (≤2,4 MB por vídeo; pasa por bocetos/animaciones/colgante/lift.py)
node bocetos/animaciones/heroes/encode.mjs club /mnt/c/Users/Veintiuno/barullo-render/heroes/club/final 6 45
```

Y en `src/content/heroes.ts`, quitar el `false` del héroe correspondiente.

Texturas: la alfombra sale de `rug-fly/tex` (bocetos/animaciones/alfombra/rug/rug_tex.py);
`runner_tex.py` y `band_tex.py` escriben en `barullo-render/heroes/<sección>/tex`.
