import type { CSSProperties, ReactNode } from "react";
import type { HeroBackdrop } from "@/content/heroes";
import { HeroVideo } from "@/components/ui/HeroVideo";
import Link from "next/link";
import { cn } from "@/lib/utils";

/**
 * Héroe de las páginas interiores: la animación ES el fondo y el título va
 * dentro, no debajo como si fuera una foto con pie.
 *
 * - El fondo es un bucle renderizado (`backdrop`, ver src/content/heroes.ts)
 *   o una escena hecha con el DOM (`scene`), como la pantalla de salidas de
 *   la agenda o el muro de fotos de la galería, que se alimentan de datos.
 * - Los renders salen sobre el mismo negro que la web y además se funden por
 *   abajo con `void`: no se ve el borde de una caja, la página sigue.
 * - El texto va abajo a la izquierda. Los másteres dejan ese hueco libre
 *   (abajo en el vertical, abajo a la izquierda en el apaisado), y un velo
 *   oscuro sólo en esa zona garantiza el contraste sin apagar el motivo.
 * - El título es HTML de verdad (h1): se lee nítido a cualquier tamaño, lo
 *   indexa Google y lo lee un lector de pantalla.
 */
export function PageHero({
  eyebrow,
  title,
  lead,
  children,
  backdrop,
  scene,
  alt = "",
  titleClassName,
  className,
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  lead?: ReactNode;
  /** Acciones (botones, anclas) bajo el texto. */
  children?: ReactNode;
  backdrop?: HeroBackdrop;
  scene?: ReactNode;
  alt?: string;
  titleClassName?: string;
  className?: string;
}) {
  const focus = {
    "--focus-n": backdrop?.narrow.focus ?? "50% 50%",
    "--focus-w": backdrop?.wide.focus ?? "50% 50%",
    "--fit-n": backdrop?.narrow.fit ?? "cover",
    "--fit-w": backdrop?.wide.fit ?? "cover",
    // en móvil el vídeo se desvanece por abajo: si sube (`shift`), su borde
    // no queda como un escalón de color sobre el fondo
    "--mask-n": backdrop?.narrow.mask ?? "linear-gradient(to bottom, #000 82%, transparent)",
    "--zoom-n": backdrop?.narrow.zoom ?? 1,
    "--shift-n": backdrop?.narrow.shift ?? "0px",
  } as CSSProperties;

  return (
    <section
      className={cn(
        "relative isolate overflow-hidden bg-void",
        // Móvil: casi toda la pantalla (menos cabecera y cinta), sin pasarse
        // en teléfonos muy altos. Escritorio: alto pero dejando asomar lo
        // siguiente, para que se entienda que hay más página.
        "min-h-[34rem] h-[min(calc(100svh-5.75rem),50rem)] sm:h-[min(84dvh,56rem)] sm:min-h-[36rem]",
        className,
      )}
      style={focus}
    >
      <div className="absolute inset-0 -z-10" aria-hidden={scene ? true : undefined}>
        {backdrop ? <HeroVideo backdrop={backdrop} alt={alt} /> : scene}
      </div>

      {/* Velos: abajo para fundirse con la página y sostener el texto; a la
          izquierda sólo en escritorio, que es donde va el título. En móvil
          el motivo queda detrás del título (como en escritorio, no encima de
          él), así que el velo de abajo es más ligero y no lo apaga. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 bottom-0 -z-[5] h-[46%] bg-gradient-to-t from-void via-void/60 to-transparent sm:h-1/2 sm:via-void/75"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-y-0 left-0 -z-[5] hidden w-[62%] bg-gradient-to-r from-void/85 via-void/35 to-transparent sm:block"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 -z-[5] h-24 bg-gradient-to-b from-void/70 to-transparent"
      />

      <div className="relative flex h-full flex-col justify-end px-4 pb-8 sm:px-8 sm:pb-14">
        <div className="mx-auto w-full max-w-6xl 2xl:max-w-7xl 3xl:max-w-[100rem]">
          <div className="hero-rise max-w-3xl">
            {eyebrow && (
              <p className="mb-3 inline-flex rounded-pill bg-acid px-3 py-1 text-xs font-black uppercase tracking-wide text-void sm:text-sm">
                {eyebrow}
              </p>
            )}
            <h1
              className={cn(
                "wide text-[clamp(4rem,19vw,11rem)] uppercase text-milk text-balance drop-shadow-[0_2px_24px_rgb(0_0_0/0.45)]",
                titleClassName,
                // después del tamaño: tailwind-merge quita el leading si un
                // text-* llega detrás
                "leading-[0.96]",
              )}
            >
              {title}
            </h1>
            {lead && (
              <div className="mt-4 max-w-2xl text-[clamp(1.05rem,3.6vw,1.45rem)] font-bold leading-snug text-milk/90 text-pretty sm:mt-6">
                {lead}
              </div>
            )}
            {children && <div className="mt-6 flex flex-wrap gap-2 sm:mt-8">{children}</div>}
          </div>
        </div>
      </div>
    </section>
  );
}

/** Ancla en forma de pastilla para las acciones del héroe. */
export function HeroLink({
  href,
  children,
  primary,
}: {
  href: string;
  children: ReactNode;
  primary?: boolean;
}) {
  return (
    <Link
      href={href}
      className={cn(
        "inline-flex min-h-11 items-center rounded-pill px-5 text-sm font-black transition-colors duration-150 sm:text-base",
        primary
          ? "bg-acid text-void hover:bg-milk"
          : "border border-milk/25 bg-void/40 text-milk backdrop-blur-md hover:border-acid hover:text-acid",
      )}
    >
      {children}
    </Link>
  );
}
