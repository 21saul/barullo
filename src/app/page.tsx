import type { Metadata } from "next";
import { addDays } from "date-fns";
import { SITE } from "@/content/site";
import { getUpcomingEvents, getGalleryAlbums } from "@/lib/events";
import { itemListJsonLd, JsonLd } from "@/lib/seo";
import { Hero } from "@/components/home/Hero";
import { MonthStrip } from "@/components/home/MonthStrip";
import { buildMonthStrip } from "@/components/home/month-strip-data";
import { GalleryWall, type WallPhoto } from "@/components/home/GalleryWall";
import { shortDate } from "@/lib/dates";
import { ProposeCta } from "@/components/home/ProposeCta";

export const metadata: Metadata = {
  title: `${SITE.name} · Club de música en Vigo`,
  description:
    "Agenda, entradas y fotos de Barullo Club, fiesta de música urbana y cultura club en Vigo y Galicia.",
  alternates: { canonical: "/" },
};

/** La agenda cambia poco: se revalida cada hora. */
export const revalidate = 3600;

export default async function HomePage() {
  const upcoming = await getUpcomingEvents();
  const albums = await getGalleryAlbums();
  // «Este mes»: lo que cae en los próximos 30 días. Si no hay nada tan
  // cerca, las seis siguientes, para que la home nunca se quede sin entradas.
  const now = new Date();
  const horizon = addDays(now, 30).getTime();
  const soon = upcoming.filter((e) => e.date.getTime() <= horizon);
  const strip = buildMonthStrip(soon.length ? soon : upcoming.slice(0, 6), now);

  // Muro de noches pasadas: las fotos se reparten por turnos (la 1.ª de cada
  // noche, luego la 2.ª...) para que las noches salgan mezcladas. 70 como mucho.
  const wall: WallPhoto[] = [];
  const longest = Math.max(0, ...albums.map((a) => a.photos.length));
  for (let i = 0; i < longest && wall.length < 70; i++) {
    for (const { event, photos } of albums) {
      if (photos[i] && wall.length < 70)
        wall.push({ src: photos[i], href: `/galeria/${event.slug}`, label: `${event.title}, ${shortDate(event.date)}` });
    }
  }
  const totalPhotos = albums.reduce((n, a) => n + a.photos.length, 0);

  return (
    <>
      <JsonLd data={itemListJsonLd(upcoming)} />

      {/* 1. Animación de marca a sangre. */}
      <Hero />

      {/* 2. Tira del mes: entradas que se deslizan y la regla de los 30 días. */}
      {strip.nights.length > 0 && <MonthStrip {...strip} total={upcoming.length} />}

      {/* 3. Noches pasadas: muro inclinado de fotos → álbumes de la galería. */}
      {wall.length > 0 && <GalleryWall photos={wall} total={totalPhotos} />}

      {/* 4. Propón tu noche. */}
      <ProposeCta />
    </>
  );
}
