import type { ClubEvent } from "@/content/events";
import { Section, SectionHeading, SectionAction } from "@/components/ui/Section";
import { EventList } from "@/components/events/EventRow";

/**
 * Vistazo a la agenda: las cuatro primeras noches de los próximos 30 días y
 * un acceso a la agenda completa, que llega hasta donde haya programación.
 */
export function AgendaPreview({ events, total }: { events: ClubEvent[]; total: number }) {
  if (!events.length) return null;
  return (
    <Section>
      <SectionHeading
        title="Este mes"
        description="Las próximas cuatro noches del club. La agenda completa llega hasta donde tenemos programado."
        action={{ href: "/agenda", label: "Agenda" }}
      />
      <EventList events={events} />
      <SectionAction href="/agenda" label={`Ver la agenda completa · ${total} noches`} />
    </Section>
  );
}
