import Link from "next/link";
import type { ClubEvent } from "@/content/events";
import { shortDate } from "@/lib/dates";
import { Marquee } from "@/components/ui/Marquee";

/**
 * Cinta de próximas fechas, a sangre y en color macizo.
 *
 * Es el patrón de Antídoto, y la clave es que sea RUIDOSA: una banda sólida de
 * acento con texto negro, no una franja oscura con letra pequeña. Anuncia
 * varias noches de golpe, grita, y no roba sitio al evento principal.
 */
export function EventTicker({ events }: { events: ClubEvent[] }) {
  if (events.length === 0) return null;

  const items = events.map((e) => (
    <Link
      key={e.slug}
      href={`/eventos/${e.slug}`}
      className="inline-flex items-baseline gap-2.5 hover:underline"
    >
      <span className="data">{shortDate(e.date)}</span>
      <span className="caps">{e.title.toUpperCase()}</span>
      {e.status === "ultimas" && <span>· ÚLTIMAS</span>}
      {e.status === "agotado" && <span>· AGOTADO</span>}
    </Link>
  ));

  return (
    <div className="bg-acid py-1 text-void">
      <Marquee
        items={items}
        separator="//"
        className="text-[13px] font-bold uppercase tracking-tight sm:text-sm"
      />
    </div>
  );
}
