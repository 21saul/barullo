import Link from "next/link";
import { Icon } from "@/components/ui/Icon";

export interface Crumb {
  label: string;
  href?: string;
}

/**
 * Migas de pan visibles.
 *
 * Ya emitíamos `BreadcrumbList` en JSON-LD para que Google pintase la ruta en
 * el resultado de búsqueda, pero el usuario no la veía por ninguna parte. Las
 * migas resuelven la pregunta "¿dónde estoy y cómo subo un nivel?" sin gastar
 * el botón atrás del navegador, que en el WebView de Instagram a veces cierra
 * la vista entera en lugar de retroceder.
 *
 * La última miga no es un enlace: enlazar a la página en la que ya estás es
 * ruido para el lector de pantalla.
 */
export function Breadcrumbs({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Ruta de navegación" className="mb-6">
      <ol className="no-scrollbar flex items-center gap-1.5 overflow-x-auto text-sm">
        {items.map((item, i) => {
          const last = i === items.length - 1;
          return (
            <li key={item.label} className="flex shrink-0 items-center gap-1.5">
              {i > 0 && <Icon name="ChevronRight" size={12} className="text-dust" />}
              {last || !item.href ? (
                <span className="font-semibold text-milk" aria-current="page">
                  {item.label}
                </span>
              ) : (
                <Link
                  href={item.href}
                  className="text-ash transition-colors hover:text-acid"
                >
                  {item.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

/**
 * Flecha de volver. Va arriba del todo en las vistas de detalle.
 *
 * Es un enlace a una ruta concreta, no un `history.back()`: si alguien entra
 * directo a un evento desde una historia de Instagram no tiene historial que
 * deshacer, y un botón atrás que no hace nada es peor que no tenerlo.
 */
export function BackLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="group mb-5 inline-flex min-h-11 items-center gap-2 text-sm font-semibold text-ash transition-colors hover:text-milk"
    >
      <span className="flex size-8 items-center justify-center rounded-pill border border-rule transition-colors duration-150 group-hover:border-acid group-hover:text-acid">
        <Icon name="ArrowLeft" size={14} />
      </span>
      {label}
    </Link>
  );
}
