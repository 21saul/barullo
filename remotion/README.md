# Barullo · Remotion (hero, personaje y plantillas de Instagram)

Paquete **aislado** de la web: tiene su propio `package.json` y su propio
`node_modules` (Remotion 4.0.537 + React 19.3), así que no comparte peers con
la app Next de la raíz. Todo se ejecuta **desde esta carpeta**.

```bash
cd remotion
npm install        # solo la primera vez
```

La primera vez que se renderiza, Remotion descarga su Chrome headless (unos 100 MB) a `node_modules`.
ffmpeg no hace falta: los scripts usan el que trae Remotion (`npx remotion ffmpeg`).

## Abrir el Studio

```bash
npm run studio
```

Se abre en `http://localhost:3000` (si el puerto está ocupado por `next dev`,
Remotion elige el siguiente libre y lo indica en consola). En el Studio,
`StoryEvent` y `FlyerAnim` muestran un formulario para editar las props en vivo.

## Composiciones

| ID | Tamaño | Duración | Qué es |
|---|---|---|---|
| `HeroLoop` | 1080×1920 | 6 s · 30 fps | Hero móvil (principal). Bucle perfecto. |
| `HeroLoopWide` | 1920×1080 | 6 s · 30 fps | Mismo hero en horizontal para escritorio. |
| `StoryEvent` | 1080×1920 | 10 s · 30 fps | Story de evento, respeta las zonas que tapa la interfaz de Instagram. |
| `FlyerAnim` | 1080×1080 | 8 s · 30 fps | Post animado para el feed. |
| `HeroCharacter` | 1080×1080 | 8 s · 30 fps | **Mascota de Barullo** en 3D (cromo negro, ref-16). Bucle perfecto, a sangre, fondo `#050505`. Móvil. |
| `HeroCharacterWide` | 1920×824 (21:9) | 8 s · 30 fps | La mascota para escritorio. 824 y no 823: H.264 4:2:0 exige pares. |
| `HeroCharacterPink` / `…PinkWide` | 1080×720 / 1920×1080 | 8 s · 30 fps | Retrato 3D hyperpop rosa anterior, de respaldo. |
| `HeroCharacterHeadBlack` | 1080×720 | 8 s · 30 fps | Prueba del retrato en cromo negro con cuernos (no se exporta). |
| `HeroCharacterVector` / `…Wide` | 1080×720 / 1920×1080 | 8 s · 30 fps | Versión vectorial (SVG) del retrato, de respaldo. |

Ojo con los nombres: la mascota móvil es 1080×1080 pero se exporta como
`hero-character-3x2.*`, porque la web ya tiene esa ruta.

### Cómo está hecho el hero y las plantillas (sin WebGL)
- **Cromo líquido** (`src/components/ChromeText.tsx`): texto SVG con gradiente
  plata y horizonte rosa, extrusión violeta, `feSpecularLighting` con una luz
  rasante que da una vuelta por bucle, reflejo diagonal que barre y
  `feDisplacementMap` sobre un ruido que se desplaza en círculo (ondula como
  líquido y vuelve exactamente al origen).
- **Bucle perfecto**: todo depende de `t = frame / duración` y solo de
  osciladores con ciclos enteros (`src/lib/tokens.ts`). La corona de pinchos
  gira exactamente un periodo de su patrón. El frame 180 sería idéntico al 0.
- Bloom, orbes glossy, pinchos cromados, destellos ✦ y grano: gradientes y
  filtros CSS/SVG (`src/components/Art.tsx`).
- Tipografías locales en `public/fonts`: Anton (display, OFL), Space Grotesk
  (UI, OFL) y Permanent Marker (acento manuscrito, Apache 2.0).

### Mascota 3D (`HeroCharacter`, `src/three/Mascot3D.tsx`)
Bola de cromo negro con pinchos, cascos de DJ (aro cromado, banda y copas rojo
oscuro, diales con pincho), dos cuchillas cromadas por ojos y sonrisa de
dientes. Diseño sacado de ref-16 (vista lateral y frontal).
- **Silueta primero**: los pinchos van en cromo grafito, un punto más claros
  que la bola, y los dientes en gris claro. Así se lee a 24 px y la sonrisa no
  se come la silueta (comprobado reduciendo a 128/48/24 px).
- Fondo **`#050505` plano**: el canvas es transparente y el color lo pone el
  CSS, sin pasar por el tone mapping. Tras codificar, los bordes se decodifican
  a (4,4,4) por el redondeo YUV de rango limitado: 1/255, imperceptible.
- Estudio de reflejos acromático: tiras blancas duras, contraluces fríos y un
  cenital suave. Supersampling ×2 (`dpr={2}`) para filos limpios.
- Animación: giro de ±17°, los diales giran 1/8 de vuelta por bucle (simetría
  de 8 → sin salto). Costura medida en PNG sin pérdidas.

### Retrato 3D (`HeroCharacterPink`, `src/three/Head3D.tsx`)
Three.js vía `@remotion/three` + `@react-three/fiber`, **renderizado en
diferido**: la web recibe un vídeo, no ejecuta WebGL.
- `src/three/Head3D.tsx`: cabeza en perfil de huevo (`LatheGeometry`), ojos
  negros glossy con párpado que parpadea una vez por bucle, pestañas y corona
  de pinchos (conos cromados), grillz, labios, piercings, perlas iridiscentes,
  gotas y una gota que cae del labio.
- Materiales `MeshPhysicalMaterial`: cromo `metalness 1 / roughness 0.1`; piel
  con `clearcoat` + `sheen` chicle (efecto subsurface); perlas con
  `iridescence`. El rubor y la sombra de ojos se pintan en una textura de
  canvas generada al vuelo.
- **Entorno de reflejos procedural y local**: un mini estudio de paneles
  (blanco, chicle, violeta, leche) convertido con `PMREMGenerator`. Sin HDRI ni
  descargas: renderiza sin red.
- Movimiento mínimo: giro de ±9° (hace que los reflejos barran el cromo),
  parpadeo, gotas, perlas en órbita y destellos.
- **WebGL en headless**: `remotion.config.ts` fija `--gl=swangle`. Probado:
  `swangle` y `angle` funcionan, `swiftshader` falla. Es render por software,
  así que tarda bastante (minutos por versión). Si lanzas
  `npx remotion render` a mano fuera de los scripts, la config se aplica igual.

## Renderizar

```bash
npm run render:hero     # vertical + horizontal: webm + mp4 + pósters
npm run render:character         # mascota 3D: 1080x1080 + 21:9 (lento, ~13 min)
npm run render:character-pink    # retrato 3D rosa de respaldo
npm run render:character-vector  # personaje vectorial de respaldo
npm run render:story    # StoryEvent con el evento demo
npm run render:flyer    # FlyerAnim con el evento demo
```

`render:hero` (y `render:character`) hace un máster casi sin pérdidas y luego codifica VP9 y H.264 a
dos pasadas con bitrate objetivo. Si un archivo se pasa de su presupuesto
(hero vertical **1,45 MB**, horizontal 1,9 MB; personaje **1,1 MiB** cada vídeo), baja el bitrate y repite: el peso
manda sobre la fidelidad. Solo uno: `npm run render:hero -- vertical` (o `wide`; en el personaje `3x2` o `wide`).
Para recomprimir sin volver a renderizar: `-- --reuse-master`.

### Props de un evento real

Las plantillas reciben:

| Prop | Tipo | Ejemplo |
|---|---|---|
| `title` | string | `"Barullo Sessions: Héctor Oaks"` |
| `date` | string | `"2026-10-23T23:59"` → se pinta `VIE 23 OCT · 23:59`. Si no es ISO, sale tal cual en mayúsculas. |
| `lineup` | string[] | `["Héctor Oaks — all night long", "Nëro — warm up"]` (lo que va tras ` — ` es el rol) |
| `room` | string | `"Sala Principal"` (vacío = no se pinta) |
| `priceFrom` | number | `15` → insignia `DESDE 15 €`; `0` → `GRATIS` |
| `flyerSrc` | string | Ruta dentro de `remotion/public` (`"flyers/mi-flyer.jpg"`), una URL `https://…`, o `""` para usar el arte generativo (orbe con pinchos). |

1. Copia el flyer a `remotion/public/flyers/`.
2. Crea un JSON con las props, por ejemplo `eventos/ruido-blanco.json`:

   ```json
   {
     "title": "Ruido Blanco · Live",
     "date": "2026-10-24T21:30",
     "lineup": ["Ruido Blanco — live", "Marea Baixa — live", "Chavasqueira — dj set"],
     "room": "Sala Principal",
     "priceFrom": 12,
     "flyerSrc": "flyers/ruido-blanco.jpg"
   }
   ```

3. Renderiza con un nombre de salida propio:

   ```bash
   npm run render:story -- --props=eventos/ruido-blanco.json --name=story-ruido-blanco
   npm run render:flyer -- --props=eventos/ruido-blanco.json --name=flyer-ruido-blanco
   ```

Las props se validan con zod antes de renderizar: si falta un campo, falla con
un mensaje claro en vez de sacar un vídeo roto. Títulos largos (hasta ~50
caracteres) y lineups de hasta 5 nombres caben; probado.

## Dónde aterrizan los archivos

Todo va a **`../public/media/brand/`**, la carpeta pública de la web, que en
Next se sirve como `/media/brand/...`. Los másteres intermedios quedan en
`remotion/out/` (ignorado por git).

| Composición | Archivo | Peso real |
|---|---|---|
| `HeroLoop` | `hero-loop-vertical.webm` (VP9) | **1,30 MB** (1.367.957 B) |
| `HeroLoop` | `hero-loop-vertical.mp4` (H.264) | **1,29 MB** (1.354.679 B) |
| `HeroLoop` | `hero-poster.jpg` (frame 0) | 118 KB |
| `HeroLoopWide` | `hero-loop-wide.webm` (VP9) | 1,68 MB |
| `HeroLoopWide` | `hero-loop-wide.mp4` (H.264) | 1,67 MB |
| `HeroLoopWide` | `hero-poster-wide.jpg` (frame 0) | 110 KB |
| `StoryEvent` | `story-event-demo.mp4` (H.264, 10 s) | 2,72 MB |
| `FlyerAnim` | `flyer-anim-demo.mp4` (H.264, 8 s) | 1,13 MB |
| `HeroCharacter` (mascota) | `hero-character-3x2.webm` (VP9, 1080×1080) | **0,99 MB** (1.042.164 B) |
| `HeroCharacter` (mascota) | `hero-character-3x2.mp4` (H.264) | **0,98 MB** (1.032.801 B) |
| `HeroCharacter` (mascota) | `hero-character-3x2-poster.jpg` | 83 KB |
| `HeroCharacterWide` (mascota) | `hero-character-wide.webm` (VP9, 1920×824) | **0,99 MB** (1.034.331 B) |
| `HeroCharacterWide` (mascota) | `hero-character-wide.mp4` (H.264) | **0,98 MB** (1.032.393 B) |
| `HeroCharacterWide` (mascota) | `hero-character-wide-poster.jpg` | 64 KB |
| `HeroCharacterPink` | `hero-character-pink-3x2.webm` / `.mp4` | 0,98 MB / 1,00 MB |
| `HeroCharacterPinkWide` | `hero-character-pink-wide.webm` / `.mp4` | 0,99 MB / 1,01 MB |
| `HeroCharacterVector` | `hero-character-vector-3x2.webm` / `.mp4` | 0,97 MB / 1,02 MB |
| `HeroCharacterVector` | `hero-character-vector-3x2-poster.jpg` | 50 KB |
| `HeroCharacterVectorWide` | `hero-character-vector-wide.webm` / `.mp4` | 0,98 MB / 1,07 MB |
| `HeroCharacterVectorWide` | `hero-character-vector-wide-poster.jpg` | 100 KB |

Medido tras el render del 20/10/2026 (MB = 1024² bytes). El hero vertical cabe
en el presupuesto de 1,5 MB **sin** bajar a 24 fps ni recortar: 1080×1920,
30 fps, 6 s. El personaje (3D y vectorial) cabe en < 1,2 MB por vídeo a
30 fps y 8 s, también sin recortar. Render del personaje 3D: ~8,5 min las dos
versiones en esta máquina. Las Stories y los posts no tienen límite de peso duro (Instagram
recomprime), así que van a CRF 20.

## Uso en la web (sugerencia para la app Next)

```html
<video autoplay muted loop playsinline preload="auto" poster="/media/brand/hero-poster.jpg">
  <source src="/media/brand/hero-loop-vertical.webm" type="video/webm" />
  <source src="/media/brand/hero-loop-vertical.mp4" type="video/mp4" />
</video>
```

Las versiones antiguas de Safari no reproducen WebM/VP9, así que el `.mp4` (H.264) va como respaldo. El orden de
los `<source>` hace que quien soporte WebM lo coja primero.
