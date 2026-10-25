import Link from "next/link";
import { subscribe } from "@/app/actions";
import { Icon } from "@/components/ui/Icon";
import { RandomMedal } from "@/components/home/RandomMedal";

/**
 * Captación de correo: el único canal que no depende del algoritmo de
 * Instagram. Es la banda roja que abre el pie, con la medalla girando.
 *
 * Dos maquetas que comparten piezas, y el CSS enseña una u otra según el
 * ancho (sin JS, sin parpadeo): en móvil, título con la medalla a su derecha
 * y el formulario en columna; desde `md`, texto a la izquierda y medalla
 * grande a la derecha. Server Action; sólo la medalla usa JS en cliente.
 */
export function Newsletter() {
  return (
    <>
      {/* Móvil */}
      <div className="bg-acid px-5 pb-8 pt-7 text-void md:hidden">
        <div className="flex items-center gap-3">
          <Title className="min-w-0 flex-1 text-[2.6rem]" />
          <Medal className="size-[6.5rem] shrink-0" sizes="104px" />
        </div>
        <Lead className="mt-4 text-base" />
        <form action={subscribe} className="mt-5 flex flex-col gap-2">
          <EmailField id="newsletter-email-m" className="min-h-14 rounded-pill bg-void px-5" />
          <SubmitButton className="min-h-14 w-full" />
        </form>
        <Privacy />
      </div>

      {/* Ordenador y tableta */}
      <div className="hidden grid-cols-2 items-center gap-10 bg-acid px-10 py-12 text-void md:grid lg:px-16 lg:py-14">
        <div className="min-w-0">
          <Title className="text-[clamp(3rem,6vw,5rem)]" />
          <Lead className="mt-4 max-w-md text-lg" />
          <form action={subscribe} className="mt-6 flex max-w-lg gap-1.5 rounded-pill bg-void p-1.5">
            <EmailField id="newsletter-email" className="min-h-12 flex-1 rounded-pill bg-transparent px-4" />
            <SubmitButton className="min-h-12 shrink-0" />
          </form>
          <Privacy />
        </div>
        <Medal className="size-[240px] justify-self-center lg:size-[320px]" sizes="(min-width: 1024px) 320px, 240px" />
      </div>
    </>
  );
}

function Title({ className }: { className: string }) {
  return (
    <h2 className={`wide uppercase leading-none ${className}`}>
      La agenda,
      <br />
      antes que nadie
    </h2>
  );
}

function Lead({ className }: { className: string }) {
  return (
    <p className={`font-bold leading-snug ${className}`}>
      Un correo a la semana con los line-ups y las preventas. Te das de baja con un clic.
    </p>
  );
}

function EmailField({ id, className }: { id: string; className: string }) {
  return (
    <>
      <label htmlFor={id} className="sr-only">
        Tu correo electrónico
      </label>
      <input
        id={id}
        type="email"
        name="email"
        required
        autoComplete="email"
        placeholder="tucorreo@ejemplo.com"
        className={`min-w-0 text-base font-semibold text-milk placeholder:text-ash ${className}`}
      />
    </>
  );
}

function SubmitButton({ className }: { className: string }) {
  return (
    <button
      type="submit"
      className={`inline-flex items-center justify-center gap-2 rounded-pill bg-milk px-6 text-base font-black text-void transition-colors hover:bg-void hover:text-milk ${className}`}
    >
      Apuntarme
      <Icon name="Send" size={17} />
    </button>
  );
}

function Privacy() {
  return (
    <p className="mt-3 px-1 text-sm font-semibold">
      Al apuntarte aceptas la{" "}
      <Link href="/legal/privacidad" className="font-extrabold underline underline-offset-2 hover:text-milk">
        política de privacidad
      </Link>
      .
    </p>
  );
}

/** Una medalla al azar en cada recarga, girando (quieta con «reducir movimiento»). */
function Medal({ className, sizes }: { className: string; sizes: string }) {
  return <RandomMedal className={`pointer-events-none relative ${className}`} sizes={sizes} />;
}
