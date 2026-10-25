import type { ClubEvent } from "@/content/events";
import { time, weekdayShort, dayNumber } from "@/lib/dates";
import { DepartureBoard, type BoardRow } from "@/components/events/DepartureBoard";

const STATUS: Record<ClubEvent["status"], string> = {
  anunciado: "A la venta",
  ultimas: "Últimas",
  agotado: "Agotado",
  gratis: "Gratis",
  cancelado: "Cancelado",
};

/** Las próximas noches convertidas en filas de la pantalla de salidas. */
export function toBoardRows(events: ClubEvent[]): BoardRow[] {
  return events.map((e) => ({
    day: `${weekdayShort(e.date)} ${dayNumber(e.date)}`,
    time: time(e.date),
    // Lo que cabe en 16 casillas: el cabeza de cartel, si no el título.
    title: (e.lineup.find((a) => a.isHeadliner)?.name ?? e.title).normalize("NFC"),
    status: STATUS[e.status],
    hot: e.status === "ultimas" || e.status === "agotado",
  }));
}

/**
 * Fondo del héroe de /agenda: la pantalla, en perspectiva, a la derecha en
 * escritorio y arriba en móvil (asomando por el borde, como si la pantalla
 * fuera más grande que el encuadre), con el resplandor rojo del club.
 */
export function AgendaScene({ events }: { events: ClubEvent[] }) {
  return (
    <div className="absolute inset-0 overflow-hidden bg-void">
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-[radial-gradient(60%_55%_at_72%_38%,rgb(230_59_46/0.22),transparent_70%)]"
      />
      <div className="absolute left-4 top-[24%] origin-top-left [perspective:1400px] sm:left-auto sm:right-[-6%] sm:top-[38%] sm:-translate-y-1/2 lg:right-[3%] 2xl:right-[6%]">
        <div className="[transform:rotateY(-16deg)_rotateX(6deg)] [transform-style:preserve-3d] sm:[transform:rotateY(-22deg)_rotateX(4deg)]">
          <DepartureBoard rows={toBoardRows(events)} visible={6} />
        </div>
      </div>
    </div>
  );
}
