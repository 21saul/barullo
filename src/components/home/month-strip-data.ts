import { addDays, differenceInCalendarDays, format, isSameDay, isToday, startOfDay } from "date-fns";
import { es } from "date-fns/locale";
import type { ClubEvent, EventStatus } from "@/content/events";
import { dayNumber, monthShort, shortDate, time, weekdayShort } from "@/lib/dates";

/**
 * Datos de la Tira del mes ya formateados. Se preparan en el servidor y el
 * componente cliente sólo pinta: así las horas salen en la zona del club y no
 * en la del navegador (si no, la hidratación no casaría).
 */
export type StripNight = {
  slug: string;
  title: string;
  flyer: { src: string; alt: string };
  day: string;
  weekday: string;
  month: string;
  today: boolean;
  label: string;
  doors: string;
  room: string;
  lineup: string;
  status: EventStatus;
  ticketUrl?: string;
  priceFrom?: number;
};

export type StripDay = {
  key: string;
  day: string;
  /** Inicial del día de la semana: «L», «M», «X»... */
  initial: string;
  /** Abreviatura del mes, sólo el día 1 y el primero de la regla. */
  month?: string;
  /** Jueves a sábado, las noches del club: raya más larga. */
  clubDay: boolean;
  /** Índice de la noche de ese día, si hay. */
  night?: number;
};

const INITIAL = ["D", "L", "M", "X", "J", "V", "S"];

export function buildMonthStrip(events: ClubEvent[], from: Date) {
  const start = startOfDay(from);
  const nights: StripNight[] = events.map((e) => {
    const headliners = e.lineup.filter((a) => a.isHeadliner).map((a) => a.name);
    return {
      slug: e.slug,
      title: e.title,
      flyer: e.flyer,
      day: dayNumber(e.date),
      weekday: weekdayShort(e.date),
      month: monthShort(e.date),
      today: isToday(e.date),
      label: shortDate(e.date),
      doors: time(e.date),
      room: e.room,
      lineup: (headliners.length ? headliners : e.lineup.map((a) => a.name)).join(", "),
      status: e.status,
      ticketUrl: e.ticketUrl,
      priceFrom: e.priceFrom,
    };
  });

  // La regla cubre 30 días, o hasta la última noche si cae más lejos.
  const last = events.at(-1)?.date ?? start;
  const length = Math.min(62, Math.max(30, differenceInCalendarDays(last, start) + 1));
  const days: StripDay[] = Array.from({ length }, (_, i) => {
    const d = addDays(start, i);
    const night = events.findIndex((e) => isSameDay(e.date, d));
    return {
      key: format(d, "yyyy-MM-dd"),
      day: format(d, "d", { locale: es }),
      initial: INITIAL[d.getDay()],
      month: i === 0 || d.getDate() === 1 ? monthShort(d) : undefined,
      clubDay: [4, 5, 6].includes(d.getDay()),
      night: night >= 0 ? night : undefined,
    };
  });

  return { nights, days };
}
