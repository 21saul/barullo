import { format, isSameDay, isTomorrow, isToday } from "date-fns";
import { es } from "date-fns/locale";

const opts = { locale: es } as const;

/** "Sáb 15 nov" — formato de tarjeta */
export const shortDate = (d: Date) => format(d, "EEE d MMM", opts).replace(".", "");
/** "Sábado 15 de noviembre de 2026" — formato de detalle */
export const longDate = (d: Date) => format(d, "EEEE d 'de' MMMM 'de' yyyy", opts);
/** "15" */
export const dayNumber = (d: Date) => format(d, "d", opts);
/** "NOV" */
export const monthShort = (d: Date) => format(d, "MMM", opts).replace(".", "").toUpperCase();
/** "SÁB" */
export const weekdayShort = (d: Date) => format(d, "EEE", opts).replace(".", "").toUpperCase();
/** "24.10" — formato de cartel y de agenda */
export const dotDate = (d: Date) => format(d, "dd.MM", opts);
/** "23:59" */
export const time = (d: Date) => format(d, "HH:mm", opts);
/** "noviembre 2026" */
export const monthYear = (d: Date) => format(d, "MMMM yyyy", opts);
/** "2026-11" — clave de ruta /agenda/[mes] */
export const monthKey = (d: Date) => format(d, "yyyy-MM");

/** Etiqueta de urgencia para la home: HOY / MAÑANA / fecha */
export function relativeLabel(d: Date) {
  if (isToday(d)) return "HOY";
  if (isTomorrow(d)) return "MAÑANA";
  return shortDate(d).toUpperCase();
}

/** El evento está pasando ahora mismo (entre puertas y cierre). */
export const isLive = (start: Date, end: Date) => {
  const now = Date.now();
  return now >= start.getTime() && now <= end.getTime();
};

export { isSameDay, isToday };
