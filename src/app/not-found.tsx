import Link from "next/link";
import { ButtonLink } from "@/components/ui/Button";
export default function NotFound() {
  return (
    <section className="relative flex min-h-[70dvh] items-center overflow-hidden px-5 pt-10 sm:px-8">
      <div className="relative mx-auto w-full max-w-xl text-center">
        <p className="wide text-acid text-8xl leading-none sm:text-9xl">
          404
        </p>
        <h1 className="caps mt-8 text-2xl leading-tight text-milk sm:text-3xl">
          Esta noche no existe
        </h1>
        <p className="mt-4 text-ash">
          El enlace está roto o el evento ya no está publicado. Mira la agenda: seguro que hay algo.
        </p>
        <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
          <ButtonLink href="/agenda">Ver la agenda</ButtonLink>
          <Link
            href="/"
            className="inline-flex min-h-12 items-center justify-center rounded-pill border border-edge px-6 font-bold text-milk hover:border-acid"
          >
            Volver al inicio
          </Link>
        </div>
      </div>
    </section>
  );
}
