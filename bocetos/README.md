# bocetos/ — Diseño de Barullo

Material de trabajo de la marca: diseños, animaciones y fotos. **No se publica**: lo que ve la web vive en
`public/media/` y ahí se queda (moverlo rompe la web). Los másteres de vídeo siguen en `remotion/out/`.

```
bocetos/
  DIRECCION-VISUAL.md   la dirección visual (fuente de verdad)
  disenos/              logo y mascota
  animaciones/          colgante, alfombra, héroes de la web y carteles animados (+ renders/)
  fotos/                inspiración y fotos demo
  scripts/              generadores compartidos (texturas y escenas de Blender)
  investigacion/        informes
```

| Carpeta | Qué hay |
|---|---|
| `DIRECCION-VISUAL.md` | La dirección visual escrita de la web (paleta, tipografía, reglas). Fuente de verdad. |
| `fotos/inspiracion/pinterest/` | Las referencias de Pinterest (ref-01..17 y hojas de contactos). Material de terceros, solo consulta. |
| `fotos/inspiracion/disenadora-carteles-persas/` | Los carteles riso de la diseñadora: alfombra persa, dragones, rojo/naranja/rosa. |
| `disenos/logo/lettering-kufi/` | El lettering kufi «barullo» vectorizado (`wordmark.svg`, `wordmark.json`), máscara y versiones planas blanca/roja. |
| `disenos/logo/estilos/<estilo>/` | **Los estilos finales**: cada uno con `lettering.png` y `medalla.png` (la «o» suelta como medalla), en PNG transparente y versión sobre negro. `_formatos-medalla/`: cinta, moneda, púas, pin. |
| `disenos/logo/exploraciones/` | Pruebas que llevaron a los estilos: `prototipos-alfombra/` (tapiz, hinchable, cromo, LED), `materiales/` (11 acabados), `plata-grabada/` (variantes grabadas + `lienzo/` con galería local). |
| `disenos/logo/chapa-3d/` | La chapa y el logo largo 3D anteriores (Blender) y avatares/favicon. |
| `disenos/logo/medalla-puas/` | La medalla de púas y el rediseño del lettering con VectorCraft. |
| `animaciones/alfombra/` | Generador procedural de alfombra persa (`carpet.py`), `texturas/` (riso, LED, ember) y `rug/` (alfombra voladora animada, en curso). |
| `animaciones/carteles/` | Carteles animados de discoteca (story y feed). `renders/`: los terminados (agenda nov. 2026, plantillas de DJ, stills), copia de `C:/Users/Veintiuno/barullo-render/carteles/`. |
| `animaciones/colgante/` | El colgante-medalla del héroe de la home (bucle de 7 s). |
| `animaciones/heroes/` | Fondos animados de cada sección: club, entradas, propón, contacto. |
| `disenos/mascota/` | El diablillo de cromo: referencias, escena de Blender y `vector/diablillo.svg`. |
| `scripts/` | Todos los generadores: texturas (`carpet.py`, `logo_tex.py`, `engrave_tex.py`, `medal_tex.py`, `trace.py`) y escenas de Blender (`engr.py` lettering, `medal.py` medalla, `mats.py`, `logo3d.py`). `estilos.json` es el catálogo de estilos y `render_estilos.sh` los renderiza todos. |
| `fotos/fotos-demo/` | Fotos demo de Unsplash (copia de `public/media/demo/`). |
| `investigacion/` | Informes (ArtCraft). |

## Renderizar los estilos

Las escenas se ejecutan con Blender 5.2 de Windows desde WSL. La carpeta de trabajo con texturas y HDRI está en
`C:/Users/Veintiuno/barullo-render/logo-alfombra/` (fuera del repo para no disparar el watcher de Next).
Para añadir un estilo: una entrada nueva en `estilos.json` y `bash render_estilos.sh` (solo renderiza lo que falta).

Lienzos en claude.ai: [materiales](https://claude.ai/artifact/LizrYVvoEUxp2yuBHY9MQa) ·
[plata grabada](https://claude.ai/artifact/4thEGskG2UeDxsXznjZsKb) · [medalla O](https://claude.ai/artifact/EjaAjWzEBAnKvgast5PG52) ·
[bocetos, todo junto](https://claude.ai/artifact/QPiHfJF8hK63T4LAGEm3RF).
