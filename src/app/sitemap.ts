import type { MetadataRoute } from "next";
import { SITE } from "@/content/site";
import { getUpcomingEvents, getPastEvents, getUpcomingMonths, getGalleryAlbums } from "@/lib/events";

export const revalidate = 3600;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const abs = (p: string) => new URL(p, SITE.url).toString();
  const now = new Date();

  const estaticas: MetadataRoute.Sitemap = [
    { url: abs("/"), lastModified: now, changeFrequency: "daily", priority: 1 },
    { url: abs("/agenda"), lastModified: now, changeFrequency: "daily", priority: 0.9 },
    { url: abs("/entradas"), lastModified: now, changeFrequency: "monthly", priority: 0.8 },
    { url: abs("/eventos-privados"), lastModified: now, changeFrequency: "monthly", priority: 0.8 },
    { url: abs("/club"), lastModified: now, changeFrequency: "monthly", priority: 0.7 },
    { url: abs("/galeria"), lastModified: now, changeFrequency: "weekly", priority: 0.6 },
    { url: abs("/contacto"), lastModified: now, changeFrequency: "yearly", priority: 0.6 },
    { url: abs("/legal/aviso-legal"), changeFrequency: "yearly", priority: 0.2 },
    { url: abs("/legal/privacidad"), changeFrequency: "yearly", priority: 0.2 },
    { url: abs("/legal/cookies"), changeFrequency: "yearly", priority: 0.2 },
    { url: abs("/legal/admision"), changeFrequency: "yearly", priority: 0.3 },
  ];

  const meses = (await getUpcomingMonths()).map((m) => ({
    url: abs(`/agenda/${m.key}`),
    lastModified: now,
    changeFrequency: "weekly" as const,
    priority: 0.7,
  }));

  const proximos = (await getUpcomingEvents()).map((e) => ({
    url: abs(`/eventos/${e.slug}`),
    lastModified: now,
    changeFrequency: "weekly" as const,
    priority: 0.9,
  }));

  // Los pasados se listan con prioridad baja: siguen aportando enlaces internos
  // e histórico, pero no deben competir con las fechas vivas.
  const pasados = (await getPastEvents()).map((e) => ({
    url: abs(`/eventos/${e.slug}`),
    lastModified: e.endDate,
    changeFrequency: "yearly" as const,
    priority: 0.2,
  }));

  const albumes = (await getGalleryAlbums()).map(({ event }) => ({
    url: abs(`/galeria/${event.slug}`),
    lastModified: event.endDate,
    changeFrequency: "yearly" as const,
    priority: 0.4,
  }));

  return [...estaticas, ...meses, ...proximos, ...pasados, ...albumes];
}
