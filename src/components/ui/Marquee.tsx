import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Cinta infinita, en CSS puro (0 KB de JS). El contenido se duplica y la
 * animación recorre el -50%, así que el salto es invisible.
 *
 * La copia va `aria-hidden` e `inert` para que ni se lea dos veces ni duplique
 * puntos de tabulación.
 */
function Track({
  items,
  separator,
  clone,
}: {
  items: ReactNode[];
  separator: ReactNode;
  clone?: boolean;
}) {
  return (
    <div
      className="flex shrink-0 items-center gap-6 pr-6"
      aria-hidden={clone || undefined}
      inert={clone || undefined}
    >
      {items.map((item, i) => (
        <span key={i} className="flex shrink-0 items-center gap-6">
          <span className="whitespace-nowrap">{item}</span>
          <span className="opacity-60">{separator}</span>
        </span>
      ))}
    </div>
  );
}

export function Marquee({
  items,
  className,
  separator = "\u2726",
  reverse = false,
}: {
  items: ReactNode[];
  className?: string;
  separator?: ReactNode;
  reverse?: boolean;
}) {
  return (
    <div className={cn("relative flex overflow-hidden", className)}>
      <div
        className="flex animate-marquee"
        style={reverse ? { animationDirection: "reverse" } : undefined}
      >
        <Track items={items} separator={separator} />
        <Track items={items} separator={separator} clone />
      </div>
    </div>
  );
}
