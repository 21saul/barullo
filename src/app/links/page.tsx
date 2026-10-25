import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { SITE } from "@/content/site";
import { getNextEvent } from "@/lib/events";
import { relativeLabel, time } from "@/lib/dates";
import { BrandHero } from "@/components/home/BrandHero";
import { WORDMARK_LOOP } from "@/content/brand";
/**
 * Sustituto propio de Linktree: la página a la que apunta la bio de Instagram.
 * Vive en nuestro dominio, así que el tráfico y los datos son nuestros.
 * No se indexa (ver robots.ts): duplicaría contenido de la home.
 */
export const metadata: Metadata = {
  title: "Enlaces",
  description: `Todos los enlaces de ${SITE.name}: entradas, agenda, galería y redes.`,
  robots: { index: false, follow: true },
};

export const revalidate = 900;

const ENLACES = [
  { href: "/agenda", label: "Agenda completa", desc: "Todas las fechas" },
  { href: "/galeria", label: "Galería", desc: "Las fotos de cada noche" },
  { href: "/club", label: "El club", desc: "Quiénes somos y residentes" },
  { href: "/eventos-privados", label: "Propón una noche", desc: "Colectivos, sellos y artistas" },
];

const REDES = [
  { href: SITE.socials.instagram, label: "Instagram" },
  { href: SITE.socials.tiktok, label: "TikTok" },
  { href: SITE.socials.soundcloud, label: "SoundCloud" },
  { href: SITE.socials.spotify, label: "Spotify" },
  { href: SITE.socials.ra, label: "Resident Advisor" },
];

export default async function LinksPage() {
  const next = await getNextEvent();

  return (
    <div className="relative min-h-screen-safe overflow-hidden px-5 pb-16 pt-8">
      <div className="relative mx-auto w-full max-w-md">
        <div>
          {/* El wordmark animado vive aquí: es la portada de quien llega
              desde la bio de Instagram. Entra diferido, como en la home. */}
          <BrandHero loop={WORDMARK_LOOP} alt={`${SITE.name} · ${SITE.tagline}`} />
          <p className="mt-4 text-center text-sm text-ash">{SITE.tagline}</p>
        </div>

        {/* El próximo evento primero: es a lo que viene el 90% del tráfico. */}
        {next && (
          <Link
            href={`/eventos/${next.slug}`}
            className="panel group mt-9 flex items-center gap-4 overflow-hidden p-3"
          >
            <div className="relative size-20 shrink-0 overflow-hidden ">
              <Image
                src={next.flyer.src}
                alt={next.flyer.alt}
                fill
                priority
                sizes="80px"
                className="object-cover"
              />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-extrabold text-acid">
                {relativeLabel(next.date)} · {time(next.date)}
              </p>
              <p className="caps mt-1 line-clamp-2 text-base leading-tight text-milk">
                {next.title}
              </p>
            </div>
            <span className="shrink-0 pr-2 text-acid" aria-hidden="true">
              →
            </span>
          </Link>
        )}

        {next?.ticketUrl && next.status !== "agotado" && (
          <a
            href={next.ticketUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-3 flex min-h-14 w-full items-center justify-center bg-acid text-lg font-semibold text-void transition-colors hover:bg-milk"
          >
            Entradas
            {next.priceFrom ? ` desde ${next.priceFrom} €` : ""}
          </a>
        )}

        <ul className="mt-3 space-y-3">
          {ENLACES.map((e) => (
            <li key={e.href}>
              <Link
                href={e.href}
                className="panel flex min-h-14 items-center justify-between gap-4 px-5 py-3 transition-colors hover:border-acid/50"
              >
                <span>
                  <span className="block font-semibold text-milk">{e.label}</span>
                  <span className="block text-xs text-ash">{e.desc}</span>
                </span>
                <span className="text-acid" aria-hidden="true">
                  →
                </span>
              </Link>
            </li>
          ))}
        </ul>

        <ul className="mt-8 flex flex-wrap justify-center gap-x-5 gap-y-2">
          {REDES.map((r) => (
            <li key={r.label}>
              <a
                href={r.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-ash transition-colors hover:text-acid"
              >
                {r.label}
              </a>
            </li>
          ))}
        </ul>

        <p className="mt-10 text-center text-xs text-dust">
          {SITE.address.street} · {SITE.address.city} · +{SITE.minAge}
        </p>
      </div>
    </div>
  );
}
