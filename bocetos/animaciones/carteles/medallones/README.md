# Serie MEDALLONES · 5 flyers

Cinco carteles animados (story 2160×3840 y feed 2160×2700, bucle de 8 s a 30 fps), uno por viernes, cada uno con un medallón «o» del catálogo de estilos (`bocetos/disenos/logo/estilos/`) girando despacio en el centro. La maqueta sigue la plantilla R2 URBANO (`REBRANDING BARULLO/03_RAMAS/R2_URBANO/01_CROMO_BRILLANTES`):

- cabecera con la estrella y BARULLO, y una píldora con el número y el nombre del medallón;
- de título, el lettering 3D en el mismo material que el medallón;
- etiquetas de género y fecha;
- el medallón;
- line up y barra de datos.

| # | Estilo | Fecha | Fondo |
|---|---|---|---|
| B/01 | `oro-turquesa` (oro viejo, rosetas y cabujón turquesa) | 06.11 | petróleo |
| B/02 | `oro-perlas` (oro, arabesco turquesa, perla) | 13.11 | azul noche |
| B/03 | `oro-girih-rubi` (oro, girih esmaltado, rubí) | 20.11 | rojo sangre |
| B/04 | `oro-esmeralda` (oro, girih verde, esmeralda) | 27.11 | verde botella |
| B/05 | `oro-rosa-coral` (oro rosa, escamas, coral) | 04.12 | magenta |

## Piezas

- `medallon_anim.py`: Blender Cycles. Usa la medalla de dos caras de `comun/medalla_lib.py` (`build_style`), así que medio giro cierra el bucle.
  - El giro va lento de cara y más rápido de canto.
  - Los contraluces se tiñen con el color del fondo.
  - Una barra de luz cruza la cara dos veces por bucle.
  - Escribe `m_####.png` y `pts_*.json` (posición en pantalla de la gema y de las 8 puntas, para los destellos).
- `render_medallones.sh`: renderiza los 240 frames de cada estilo por tramos de 30 (un Blender por tramo). Repite lo que falte hasta 3 pasadas y une los JSON en `pts.json`.
- `render_lettering.sh`: renderiza el lettering de cada estilo al 200% (`RES_PCT=200` en `scripts/engr.py`).
- La maqueta está en Remotion, en `remotion/src/carteles/Medallones.tsx`. Las composiciones son `Medallon1-Story` … `Medallon5-Feed`, y sus datos están en `Root.tsx` (`MEDALLONES`).
  - Con `frames: false`, el cartel usa la medalla fija de `assets/med/key/` en lugar de la secuencia renderizada.
  - El fondo se pinta en código: degradado, rayos, celosía de estrellas en hilo de oro y polvo de oro.

## Regenerar

```bash
cd bocetos/animaciones/carteles/medallones
setsid nohup bash render_lettering.sh > …/logs/lettering.log 2>&1 &
setsid nohup bash render_medallones.sh > …/logs/medallones.log 2>&1 &   # ~50 s/frame, 1200 frames
python3 ../comun/serve.py /mnt/c/Users/Veintiuno/barullo-render/carteles/assets &
bash render_flyers.sh            # los 5 carteles a bocetos/animaciones/carteles/medallones/0X-<estilo>/
```
