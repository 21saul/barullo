# Barullo · web del club

Web del club Barullo (Vigo). Pensada para abrirse desde el enlace de la bio de
Instagram, en móvil y con mala cobertura.

## Arranque

```bash
npm install
npm run dev        # http://localhost:3000
```

| Script | Para qué |
|---|---|
| `npm run dev` | Desarrollo con Turbopack |
| `npm run build` | Build de producción |
| `npm run typecheck` | TypeScript sin emitir |
| `npm run budget` | Mide KB de JS/CSS por ruta (requiere `next start -p 3100`) |
| `npm run shot` | Capturas móvil + escritorio (requiere `libasound2`, ver más abajo) |

## Stack

| Capa | Elección | Por qué |
|---|---|---|
| Framework | Next.js 16 · App Router | Server Components: el contenido viaja en HTML, el JS sólo hidrata |
| UI | React 19 + TypeScript | — |
| Estilos | Tailwind v4 (CSS-first) | Tokens en `@theme`, sin config JS |
| Iconos | Lucide, inlineado en build | SVG plano: 0 KB de JS. Los logos de marca van aparte |
| Formularios | Server Actions + zod | Validación en servidor, cero JS de formulario en cliente |
| Fechas | date-fns + locale `es` | — |
| Despliegue | Vercel (previsto) | ISR por ruta + `next/og` en el edge |

**Dos librerías de cliente, y sólo dos** (v3, octubre 2026): `embla-carousel`
para los carruseles (Tickets, noches pasadas, otras noches) y `photoswipe` para
el visor de fotos de la galería, que se descarga al tocar la primera foto.
Marquesina, acordeón y apariciones siguen en CSS.

## Estructura

```
src/
  app/                     Rutas (App Router)
    page.tsx               Home
    agenda/                Listado + /agenda/[mes] (long-tail SEO)
    eventos/[slug]/        Ficha + opengraph-image.tsx (OG por evento)
    entradas/              Cómo se compra y qué piden en puerta
    club/                  Texto, alfombra, residentes y espacios
    galeria/ galeria/[slug] Álbumes por noche + visor PhotoSwipe
    eventos-privados/      «Propón una noche» (colectivos, sellos, fuera de horario)
    contacto/ links/       Contacto y link-in-bio
    legal/[doc]/           Aviso legal, privacidad, cookies, admisión
    actions.ts             Server Actions de los formularios
    sitemap.ts robots.ts   SEO técnico
  components/
    layout/ home/ events/ forms/ ui/
  content/                 ← DATOS. Es lo único que se toca para actualizar
    site.ts                NAP, redes, navegación
    events.ts              Eventos (demo)
    faq.ts  legal.ts
  lib/
    events.ts              Capa de acceso a datos ← punto de cambio al CMS
    seo.ts(x)              Constructores de JSON-LD
    dates.ts  utils.ts
bocetos/                   Diseños, animaciones y fotos de trabajo (ver bocetos/README.md)
public/media/demo/         Fotos demo (Unsplash, licencia libre)
```

## Cómo se actualiza el contenido

Hoy todo vive en `src/content/`. **Las vistas no leen datos directamente**:
pasan siempre por `src/lib/events.ts`. Para enchufar un CMS (Sanity, Payload)
basta con cambiar el cuerpo de esas funciones por el `fetch` correspondiente;
ni un componente se toca.

Las fechas demo se calculan a partir de *hoy*, así que la plantilla nunca se ve
caducada.

## SEO

- `generateMetadata` por ruta, canonical en todas.
- JSON-LD: `NightClub` (global), `MusicEvent` por evento, `BreadcrumbList`,
  `FAQPage` en `/entradas` y `/eventos-privados`, `ItemList` en los listados.
- **OG dinámicas por evento** (`next/og`): al compartir una fiesta por WhatsApp
  sale el cartel con fecha y line-up renderizados. Es la pieza con más retorno
  de la web y ninguno de los clubes de referencia la tiene.
- `/agenda/[mes]` genera una URL por mes: ahí está el long-tail.
- `noindex` en `/links`, en los legales y en los eventos ya pasados.
- El NAP de `src/content/site.ts` debe coincidir **letra a letra** con la ficha
  de Google Business o el SEO local se resiente.

## Sistema de diseño

La fuente de verdad es `bocetos/DIRECCION-VISUAL.md` y los tokens viven en
`src/app/globals.css` (`@theme`). Resumen de lo que hay que saber para tocar
una pantalla:

- **Un club, no una discoteca.** No hay reserva de mesa (`/reservas` redirige
  a `/eventos-privados`, que es «Propón una noche»).
- **Color:** negro, hueso y rojo Barullo `#E63B2E` del manual de marca. Sobre
  rojo el texto va en negro.
- **Tipografía:** Anton (gorda, tipo Impact) para titulares con la utilidad
  `wide`, y Nunito (redondeada) para todo lo demás; `data` es Nunito 800 con
  cifras tabulares. Anton sólo tiene un peso: `wide` anula la negrita sintética.
- **Escritorio:** se diseña para móvil, pero el contenido crece con la
  pantalla: `max-w-6xl` → `2xl:max-w-7xl` → `3xl:max-w-[100rem]` (breakpoint
  propio de 1760 px en `@theme`; con `min-[1920px]:` la regla `2xl:` ganaba por
  orden). El héroe se limita a `82dvh` en pantallas anchas para no pasar de la
  ventana.
- **Forma:** radios con continuidad: `rounded-md` (14 px) para tarjetas y
  fotos, `rounded-lg` (28 px) para bloques grandes, `rounded-pill` para botones
  y etiquetas.
- **Iconos:** `<Icon name="…" />`. Son SVG inline de Lucide, trazo 2,25 sobre
  rejilla de 24, generados por `npm run icons` desde `scripts/gen-icons.cjs`.
  Para añadir uno, busca el nombre en lucide.dev, mételo en el MAP del script y
  vuelve a ejecutarlo. **No** importes `lucide-react` en componentes.
- **Logos de redes:** `<BrandIcon name="Instagram" />`. Van aparte porque
  Lucide no trae marcas: son trazados macizos a 256 y se editan a mano.
- **Utilidades de superficie:** `card` (pulsable, con hover) y `panel`
  (estático, sin hover). No lleves `bg-coal border border-rule` a mano.
- **Aparición al hacer scroll:** clase `reveal` (+ `reveal-2`/`reveal-3` para
  escalonar). Es CSS puro con `animation-timeline: view()` dentro de un
  `@supports`: donde no se soporta, el contenido sale y ya está.

## Decisiones que conviene no deshacer sin pensarlo

- **`dvh`, nunca `vh`.** En el navegador de Instagram, `100vh` queda por debajo
  de la barra del sistema y se come el botón de entradas.
- **Respaldo `@supports` para el texto cromado.** Sin él, un navegador que no
  soporte `background-clip:text` pinta el nombre del club transparente sobre
  negro: invisible.
- **Nada de scroll suavizado por JS** (Lenis, GSAP ScrollSmoother): se rompe en
  el WebView de iOS.
- **`cacheComponents` desactivado** en `next.config.ts`: es incompatible con
  `export const revalidate` por segmento.
- **La venta de entradas es externa** (Fourvenues/DICE). Como en todos los
  clubes del sector. Aquí sólo se enlaza.
- **La proporción del héroe se escribe literal** en `src/content/brand.ts`
  (`frame: "aspect-square sm:aspect-[21/9]"`). Tailwind genera CSS leyendo el
  código fuente: una clase compuesta en tiempo de ejecución (`sm:${algo}`) no
  llega nunca a la hoja de estilos, y el marco se queda a altura cero.
- **No hay barra fija de compra abajo.** El botón «Entradas» de la cabecera
  está siempre visible, también en móvil; la barra duplicaba el mismo botón.
- **El bucle del héroe lleva botón de pausa.** Dura 8 s y arranca solo: una
  animación que se mueve más de cinco segundos junto a texto tiene que poder
  pararse (WCAG 2.2.2). Respetar `prefers-reduced-motion` no basta.
- **Los títulos del menú móvil escalan con `clamp()`, no con un tamaño fijo**:
  la palabra más larga tiene que caber con la flecha en 360 px.
- **No se usa `focus:outline-none` en ningún control.** Hay un anillo de foco
  global en `globals.css`; quitarlo en un campo lo deja sin indicador para
  quien navega con teclado.
- **Nunca se elige el máster de vídeo con `sm:hidden`.** Ocultar con CSS un
  `<video autoPlay>` no evita su descarga: se bajarían los dos másteres (3 MB)
  en todos los dispositivos. La elección va en JS con `matchMedia`, montando
  un solo `<video>` (`BrandHero`). Costó un bug real, no se deshaga.
- **Los vídeos nunca bloquean el primer pintado.** Entran en
  `requestIdleCallback` y sólo si no hay `prefers-reduced-motion`, ni
  `saveData`, ni conexión lenta. Los fondos (`VideoBackdrop`) además son sólo
  de escritorio: en móvil ese efecto lo dan los `Bloom` en CSS por 0 KB.

## Pendiente antes de producción

- [ ] Dominio real en `SITE.url` (`src/content/site.ts`): afecta a canonical, sitemap y OG.
- [ ] NAP real: dirección, teléfono, coordenadas, horarios.
- [ ] Conectar los formularios: hoy `src/app/actions.ts` **sólo valida y registra en consola, no envía ni guarda nada**.
- [ ] Decidir proveedor de ticketing y poner las URLs reales.
- [ ] Sustituir las fotos demo por material propio (Unsplash + Wikimedia Commons; créditos en `/legal/creditos`, `npm run photos` tras cambiarlas).
- [ ] Completar los `[PENDIENTE]` de `src/content/legal.ts` y que lo revise alguien con criterio jurídico.
- [x] Tipografía v3: Anton + Nunito.

## QA visual

El Chromium de Playwright no arranca en este WSL (le falta `libasound2`). En
vez de instalarlo con sudo, se conecta Playwright **al Chrome de Windows** por
CDP, que ya está en la máquina y funciona gracias al modo de red *mirrored* de
WSL2:

```bash
# 1. Arrancar Chrome de Windows en modo headless con depuración remota
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless --disable-gpu --remote-debugging-port=9222 \
  --remote-allow-origins='*' --user-data-dir='C:\\Windows\\Temp\\bchrome' about:blank &

# 2. Con el dev server levantado:
node scripts/qa.cjs "/,/agenda,/links"   # desbordamiento horizontal + errores JS + capturas
# BASE=http://localhost:3100 node scripts/qa.cjs …  para medir contra producción
node scripts/crop.cjs                    # fold y secciones sueltas
node scripts/qa/measure-menu.cjs         # anchos reales del menú móvil
```

`scripts/qa.cjs` avisa si `scrollWidth > clientWidth` (desbordamiento
horizontal, el fallo clásico en móvil) y lista los elementos culpables.

**Trampa que ya costó una tarde:** si lanzas `next build` con un `next start`
corriendo contra el mismo `.next`, el servidor viejo empieza a devolver **500
en el CSS** y las capturas salen con la página sin estilos — se parece mucho a
un fallo de diseño y no lo es. Para en el servidor antes de reconstruir, y si
una captura sale rarísima, comprueba primero el CSS:

```bash
CSS=$(curl -s http://localhost:3100/ | grep -o '/_next/static/[^"]*\.css' | head -1)
curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:3100$CSS"   # tiene que ser 200
```

Si alguna vez se prefiere el Chromium nativo:
`sudo apt-get install -y libasound2t64 libnss3 libatk-bridge2.0-0 libgtk-3-0 libgbm1`
