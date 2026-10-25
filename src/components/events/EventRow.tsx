import Image from "next/image";
import Link from "next/link";
import type { ClubEvent } from "@/content/events";
import { ramaOf } from "@/content/ramas";
import { Icon } from "@/components/ui/Icon";
import { monthKey, monthShort, monthYear, time, weekdayShort, isToday } from "@/lib/dates";
import { RamaTag, StatusBadge } from "./StatusBadge";
import { cn } from "@/lib/utils";

/**
 * Una noche = una fila. Tres columnas fijas y siempre en el mismo orden, para
 * que la vista recorra la lista en vertical sin buscar:
 *   [fecha]  [título · line-up · etiquetas]  [cartel + flecha]
 * La fecha va en un bloque propio (día gordo, día de la semana y mes), el
 * título en Anton y los datos en cápsulas debajo. Toda la fila es un enlace.
 */
export function EventRow({ event, priority = false }: { event: ClubEvent; priority?: boolean }) {
  const rama = ramaOf(event);
  const lineup = event.lineup.map((a) => a.name).join(", ");
  const today = isToday(event.date);

  return (
    <article className="group relative">
      <Link
        href={`/eventos/${event.slug}`}
        className="grid grid-cols-[4rem_1fr] items-center gap-4 rounded-md px-2 py-4 transition-colors duration-150 hover:bg-coal sm:grid-cols-[5rem_1fr_auto] sm:gap-6 sm:px-4 sm:py-5"
      >
        <div
          className={cn(
            "flex aspect-square flex-col items-center justify-center rounded-md text-center ring-1",
            today ? "bg-acid text-void ring-acid" : "bg-coal text-milk ring-rule group-hover:bg-slate",
          )}
        >
          <span className={cn("text-[11px] font-extrabold uppercase leading-none", today ? "text-void" : "text-ash")}>
            {today ? "Hoy" : weekdayShort(event.date)}
          </span>
          <span className="data mt-1 text-[1.75rem] font-black leading-none sm:text-[2.125rem]">{event.date.getDate()}</span>
          <span className={cn("mt-1 text-[11px] font-extrabold uppercase leading-none", today ? "text-void" : "text-dust")}>
            {monthShort(event.date)}
          </span>
        </div>

        <div className="min-w-0">
          <h3 className="caps text-lg leading-tight text-milk text-balance transition-colors group-hover:text-acid sm:text-[1.375rem]">
            {event.title}
          </h3>
          {lineup && <p className="mt-1.5 line-clamp-1 text-sm font-semibold text-ash sm:text-base">{lineup}</p>}
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
            <RamaTag rama={rama} />
            <StatusBadge status={event.status} />
            <span className="ml-1 inline-flex items-center gap-1 text-xs font-bold text-dust">
              <Icon name="Clock3" size={13} />
              {time(event.date)}
              <span aria-hidden="true" className="px-1 text-edge">/</span>
              {event.room}
            </span>
          </div>
        </div>

        <div className="hidden items-center gap-5 sm:flex">
          <div className="relative size-24 overflow-hidden rounded-md bg-slate">
            <Image
              src={event.flyer.src}
              alt=""
              fill
              sizes="96px"
              priority={priority}
              className="object-cover transition duration-300 group-hover:scale-105"
            />
          </div>
          <span className="flex size-11 items-center justify-center rounded-full border border-edge text-milk transition-colors group-hover:border-acid group-hover:bg-acid group-hover:text-void">
            <Icon name="ArrowUpRight" size={18} />
          </span>
        </div>
      </Link>
    </article>
  );
}

/**
 * Lista de noches. Con `byMonth`, separa por meses con una cabecera pegajosa,
 * como el «October» de Robert Johnson o el «OCTUBRE» de Mondo: al hacer scroll
 * largo siempre sabes en qué mes estás.
 */
export function EventList({
  events,
  byMonth = false,
  priorityCount = 0,
}: {
  events: ClubEvent[];
  byMonth?: boolean;
  priorityCount?: number;
}) {
  if (!byMonth) {
    return (
      <ul className="divide-y divide-rule">
        {events.map((e, i) => (
          <li key={e.slug}>
            <EventRow event={e} priority={i < priorityCount} />
          </li>
        ))}
      </ul>
    );
  }

  const groups = new Map<string, ClubEvent[]>();
  for (const e of events) {
    const k = monthKey(e.date);
    groups.set(k, [...(groups.get(k) ?? []), e]);
  }
  let n = 0;

  return (
    <div>
      {[...groups.values()].map((list) => (
        <section key={monthKey(list[0].date)} aria-label={monthYear(list[0].date)}>
          <h3 className="sticky top-16 z-10 -mx-1 bg-void/90 px-1 py-3 backdrop-blur">
            <span className="caps text-lg text-milk">{monthYear(list[0].date)}</span>
            <span className="ml-3 text-sm font-bold text-dust">
              {list.length} {list.length === 1 ? "noche" : "noches"}
            </span>
          </h3>
          <ul className="divide-y divide-rule">
            {list.map((e) => (
              <li key={e.slug}>
                <EventRow event={e} priority={n++ < priorityCount} />
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
