import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { getGalleryAlbums } from "@/lib/events";
import { longDate } from "@/lib/dates";
import { breadcrumbJsonLd, JsonLd } from "@/lib/seo";
import { Section } from "@/components/ui/Section";
import { PageHero, HeroLink } from "@/components/ui/PageHero";
import { GalleryScene } from "@/components/gallery/GalleryScene";
import { AlbumCard } from "@/components/gallery/AlbumCard";
import { Icon } from "@/components/ui/Icon";

export const metadata: Metadata = {
  title: "Galería",
  description:
    "Fotos de las noches en Barullo, Vigo: sesiones, conciertos y aniversarios. Un álbum por noche.",
  alternates: { canonical: "/galeria" },
  openGraph: { title: "Galería · Barullo Vigo", url: "/galeria" },
};

export const revalidate = 3600;

export default async function GaleriaPage() {
  const albums = await getGalleryAlbums();
  const [latest, ...rest] = albums;
  const total = albums.reduce((n, a) => n + a.photos.length, 0);
  // Para el muro del héroe: las fotos de todas las noches, intercaladas para
  // que las columnas no salgan agrupadas por fiesta.
  const longest = Math.max(0, ...albums.map((a) => a.photos.length));
  const wallPhotos = Array.from({ length: longest }, (_, i) =>
    albums.map((a) => a.photos[i]).filter((p): p is string => Boolean(p)),
  ).flat();

  return (
    <>
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "Galería", href: "/galeria" },
        ])}
      />

      <PageHero
        scene={wallPhotos.length > 0 && <GalleryScene photos={wallPhotos} />}
        eyebrow={`${total} fotos · ${albums.length} noches`}
        title="Galería"
        lead={<p>Un álbum por noche: busca la tuya. Las subimos el lunes después de cada fiesta.</p>}
      >
        {latest && (
          <HeroLink href={`/galeria/${latest.event.slug}`} primary>
            Última noche
          </HeroLink>
        )}
        <HeroLink href="#albumes">Todos los álbumes</HeroLink>
      </PageHero>

      <Section id="albumes" className="pt-8 md:pt-12">
        {!latest ? (
          <p className="rounded-md bg-coal p-6 text-ash">
            Todavía no hay fotos publicadas. Las subimos el lunes después de cada noche.
          </p>
        ) : (
          <>
            {/* La última noche, en grande: es la que todo el mundo busca. */}
            <Link
              href={`/galeria/${latest.event.slug}`}
              className="group grid gap-2 overflow-hidden rounded-lg sm:grid-cols-[1.6fr_1fr] sm:grid-rows-2"
            >
              {latest.photos.slice(0, 3).map((src, i) => (
                <div
                  key={src}
                  className={
                    i === 0
                      ? "relative aspect-[4/5] overflow-hidden rounded-md bg-slate sm:row-span-2 sm:aspect-auto sm:min-h-[32rem]"
                      : "relative hidden overflow-hidden rounded-md bg-slate sm:block"
                  }
                >
                  <Image
                    src={src}
                    alt={i === 0 ? `Última noche: ${latest.event.title}` : ""}
                    fill
                    priority={i === 0}
                    sizes={i === 0 ? "(min-width: 640px) 60vw, 100vw" : "35vw"}
                    className="object-cover transition-transform duration-700 ease-[var(--ease-soft)] group-hover:scale-[1.03]"
                  />
                  {i === 0 && (
                    <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-void via-void/30 to-transparent p-5 sm:p-8">
                      <span className="mb-3 inline-flex w-fit items-center gap-1.5 rounded-pill bg-acid px-3 py-1 text-xs font-black text-void">
                        <Icon name="Camera" size={13} />
                        Última noche · {latest.photos.length} fotos
                      </span>
                      <p className="text-sm font-bold first-letter:uppercase text-ash">{longDate(latest.event.date)}</p>
                      <h2 className="wide mt-1 text-[clamp(2.5rem,10vw,5rem)] uppercase leading-none text-milk text-balance">
                        {latest.event.title}
                      </h2>
                    </div>
                  )}
                </div>
              ))}
            </Link>

            {rest.length > 0 && (
              <ul className="mt-12 grid grid-cols-2 gap-x-2 gap-y-8 sm:gap-x-4 lg:grid-cols-3">
                {rest.map(({ event, photos }) => (
                  <li key={event.slug}>
                    <AlbumCard event={event} photos={photos} />
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </Section>
    </>
  );
}
