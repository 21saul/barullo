# Barullo · Dirección visual

> **Actualización 20/10/2026 (v2).** Este documento describe la v1. La v2 la
> sustituye en lo que choca:
> - **Paleta, logo y fuentes de marca:** negro `#0B0B0B`, hueso `#F2EFE8` y
>   rojo `#E63B2E`; el emblema real; Archivo variable al 125 % (`wide`) más
>   Space Mono (`data`). Ya no se usan Syne, Inter ni el texto cromado.
> - **Forma:** radios a 0.
> - **Agenda:** en lista.
> - **Barra de datos:** en celdas, como en los carteles.
>
> El porqué y el estudio de 34 webs de clubs y festivales están en
> `research/competencia-webs-clubs.md`. Los tokens viven en
> `src/app/globals.css`. Sigue vigente la regla de las dos capas: el
> hyperpop, en las imágenes; la interfaz, seca.

Extraída de 15 referencias de Pinterest (ver `bocetos/fotos/inspiracion/pinterest/`).

## Qué es

**Dos capas que no se mezclan. Esta es la regla que manda sobre el resto.**

**1. La interfaz: brutalista y seca.** Negro, blanco, un solo acento rojo.
Esquinas a 90°, filetes de una línea, bloques macizos de color, condensada
pesada en mayúsculas, imágenes a sangre. Así funciona Antídoto y así funcionan
las webs de club que se ven bien: la UI se aparta para que la imagen pegue.

**2. Las imágenes: cromo negro líquido.** Objetos 3D hiperbrillantes,
acromáticos, con reflejo especular durísimo. Cuernos, pinchos, piercings,
grillz. Un apunte de rojo, nunca una zona. Ver `bocetos/fotos/inspiracion/pinterest/ref-16.jpg` y
`ref-17.jpg`, que son las que fijan el tono.

**El error que costó rehacerlo todo:** meter el hyperpop en la interfaz
—gradientes morados, halos difuminados, esquinas redondeadas, resplandores—.
Eso vuelve la página blanda y la hace parecer una landing genérica. El efecto
vive en las imágenes; la interfaz es el marco negro que las sostiene.

**Qué NO es:** rosa caramelo, violeta, sopa de degradados, tarjetas flotantes
con sombra, fotografía de club con grano.

**Nota técnica de contraste:** un objeto negro sobre fondo negro desaparece. Lo
que separa el cromo negro del `--void` son los brillos blancos de borde nítido
y un rim light frío. Mirar ref-17: es casi todo negro y se lee perfectamente.

## Paleta

Pizarra fría, no negro puro. El `#000` absoluto cansa la vista en una pantalla
de móvil y hace que cualquier filete cante; un gris muy oscuro con tirada fría
deja que las superficies se separen del fondo sin tener que iluminarlas.

| Token | Hex | Uso | Contraste sobre `--void` |
|---|---|---|---|
| `--void` | `#0B0D11` | Fondo de página | — |
| `--coal` | `#13161B` | Superficie: tarjetas, cabecera fija | — |
| `--slate` | `#1B1F26` | Superficie elevada: hover, campos | — |
| `--rule` | `#272C34` | Filete por defecto | — |
| `--edge` | `#3A414B` | Filete con intención: activo, hover | — |
| `--milk` | `#ECEEF2` | Texto principal | 15,9:1 |
| `--ash` | `#9AA1AC` | Texto secundario | 7,4:1 |
| `--dust` | `#6B727D` | Terciario: texto grande o deshabilitado | 3,4:1 |
| `--acid` | `#FF3B4E` | **El** acento. Único | 5,5:1 |
| `--ember` | `#2A1218` | Rojo apagadísimo: fondo de aviso, nunca texto | — |
| `--chrome-hi/mid/lo` | `#FFFFFF` `#C9CBD2` `#6E7076` | Gradiente metálico, acromático | — |

Sobre `--acid` el texto va **en oscuro**: el blanco sobre este rojo se queda en
3,5:1 y no pasa AA. Por eso todos los botones rojos llevan `text-void`.

## Jerarquía por relleno

Toda la regla de color del sitio cabe en tres líneas:

| Nivel | Tratamiento | Ejemplo |
|---|---|---|
| Primario | Relleno macizo de acento | Comprar entradas, "Últimas entradas" |
| Secundario | Sólo contorno (`--edge`) | Ver la agenda, Ver galería |
| Terciario | Sin relleno ni borde | Volver, cancelar |

Los estados de evento siguen la misma regla: macizo cuando hay que correr
(últimas, entrada libre), contorno cuando es información tranquila (a la venta,
agotado). Y el color **siempre** va acompañado de texto: un distintivo que sólo
se distinga por ser rojo no existe para quien no distingue el rojo.

## Tratamientos

**Permitidos:**
1. **Texto cromado** — gradiente plata acromático con `background-clip:text`.
   **Sólo en el wordmark.** En cualquier otro sitio ensucia.
2. **Imágenes a sangre** — tocando los bordes de la pantalla, sin marco.
3. **Bloques macizos de color** — la cinta de eventos, los botones.
4. **Filetes de una línea** (`--rule`), y radios contenidos: `10px` en
   controles, `14px` en tarjetas, píldora sólo en distintivos y botones
   redondos de icono. Suaves, no widgets.
5. **Grano fino** al 3 %, textura y nada más.
6. **Aparición al hacer scroll** con `animation-timeline: view()`, dentro de un
   `@supports`. Donde el navegador no lo entiende —hoy el WebView de iOS— no
   pasa nada y el contenido se ve entero. Cuesta 0 KB de JavaScript.

**Prohibidos** (son lo que hundió la primera versión):
- Degradados de **color** de fondo. El fondo es `--void`, plano. (Un degradado
  de negro a transparente sobre una foto, para que el texto se lea, sí.)
- Halos difuminados / bloom de color.
- Sombras de color. Las sombras son negras, cortas y casi invisibles: una
  sombra ancha sobre fondo oscuro no se lee como profundidad, se lee como
  suciedad.
- Cristal esmerilado decorativo (el `backdrop-blur` sólo donde algo se solapa
  de verdad: cabecera fija, barra de compra, distintivos sobre foto).
- Un segundo color de acento.

## Tipografía

Dos familias y ni una más.

- **Display — Syne (700/800).** Es la pieza artística del sistema: ancho raro,
  terminaciones que no se parecen a ninguna tipografía de sistema. Es la que
  conecta con el personaje 3D. Titulares, botones y números grandes.
- **Texto — Inter.** La cara más neutra y más probada que hay para pantalla:
  ojo enorme, formas sin personalidad propia y caracteres que no se confunden
  entre sí (la "I" lleva remates, el "1" lleva base). No aporta estilo, y es
  justo lo que se le pide: el estilo lo pone el titular.

Sólo se cargan los pesos que se usan: los cinco de Syne costaban ~40 KB para
nada. Ambas por `next/font`, autoalojadas, con `display: swap`.

## Iconografía

**Lucide.** De trazo, esquinas y extremos redondeados, rejilla de 24.

El grosor por defecto es **2,25** y no el 2 de fábrica: la dirección visual
pide un icono con cuerpo. El trazo es relativo al `viewBox`, así que ese 2,25
mantiene la misma proporción a cualquier tamaño (1,9 px reales a 20 px, 1,5 a
16) y no hay que retocarlo por tamaño. Por encima de ~2,5 las formas pequeñas
—las muescas del ticket, los palos de la lista— se cierran y el icono pasa a
ser un manchurrón. Tamaños: 13–16px dentro de texto, 20px en controles, 28px
cuando es el ancla de un bloque.

No se importa `lucide-react`. Los trazados se copian al compilar con
`npm run icons`, que genera `src/components/ui/Icon.tsx` como SVG plano. Coste
en JavaScript: **cero**. Para añadir un icono, busca su nombre en lucide.dev,
mételo en el MAP de `scripts/gen-icons.cjs` y vuelve a ejecutarlo. El MAP lleva
sólo lo que se usa: `Icon` se importa desde `Header`, que es componente de
cliente, así que cada trazado del MAP viaja al navegador aunque nadie lo pinte.

**Logotipos de marca aparte.** Lucide los retiró en la v1 —son marcas
registradas y no puede mantenerlas—, así que Instagram, TikTok, SoundCloud y
Spotify viven en `src/components/ui/BrandIcon.tsx`, macizos y a 256. Están
dibujados con el peso `bold` de Phosphor, que a esa rejilla equivale al mismo
grosor óptico: en la fila de redes del pie no se nota el cambio de familia.

## Rendimiento (manda sobre todo lo anterior)
La web se abre desde el navegador de Instagram con 4G. Los efectos se hacen en
CSS (gradientes, `filter`, `mask`) — **no** con WebGL ni vídeo pesado en el hero.

**Cifra real medida, no aspiracional** (`npm run budget` contra el build de
producción): **195 KB de JS comprimido y 11 KB de CSS** en la home; entre 191 y
195 KB en el resto de rutas. De eso, prácticamente todo es el runtime de Next 16
+ React 19; el código propio apenas suma. El objetivo inicial de «< 100 KB» era
inalcanzable con el App Router y se corrige aquí para no mentirnos.

Lo que sí se protege:
- **Nada bloquea el primer pintado.** Todo el contenido viaja en el HTML
  estático (23 KB en la home); el JS sólo hidrata el menú, la barra de compra
  y los formularios.
- **Tres componentes de cliente en todo el sitio**: `Header`, `TicketDock` y
  `BrandHero`. Tarjetas, agenda, galería y fichas son Server Components puros.
- **Los iconos no son JavaScript.** Son SVG inline generados al compilar.
- **Cero librerías de animación.** Marquesina, destellos, bloom, acordeón de
  FAQ y carrusel están en CSS. Se desinstalaron `motion` y `embla-carousel`
  tras comprobar que no hacían falta: si vuelven, que sea con un motivo.
- **Imágenes:** AVIF/WebP vía `next/image`, `priority` sólo en el cartel del
  hero (es el LCP), `lazy` en todo lo demás.

---

## Decisión: cómo se producen los personajes

**20/10/2026.** Las referencias piden retratos 3D glossy. Se evaluaron las vías:

| Vía | Resultado | Coste |
|---|---|---|
| ArtCraft automatizado | **Descartada.** No tiene CLI ni MCP: `crates/` sólo trae `api_clients, desktop, lib, schema, testing, vendor`. La frase "UI, CLI, canal JSON o MCP" es de **PhotoCraft**, otro repo, que es un editor de fotos y no genera con IA. Su única automatización oficial es una API en la nube cuya clave activa su equipo a mano. | — |
| ArtCraft a mano (app Windows) | Viable. El programa es gratis y open source, pero los modelos corren en la nube de terceros. | 0,02–0,20 $/imagen |
| API de imagen directa (fal/OpenAI/Google) | Viable y más directa que ArtCraft. | 0,02–0,20 $/imagen |
| Modelo local | **Inviable aquí.** Sin CUDA en WSL (`/usr/lib/wsl/lib` sólo tiene `libd3d12` y `libdxcore`) y 7,7 GB de RAM. | — |
| **3D renderizado en diferido** | **Elegida.** `@remotion/three` + `three`: se renderiza 3D real fuera de línea y se publica como vídeo. | 0 € |

**Por qué la última.** Lo que hace que las referencias funcionen es material y luz, no dibujo:
especular duro, cromo reflejando el entorno, clearcoat, algo de translucidez. Eso sale
de `MeshPhysicalMaterial` con `envMap`, y se acerca mucho más que una ilustración
vectorial plana.

**No contradice la prohibición de WebGL** de la sección de rendimiento: el navegador no
ejecuta WebGL, sólo reproduce un `.webm` ya renderizado. El coste en el cliente es el
de un vídeo, y además entra diferido (ver `BrandHero`).

**Queda abierto:** si algún día hay presupuesto o una cuenta de generación ya pagada,
la vía de imagen por IA da más fidelidad para los **carteles de evento**, que hoy siguen
con fotos de stock de Unsplash como marcador.
