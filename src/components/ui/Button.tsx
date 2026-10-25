import Link from "next/link";
import type { ComponentProps, ReactNode } from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "chrome" | "outline" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

/**
 * Tres niveles de jerarquía y ni uno más:
 *   macizo   -> la acción que queremos que pulses (comprar, reservar)
 *   contorno -> la alternativa razonable (ver agenda, ver galería)
 *   fantasma -> lo terciario (cancelar, volver)
 *
 * Esa es la regla de color de toda la web: relleno sólido para lo importante,
 * borde para lo secundario, nada para lo demás.
 */
const VARIANTS: Record<Variant, string> = {
  primary: "bg-acid text-void hover:bg-milk",
  chrome: "bg-milk text-void hover:bg-acid",
  outline: "border border-edge text-milk hover:border-acid hover:text-acid",
  ghost: "text-ash hover:bg-slate hover:text-milk",
  danger: "bg-blood text-void hover:bg-milk",
};

const SIZES: Record<Size, string> = {
  sm: "min-h-10 px-4 text-sm",
  // 48px de alto: el mínimo cómodo para el pulgar en móvil.
  md: "min-h-12 px-6 text-base",
  lg: "min-h-14 px-8 text-lg",
};

const BASE =
  "inline-flex items-center justify-center gap-2 rounded-pill font-black transition-colors duration-150 active:scale-[0.98] disabled:pointer-events-none disabled:opacity-40";

type Props = {
  variant?: Variant;
  size?: Size;
  className?: string;
  children: ReactNode;
};

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...rest
}: Props & ComponentProps<"button">) {
  return (
    <button className={cn(BASE, VARIANTS[variant], SIZES[size], className)} {...rest}>
      {children}
    </button>
  );
}

export function ButtonLink({
  variant = "primary",
  size = "md",
  className,
  children,
  href,
  external,
  ...rest
}: Props & { href: string; external?: boolean } & Omit<ComponentProps<"a">, "href">) {
  const classes = cn(BASE, VARIANTS[variant], SIZES[size], className);

  if (external) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className={classes} {...rest}>
        {children}
      </a>
    );
  }
  return (
    <Link href={href} className={classes} {...rest}>
      {children}
    </Link>
  );
}
