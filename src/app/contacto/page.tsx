import type { Metadata } from "next";
import Link from "next/link";
import { SITE } from "@/content/site";
import { breadcrumbJsonLd, organizationJsonLd, JsonLd } from "@/lib/seo";
import { ContactForm } from "@/components/forms/ContactForm";
import { Section } from "@/components/ui/Section";
import { PageHero, HeroLink } from "@/components/ui/PageHero";
import { CONTACTO_HERO } from "@/content/heroes";
import { Icon, type IconName } from "@/components/ui/Icon";
import { BrandIcon } from "@/components/ui/BrandIcon";
import { SelloMedalla } from "@/components/brand/SelloMedalla";

export const metadata: Metadata = {
  title: "Contacto",
  description: `Contacto de Barullo, club de música en ${SITE.city}: booking, propuestas de noches, prensa y dudas generales.`,
  alternates: { canonical: "/contacto" },
  openGraph: { title: "Contacto · Barullo Vigo", url: "/contacto" },
};

/** A quién escribir según lo que necesites. */
const VIAS: { icon: IconName; title: string; text: string; href: string; cta: string; external?: boolean }[] = [
  {
    icon: "Headphones",
    title: "Booking",
    text: "Artistas y agencias. Manda enlaces a tu música, no archivos.",
    href: `mailto:${SITE.bookingEmail}`,
    cta: SITE.bookingEmail,
  },
  {
    icon: "Megaphone",
    title: "Propón una noche",
    text: "Colectivos y sellos con una fiesta que encaje en el club.",
    href: "/eventos-privados",
    cta: "Ver cómo funciona",
  },
  {
    icon: "Mail",
    title: "General y prensa",
    text: "Dudas, acreditaciones, objetos perdidos y todo lo demás.",
    href: `mailto:${SITE.email}`,
    cta: SITE.email,
  },
];

export default function ContactoPage() {
  return (
    <>
      <JsonLd data={organizationJsonLd()} />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "Contacto", href: "/contacto" },
        ])}
      />

      <PageHero
        backdrop={CONTACTO_HERO}
        alt="El neón rojo de Barullo encendido sobre la pared de bloques de vidrio del club"
        eyebrow="Booking · propuestas · prensa"
        title="Contacto"
        lead={<p>Escríbenos a quien toque y te contestamos en un par de días.</p>}
      >
        <HeroLink href={SITE.socials.instagram} primary>
          Mensaje por Instagram
        </HeroLink>
        <HeroLink href="#formulario">Formulario</HeroLink>
      </PageHero>

      <Section className="pt-8 md:pt-12">
        <ul className="grid gap-3 md:grid-cols-3">
          {VIAS.map((v) => {
            const inner = (
              <>
                <span className="flex size-14 items-center justify-center rounded-full bg-slate text-acid transition-colors group-hover:bg-void">
                  <Icon name={v.icon} size={24} />
                </span>
                <span className="mt-8 block">
                  <span className="caps block text-2xl leading-tight text-milk group-hover:text-void">{v.title}</span>
                  <span className="mt-2 block leading-snug text-ash group-hover:text-void/75">{v.text}</span>
                  <span className="mt-5 inline-flex items-center gap-1.5 break-all font-extrabold text-milk group-hover:text-void">
                    {v.cta}
                    <Icon name="ArrowUpRight" size={16} className="shrink-0" />
                  </span>
                </span>
              </>
            );
            const cls =
              "group flex h-full flex-col rounded-lg bg-coal p-6 ring-1 ring-rule transition-colors duration-200 hover:bg-acid hover:ring-acid";
            return (
              <li key={v.title}>
                {v.href.startsWith("/") ? (
                  <Link href={v.href} className={cls}>{inner}</Link>
                ) : (
                  <a href={v.href} className={cls}>{inner}</a>
                )}
              </li>
            );
          })}
        </ul>

        <a
          href={SITE.socials.instagram}
          target="_blank"
          rel="noopener noreferrer"
          className="group mt-3 flex items-center gap-4 rounded-lg bg-milk p-5 text-void transition-colors hover:bg-acid sm:p-6"
        >
          <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-void text-milk">
            <BrandIcon name="Instagram" size={22} />
          </span>
          <span className="flex-1">
            <span className="block font-black">Lo más rápido: un mensaje directo</span>
            <span className="block text-sm font-semibold text-void/70">@barulloclub en Instagram</span>
          </span>
          <Icon name="ArrowUpRight" size={22} />
        </a>
      </Section>

      <Section id="formulario">
        <div className="grid gap-10 rounded-lg bg-coal p-6 ring-1 ring-rule sm:p-10 lg:grid-cols-[1fr_1.3fr] lg:gap-16">
          <div>
            <h2 className="wide text-[clamp(2.5rem,9vw,4rem)] uppercase leading-none text-milk">
              O déjanos un mensaje
            </h2>
            <p className="mt-4 leading-relaxed text-ash">
              Elige el asunto y llegará a la persona que lo lleva. Respondemos en 24 a 48 horas
              laborables.
            </p>
            <SelloMedalla id="contacto" className="mt-8 size-32 -rotate-6 sm:size-40" />
            {/* NAP: debe coincidir con la ficha de Google Business. */}
            <address className="mt-8 space-y-3 text-sm font-semibold not-italic text-ash">
              <p className="flex items-start gap-3">
                <Icon name="Clock3" size={17} className="mt-0.5 shrink-0 text-acid" />
                {SITE.openingHoursText}
              </p>
              <p className="flex items-start gap-3">
                <Icon name="MapPin" size={17} className="mt-0.5 shrink-0 text-acid" />
                {SITE.address.street}, {SITE.address.postalCode} {SITE.address.city}
              </p>
              <p className="flex items-start gap-3">
                <Icon name="Phone" size={17} className="mt-0.5 shrink-0 text-acid" />
                <a href={`tel:${SITE.phone.replace(/\s/g, "")}`} className="hover:text-milk">
                  {SITE.phone}
                </a>
              </p>
            </address>
          </div>
          <ContactForm />
        </div>
      </Section>
    </>
  );
}
