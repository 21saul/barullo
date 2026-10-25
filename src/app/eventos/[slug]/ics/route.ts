import { SITE } from "@/content/site";
import { getEventBySlug } from "@/lib/events";

/**
 * «Añadir al calendario» (.ics). Ningún club de la investigación lo ofrece y
 * es lo que convierte un «igual voy» en una alarma en el móvil. iOS lo abre
 * directamente en Calendario; Android, con la app de calendario que tenga.
 */
const stamp = (d: Date) => d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
/** RFC 5545: comas, puntos y comas y barras invertidas van escapados. */
const esc = (s: string) => s.replace(/[\\,;]/g, (c) => `\\${c}`).replace(/\n/g, "\\n");

export async function GET(_req: Request, ctx: RouteContext<"/eventos/[slug]/ics">) {
  const { slug } = await ctx.params;
  const event = await getEventBySlug(slug);
  if (!event) return new Response("Not found", { status: 404 });

  const url = `${SITE.url}/eventos/${slug}`;
  const lineup = event.lineup.map((a) => a.name).join(", ");
  const body = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Barullo//Agenda//ES",
    "BEGIN:VEVENT",
    `UID:${slug}@${new URL(SITE.url).host}`,
    `DTSTAMP:${stamp(new Date())}`,
    `DTSTART:${stamp(event.date)}`,
    `DTEND:${stamp(event.endDate)}`,
    `SUMMARY:${esc(`${event.title} · ${SITE.name}`)}`,
    `DESCRIPTION:${esc(`${lineup}\n${url}`)}`,
    `LOCATION:${esc(`${SITE.name}, ${SITE.address.street}, ${SITE.address.postalCode} ${SITE.address.city}`)}`,
    `URL:${url}`,
    "END:VEVENT",
    "END:VCALENDAR",
  ].join("\r\n");

  return new Response(body, {
    headers: {
      "Content-Type": "text/calendar; charset=utf-8",
      "Content-Disposition": `attachment; filename="barullo-${slug}.ics"`,
    },
  });
}
