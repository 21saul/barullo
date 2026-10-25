# Carteles animados · noviembre 2026

Tres carteles de discoteca para Barullo Clvb (Kingston Club, Vigo). Cada uno se entrega en story (2160×3840) y feed (2160×2700), como bucle de 8 s a 30 fps. Siguen la estructura de la plantilla R1 16.10: fecha gigante, objeto 3D, logo, LINE UP y barra de datos en celdas.

| Carpeta | Concepto | 3D |
|---|---|---|
| `01-medalla/` | Medalla «o» de plata joya con rubí, medio giro cada 4 s, sobre alfombra LED | Blender Cycles (`medalla_anim.py`) |
| `02-alfombra-voladora/` | Alfombra persa voladora y logo oro-perlas flotando, mundo riso | Blender EEVEE (`rug_fly.py`, copia de `alfombra/rug/` con vista `band`) |
| `03-cyborg/` | Mascota cyber en cromo negro con la medalla al pecho, sobre alfombra LED | Blender EEVEE (`cyborg_cartel.py`, importa `remotion/blender/barullo_cyber.py`) |
| `05-agenda-mes/` | **Agenda del mes**: todas las noches desde un JSON (story ~20 s por semanas, feed en bucle y PNG). Ver su README | No (medallones del catálogo en PNG) |
| `comun/` | `medalla_lib.py` (medalla compartida), `prep.py` (texturas y assets), `serve.py`, `stills.sh`, `render_cartel.sh` | |

La maquetación y la tipografía están en Remotion: `remotion/src/carteles/` (`Medalla.tsx`, `Alfombra.tsx`, `Cyborg.tsx`, `ui.tsx`).

## Cómo regenerar

Todo se trabaja fuera del repo, en `C:/Users/Veintiuno/barullo-render/carteles/`, para no disparar el watcher de Next:

- `public/`: solo fuentes (Archivo, Space Mono, Chakra Petch).
- `assets/`: texturas, lettering, frames de Blender (`f01/`, `f02/`, `f03/`) y fotogramas clave (`f0Xkey/`).

1. **Assets:** `python3 comun/prep.py <carteles>/assets /home/ddev/www/barullo`. Genera la alfombra LED y riso a tamaño de cartel, `shapes.json` y el lettering recortado de `barullo-render/estilos/`. Después, copia las fuentes a `public/fonts`.
2. **Frames 3D:** desde WSL, con `blender.exe -b --factory-startup --python '\\wsl.localhost\DDEV\home\ddev\www\barullo\design\carteles\…'`. La línea exacta está en el docstring de cada script.
   - Medalla: `-- C:/Users/Veintiuno/barullo-render/logo-alfombra <out> 0-119 48 1600`. Une los `gem_*.json` en `gem.json`.
   - Alfombra: `-- <tex> <out> band 0-239 eevee 64 100`. La textura sale de `rug_tex.py none <tex> 8` y `fringe_cache.npy` de `rug_motion.py`; los dos tienen que estar en `<out>`.
   - Cyborg: `-- --lib <human_base_meshes_bundle.blend> --tex <logo-alfombra/tex/medal> --out <out>/ --view story|feed --frames 1-240`. Renombra el json a `gem_story.json` y `gem_feed.json`.
   - EEVEE a 4K devuelve frames vacíos si otro Blender ocupa la GPU integrada. Renderiza con la GPU libre.
3. **Servidor de assets:** `python3 comun/serve.py <carteles>/assets` (puerto 8765).
4. **Vídeo y JPG:** `bash comun/render_cartel.sh Medalla f01 56 01-medalla`, y lo mismo con `Alfombra f02 …` y `Cyborg f03 …`. Para revisar fijos rápidos, `bash comun/stills.sh <frame> Medalla-Story …`.

Los datos del evento (fecha, line up, sala, género) son props de la composición (`base()` en `Root.tsx`). Se pueden cambiar con `--props`.
