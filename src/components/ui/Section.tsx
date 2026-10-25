import Link from "next/link";
import type { ReactNode } from "react";
import { Icon } from "@/components/ui/Icon";
import { cn } from "@/lib/utils";

export function Section({
  children,
  className,
  id,
}: {
  children: ReactNode;
  className?: string;
  id?: string;
}) {
  return (
    <section id={id} className={cn("relative px-4 py-12 sm:px-8 md:py-20", className)}>
      <div className="mx-auto w-full max-w-6xl 2xl:max-w-7xl 3xl:max-w-[100rem]">{children}</div>
    </section>
  );
}

/**
 * Cabecera de sección, como la de Antídoto: título gordo a la izquierda,
 * «ver todos» a la derecha y un filete debajo. El enlace se ve también en
 * móvil, a la altura del título, que es donde se busca.
 *
 * `as`: en la home es h2, en interiores h1 (jerarquía para SEO y lectores).
 */
export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
  as: Tag = "h2",
  className,
}: {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  action?: { href: string; label: string };
  as?: "h1" | "h2";
  className?: string;
}) {
  return (
    <div className={cn("mb-6 sm:mb-8", className)}>
      <div className="flex items-end justify-between gap-4 border-b border-rule pb-4">
        <div className="min-w-0">
          {eyebrow && <p className="mb-2 text-sm font-bold text-acid">{eyebrow}</p>}
          <Tag className="wide text-[clamp(2.5rem,11vw,5rem)] uppercase leading-none text-milk text-balance">
            {title}
          </Tag>
        </div>

        {action && (
          <Link
            href={action.href}
            className="group mb-1 inline-flex shrink-0 items-center gap-2 text-sm font-extrabold text-milk transition-colors duration-150 hover:text-acid sm:text-base"
          >
            {action.label}
            <span className="flex size-8 items-center justify-center rounded-full bg-milk text-void transition-colors group-hover:bg-acid">
              <Icon name="ArrowUpRight" size={16} />
            </span>
          </Link>
        )}
      </div>
      {description && (
        <p className="mt-4 max-w-prose text-base leading-relaxed text-ash sm:text-lg">{description}</p>
      )}
    </div>
  );
}

/** Enlace ancho al final de un bloque, para el pulgar. */
export function SectionAction({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="group mt-6 flex min-h-14 w-full items-center justify-between rounded-pill border border-edge pl-6 pr-2 text-base font-extrabold text-milk transition-colors duration-150 hover:border-acid"
    >
      {label}
      <span className="flex size-10 items-center justify-center rounded-full bg-acid text-void transition-transform group-hover:translate-x-0.5">
        <Icon name="ArrowRight" size={18} />
      </span>
    </Link>
  );
}
