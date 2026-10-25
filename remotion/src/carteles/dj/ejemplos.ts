import { DjProps } from './comun';

// Datos de ejemplo (fotos de relleno de Unsplash, ver bocetos/animaciones/carteles/04-dj-plantillas/fotos-placeholder/CREDITOS.md).
// Para otro DJ: copiar uno de los JSON de bocetos/animaciones/carteles/04-dj-plantillas/djs/ y renderizar con --props.
const KINGSTON = { nombre: 'KINGSTON CLUB', direccion: 'RÚA ROGELIO ABALDE 18', ciudad: 'VIGO', horario: '1:00 — 4:30' };

export const EJ_MEDALLON: DjProps = {
  dj: 'CARAMELORARØ', rol: 'DJ SET', genero: 'TECHNO · HARDGROOVE',
  foto: 'dj-humo-teal', encuadre: { x: 0.56, y: 0.3, zoom: 1.0 },
  fecha: '13.11', dia: 'VIERNES', anio: '2026', semana: 'NOVIEMBRE · SEMANA 02', sala: KINGSTON,
  color: '#3FD8C8', color2: '#1FA89C', medalla: 'oro-turquesa', variantes: 6,
};

export const EJ_CRISTAL: DjProps = {
  dj: 'CONGUCHU', rol: 'DJ SET', genero: 'ELECTRÓNICA · BREAKS',
  foto: 'dj-cascos-violeta', encuadre: { x: 0.45, y: 0.36, zoom: 1.0 },
  fecha: '20.11', dia: 'VIERNES', anio: '2026', semana: 'NOVIEMBRE · SEMANA 03', sala: KINGSTON,
  color: '#E63B2E', color2: '#FF6A4D', medalla: 'oro-turquesa', variantes: 6,
};

export const EJ_RECORTE: DjProps = {
  dj: 'BOUZAS', rol: 'ALL NIGHT LONG', genero: 'HOUSE · DISCO',
  foto: 'dj-brazo-arriba', encuadre: { x: 0.5, y: 0.5, zoom: 1.0 },
  fecha: '27.11', dia: 'VIERNES', anio: '2026', semana: 'NOVIEMBRE · SEMANA 04', sala: KINGSTON,
  color: '#E63B2E', color2: '#FF6A4D', medalla: 'oro-turquesa', variantes: 6,
};
