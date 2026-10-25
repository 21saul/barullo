import Image from "next/image";
import Link from "next/link";
import type { ClubEvent } from "@/content/events";
import { shortDate } from "@/lib/dates";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Carousel } from "@/components/ui/Carousel";

/**
 * Noches pasadas: una portada por noche que abre su álbum. En carrusel con
 * las portadas laterales algo encogidas, para que la del centro mande; al
 * arrastrar se nota el cambio de plano.
 */
export function GalleryStrip({ albums }: { albums: { event: ClubEvent; photos: string[] }[] }) {
  if (albums.length === 0) return null;

  return (
    <Section>
      <SectionHeading title="Noches pasadas" action={{ href: "/galeria", label: "Galería" }} />
      <Carousel
        label="Álbumes de noches pasadas"
        tween
        slideClassName="basis-[72%] sm:basis-[42%] lg:basis-[30%]"
      >
        {albums.slice(0, 8).map(({ event, photos }, i) => (
          <Link
            key={event.slug}
            href={`/galeria/${event.slug}`}
            className="group relative block aspect-[4/5] overflow-hidden rounded-md bg-slate"
          >
            <Image
              src={photos[0] ?? event.flyer.src}
              alt={`Fotos de ${event.title}`}
              fill
              sizes="(min-width: 1024px) 30vw, (min-width: 640px) 42vw, 72vw"
              priority={i === 0}
              className="object-cover transition-transform duration-700 ease-[var(--ease-soft)] group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-void via-void/20 to-transparent" />
            <span className="absolute right-3 top-3 rounded-pill bg-void/80 px-3 py-1 text-xs font-extrabold text-milk backdrop-blur">
              {photos.length} fotos
            </span>
            <div className="absolute inset-x-0 bottom-0 p-4">
              <p className="text-sm font-bold capitalize text-ash">{shortDate(event.date)}</p>
              <h3 className="caps mt-1 text-lg leading-tight text-milk text-balance sm:text-xl">
                {event.title}
              </h3>
            </div>
          </Link>
        ))}
      </Carousel>
    </Section>
  );
}
