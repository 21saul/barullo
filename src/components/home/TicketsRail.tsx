import type { ClubEvent } from "@/content/events";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Carousel } from "@/components/ui/Carousel";
import { EventTicket } from "@/components/events/EventTicket";

/**
 * Lo primero bajo la animación, como en Antídoto: «Tickets» y «Ver todos», y
 * las próximas noches en carrusel. Cada tarjeta lleva a su ficha (la
 * plantilla de evento) y el botón de entradas sale directo al proveedor.
 */
export function TicketsRail({ events }: { events: ClubEvent[] }) {
  if (!events.length) return null;
  return (
    <Section className="pt-8 md:pt-14">
      <SectionHeading title="Tickets" action={{ href: "/agenda", label: "Ver todos" }} />
      <Carousel
        label="Próximas noches"
        slideClassName="basis-[82%] sm:basis-[46%] lg:basis-[31%] xl:basis-[25%]"
      >
        {events.map((e, i) => (
          <EventTicket key={e.slug} event={e} priority={i < 2} />
        ))}
      </Carousel>
    </Section>
  );
}
