# Webs de clubs y festivales: cómo las hace la competencia

Investigación del 20 de octubre de 2026 para rediseñar la web de Barullo.

**Método.** He abierto 34 webs con un Chrome real emulando un iPhone (390×844, Safari iOS 18). De cada una he guardado una captura de la primera pantalla y otra de la página entera. Además he extraído su huella técnica: framework, fuentes que se descargan, librerías JS, servicios de terceros, navegación y titulares en orden. El script está en `research/scripts/probe.cjs`. Las capturas son material de trabajo y no se versionan.

**Muestra.**

| Tipo | Webs |
|---|---|
| Clubs de culto (underground) | Berghain, Tresor, OHM (Berlín) · De School, Shelter (Ámsterdam) · fabric, FOLD (Londres) · Basement, Nowadays (Nueva York) · Robert Johnson (Offenbach) |
| Superclubs | Pacha, Amnesia, Hï Ibiza, DC-10, Ushuaïa (Ibiza) |
| España | Razzmatazz, Input, Sala Apolo (Barcelona) · Mondo Disko (Madrid) |
| Festivales | Sónar, Primavera Sound, Dekmantel, Awakenings, DGTL, Time Warp, Tomorrowland, Kappa FuturFestival, Movement |
| Medios y plataformas | Boiler Room, Resident Advisor, DICE |

Concrete (París), Ushuaïa, Movement y DICE bloquean los navegadores automáticos o tardan demasiado; de esas sólo se sacó información parcial. La web de Printworks está en «coming soon».

---

## 1. Conclusión en cinco líneas

1. **Las mejores webs de club son listas, no landings.** Berghain, OHM, Basement, Robert Johnson y fabric enseñan la agenda como una lista tipográfica: fecha, nombre y line-up, y a otra cosa. No hay bloques de «quiénes somos» con iconos ni tarjetas redondeadas con sombra.
2. **La primera pantalla responde a «¿qué hay y cuándo?».** En el 80 % de los clubs lo primero bajo la cabecera es la próxima fecha o la agenda directamente. Las que abren con un vídeo de ambiente (Pacha, Hï, DC-10) son superclubs que venden marca y turismo, no la noche del viernes.
3. **La identidad la ponen dos cosas: una tipografía propia o muy marcada, y el arte de los carteles.** La interfaz es casi siempre negro + un color + blanco, con esquinas rectas.
4. **La entrada se vende fuera** (RA, DICE, Shotgun, Fourvenues, Xceed). La web sólo enlaza, y el botón es pequeño y repetido en cada fila (fabric: «BUY TICKETS» en cada evento).
5. **El fallo más común es el banner de cookies.** En 12 de 34 webs el banner tapa más de media pantalla en el primer pantallazo del móvil. Las webs de culto (Berghain, OHM, Robert Johnson, De School) **no tienen banner**, porque no cargan rastreadores de terceros.

---

## 2. Qué hay en la home, en orden

Orden real de los bloques en móvil, sacado de las capturas a página completa:

| Web | 1.º (primera pantalla) | 2.º | 3.º | 4.º | Después |
|---|---|---|---|---|---|
| **Berghain** | Arte del mes (grabado) | «Next up»: rejilla 2×N de fechas (día, fecha, nombre, sala) | «Soon» | Kantine (programa de la otra sala, en lista) | Tienda/label, pie mínimo |
| **OHM** | Logo en caja sobre retícula | Lista de fechas: `23/10 23:59` + título + line-up en mono | — | Residentes en lista gigante con barras `/` | Info |
| **Basement** | «UPCOMING» | Por noche: fecha grande, line-up por sala (BASEMENT / STUDIO en verde), un objeto recortado como imagen | … 6 noches seguidas | — | Dirección, iconos, legal |
| **fabric** | Último mix/noticia destacada | Carrusel de carteles | Noticias (nuevo residente, colaboraciones) | Membresía fabricfirst | Newsletter, pie con FAQ/Contacto/Mesas |
| **Shelter** | Logotipo deformado a pantalla completa | Lista de eventos | Night Gallery (exposiciones) | Down The Hatch (bar) | House rules, Party responsibly |
| **Robert Johnson** | Menú en dos columnas, verde | Mes («October») | Lista `02/10  Electric Friday / In-kasso / not even noticed`, a 32 px | — | — |
| **Razzmatazz** | Evento destacado a sangre con botones «Menú» y «Agenda» fijos | Eventos de club por fecha | Los clubs (salas/fiestas con nombre) | Info y mapa | Newsletter |
| **Apolo** | Carrusel del próximo concierto (fecha + título en condensada) | «Más eventos»: tarjeta por evento | Política de respeto («Apolo Rules») | Noticias | Newsletter, patrocinadores |
| **Mondo Disko** | Vídeo + logo | «PROGRAMACIÓN» por meses (OCTUBRE, NOVIEMBRE…) con el cartel entero | Mixes | Tienda | — |
| **Input** | Vídeo 3D + «BUY TICKETS» fijo arriba | «NEXT EVENTS» | Our club | Respect | Newsletter |
| **Pacha** | «This is Pacha Ibiza» sobre vídeo | Upcoming events (carrusel de carteles) | VIP | Restaurante, hotel, tienda | La Familia |
| **Hï Ibiza** | Vídeo + «VOTE» DJ Mag | Residencias | Club residentes | Arte, noticias | — |
| **Amnesia** | Glitch animado «MEMORIES» | Calendario | Fiestas | Noticias | Tienda |
| **Awakenings** | Fila de «stories» circulares con las ediciones | Héroe del próximo evento + «LINEUP & TICKETS» | Lista de eventos | — | Apparel, FAQ, Social Safety |
| **Time Warp** | Foto + `TIME WARP NEW YORK CITY · 20 + 21 NOVEMBER` | «Tickets now available» | Carrusel de ediciones | — | — |
| **Boiler Room** | Logo + «FIND AN EVENT» | Upcoming por ciudad | Vídeo | Tienda | Newsletter |

**Patrón dominante en clubs:**

```
[cabecera mínima: logo · Entradas · menú]
[PRÓXIMA NOCHE ó AGENDA directamente]   ← siempre
[resto de la agenda en lista]
[un bloque de identidad: residentes / sello / galería / mixes]
[info práctica: dirección, horario, normas de la casa]
[newsletter]
[pie: legal, redes]
```

**Lo que NO aparece en ninguna web de culto:** contadores tipo «400 de aforo / 2 salas», bloques de beneficios con icono, testimonios, «¿Por qué elegirnos?». Ese lenguaje es de plantilla y es lo que hace que una web de club parezca «tosca» o de agencia.

---

## 3. Navegación y accesos directos

**Menú (lo que aparece y con qué frecuencia):**

| Apartado | Frecuencia | Nombres habituales |
|---|---|---|
| Agenda / programa | 34/34 | Program, Events, What's On, Agenda, Calendario, Programación |
| Entradas | 30/34 (como botón aparte en la mitad) | Tickets, Buy Tickets, Entradas |
| Info / visita | 26/34 | Info, Hours & Location, Guest Information, Ubicación, FAQ |
| Tienda / merch | 18/34 | Shop, Store, Merch, Record Shop |
| Normas / espacio seguro | 14/34 | Awareness, House Rules, Safer Space, Respect, Social Safety, Apolo Rules, Party Responsibly |
| Residentes | 9/34 | Residents, Residentes |
| Galería / archivo | 9/34 | Night Gallery, Galerías, Archive, Histórico, Past |
| Mixes / podcast / radio | 9/34 | Mixes, Podcasts, SonarMix, Radio, Audio |
| Mesas / VIP / privados | 8/34 | Book VIP Zone, Book a Table, Private Hire, Private Events, Hire |
| Newsletter | 31/34 (casi siempre en el pie) | — |
| Trabajo | 7/34 | Jobs, Trabaja con nosotros |

**Patrones de acceso directo que funcionan en móvil:**

- **Botón de entradas fijo, siempre visible.** Input lo lleva pegado bajo el logo («BUY TICKETS») y Razzmatazz tiene dos botones flotantes abajo («Menú» y «Agenda»). Kappa y Primavera lo meten en la cabecera.
- **Menú numerado** (`00 Home`, `01 Events`…): Shelter y Amnesia. Es un detalle editorial barato que ordena.
- **«Stories» circulares** con las próximas ediciones (Awakenings). Imita Instagram y se entiende al instante.
- **Filtro de agenda por sala o fiesta** (Razzmatazz, Basement con BASEMENT/STUDIO, Berghain con Säule/Halle/Panorama Bar). Barullo tiene ramas de género, que encajan aquí.

**Qué conviene poner:**

- Entradas (botón, no enlace de menú), Agenda, Info (cómo llegar, horario, edad, normas), Galería, Reservas y Contacto.
- **Normas de la casa / espacio seguro.** El 40 % lo tiene, y en Europa ya se espera. Además da confianza a quien viene por primera vez.

**Qué no conviene poner:**

- Más de 6 entradas en el menú.
- Idiomas en la cabecera si no hay traducción real.
- Iconos de redes en la cabecera móvil: roban sitio al botón de entradas.
- Un enlace a «Entradas» que se repite tres veces en la misma pantalla (le pasaba a Barullo: cabecera + héroe + barra fija).

---

## 4. Estilo visual

### 4.1 Color

| Paleta | Webs |
|---|---|
| Negro + blanco, sin acento | Berghain (`#141414`), Tresor, OHM, Shelter, Basement, Nowadays, Boiler Room |
| Negro + 1 acento fuerte | Basement (verde terminal), Robert Johnson (verde sobre blanco), Amnesia (rosa + amarillo), Awakenings (rojo-rosa), Boiler Room (amarillo en el CTA) |
| Fondo claro | Razzmatazz, Mondo, Hï, Kappa, Primavera (`#EFEAE7`, color hueso), Robert Johnson, De School (crema) |
| Color de marca a sangre | Dekmantel (lima `#BCE74D`), Amnesia |

Regla que se repite: **la interfaz no tiene degradados.** Donde hay color, viene del arte de los carteles. El fondo es plano.

### 4.2 Tipografía (fuentes reales descargadas)

| Web | Display | Texto | Mono |
|---|---|---|---|
| Berghain | Graphik | Graphik | — |
| OHM | OHM Favorit (propia) | — | Favorit Mono, Connect Mono |
| De School | Basis Grotesque Pro | — | Basis Grotesque Mono |
| fabric | Apercu Pro | Arial | — |
| Shelter | Neue Haas Display | — | — |
| Basement | Euro Extended Bold | Inter | Spoof |
| Robert Johnson | Riforma LL | — | — |
| Tresor | Px Grotesk | — | — |
| Nowadays | FK Grotesk Neue | EK Modena | — |
| Boiler Room | Univers, Akzidenz-Grotesk | — | — |
| Pacha | TT Hoves, Supreme LL, Montia (script) | — | — |
| Amnesia | OT Neue Montreal **Extra Squeezed** | GT America | — |
| Hï Ibiza | Neue Haas Grotesk Display | Magic UI Pro | — |
| Razzmatazz | Antique Legacy | — | — |
| Apolo | Anton (condensada) | GT Walsheim | — |
| Mondo | Special Gothic **Expanded** One | Montserrat | — |
| Primavera | GT America Black | GT America | **GT America Mono** |
| Kappa | Suisse Int'l | — | — |
| Dekmantel | Dekmantel BB Blur (propia) | — | — |
| Awakenings | Auxilia (propia) | Titillium | — |

**Lectura:**

- **Grotescos neo-suizos** (Graphik, Neue Haas, Suisse, Univers, Akzidenz, GT America) para la base: neutros, de precisión.
- **Un extremo de anchura** para el carácter: muy expandida (Euro Extended, Special Gothic Expanded) o muy condensada (Anton, Neue Montreal Extra Squeezed).
- **Monoespaciada para datos** (fechas, horas, salas): OHM, De School, Primavera y Basement. Da aire de «programa», de terminal, de cartel técnico.
- **Fuente propia** en los que más identidad tienen: OHM, Dekmantel, Awakenings, Berghain (logo).
- **Casi nadie usa Inter como única fuente.** Es la fuente por defecto de las plantillas; cuando aparece (Basement) es sólo para el cuerpo.

### 4.3 Iconografía

- **Mínima.** Las webs de culto casi no tienen iconos: flecha (`→`, `↗`), hamburguesa y, como mucho, redes en el pie. OHM dibuja sus símbolos en ASCII/mono.
- **Flechas tipográficas** en vez de iconos de librería: «Show full program ›» (Berghain), «→» (Boiler Room), «↘ UP NEXT» (Input).
- Superclubs y festivales usan fuentes de iconos propias (Kappa, Primavera) o Bootstrap Icons (Mondo) y Font Awesome (DC-10). Pesan y se ven genéricas.
- **Nadie pone iconos de reloj y chincheta en cada tarjeta.** El dato va en mono y se entiende solo: `VIE 24.10 · 23:59 · SALA 1`.

### 4.4 Forma

- **Esquinas rectas** en 25 de 34. Redondeadas sólo en Tomorrowland, Hï, Kappa y en el botón de Pacha: son las más «producto/app».
- **Filetes de 1 px** para separar filas (OHM, Basement, Berghain).
- **Imágenes a sangre o recortadas** (Basement recorta objetos sobre negro, sin caja).
- **Mayúsculas** en titulares y line-ups.

### 4.5 Movimiento

- Vídeo en bucle en el héroe: Pacha, Hï, DC-10, Mondo, Input, Shelter.
- **Lenis** (scroll suave): Input y Shelter. **GSAP**: Input.
- Carruseles con **Swiper** (Pacha, Tomorrowland, Kappa, DC-10), Splide (Tresor, Mondo) y Slick (Apolo).
- Las de culto no tienen animación. La tipografía es la animación.

---

## 5. Tecnología

| Stack | Webs |
|---|---|
| **WordPress** (Divi, WPBakery) | Tresor, Input, Nowadays, OHM, DC-10 |
| **Webflow** | fabric, Kappa |
| **Squarespace** | FOLD |
| **Next.js** | Pacha, Sónar, Tomorrowland (+ Prismic), Boiler Room |
| **Nuxt (Vue)** | Hï Ibiza, Razzmatazz, Shelter (+ DatoCMS) |
| **React a medida** | De School, Basement |
| A medida / PHP | Berghain, Robert Johnson, Amnesia, Mondo, Apolo, Primavera (GraphQL propio) |

**CMS headless** en las más modernas: Prismic (Tomorrowland), DatoCMS (Shelter), un CMS propio en `cms.` (De School) y GraphQL (Primavera).

**Ticketing (enlazado, nunca integrado):** RA (OHM, Razzmatazz), DICE (Razzmatazz), Notikumi (Apolo), Mutick y Entradium (Razzmatazz), Shotgun y Fourvenues (habitual en España), y Superstruct members (Sónar, Awakenings). DICE ofrece un widget oficial de listado (Partner ID + API key desde DICE MIO); hay un plugin de WordPress que lo envuelve.

**Media:**
- Imágenes: CDN propio (`cdn.`, `assets.`), Cloudinary (Input), BunnyCDN (Hï), S3 (Pacha) y Webflow CDN.
- Vídeo: Vimeo (Shelter) o MP4 propio.
- Audio: embed de SoundCloud (Mondo).

**Medición y consentimiento:**
- Cookiebot (8 webs), OneTrust, CookieYes, iubenda y CookieFirst.
- Rastreadores: GA4, Meta Pixel, TikTok Pixel, Clarity y Hotjar.
- **Berghain, OHM, Robert Johnson y De School cargan cero rastreadores de terceros** y por eso no necesitan banner. Es una decisión de marca: respeto y rapidez.

**Rendimiento observado:** las de culto son las más ligeras (Berghain hace 3 peticiones de dominio propio). Las de superclub cargan entre 25 y 40 dominios de terceros.

---

## 6. Galerías de fotos

| Web | Cómo lo hace |
|---|---|
| **Shelter** · Night Gallery | Una página por **exposición o noche** (`/nightgallery/cloudwalk`): título gigante, texto breve y fotos **a ancho completo, una debajo de otra** (scroll vertical, sin rejilla). Debajo, «View more of our exhibitions» con portadas de las otras galerías. |
| **Sónar** · Galerías | Álbumes por edición y día; patrocinado por Fujifilm (House of Photography). |
| **Razzmatazz** · Histórico | Archivo de carteles por año. |
| **Berghain** | **Sin fotos de público** (política de no fotografiar). La galería es el arte de los carteles. |
| **Boiler Room** | La galería es el vídeo. |
| **Hï, Pacha, Amnesia** | Carruseles Swiper de fotos de ambiente en la home; sin álbum por noche. |
| **fabric** | Fotos sólo en noticias. |

**Patrones útiles:**

1. **Álbum por noche, no un saco de fotos.** La gente busca «la del sábado». La URL `/galeria/2026-10-24-hector-oaks` se comparte por WhatsApp y posiciona.
2. **Móvil: una columna a ancho completo o rejilla de 2**, nunca miniaturas de 4 en fila.
3. **Visor a pantalla completa con gesto de deslizar** (PhotoSwipe v5 es el estándar: unos 15 KB, zoom con pellizco y deslizar para cerrar). También lightGallery.
4. **Portada = una foto + fecha + nombre de la noche + número de fotos.**
5. **Encuéntrate por selfie** (reconocimiento facial): plataformas como Captured, Pixeva o Kamero ofrecen «sube un selfie y te enseño tus fotos» con un QR en el local. Ningún club de la muestra lo tiene todavía. Ojo: en la UE la biometría es dato especial (art. 9 RGPD) y exige consentimiento explícito y borrado rápido.

---

## 7. Ficha de evento (lo que no falta)

Sacado de Berghain (`/en/event/…`), fabric (What's On) y RA:

- **Fecha completa + hora de inicio + hora de fin** (fabric: `Fri | 23.10 | 23.00 — 06.00`).
- **Line-up por sala**, con el sello o colectivo de cada artista en pequeño (Berghain: «Chami *dig curated*», «Norman Nodge *ostgut ton*»).
- **Bio del artista principal** en un párrafo.
- **Botón de entradas** con precio y proveedor.
- **Arte del cartel** con su crédito («Artwork by …»): Tresor y Berghain siempre lo acreditan.
- Edad mínima, política de puerta y, en algunos, «no fotos».

---

## 8. Diagnóstico de la web actual de Barullo

Capturada con el mismo móvil emulado y la misma herramienta que las demás webs.

| Problema | Por qué se ve «tosco» |
|---|---|
| El logo es «BARULLO» en texto cromado | Las webs de referencia tienen logo propio. Barullo **tiene** uno (la chapa octograma con «ba/ru/llo» en cúfico) y la web no lo usa. |
| Paleta pizarra azulada + rojo `#FF3B4E` | No es la de marca (negro `#0B0B0B`, hueso `#F2EFE8`, rojo `#E63B2E`). Se ve «modo oscuro de app», no cartel. |
| Inter + Archivo a anchura normal | Es la combinación por defecto de mil plantillas. El manual de marca pide Archivo 800 expandida para line-ups y Space Mono para datos. |
| Radios de 10–20 px, píldoras y cápsulas | Las webs de club usan esquina recta. El radio es lo que más «SaaS» la hace parecer. |
| Etiquetas («eyebrows») en píldora roja encima de cada titular | Plantilla de landing. |
| Bloque «2 · 400 · Jue–Sáb» en cajitas | Lenguaje de producto, no de club. |
| Iconos de reloj y chincheta en cada dato | Ruido; los datos en mono se leen solos. |
| Agenda en carrusel horizontal de tarjetas | Esconde fechas (en móvil se ve 1,2 tarjetas). Todas las de culto usan **lista vertical**. |
| Galería con huecos vacíos cuando no hay fotos | Se ve rota. |
| Dos botones rojos «Comprar entradas» seguidos | El del héroe y la barra fija coinciden en el primer scroll. |
| Héroe de 3 bloques (vídeo + texto + cartel) | La primera pantalla no tiene una jerarquía clara. |

---

## 9. Cómo puede innovar Barullo

Ideas ordenadas por impacto y coste, con lo que ya hay en el repo.

1. **La web es el cartel.** El manual de marca ya define la rejilla del cartel: cabecera con emblema, título, imagen única, line-up centrado en Archivo y **barra de datos en celdas** `[emblema][rama][SALA][día · hora][fecha]`. Llevarla tal cual a la web, en las fichas, en la home y en la agenda, hace que web, story y cartel sean la misma pieza. **Nadie en la muestra lo hace.** *(Implementado.)*
2. **Ramas de color por género** («Un emblema, muchas frecuencias»). Cada noche lleva el chip de su rama: B/01 Techno (rojo láser), B/02 Urbano (cobalto), B/03 DnB·Afro (lima). Así la agenda se lee de reojo por estilo, y se puede filtrar. Es el equivalente de las salas de Berghain o Basement, pero por frecuencia. *(Chip implementado; el filtro queda pendiente.)*
3. **Agenda tipográfica**, estilo OHM o Basement, con el cartel pequeño al lado. *(Implementado.)*
4. **Accesos directos de 1 toque**: Entradas, Mesa, Cómo llegar (abre Maps) y Normas de la casa. *(Implementado.)*
5. **Galería por noche** con portada, número de fotos y visor de deslizar; URL compartible. *(Implementado: portadas en la home y `/galeria` con un álbum por noche, índice de fechas y ancla compartible `/galeria#noche`. El visor PhotoSwipe queda pendiente.)*
6. **Sin banner de cookies.** Usar Vercel Analytics (ya instalado, sin cookies) y no meter Meta ni TikTok Pixel en la web; las campañas se miden con UTM. Es la jugada de Berghain y OHM: la primera pantalla limpia.
7. **«Esta noche» en directo.** Mientras dura la noche, el héroe muestra la etiqueta `ABIERTO AHORA` con un punto latiendo, y la agenda marca `HOY` en rojo. Es barato (sólo depende de la fecha) y se siente de app. *(Implementado. Pendiente: que el botón pase a «Lista / taquilla».)*
8. **Añadir al calendario (.ics)** en cada evento. Ningún club de la muestra lo ofrece en la web. *(Implementado: `/eventos/[slug]/ics`.)*
9. **Mixes de residentes** (SoundCloud embebido con carga diferida, sólo al pulsar).
10. **Encuéntrate en la galería** (selfie → tus fotos), cumpliendo el art. 9 del RGPD. Sería la primera vez en un club español; mejor como piloto con un proveedor.
11. **Wallet pass / PWA**: añadir Barullo a la pantalla de inicio, con aviso de preventa. Sólo si la newsletter funciona.

**Qué NO copiar:**
- Vídeo de ambiente como único héroe (Pacha, Hï): pesa y no contesta a «¿qué hay?».
- Carruseles automáticos (Apolo, Tomorrowland): nadie ve la 3.ª diapositiva.
- Banners de cookies a pantalla completa.
- Más de 3 fuentes.
- La web de festival (cuenta atrás, line-up por días): Barullo es un club semanal.

---

## 10. Librerías recomendadas (si hacen falta)

| Necesidad | Librería | Peso aprox. | Nota |
|---|---|---|---|
| Visor de galería | **PhotoSwipe 5** | ~15 KB gz | Gestos nativos, sin dependencias. Estándar del sector. |
| Carrusel (si de verdad hace falta) | CSS `scroll-snap` | 0 KB | Ya se usa en el repo. Embla, si hiciera falta JS. |
| Scroll suave | Lenis | ~4 KB | Input y Shelter. **No recomendado** en móvil e Instagram: se pelea con el scroll nativo. |
| Animación | CSS `animation-timeline: view()` | 0 KB | Ya en el repo. GSAP sólo para piezas puntuales. |
| Fuentes | `next/font` (Archivo variable con eje `wdth`, Space Mono) | — | Autoalojadas: sin Google en tiempo de ejecución. |
| CMS | Sanity, Payload o DatoCMS | — | `src/lib/events.ts` ya es el punto de cambio. |
| Ticketing | Enlace a Fourvenues, DICE o Shotgun | — | El widget de DICE existe si se cambia de proveedor. |
| Analítica | Vercel Analytics | — | Ya instalado, sin cookies y sin banner. |

---

## 11. Skills de agente consultadas (`/find-skills`)

Búsquedas en skills.sh: «nightclub website» (0 resultados), «event website», «photo gallery», «mobile web design» y «landing page design».

| Skill | Instalaciones | ¿Sirve? |
|---|---|---|
| `nextlevelbuilder/ui-ux-pro-max-skill@ui-ux-pro-max` | 405K | **Ya instalada** en el proyecto. Guías de UX móvil y paletas. |
| `anthropics/skills@frontend-design` | 1M | **Ya instalada.** Dirección estética. |
| `samber/dev-event-organizer-skills@event-landing-page` | 4K | Orientada a conferencias tech; poco aplicable. |
| `kostja94/marketing-skills@schema-markup` | 1,3K | JSON-LD de eventos; el repo ya lo tiene (`src/lib/seo.tsx`). |
| `nutlope/hallmark@hallmark` | 65K | Landings genéricas: justo lo que hay que evitar. |
| Galerías de fotos | <300 | Nada fiable; no se instala ninguna. |

No hace falta instalar nada nuevo: las dos skills útiles ya estaban.

---

## Fuentes

- Capturas y huellas técnicas propias de 34 webs, tomadas el 20 de octubre de 2026 (lista arriba).
- [Captured: fotografía de eventos con reconocimiento facial (PetaPixel)](https://petapixel.com/2024/08/16/facial-recognition-tech-could-transform-event-photography)
- [Cómo funciona la búsqueda por selfie (Kamero)](https://helios-event.kamero.ai/resources/how-selfie-search-finds-your-photos)
- [Find Your Photos con reconocimiento facial (Nunify)](https://help.nunify.com/en/articles/15858870-how-to-find-your-photos-using-facial-recognition)
- [Xinc Events for Dice: widget oficial de DICE](https://ja.wordpress.org/plugins/xinc-events-for-dice/)
- [Ejemplos de webs de nightclub (Zarla)](https://www.zarla.com/guides/nightclub-website-examples)
- [31 webs de club (HubSpot)](https://blog.hubspot.com/website/club-websites)
- skills.sh: búsquedas con `npx skills find`.

---

## 12. Qué se ha cambiado en la web (v2, 20 de octubre de 2026)

| Pieza | Antes | Ahora |
|---|---|---|
| Logo | «BARULLO» en texto cromado | Emblema real (octograma «ba/ru/llo») + lockup «BARULLO · CLVB · VIGO» (`components/brand/Emblem.tsx`) |
| Paleta | Pizarra azulada + `#FF3B4E` | Negro `#0B0B0B`, hueso `#F2EFE8`, rojo Barullo `#E63B2E`, y colores de rama sólo en chips |
| Fuentes | Archivo + Inter | Archivo variable (100 % texto, 125 % titulares con `wide`) + Space Mono (`data`) |
| Forma | Radios de 10–20 px y píldoras | Esquina recta y filetes de 1 px |
| Cabecera | Logo · menú en cápsula · Entradas (sólo escritorio) | Lockup · Entradas (también en móvil) · menú numerado a pantalla completa |
| Héroe | Vídeo + bloque de texto + flyer | Vídeo + rejilla de cartel: rama, estado, fecha gigante, line-up de uno en uno, barra de datos en celdas y CTA |
| Agenda | Carrusel de tarjetas | Lista tipográfica con filete de rama, separada por meses con cabecera pegajosa (`EventRow`) |
| Accesos directos | — | Entradas · Mesa · Cómo llegar (Maps) · Normas |
| Galería | Mosaico suelto | Álbum por noche, en la home y en `/galeria` |
| Identidad | «Una sala de Vigo…» + cifras en cajas | «Un emblema, muchas frecuencias» + lista de ramas |
| Reservas y privados | Dos tarjetas con icono | Dos filas de texto gigante |
| Newsletter | Panel con vídeo de cromo | Bloque hueso a sangre (paleta invertida) |
| Pie | Iconos de redes | Emblema grande, datos en mono, redes en texto con ↗ |
| Barra fija móvil | Umbral fijo (se duplicaba con el CTA) | Sube sólo cuando el CTA del héroe ha salido de pantalla |
| Ficha de evento | Fichas con iconos | Cartel: fecha, line-up, barra de datos y «Añadir al calendario» |

**Pendiente:**
- Filtro de agenda por rama.
- Visor PhotoSwipe.
- Quitar la galería de eventos futuros en los datos demo.
- Mixes de residentes.
- Selfie-search.
