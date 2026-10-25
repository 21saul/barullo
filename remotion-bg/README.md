# Barullo · fondos animados (Remotion)

Paquete aislado (su propio `package.json` y `node_modules`) con los fondos en
bucle de la web. Remotion 4.0.537, React 19.2. No comparte dependencias con la app Next.

```bash
cd remotion-bg
npm i
npm run studio          # previsualizar
npm run render          # renderiza todo a ../public/media/brand/
npm run render -- BgLiquidChrome-wide   # sólo una composición
```

`scripts/render.mjs` sube el CRF de 4 en 4 hasta que cada archivo pesa menos de 800 KB,
y saca el póster (`-poster.jpg`, primer frame) de cada fondo.

## Salidas (pesos reales, medidos tras el render)

| Composición | Para qué pantalla | Archivo | Peso |
|---|---|---|---|
| `BgLiquidChrome-vertical` (1080×1920, 16 s) | Portada/hero en móvil | `bg-liquid-chrome-vertical.webm` | 222 KB |
| | | `bg-liquid-chrome-vertical.mp4` | 641 KB |
| | | `bg-liquid-chrome-vertical-poster.jpg` | 42 KB |
| `BgLiquidChrome-wide` (1920×1080, 16 s) | Portada/hero en escritorio · bloque newsletter | `bg-liquid-chrome-wide.webm` | 234 KB |
| | | `bg-liquid-chrome-wide.mp4` | 689 KB |
| | | `bg-liquid-chrome-wide-poster.jpg` | 40 KB |
| `BgBloomDrift-vertical` (1080×1920, 14 s) | Secciones intermedias y cabeceras interiores (agenda, club, contacto) en móvil | `bg-bloom-drift-vertical.webm` | 159 KB |
| | | `bg-bloom-drift-vertical.mp4` | 652 KB |
| | | `bg-bloom-drift-vertical-poster.jpg` | 22 KB |
| `BgBloomDrift-wide` (1920×1080, 14 s) | Lo mismo en escritorio | `bg-bloom-drift-wide.webm` | 161 KB |
| | | `bg-bloom-drift-wide.mp4` | 704 KB |
| | | `bg-bloom-drift-wide-poster.jpg` | 24 KB |
| `BgSparkleField` (1920×1080, 4 s, VP9 con alfa) | **Cancelado**, no se publica | — | (148 KB en la última prueba) |

Pon `<source>` WebM primero (VP9, pesa entre ⅓ y ¼ que el MP4) y el MP4 (H.264) como reserva para Safari.

## Cómo está hecho

- **Bucle perfecto.** Todo el movimiento es función de la fase `2π·frame/duración`
  con frecuencias enteras. Comprobado midiendo píxeles: la diferencia último→primer frame
  es igual a la de dos frames consecutivos (cromo 0,274 / 0,274; bloom 0,222 / 0,207).
- **BgLiquidChrome:** gradiente de "horizonte cromado", como el wordmark de `hero-poster.jpg`:
  suelo noche → violeta → chicle → leche, cielo plata, filo duro con brillo especular.
  Los horizontes son paths SVG vectoriales (suma de senos), con filo nítido. El interior
  interpola entre horizontes y va difuminado, recortado por clipPath. El contraste se baja
  en origen con un velo `--void` al 66 % y viñeta.
  Primera versión descartada: `feTurbulence` + `feDisplacementMap`. Quedaba como lámpara de lava
  y el mapa de 8 bits deja el filo dentado con escalas grandes.
- **BgBloomDrift:** 5 halos radiales (`--bubblegum`, `--violet`, `--iris`) en `screen` sobre
  `--void`, con trayectorias de Lissajous lentas. Sin filtros, sólo gradientes.
- Sin WebGL/Three: sólo SVG, gradientes CSS y filtros SVG.

## Pendiente / limitaciones

- **BgSparkleField cancelado.** El WebM VP9 con alfa funciona: decodificado con libvpx, el 99,5 %
  de los píxeles es transparente. Pero Safari/WebKit no reproduce alfa VP9, y eso incluye el
  navegador in-app de Instagram en iOS, que es el caso principal de la web. La alternativa
  (HEVC con alfa) sólo se codifica con VideoToolbox de macOS. La web usa en su lugar los
  destellos SVG de `src/components/ui/Sparkles.tsx`. El código sigue en `src/BgSparkleField.tsx`
  por si hiciera falta (`npm run render -- BgSparkleField`).
- El aviso "Version mismatch: zod" que sale al usar `npx remotion` desde la raíz del repo
  viene del `node_modules` de la app. Dentro de `remotion-bg/` las versiones son correctas.
