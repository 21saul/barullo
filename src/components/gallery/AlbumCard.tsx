import Image from "next/image";
import Link from "next/link";
import type { ClubEvent } from "@/content/events";
import { shortDate } from "@/lib/dates";

/**
 * Álbum como un montón de copias en papel: la portada encima y dos fotos más
 * asomando por detrás, giradas. Al pasar por encima se abren en abanico; así
 * se ve que dentro hay más de una foto sin tener que entrar.
 */
export function AlbumCard({ event, photos }: { event: ClubEvent; photos: string[] }) {
  const [cover, second, third] = [photos[0] ?? event.flyer.src, photos[1], photos[2]];
  return (
    <Link href={`/galeria/${event.slug}`} className="group block">
      <div className="relative aspect-[4/5] p-3 sm:p-4">
        {third && (
          <div className="absolute inset-3 overflow-hidden rounded-md bg-slate ring-1 ring-rule transition-transform duration-500 ease-[var(--ease-soft)] [transform:rotate(-5deg)] group-hover:[transform:rotate(-9deg)_translateX(-6%)] sm:inset-4">
            <Image src={third} alt="" fill sizes="30vw" className="object-cover opacity-60" />
          </div>
        )}
        {second && (
          <div className="absolute inset-3 overflow-hidden rounded-md bg-slate ring-1 ring-rule transition-transform duration-500 ease-[var(--ease-soft)] [transform:rotate(4deg)] group-hover:[transform:rotate(8deg)_translateX(6%)] sm:inset-4">
            <Image src={second} alt="" fill sizes="30vw" className="object-cover opacity-75" />
          </div>
        )}
        <div className="relative h-full overflow-hidden rounded-md bg-slate ring-1 ring-white/10 transition-transform duration-500 ease-[var(--ease-soft)] group-hover:-translate-y-1">
          <Image
            src={cover}
            alt={`Portada del álbum de ${event.title}`}
            fill
            sizes="(min-width: 1024px) 30vw, 50vw"
            className="object-cover"
          />
          <span className="absolute right-2.5 top-2.5 rounded-pill bg-void/80 px-2.5 py-1 text-xs font-extrabold text-milk backdrop-blur">
            {photos.length} fotos
          </span>
        </div>
      </div>
      <div className="px-3 sm:px-4">
        <p className="text-sm font-bold capitalize text-dust">{shortDate(event.date)}</p>
        <h3 className="caps mt-1 text-lg leading-tight text-milk transition-colors group-hover:text-acid sm:text-xl">
          {event.title}
        </h3>
      </div>
    </Link>
  );
}
