import { EVENTS, type ClubEvent } from "@/content/events";
import { monthKey } from "@/lib/dates";

/**
 * Capa de acceso a datos. Hoy lee del array demo de `src/content/events.ts`.
 * Para pasar a un CMS (Sanity, Payload...) basta con cambiar el cuerpo de
 * estas funciones por el fetch correspondiente: las vistas no se tocan.
 */

const byDateAsc = (a: ClubEvent, b: ClubEvent) => a.date.getTime() - b.date.getTime();
const byDateDesc = (a: ClubEvent, b: ClubEvent) => b.date.getTime() - a.date.getTime();

/** Un evento sigue siendo "próximo" hasta su hora de cierre, no hasta que empieza. */
const isUpcoming = (e: ClubEvent) => e.endDate.getTime() >= Date.now();

export async function getUpcomingEvents(limit?: number): Promise<ClubEvent[]> {
  const list = EVENTS.filter(isUpcoming).filter((e) => e.status !== "cancelado").sort(byDateAsc);
  return limit ? list.slice(0, limit) : list;
}

export async function getPastEvents(limit?: number): Promise<ClubEvent[]> {
  const list = EVENTS.filter((e) => !isUpcoming(e)).sort(byDateDesc);
  return limit ? list.slice(0, limit) : list;
}

/** El evento que manda en la home: el próximo en el calendario. */
export async function getNextEvent(): Promise<ClubEvent | null> {
  return (await getUpcomingEvents(1))[0] ?? null;
}

/** Destacados para la home, excluyendo el que ya ocupa el hero. */
export async function getFeaturedEvents(excludeSlug?: string): Promise<ClubEvent[]> {
  const upcoming = await getUpcomingEvents();
  return upcoming.filter((e) => e.slug !== excludeSlug);
}

export async function getEventBySlug(slug: string): Promise<ClubEvent | null> {
  return EVENTS.find((e) => e.slug === slug) ?? null;
}

export async function getAllEventSlugs(): Promise<string[]> {
  return EVENTS.map((e) => e.slug);
}

/** Eventos de un mes concreto. `key` en formato "2026-11". */
export async function getEventsByMonth(key: string): Promise<ClubEvent[]> {
  return EVENTS.filter((e) => monthKey(e.date) === key).sort(byDateAsc);
}

/**
 * Meses con eventos próximos. Alimenta /agenda/[mes], que es donde se pesca
 * el long-tail: "eventos en Vigo noviembre", "discoteca vigo este sábado".
 */
export async function getUpcomingMonths(): Promise<{ key: string; count: number }[]> {
  const upcoming = await getUpcomingEvents();
  const map = new Map<string, number>();
  for (const e of upcoming) {
    const k = monthKey(e.date);
    map.set(k, (map.get(k) ?? 0) + 1);
  }
  return [...map.entries()].map(([key, count]) => ({ key, count })).sort((a, b) => a.key.localeCompare(b.key));
}

/** Fotos agrupadas por noche, de la más reciente a la más antigua. */
export async function getGalleryAlbums(): Promise<{ event: ClubEvent; photos: string[] }[]> {
  const past = await getPastEvents();
  return past
    .filter((event) => (event.gallery?.length ?? 0) > 0)
    .map((event) => ({ event, photos: event.gallery ?? [] }));
}

export type { ClubEvent };
