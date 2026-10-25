import { SITE } from "@/content/site";
import type { ClubEvent } from "@/content/events";

const abs = (path: string) => new URL(path, SITE.url).toString();

/** NightClub hereda de LocalBusiness: es el tipo correcto para SEO local. */
export function organizationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "NightClub",
    "@id": abs("/#club"),
    name: SITE.name,
    legalName: SITE.legalName,
    url: SITE.url,
    description: SITE.shortDescription,
    telephone: SITE.phone,
    email: SITE.email,
    address: {
      "@type": "PostalAddress",
      streetAddress: SITE.address.street,
      postalCode: SITE.address.postalCode,
      addressLocality: SITE.address.city,
      addressRegion: SITE.address.region,
      addressCountry: SITE.address.country,
    },
    geo: { "@type": "GeoCoordinates", latitude: SITE.geo.lat, longitude: SITE.geo.lng },
    openingHoursSpecification: SITE.openingHours.map((h) => ({
      "@type": "OpeningHoursSpecification",
      dayOfWeek: h.days,
      opens: h.opens,
      closes: h.closes,
    })),
    maximumAttendeeCapacity: SITE.capacity,
    sameAs: Object.values(SITE.socials),
    image: abs("/media/fotos/2025-09-05/01.jpg"),
    priceRange: "€€",
  };
}

const STATUS_MAP = {
  cancelado: "https://schema.org/EventCancelled",
  agotado: "https://schema.org/EventScheduled",
  anunciado: "https://schema.org/EventScheduled",
  ultimas: "https://schema.org/EventScheduled",
  gratis: "https://schema.org/EventScheduled",
} as const;

/** MusicEvent: lo que hace que el evento salga en el carrusel de eventos de Google. */
export function eventJsonLd(e: ClubEvent) {
  return {
    "@context": "https://schema.org",
    "@type": "MusicEvent",
    "@id": abs(`/eventos/${e.slug}#event`),
    name: e.title,
    description: e.tagline ?? e.description[0],
    startDate: e.date.toISOString(),
    endDate: e.endDate.toISOString(),
    eventStatus: STATUS_MAP[e.status],
    eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode",
    image: [abs(e.flyer.src)],
    url: abs(`/eventos/${e.slug}`),
    location: {
      "@type": "MusicVenue",
      name: SITE.name,
      address: {
        "@type": "PostalAddress",
        streetAddress: SITE.address.street,
        postalCode: SITE.address.postalCode,
        addressLocality: SITE.address.city,
        addressRegion: SITE.address.region,
        addressCountry: SITE.address.country,
      },
    },
    performer: e.lineup.map((a) => ({ "@type": "MusicGroup", name: a.name })),
    organizer: { "@type": "Organization", name: SITE.name, url: SITE.url },
    ...(e.ticketUrl && {
      offers: {
        "@type": "Offer",
        url: e.ticketUrl,
        price: e.priceFrom ?? 0,
        priceCurrency: "EUR",
        availability:
          e.status === "agotado" ? "https://schema.org/SoldOut" : "https://schema.org/InStock",
        validFrom: new Date().toISOString(),
      },
    }),
    typicalAgeRange: `${e.minAge}-`,
  };
}

export function breadcrumbJsonLd(trail: { name: string; href: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: trail.map((t, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: t.name,
      item: abs(t.href),
    })),
  };
}

export function faqJsonLd(items: { q: string; a: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((i) => ({
      "@type": "Question",
      name: i.q,
      acceptedAnswer: { "@type": "Answer", text: i.a },
    })),
  };
}

/** Lista de eventos en una página de agenda: ayuda a Google a entender el conjunto. */
export function itemListJsonLd(events: ClubEvent[]) {
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: events.map((e, i) => ({
      "@type": "ListItem",
      position: i + 1,
      url: abs(`/eventos/${e.slug}`),
      name: e.title,
    })),
  };
}

/** Inyecta JSON-LD. Next no escapa `dangerouslySetInnerHTML`, de ahí el replace. */
export function JsonLd({ data }: { data: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  );
}

export { abs };
