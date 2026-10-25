import { staticFile } from 'remotion';
import { z } from 'zod';

/**
 * Props de StoryEvent y FlyerAnim. Con el esquema, el Studio muestra un
 * formulario para editarlas y `--props` se valida antes de renderizar.
 */
export const eventSchema = z.object({
  title: z.string().min(1),
  /** ISO "2026-10-23T23:59" (recomendado) o texto libre, que se pinta tal cual. */
  date: z.string().min(1),
  /** Un artista por línea; " — " separa el nombre del rol ("warm up", "live"...). */
  lineup: z.array(z.string()),
  room: z.string(),
  /** Precio mínimo en euros. 0 = gratis. */
  priceFrom: z.number().min(0),
  /** Ruta dentro de remotion/public, URL https:// o vacío (arte generativo). */
  flyerSrc: z.string(),
});

export type EventProps = z.infer<typeof eventSchema>;

export const DEMO_EVENT: EventProps = {
  title: 'Barullo Sessions: Héctor Oaks',
  date: '2026-10-23T23:59',
  lineup: ['Héctor Oaks — all night long', 'Nëro — warm up'],
  room: 'Sala Principal',
  priceFrom: 15,
  flyerSrc: 'flyers/demo-nave-techno.jpg',
};

const DAYS = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB'];
const MONTHS = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];

/** "2026-10-23T23:59" → "VIE 23 OCT · 23:59". Si no es ISO, devuelve el texto en mayúsculas. */
export const formatDate = (raw: string) => {
  const m = raw.trim().match(/^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?/);
  if (!m) return raw.toUpperCase();
  const [, y, mo, d, hh, mm] = m;
  const date = new Date(Number(y), Number(mo) - 1, Number(d));
  const day = `${DAYS[date.getDay()]} ${Number(d)} ${MONTHS[Number(mo) - 1]}`;
  return hh ? `${day} · ${hh}:${mm}` : day;
};

export const formatPrice = (price: number) =>
  price <= 0 ? 'GRATIS' : `${Number.isInteger(price) ? price : price.toFixed(2).replace('.', ',')} €`;

export const splitArtist = (line: string) => {
  const [name, ...role] = line.split(/\s+[—–·]\s+/);
  return { name, role: role.join(' · ') };
};

/** `flyerSrc` → URL utilizable por <Img>, o null para usar el arte generativo. */
export const resolveFlyer = (src: string) => {
  const s = src.trim();
  if (!s) return null;
  if (/^(https?:|data:)/.test(s)) return s;
  return staticFile(s.replace(/^\/+/, ''));
};
