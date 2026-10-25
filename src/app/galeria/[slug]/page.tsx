import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getGalleryAlbums } from "@/lib/events";
import { longDate } from "@/lib/dates";
import { breadcrumbJsonLd, JsonLd } from "@/lib/seo";
import { Section } from "@/components/ui/Section";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { PhotoGrid } from "@/components/gallery/PhotoGrid";
import { Icon } from "@/components/ui/Icon";

export const revalidate = 3600;

export async function generateStaticParams() {
  return (await getGalleryAlbums()).map(({ event }) => ({ slug: event.slug }));
}

export async function generateMetadata({ params }: PageProps<"/galeria/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const album = (await getGalleryAlbums()).find((a) => a.event.slug === slug);
  if (!album) return {};
  return {
    title: `Fotos: ${album.event.title}`,
    description: `${album.photos.length} fotos de ${album.event.title} en Barullo, ${longDate(album.event.date)}.`,
    alternates: { canonical: `/galeria/${slug}` },
    openGraph: { images: [album.photos[0]] },
  };
}

export default async function AlbumPage({ params }: PageProps<"/galeria/[slug]">) {
  const { slug } = await params;
  const albums = await getGalleryAlbums();
  const i = albums.findIndex((a) => a.event.slug === slug);
  if (i < 0) notFound();
  const { event, photos } = albums[i];
  // La lista va de la más reciente a la más antigua.
  const newer = albums[i - 1];
  const older = albums[i + 1];

  return (
    <>
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "Galería", href: "/galeria" },
          { name: event.title, href: `/galeria/${slug}` },
        ])}
      />
      <Section className="pt-6">
        <Breadcrumbs
          items={[
            { label: "Inicio", href: "/" },
            { label: "Galería", href: "/galeria" },
            { label: event.title },
          ]}
        />

        <header className="mb-8 flex flex-col gap-4 border-b border-rule pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-bold first-letter:uppercase text-acid">{longDate(event.date)}</p>
            <h1 className="wide mt-1 text-[clamp(2.75rem,11vw,5.5rem)] uppercase leading-none text-milk text-balance">
              {event.title}
            </h1>
            <p className="mt-3 font-semibold text-ash">
              {photos.length} fotos · {event.room}. Toca una para verla a pantalla completa.
            </p>
          </div>
          <Link
            href={`/eventos/${event.slug}`}
            className="inline-flex min-h-12 shrink-0 items-center gap-2 self-start rounded-pill border border-edge px-5 font-extrabold text-milk transition-colors hover:border-acid hover:text-acid sm:self-auto"
          >
            Ficha de la noche
            <Icon name="ArrowUpRight" size={16} />
          </Link>
        </header>

        <PhotoGrid photos={photos} title={event.title} />

        <nav aria-label="Otros álbumes" className="mt-12 grid grid-cols-2 gap-3">
          {newer ? (
            <Link href={`/galeria/${newer.event.slug}`} className="group rounded-md bg-coal p-4 ring-1 ring-rule transition-colors hover:ring-edge">
              <span className="flex items-center gap-1 text-sm font-bold text-dust">
                <Icon name="ArrowLeft" size={14} /> Más reciente
              </span>
              <span className="caps mt-1 block text-base leading-tight text-milk group-hover:text-acid">{newer.event.title}</span>
            </Link>
          ) : (
            <span />
          )}
          {older && (
            <Link href={`/galeria/${older.event.slug}`} className="group rounded-md bg-coal p-4 text-right ring-1 ring-rule transition-colors hover:ring-edge">
              <span className="flex items-center justify-end gap-1 text-sm font-bold text-dust">
                Anterior <Icon name="ArrowRight" size={14} />
              </span>
              <span className="caps mt-1 block text-base leading-tight text-milk group-hover:text-acid">{older.event.title}</span>
            </Link>
          )}
        </nav>
      </Section>
    </>
  );
}
