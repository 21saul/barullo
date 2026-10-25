import type { Metadata } from "next";
import Link from "next/link";
import { SITE } from "@/content/site";
import { getUpcomingEvents, getUpcomingMonths, getPastEvents } from "@/lib/events";
import { monthYear } from "@/lib/dates";
import { itemListJsonLd, breadcrumbJsonLd, JsonLd } from "@/lib/seo";
import { EventList } from "@/components/events/EventRow";
import { Section, SectionHeading } from "@/components/ui/Section";
import { PageHero, HeroLink } from "@/components/ui/PageHero";
import { AgendaScene } from "@/components/events/AgendaScene";
import { parse } from "date-fns";

export const metadata: Metadata = {
  title: "Agenda de eventos",
  description:
    "Todos los conciertos y sesiones de Barullo en Vigo: fechas, line-up, horarios, precios y entradas. Agenda actualizada cada semana.",
  alternates: { canonical: "/agenda" },
  openGraph: {
    title: "Agenda de eventos · Barullo Vigo",
    description: "Todos los conciertos y sesiones de Barullo en Vigo.",
    url: "/agenda",
  },
};

export const revalidate = 1800;

export default async function AgendaPage() {
  const upcoming = await getUpcomingEvents();
  const months = await getUpcomingMonths();
  const past = await getPastEvents(6);

  return (
    <>
      <JsonLd data={itemListJsonLd(upcoming)} />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "Agenda", href: "/agenda" },
        ])}
      />

      <PageHero
        scene={<AgendaScene events={upcoming} />}
        eyebrow={`${SITE.city} · jueves a sábado`}
        title="Agenda"
        lead={
          <p>
            {upcoming.length} noches por delante en Barullo: fechas, line-up, horarios y entradas.
          </p>
        }
      >
        <HeroLink href="#noches" primary>
          Ver todas las noches
        </HeroLink>
        <HeroLink href="/entradas">Cómo funcionan las entradas</HeroLink>
      </PageHero>

      <div className="relative">
        <Section className="pb-0 pt-8 md:pt-10" id="noches">
          {/* Filtro por mes. Cada mes es una URL propia: es donde se pesca el
              long-tail de "eventos en Vigo <mes>". */}
          {months.length > 1 && (
            <nav aria-label="Filtrar por mes" className="flex flex-wrap gap-2">
              <span className="inline-flex min-h-10 items-center rounded-pill bg-milk px-4 text-sm font-extrabold text-void">
                Todo
              </span>
              {months.map((m) => (
                <Link
                  key={m.key}
                  href={`/agenda/${m.key}`}
                  className="inline-flex min-h-10 items-center gap-2 rounded-pill border border-edge px-4 text-sm font-extrabold text-milk transition-colors hover:border-acid hover:text-acid"
                >
                  <span className="first-letter:uppercase">
                    {monthYear(parse(m.key, "yyyy-MM", new Date()))}
                  </span>
                  <span className="text-dust">{m.count}</span>
                </Link>
              ))}
            </nav>
          )}
        </Section>
      </div>

      <Section className="pt-6">
        {upcoming.length === 0 ? (
          <p className="text-ash">
            No hay fechas publicadas ahora mismo. Síguenos en{" "}
            <a href={SITE.socials.instagram} className="text-acid underline">
              Instagram
            </a>{" "}
            para enterarte de los próximos anuncios.
          </p>
        ) : (
          <EventList events={upcoming} byMonth priorityCount={3} />
        )}
      </Section>

      {past.length > 0 && (
        <Section>
          <SectionHeading
            title="Ya sonó"
            description="Las últimas noches del club. Las fotos de cada una están en la galería."
            action={{ href: "/galeria", label: "Galería" }}
          />
          <div className="opacity-70 transition-opacity hover:opacity-100">
            <EventList events={past} />
          </div>
        </Section>
      )}
    </>
  );
}
