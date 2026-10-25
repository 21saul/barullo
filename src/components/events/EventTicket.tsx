import Image from "next/image";
import Link from "next/link";
import type { ClubEvent } from "@/content/events";
import { ramaOf } from "@/content/ramas";
import { shortDate, time, isToday } from "@/lib/dates";
import { RamaTag, StatusBadge } from "./StatusBadge";
import { cn } from "@/lib/utils";

/**
 * Tarjeta de la próxima noche con forma de entrada: el cartel arriba, el
 * troquel (las dos muescas y la línea de puntos) y la matriz con los datos
 * abajo. Es la pieza del carrusel «Tickets» de la home, como en Antídoto.
 *
 * Toda la tarjeta lleva a la ficha de la noche (enlace estirado), y el botón
 * de entradas va encima y sale directo al proveedor. Dos enlaces hermanos, no
 * anidados: un <a> dentro de otro no es HTML válido.
 */
export function EventTicket({ event, priority = false }: { event: ClubEvent; priority?: boolean }) {
  const rama = ramaOf(event);
  const today = isToday(event.date);
  const headliners = event.lineup.filter((a) => a.isHeadliner).map((a) => a.name);
  const lineup = (headliners.length ? headliners : event.lineup.map((a) => a.name)).join(", ");
  const canBuy = event.ticketUrl && event.status !== "agotado" && event.status !== "cancelado";

  return (
    <article className="group relative flex h-full flex-col overflow-hidden rounded-md bg-coal ring-1 ring-rule transition-[box-shadow] duration-200 hover:ring-edge">
      <div className="relative aspect-[4/5] overflow-hidden bg-slate">
        <Image
          src={event.flyer.src}
          alt={event.flyer.alt}
          fill
          sizes="(min-width: 1024px) 30vw, (min-width: 640px) 45vw, 82vw"
          priority={priority}
          className="object-cover transition-transform duration-500 ease-[var(--ease-soft)] group-hover:scale-[1.04]"
        />
        <div className="absolute inset-x-0 top-0 flex flex-wrap gap-1.5 p-3">
          <StatusBadge status={event.status} />
          <RamaTag rama={rama} />
        </div>
        {/* Fecha grande sobre el cartel, como el sello de una entrada. */}
        <div className="absolute bottom-3 left-3 rounded-sm bg-void/85 px-3 py-2 text-center backdrop-blur">
          <p className={cn("text-[11px] font-extrabold uppercase", today ? "text-acid" : "text-ash")}>
            {today ? "Hoy" : shortDate(event.date).split(" ")[0]}
          </p>
          <p className="data text-3xl font-black leading-none text-milk">{event.date.getDate()}</p>
        </div>
      </div>

      <div className="flex flex-1 flex-col px-4 pb-4 pt-4">
        <h3 className="caps text-lg leading-tight text-milk text-balance">
          <Link href={`/eventos/${event.slug}`} className="after:absolute after:inset-0 after:content-['']">
            {event.title}
          </Link>
        </h3>
        {lineup && <p className="mt-2 line-clamp-1 text-sm font-semibold text-ash">{lineup}</p>}
      </div>

      {/* Troquel: muescas del color del fondo + línea de puntos. */}
      <div className="relative h-0" aria-hidden="true">
        <span className="absolute -left-2.5 -top-2.5 size-5 rounded-full bg-void ring-1 ring-rule" />
        <span className="absolute -right-2.5 -top-2.5 size-5 rounded-full bg-void ring-1 ring-rule" />
        <span className="absolute inset-x-4 top-0 border-t-2 border-dotted border-edge" />
      </div>

      <div className="flex items-center justify-between gap-3 px-4 py-3.5">
        <dl className="min-w-0 leading-tight">
          <dt className="sr-only">Fecha y puertas</dt>
          <dd className="data whitespace-nowrap text-[15px] capitalize text-milk">{shortDate(event.date)}</dd>
          <dd className="mt-0.5 whitespace-nowrap text-[13px] font-bold text-dust">
            Puertas {time(event.date)}
          </dd>
        </dl>
        {canBuy ? (
          <a
            href={event.ticketUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="relative z-10 inline-flex h-10 shrink-0 items-center gap-1.5 rounded-pill bg-acid px-4 text-sm font-black text-void transition-colors hover:bg-milk"
          >
            Entradas
            {event.priceFrom ? <span className="font-bold text-void/70">· {event.priceFrom} €</span> : null}
          </a>
        ) : (
          <span className="relative z-10 shrink-0 rounded-pill border border-edge px-4 py-2 text-sm font-bold text-ash">
            {event.status === "gratis" ? "Entrada libre" : event.status === "agotado" ? "Agotado" : "Ver noche"}
          </span>
        )}
      </div>
    </article>
  );
}
