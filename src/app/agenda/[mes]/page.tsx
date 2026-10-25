import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { parse, isValid } from "date-fns";
import { SITE } from "@/content/site";
import { getEventsByMonth, getUpcomingMonths } from "@/lib/events";
import { monthYear } from "@/lib/dates";
import { itemListJsonLd, breadcrumbJsonLd, JsonLd } from "@/lib/seo";
import { EventList } from "@/components/events/EventRow";
import { Section } from "@/components/ui/Section";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { PageHero, HeroLink } from "@/components/ui/PageHero";
import { AgendaScene } from "@/components/events/AgendaScene";
export const revalidate = 1800;

/**
 * Una URL por mes. Es la página que compite por "qué hacer en Vigo en
 * noviembre", "discotecas Vigo diciembre" y compañía: long-tail barato y con
 * intención de compra alta.
 */
export async function generateStaticParams() {
  const months = await getUpcomingMonths();
  return months.map((m) => ({ mes: m.key }));
}

function parseMonth(mes: string) {
  const d = parse(mes, "yyyy-MM", new Date());
  return isValid(d) ? d : null;
}

export async function generateMetadata({
  params,
}: PageProps<"/agenda/[mes]">): Promise<Metadata> {
  const { mes } = await params;
  const date = parseMonth(mes);
  if (!date) return {};

  const label = monthYear(date);
  const Label = label.charAt(0).toUpperCase() + label.slice(1);

  return {
    title: `Eventos en ${Label}`,
    description: `Agenda de Barullo en ${SITE.city} para ${label}: conciertos, sesiones, line-up completo, horarios y entradas.`,
    alternates: { canonical: `/agenda/${mes}` },
    openGraph: {
      title: `Eventos en ${Label} · Barullo Vigo`,
      description: `Qué hacer en ${SITE.city} en ${label}: la agenda completa de Barullo.`,
      url: `/agenda/${mes}`,
    },
  };
}

export default async function MesPage({ params }: PageProps<"/agenda/[mes]">) {
  const { mes } = await params;
  const date = parseMonth(mes);
  if (!date) notFound();

  const events = await getEventsByMonth(mes);
  if (events.length === 0) notFound();

  const label = monthYear(date);
  const Label = label.charAt(0).toUpperCase() + label.slice(1);

  return (
    <>
      <JsonLd data={itemListJsonLd(events)} />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "Agenda", href: "/agenda" },
          { name: Label, href: `/agenda/${mes}` },
        ])}
      />

      <PageHero
        scene={<AgendaScene events={events} />}
        eyebrow={`Agenda · ${SITE.city}`}
        title={Label}
        titleClassName="text-[clamp(3.5rem,15vw,9.5rem)]"
        lead={
          <p>
            {events.length} {events.length === 1 ? "fecha" : "fechas"} en Barullo, {SITE.city}.
          </p>
        }
      >
        <HeroLink href="#fechas" primary>
          Ver las fechas
        </HeroLink>
        <HeroLink href="/agenda">Toda la agenda</HeroLink>
      </PageHero>

      <div className="relative">
        <Section className="pt-6" id="fechas">
          <Breadcrumbs
            items={[
              { label: "Inicio", href: "/" },
              { label: "Agenda", href: "/agenda" },
              { label: Label },
            ]}
          />
          <EventList events={events} priorityCount={3} />
        </Section>
      </div>
    </>
  );
}
