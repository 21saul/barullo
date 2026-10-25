import type { ClubEvent } from "@/content/events";
import { ButtonLink } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import { Icon } from "@/components/ui/Icon";

const PROVIDER_LABEL: Record<string, string> = {
  fourvenues: "Fourvenues",
  dice: "DICE",
  xceed: "Xceed",
  entradium: "Entradium",
  taquilla: "taquilla",
};

/**
 * La venta la lleva el proveedor externo (Fourvenues/DICE/...), como hacen
 * todos los clubes del sector. Aquí sólo se enlaza, dejando claro a dónde va.
 */
export function TicketButton({
  event,
  size = "lg",
  className,
}: {
  event: ClubEvent;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  if (event.status === "cancelado") {
    return (
      <p className={cn("text-sm font-semibold text-blood", className)}>
        Evento cancelado. Si tenías entrada, te devolvemos el importe.
      </p>
    );
  }

  if (event.status === "agotado") {
    return (
      <div className={cn("flex flex-col gap-2", className)}>
        <span className="inline-flex min-h-12 items-center justify-center rounded-pill border border-edge px-6 font-black text-dust">
          Entradas agotadas
        </span>
        <p className="px-1 text-[13px] font-semibold text-dust">
          Se liberan devoluciones hasta el día del evento. Avisamos por Instagram.
        </p>
      </div>
    );
  }

  if (!event.ticketUrl) {
    return (
      <span
        className={cn(
          "inline-flex min-h-12 items-center justify-center rounded-pill border border-edge px-6 font-bold text-ash",
          className,
        )}
      >
        Entradas próximamente
      </span>
    );
  }

  const provider = event.ticketProvider ? PROVIDER_LABEL[event.ticketProvider] : null;

  // El precio NO va dentro de la etiqueta del botón: "Entradas desde 15 €" en
  // una condensada pesada se parte en dos líneas en una pantalla de 393px y el
  // botón se deforma. Va al lado, en texto normal, donde además se lee mejor.
  const label = event.status === "gratis" ? "Apuntarme a la lista" : "Comprar entradas";
  const precio =
    event.status !== "gratis" && event.priceFrom ? `desde ${event.priceFrom} €` : null;

  return (
    <div className={cn("flex flex-col gap-2", className)}>
      <ButtonLink
        href={event.ticketUrl}
        external
        size={size}
        variant={event.status === "ultimas" ? "danger" : "primary"}
        // A ancho completo el `px-8` del tamaño `lg` no pinta nada y es justo lo
        // que hacía que "Comprar entradas" se partiera en dos líneas a 393 px.
        className="w-full px-4 text-lg sm:w-auto sm:px-9"
      >
        <Icon name="Ticket" size={18} />
        {label}
      </ButtonLink>
      {/* Precio y proveedor bajo el botón, en una sola línea de letra pequeña:
          dentro del botón, en condensada pesada, "Entradas desde 15 €" se
          partía en dos líneas en una pantalla de 393 px. */}
      {(precio || provider) && (
        <p className="px-1 text-[13px] font-semibold text-dust">
          {precio && <span className="font-bold text-ash">Entradas {precio}</span>}
          {precio && provider && " · "}
          {provider && `Venta gestionada por ${provider}, se abre en otra pestaña.`}
        </p>
      )}
    </div>
  );
}
