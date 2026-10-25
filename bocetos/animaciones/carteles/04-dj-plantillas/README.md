# Anuncio de DJ · 3 plantillas animadas

Un post por artista (story 9:16 y feed 4:5, bucle de 8 s a 30 fps). Las tres llevan la base de la marca: cabecera con la chapa
y BARULLO en Kufi, píldora (semana o rol) y la barra de datos en celdas. Cambiar de DJ = otra foto + otro JSON.

| Plantilla | Composición | Idea |
|---|---|---|
| **A · MEDALLÓN** | `DjMedallon-Story` / `-Feed` | La foto del/de la DJ dentro del hueco de la medalla «o» de oro (render de Blender de frente, `medallon_marco.py`). El oro cambia de brillo (6 variantes de luz fundidas en bucle), el medallón se mece en 3D con la foto dentro, destellos en las puntas al compás. Fondo negro con halo y octogramas de línea girando. |
| **B · CRISTAL** | `DjCristal-Story` / `-Feed` | Organización tipo Mondo: la foto manda, a sangre, en duotono negro→color→hueso con un velo translúcido; panel de cristal esmerilado con día, fecha en Kufi, nombre condensado y rol. La foto empuja y deriva despacio, un brillo cruza el cristal. |
| **C · RECORTE** | `DjRecorte-Story` / `-Feed` | El/la DJ recortado/a en B/N con borde de pegatina, delante de la chapa negra gigante (gira 45° por bucle) y franjas con su nombre en Kufi que corren. Fondo de color plano, sello octogonal con la fecha que late, banda negra con el nombre. |

Código: `remotion/src/carteles/dj/` (`comun.tsx` con props, cabecera, barra, duotono; `DjMedallon.tsx`, `DjCristal.tsx`, `DjRecorte.tsx`; `ejemplos.ts`).
Las composiciones están registradas en `remotion/src/carteles/Root.tsx`.

## Props (un JSON por DJ, ejemplos en `djs/`)

```json
{ "dj": "CONGUCHU", "rol": "DJ SET", "genero": "ELECTRÓNICA · BREAKS",
  "foto": "dj-cascos-violeta", "encuadre": {"x": 0.45, "y": 0.36, "zoom": 1.0},
  "fecha": "20.11", "dia": "VIERNES", "anio": "2026", "semana": "NOVIEMBRE · SEMANA 03",
  "sala": {"nombre": "KINGSTON CLUB", "direccion": "RÚA ROGELIO ABALDE 18", "ciudad": "VIGO", "horario": "1:00 — 4:30"},
  "color": "#E63B2E", "color2": "#FF6A4D", "medalla": "oro-turquesa", "variantes": 6 }
```

- `foto`: nombre base de la foto preparada (sin extensión). `encuadre.x/y`: punto de la foto que se centra (0..1); `zoom` > 1 acerca.
  En C, `encuadre.x` desplaza el recorte y `zoom` lo escala.
- `color`: A → color de líneas y textos de acento (turquesa con el oro-turquesa); B → tono medio del duotono y celda de fecha;
  C → color del fondo (rojo Barullo `#E63B2E` por defecto). `color2`: A → halo y destellos; B → velo translúcido.
- `semana`: va en la píldora (B, C) o bajo la cabecera (A). Vacío para ocultarla. El nombre se ajusta solo al ancho.
- `medalla`: carpeta `marco-<estilo>` en los assets (solo A). Hay `oro-turquesa`; otro estilo del catálogo se renderiza con `medallon_marco.py`.

## Flujo para un DJ nuevo

1. **Foto** (vertical u horizontal, mín. 1500 px, la cara bien iluminada):
   `PYTHONPATH=~/.local/rembg-lib python3 prep_foto.py /ruta/foto.jpg` → deja `<n>.jpg`, `-blur.jpg`, `-cut.png`, `-borde.png`, `.json`
   en `C:/Users/Veintiuno/barullo-render/carteles/assets/dj-plantillas/fotos/`. (rembg es libre y local:
   `pip install --target ~/.local/rembg-lib "rembg[cpu]"`; el primer uso descarga el modelo.) Revisar el recorte para la plantilla C.
2. **JSON**: copiar uno de `djs/` y cambiar datos y `foto`.
3. **Servidor de assets** (si no está): `python3 ../comun/serve.py /mnt/c/Users/Veintiuno/barullo-render/carteles/assets`.
4. **Revisar fijos**: `PROPS="$(cat djs/x.json)" bash stills.sh 40 DjCristal-Story DjCristal-Feed`.
5. **Render**: `bash render_dj.sh DjCristal djs/x.json` → `barullo-render/carteles/dj-plantillas/x/`
   (`story.mp4` 2160×3840, `feed.mp4` 2160×2700, `story-1080.mp4`, `feed-1080.mp4`, `story.png`, `feed.png`).

## Medalla de la plantilla A

`medallon_marco.py` (Cycles CPU): medalla del catálogo de frente, sin gema, hueco agrandado ×1.3 (`HOLE=`) con filete de oro,
N variantes de luz (`l_<i>.png`) + `marco.json` (polígono del hueco y puntas). Unos 5 min por variante a 2048 px.

    blender.exe -b --factory-startup --python '\\wsl.localhost\DDEV\home\ddev\www\barullo\design\carteles\04-dj-plantillas\medallon_marco.py' -- C:/Users/Veintiuno/barullo-render/logo-alfombra oro-turquesa C:/Users/Veintiuno/barullo-render/carteles/assets/dj-plantillas/marco-oro-turquesa 6 20 2048

## Fotos

`fotos-placeholder/` son **fotos de relleno de Unsplash** (ver `CREDITOS.md`), no son DJs de Barullo. Sustituir antes de publicar.
