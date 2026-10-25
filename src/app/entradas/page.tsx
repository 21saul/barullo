import type { Metadata } from "next";
import Link from "next/link";
import { SITE } from "@/content/site";
import { FAQ_ENTRADAS } from "@/content/faq";
import { getUpcomingEvents } from "@/lib/events";
import { faqJsonLd, breadcrumbJsonLd, JsonLd } from "@/lib/seo";
import { EventTicket } from "@/components/events/EventTicket";
import { Carousel } from "@/components/ui/Carousel";
import { Section, SectionHeading } from "@/components/ui/Section";
import { PageHero, HeroLink } from "@/components/ui/PageHero";
import { ENTRADAS_HERO } from "@/content/heroes";
import { Faq } from "@/components/ui/Faq";
import { Icon } from "@/components/ui/Icon";
export const metadata: Metadata = {
  title: "Entradas",
  description:
    "Cómo comprar entradas para Barullo en Vigo: preventa online, listas de invitados, precios, edad mínima y condiciones de acceso.",
  alternates: { canonical: "/entradas" },
  openGraph: { title: "Entradas y listas · Barullo Vigo", url: "/entradas" },
};

export const revalidate = 3600;

const PASOS = [
  {
    icon: "Ticket",
    title: "Compra online",
    text: "Elige la noche en la agenda y pulsa en el botón de entradas. La venta la gestionan Fourvenues o DICE según el evento; el precio de preventa sube conforme se agotan tramos.",
  },
  {
    icon: "ListChecks",
    title: "O apúntate en lista",
    text: "Los jueves y en algunas sesiones hay lista con entrada libre o reducida antes de una hora concreta. El enlace de lista aparece en la ficha del evento.",
  },
  {
    icon: "IdCard",
    title: "Trae tu documento",
    text: "En puerta hace falta DNI, NIE o pasaporte en vigor. Sin documento no se entra, aunque tengas la entrada comprada.",
  },
  {
    icon: "CreditCard",
    title: "Enseña el QR",
    text: "Basta con el QR en el móvil, no hace falta imprimir nada. Si compraste varias, cada persona entra con el suyo.",
  },
] as const;

export default async function EntradasPage() {
  const upcoming = await getUpcomingEvents(8);

  return (
    <>
      <JsonLd data={faqJsonLd([...FAQ_ENTRADAS])} />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "Entradas", href: "/entradas" },
        ])}
      />

      <PageHero
        backdrop={ENTRADAS_HERO}
        alt="Tres pulseras de tela tejidas con el logo de Barullo flotando entre brasas"
        eyebrow="Preventa · listas · puerta"
        title="Entradas"
        lead={
          <p>
            Dónde se compran, cómo funcionan las listas y qué te van a pedir en la puerta de la sala en{" "}
            {SITE.city}.
          </p>
        }
      >
        {upcoming.length > 0 && (
          <HeroLink href="#a-la-venta" primary>
            Noches a la venta
          </HeroLink>
        )}
        <HeroLink href="#como-entrar">Cómo entrar</HeroLink>
      </PageHero>

      <div className="relative overflow-hidden">
        <Section className="pt-8 md:pt-12" id="como-entrar">
          <ol className="grid gap-3 sm:grid-cols-2">
            {PASOS.map((p, i) => (
              <li key={p.title} className="rounded-lg bg-coal p-6 ring-1 ring-rule">
                <div className="flex items-center justify-between">
                  <span className="flex size-12 items-center justify-center rounded-full bg-slate text-acid">
                    <Icon name={p.icon} size={22} aria-hidden="true" />
                  </span>
                  <span className="data text-5xl font-black leading-none text-edge">{i + 1}</span>
                </div>
                <h2 className="caps mt-6 text-xl leading-tight text-milk">{p.title}</h2>
                <p className="mt-2 leading-relaxed text-ash">{p.text}</p>
              </li>
            ))}
          </ol>
        </Section>
      </div>

      {upcoming.length > 0 && (
        <Section id="a-la-venta">
          <SectionHeading title="A la venta" action={{ href: "/agenda", label: "Agenda" }} />
          <Carousel label="Noches a la venta" slideClassName="basis-[82%] sm:basis-[46%] lg:basis-[31%]">
            {upcoming.map((e, i) => (
              <EventTicket key={e.slug} event={e} priority={i === 0} />
            ))}
          </Carousel>
        </Section>
      )}

      <Section>
        <SectionHeading title="Dudas" />
        <Faq items={FAQ_ENTRADAS} />
        <p className="mt-8 text-sm text-ash">
          ¿No está tu duda?{" "}
          <Link href="/contacto" className="font-semibold text-acid hover:text-milk">
            Escríbenos
          </Link>{" "}
          y te respondemos en 24-48 h.
        </p>
      </Section>
    </>
  );
}
