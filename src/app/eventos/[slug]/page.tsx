import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import { SITE } from "@/content/site";
import { getEventBySlug, getAllEventSlugs, getUpcomingEvents } from "@/lib/events";
import { longDate, time } from "@/lib/dates";
import { eventJsonLd, breadcrumbJsonLd, JsonLd } from "@/lib/seo";
import { StatusBadge, RamaTag } from "@/components/events/StatusBadge";
import { TicketButton } from "@/components/events/TicketButton";
import { EventTicket } from "@/components/events/EventTicket";
import { Carousel } from "@/components/ui/Carousel";
import { PhotoGrid } from "@/components/gallery/PhotoGrid";
import { BrandIcon } from "@/components/ui/BrandIcon";
import { cn } from "@/lib/utils";
import { ramaOf } from "@/content/ramas";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Icon, type IconName } from "@/components/ui/Icon";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
export const revalidate = 1800;

export async function generateStaticParams() {
  const slugs = await getAllEventSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: PageProps<"/eventos/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const event = await getEventBySlug(slug);
  if (!event) return {};

  const lineup = event.lineup.map((a) => a.name).join(", ");
  const description =
    event.tagline ??
    `${lineup} en Barullo, ${SITE.city}. ${longDate(event.date)}, ${event.room}.`;

  return {
    title: event.title,
    description,
    alternates: { canonical: `/eventos/${slug}` },
    openGraph: {
      type: "article",
      title: `${event.title} · Barullo Vigo`,
      description,
      url: `/eventos/${slug}`,
    },
    // Un evento pasado sigue siendo útil para el usuario y para el histórico,
    // pero no queremos que compita en el índice con las fechas vivas.
    robots:
      event.endDate.getTime() < Date.now()
        ? { index: false, follow: true }
        : { index: true, follow: true },
  };
}

export default async function EventoPage({ params }: PageProps<"/eventos/[slug]">) {
  const { slug } = await params;
  const event = await getEventBySlug(slug);
  if (!event) notFound();

  // Server Component: esto se evalúa en el servidor una vez por render, con
  // ISR por delante. No es un render de cliente que pueda quedarse obsoleto.
  // eslint-disable-next-line react-hooks/purity
  const isPast = event.endDate.getTime() < Date.now();
  const upcoming = (await getUpcomingEvents(7)).filter((e) => e.slug !== slug).slice(0, 6);

  const rama = ramaOf(event);
  const DATOS: { icon: IconName; label: string; value: string }[] = [
    { icon: "CalendarDays", label: "Fecha", value: longDate(event.date).replace(/ de \d{4}$/, "") },
    { icon: "Clock3", label: "Horario", value: `${time(event.date)} a ${time(event.endDate)}` },
    // En una noche pasada el precio ya no informa de nada (y sin dato saldría «Entrada libre»).
    ...(isPast ? [] : [{ icon: "Ticket" as const, label: "Precio", value: event.priceFrom ? `Desde ${event.priceFrom} €` : "Entrada libre" }]),
    { icon: "ShieldCheck", label: "Acceso", value: `+${event.minAge} con DNI` },
  ];

  return (
    <>
      <JsonLd data={eventJsonLd(event)} />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "Agenda", href: "/agenda" },
          { name: event.title, href: `/eventos/${slug}` },
        ])}
      />

      {/* Plantilla de noche. Arriba, el cartel desenfocado a sangre hace de
          ambiente y tiñe la página con los colores de esa noche; encima, el
          flyer nítido y la ficha. */}
      <div className="relative isolate overflow-hidden">
        <div className="absolute inset-0 -z-10" aria-hidden="true">
          <Image src={event.flyer.src} alt="" fill sizes="100vw" className="scale-125 object-cover opacity-45 blur-3xl" />
          <div className="absolute inset-0 bg-gradient-to-b from-void/40 via-void/80 to-void" />
        </div>

        <Section className="pt-6">
          <Breadcrumbs
            items={[
              { label: "Inicio", href: "/" },
              { label: "Agenda", href: "/agenda" },
              { label: event.title },
            ]}
          />

          <div className="grid gap-8 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)] lg:gap-14">
            <div className="relative aspect-[4/5] overflow-hidden rounded-lg bg-slate ring-1 ring-white/10">
              <Image
                src={event.flyer.src}
                alt={event.flyer.alt}
                fill
                priority
                sizes="(max-width: 1024px) 100vw, 40vw"
                className="object-cover"
              />
            </div>

            <div className="flex flex-col">
              <div className="flex flex-wrap items-center gap-1.5">
                {!isPast && <StatusBadge status={event.status} />}
                <RamaTag rama={rama} />
                {isPast && (
                  <span className="rounded-pill border border-edge px-2.5 py-1 text-[11px] font-extrabold leading-none text-ash">
                    Noche pasada
                  </span>
                )}
              </div>

              <h1 className="wide mt-5 text-[clamp(3rem,13vw,6.5rem)] uppercase leading-none text-milk text-balance">
                {event.title}
              </h1>
              {event.tagline && <p className="mt-4 text-xl font-semibold text-ash">{event.tagline}</p>}

              <dl className="mt-7 grid grid-cols-2 gap-2">
                {DATOS.map((d) => (
                  <div key={d.label} className="flex items-start gap-3 rounded-md bg-coal/80 p-3.5 ring-1 ring-rule backdrop-blur">
                    <Icon name={d.icon} size={18} className="mt-0.5 shrink-0 text-acid" />
                    <div className="min-w-0">
                      <dt className="text-xs font-bold text-dust">{d.label}</dt>
                      <dd className="mt-0.5 font-extrabold first-letter:uppercase leading-snug text-milk">{d.value}</dd>
                    </div>
                  </div>
                ))}
                <div className="col-span-2 flex items-center gap-3 rounded-md bg-coal/80 p-3.5 ring-1 ring-rule backdrop-blur">
                  <Icon name="Disc" size={18} className="shrink-0 text-acid" />
                  <p className="font-extrabold text-milk">
                    {event.room}
                    <span className="ml-2 font-semibold text-dust">{event.genres.join(", ")}</span>
                  </p>
                </div>
              </dl>

              {!isPast && (
                <div id="cta-principal" className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-start">
                  <TicketButton event={event} className="sm:flex-1" />
                  <a
                    href={`/eventos/${event.slug}/ics`}
                    className="inline-flex min-h-14 items-center justify-center gap-2 rounded-pill border border-edge px-6 font-extrabold text-milk transition-colors hover:border-acid hover:text-acid"
                  >
                    <Icon name="CalendarPlus" size={18} />
                    Al calendario
                  </a>
                </div>
              )}
            </div>
          </div>
        </Section>
      </div>

      {/* Line-up: una tarjeta por artista, el cabeza de cartel a lo ancho. */}
      <Section className="pt-4">
        <SectionHeading title="Line-up" />
        <ul className="grid gap-3 sm:grid-cols-2">
          {event.lineup.map((a) => (
            <li
              key={a.name}
              className={cn(
                "flex items-center justify-between gap-4 rounded-md p-5 ring-1",
                a.isHeadliner ? "bg-milk text-void ring-milk sm:col-span-2" : "bg-coal text-milk ring-rule",
              )}
            >
              <div className="min-w-0">
                <p className={cn(a.isHeadliner ? "wide text-[clamp(2.25rem,9vw,4rem)] uppercase leading-none" : "caps text-xl leading-tight")}>
                  {a.name}
                </p>
                {a.role && (
                  <p className={cn("mt-2 text-sm font-bold first-letter:uppercase", a.isHeadliner ? "text-void/60" : "text-dust")}>
                    {a.role}
                  </p>
                )}
              </div>
              {a.soundcloud && (
                <a
                  href={a.soundcloud}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`${a.name} en SoundCloud`}
                  className={cn(
                    "flex size-12 shrink-0 items-center justify-center rounded-full transition-colors",
                    a.isHeadliner ? "bg-void text-milk hover:bg-acid hover:text-void" : "bg-slate text-milk hover:bg-acid hover:text-void",
                  )}
                >
                  <BrandIcon name="SoundCloud" size={20} />
                </a>
              )}
            </li>
          ))}
        </ul>

        <div className="mt-10 max-w-2xl space-y-4 text-lg leading-relaxed text-ash">
          {event.description.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </div>
      </Section>

      {/* Fotos sólo cuando la noche ya pasó. */}
      {isPast && event.gallery && event.gallery.length > 0 && (
        <Section>
          <SectionHeading title="Así se vio" action={{ href: `/galeria/${event.slug}`, label: "Álbum" }} />
          <PhotoGrid photos={event.gallery} title={event.title} />
        </Section>
      )}

      {upcoming.length > 0 && (
        <Section>
          <SectionHeading title="Otras noches" action={{ href: "/agenda", label: "Agenda" }} />
          <Carousel label="Otras noches" slideClassName="basis-[82%] sm:basis-[46%] lg:basis-[31%]">
            {upcoming.map((e) => (
              <EventTicket key={e.slug} event={e} />
            ))}
          </Carousel>
        </Section>
      )}
    </>
  );
}
