import type { EventStatus } from "@/content/events";
import type { Rama } from "@/content/ramas";
import { cn } from "@/lib/utils";

/**
 * Etiquetas de la noche. Cápsula con punto de color: el punto dice el estado
 * de reojo y el texto lo dice para quien no distingue el color. Macizo sólo
 * cuando hay que correr (últimas) o cuando es gratis.
 */
const STYLES: Record<EventStatus, { label: string; className: string; dot: string }> = {
  anunciado: { label: "A la venta", className: "border-edge text-milk", dot: "bg-r3" },
  ultimas: { label: "Últimas entradas", className: "border-acid bg-acid text-void", dot: "bg-void animate-pulse-dot" },
  agotado: { label: "Agotado", className: "border-rule text-dust", dot: "bg-dust" },
  cancelado: { label: "Cancelado", className: "border-rule text-dust line-through", dot: "bg-dust" },
  gratis: { label: "Entrada libre", className: "border-milk bg-milk text-void", dot: "bg-acid" },
};

const FLAG =
  "inline-flex items-center gap-1.5 whitespace-nowrap rounded-pill border px-2.5 py-1 text-[11px] font-extrabold leading-none tracking-[0.01em]";

export function StatusBadge({ status, className }: { status: EventStatus; className?: string }) {
  const s = STYLES[status];
  return (
    <span className={cn(FLAG, s.className, className)}>
      <span aria-hidden="true" className={cn("size-1.5 rounded-full", s.dot)} />
      {s.label}
    </span>
  );
}

/** Género de la noche: punto del color de la rama y el nombre, sin código. */
export function RamaTag({ rama, className }: { rama: Rama; className?: string }) {
  return (
    <span className={cn(FLAG, "border-rule bg-slate/80 text-milk backdrop-blur", className)}>
      <span aria-hidden="true" className={cn("size-1.5 rounded-full", rama.dot)} />
      {rama.name}
    </span>
  );
}
