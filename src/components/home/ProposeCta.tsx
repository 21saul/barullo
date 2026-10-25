import Link from "next/link";
import { Icon } from "@/components/ui/Icon";
import { RandomMedal } from "@/components/home/RandomMedal";

/**
 * La llamada que no es comprar una entrada. Un club vive de quien programa:
 * colectivos, sellos y artistas que quieren hacer su noche aquí.
 *
 * Panel oscuro como el resto de la home; el rojo se queda en un plato redondo
 * sobre el que gira una de las medallas, otra en cada recarga. Es la única
 * pieza que se mueve sola en la sección.
 *
 * Una sola rejilla con dos colocaciones: en móvil, título arriba con la
 * medalla pequeña a su derecha y el resto debajo a todo el ancho; en
 * ordenador, texto a la izquierda y la medalla grande a la derecha ocupando
 * las dos filas. La medalla es un único elemento para las dos colocaciones.
 */
export function ProposeCta() {
  return (
    <section className="px-4 py-12 sm:px-8 md:py-20">
      <div className="mx-auto grid w-full max-w-6xl grid-cols-[minmax(0,1fr)_auto] items-center gap-x-4 overflow-hidden rounded-lg bg-coal px-5 py-8 ring-1 ring-rule sm:px-12 sm:py-14 lg:grid-cols-[minmax(0,7fr)_minmax(0,5fr)] lg:gap-x-14 lg:py-16 2xl:max-w-7xl 3xl:max-w-[100rem]">
        <h2 className="wide text-[clamp(2.4rem,9vw,5.25rem)] uppercase leading-none text-milk text-balance lg:self-end">
          ¿Tienes una noche en la cabeza?
        </h2>

        <div className="relative aspect-square w-32 sm:w-40 lg:row-span-2 lg:w-full lg:max-w-md lg:justify-self-center">
          <div className="absolute inset-[9%] rounded-full bg-acid" />
          <RandomMedal className="absolute inset-0" sizes="(min-width: 1024px) 28rem, 10rem" />
        </div>

        <div className="col-span-2 lg:col-span-1 lg:self-start">
          <p className="mt-5 max-w-md text-lg font-semibold leading-snug text-ash">
            Colectivos, sellos y artistas: si tienes algo que contar con música, el club se presta.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              href="/eventos-privados"
              className="group inline-flex min-h-14 items-center gap-3 rounded-pill bg-acid pl-6 pr-2 text-lg font-black text-void transition-colors hover:bg-milk"
            >
              Propón tu noche
              <span className="flex size-10 items-center justify-center rounded-full bg-void text-milk transition-transform group-hover:rotate-45">
                <Icon name="ArrowUpRight" size={20} />
              </span>
            </Link>
            <Link
              href="/contacto"
              className="inline-flex min-h-14 items-center rounded-pill px-6 text-lg font-black text-milk ring-2 ring-edge ring-inset transition-colors hover:bg-milk hover:text-void hover:ring-milk"
            >
              Escríbenos
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
