import Link from "next/link";
import { KufiWordmark } from "@/components/brand/KufiWordmark";
import { cn } from "@/lib/utils";

/**
 * Logo de la cabecera: el wordmark kufi «barullo» del diseñador, el mismo que
 * va tejido en la alfombra del héroe. Sustituye al lockup emblema + texto.
 *
 * `size` es la altura del wordmark en px.
 */
export function Wordmark({
  className,
  asLink = true,
  size = 34,
}: {
  className?: string;
  asLink?: boolean;
  size?: number;
}) {
  const logo = (
    <KufiWordmark
      title={asLink ? "" : "Barullo"}
      className={cn("block text-milk", className)}
      style={{ height: size, width: "auto" }}
    />
  );

  if (!asLink) return logo;
  return (
    <Link
      href="/"
      aria-label="Barullo · inicio"
      className="inline-flex transition-colors duration-150 hover:[&_svg]:text-acid"
    >
      {logo}
    </Link>
  );
}
