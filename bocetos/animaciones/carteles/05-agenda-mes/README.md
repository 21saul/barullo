# 05 · Agenda del mes

Cartel animado con **todas las noches del mes**. Se publica el día 1 y se fija arriba del perfil.
Hay una sola fuente de datos: `agenda-2026-11.json`. **Las noches de noviembre son de ejemplo (PLACEHOLDER)** y hay que cambiarlas por las reales.

| Salida | Formato | Qué es |
|---|---|---|
| `…_agenda_story.mp4` | 1080×1920 · 30 fps · ~20 s | Intro (emblema, medallón, NOVIEMBRE en Kufi, tira de fechas) → una escena por semana (SEMANA 01/04…, máx. 3 noches) → el mes entero → cierre (ENTRADAS · LINK EN BIO). Entre escenas, cortinilla roja con la estrella. |
| `…_agenda_feed.mp4` | 1080×1350 · 30 fps · bucle de 8 s | El mes de un vistazo. La fila activa recorre las noches, la medalla cambia con ella (se pone de canto) y abajo corre la cinta roja. |
| `…_agenda_feed.png/.jpg` | 2160×2700 | Fijo del feed sin fila activa (post o impresión). |
| `…_agenda_story.png/.jpg` | 2160×3840 | Fotograma «el mes entero» de la story. |

## Cambiar el mes

1. Copia `agenda-2026-11.json` → `agenda-2026-12.json` y edita los campos:
   - `month` (en mayúsculas, p. ej. `DICIEMBRE`) y `year`.
   - `events[]`, una entrada por noche:
     - `date`: `AAAA-MM-DD`. El día de la semana sale solo.
     - `title`: el **género real** de la noche (TECHNO, REGGAETON, DRUM & BASS…). Nunca nombres inventados.
     - `tag`: una línea corta (opcional).
     - `lineup`: un DJ por línea. CARAMELORARØ siempre con Ø.
     - `venue`: `kingston`, `doppler` o `rem`. Las salas están en `venues` y se pueden añadir.
     - `hours`: opcional. Si no se pone, se usa el horario de la sala.
     - `medal`: el estilo de medallón, que da el color de la noche. Puede ser `oro-turquesa` · `oro-girih-rubi` · `plata-joya-rubi` · `oro-esmeralda` · `oro-perlas` · `oro-rosa-coral`.
     - `color`: opcional, `#RRGGBB`, para forzar el color de la noche.
2. Arranca el servidor de assets, si no está ya: `python3 ../comun/serve.py /mnt/c/Users/Veintiuno/barullo-render/carteles/assets`
3. Para revisar rápido: `bash render.sh agenda-2026-12.json check`. Los fotogramas quedan en `barullo-render/carteles/agenda-mes/<mes>/check/`.
4. Para el render final: `bash render.sh agenda-2026-12.json`. Los archivos quedan en `C:/Users/Veintiuno/barullo-render/carteles/agenda-mes/2026-12_DICIEMBRE/` y se copian a
   `Desktop/REBRANDING BARULLO/04_CARTELES/AGENDA_MES/`.

La duración de la story se calcula sola: 2,8 s de intro + 3 s por semana + 3,6 s del mes + 2 s de cierre.
Caben bien entre 4 y 10 noches. Si una semana tiene 3 noches, la escena reduce el tamaño de todo. Ninguna línea se corta, porque las que no caben se escalan.

## Piezas

- Composición: `remotion/src/carteles/Agenda.tsx` (`Agenda-Story`, `Agenda-Feed`, registradas en `Root.tsx`). Studio:
  `cd remotion && npx remotion studio src/carteles/index.ts --public-dir=/mnt/c/Users/Veintiuno/barullo-render/carteles/public`.
- Assets (en `barullo-render/carteles/assets/agenda/`, servidos en :8765):
  - `emblema.svg`: el logo real, octograma rojo + ba/ru/llo, de `01_LOGO/ORIGINAL_REDIBUJADO`.
  - `med-<estilo>.png`: los medallones del catálogo `bocetos/disenos/logo/estilos/`, a 800 px.
  - `lettering-oro-turquesa.png`: el lettering 3D del cierre.
  - El fondo es la alfombra LED de los carteles de noviembre (`led-story.jpg` y `led-feed.jpg`).
- Fuentes (máx. 3): Kufi Barullo (fechas, mes y BARULLO), Archivo 800/700 al 125 % (géneros y line-up), Space Mono (datos).
- Referencias y lo que se coge de cada una: `REFERENCIAS.md`.
