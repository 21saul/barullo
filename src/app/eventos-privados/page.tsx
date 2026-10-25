import type { Metadata } from "next";
import { SITE } from "@/content/site";
import { FAQ_PRIVADOS } from "@/content/faq";
import { faqJsonLd, breadcrumbJsonLd, JsonLd } from "@/lib/seo";
import { SelloMedalla } from "@/components/brand/SelloMedalla";
import { BookingForm } from "@/components/forms/BookingForm";
import { Section, SectionHeading } from "@/components/ui/Section";
import { PageHero, HeroLink } from "@/components/ui/PageHero";
import { PROPON_HERO } from "@/content/heroes";
import { Faq } from "@/components/ui/Faq";
import { Icon, type IconName } from "@/components/ui/Icon";
export const metadata: Metadata = {
  title: "Propón una noche",
  description:
    "Colectivos, sellos y artistas: propón tu noche en Barullo, Vigo. También cedemos el club para presentaciones, rodajes y celebraciones fuera del horario de apertura.",
  alternates: { canonical: "/eventos-privados" },
  openGraph: { title: "Propón una noche · Barullo Vigo", url: "/eventos-privados" },
};

/** Cómo se programa una noche de fuera, paso a paso. Es una secuencia real. */
const PASOS = [
  { t: "Nos escribes", d: "Quién sois, qué música, qué fecha os iría bien y enlaces a lo que hacéis." },
  { t: "Lo escuchamos", d: "Lo revisa el equipo de programación y te contestamos en una semana." },
  { t: "Cerramos fecha", d: "Acordamos sala, horario, puerta y reparto. Sin letra pequeña." },
  { t: "Lo anunciamos juntos", d: "Cartel, redes y venta de entradas desde la web del club." },
];

const FORMATOS: { icon: IconName; nombre: string; texto: string }[] = [
  { icon: "Users", nombre: "Colectivos", texto: "Vuestra fiesta, con vuestra gente, en el Sótano o en la Sala Principal." },
  { icon: "Disc", nombre: "Sellos", texto: "Showcases, presentaciones de disco y aniversarios de catálogo." },
  { icon: "Headphones", nombre: "Artistas", texto: "Directos y sesiones de formato largo con equipo técnico de la casa." },
  { icon: "Camera", nombre: "Fuera de horario", texto: "Presentaciones, rodajes y celebraciones de lunes a jueves." },
];

export default function EventosPrivadosPage() {
  return (
    <>
      <JsonLd data={faqJsonLd([...FAQ_PRIVADOS])} />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "Propón una noche", href: "/eventos-privados" },
        ])}
      />

      <PageHero
        backdrop={PROPON_HERO}
        alt="Una alfombra persa larga desenrollándose sin fin por el suelo del club"
        eyebrow="Colectivos · sellos · artistas"
        title="Propón una noche"
        titleClassName="text-[clamp(3.5rem,15vw,9.5rem)]"
        lead={<p>Si tienes una fiesta, un sello o un proyecto con algo que contar, te extendemos la alfombra.</p>}
      >
        <HeroLink href="#propuesta" primary>
          Contar mi idea
        </HeroLink>
        <HeroLink href="#como-funciona">Cómo funciona</HeroLink>
      </PageHero>

      <Section className="pt-8 md:pt-12">
        <ul className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {FORMATOS.map((f) => (
            <li key={f.nombre} className="rounded-lg bg-coal p-5 ring-1 ring-rule">
              <span className="flex size-12 items-center justify-center rounded-full bg-slate text-acid">
                <Icon name={f.icon} size={22} />
              </span>
              <h2 className="caps mt-6 text-xl leading-tight text-milk">{f.nombre}</h2>
              <p className="mt-2 text-sm font-semibold leading-snug text-ash">{f.texto}</p>
            </li>
          ))}
        </ul>
      </Section>

      <Section id="como-funciona">
        <SectionHeading title="Cómo funciona" />
        <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {PASOS.map((p, i) => (
            <li key={p.t} className="relative rounded-lg bg-coal p-5 ring-1 ring-rule">
              <span className="data text-5xl font-black leading-none text-acid">{i + 1}</span>
              <h3 className="mt-4 text-lg font-black text-milk">{p.t}</h3>
              <p className="mt-1 text-sm font-semibold leading-snug text-ash">{p.d}</p>
            </li>
          ))}
        </ol>
      </Section>

      <Section id="propuesta">
        <div className="grid gap-10 rounded-lg bg-coal p-6 ring-1 ring-rule sm:p-10 lg:grid-cols-[1fr_1.3fr] lg:gap-16">
          <div>
            <h2 className="wide text-[clamp(2.5rem,9vw,4rem)] uppercase leading-none text-milk">
              Cuéntanos tu idea
            </h2>
            <p className="mt-4 leading-relaxed text-ash">
              Con una fecha aproximada y un par de enlaces nos basta para empezar. También por correo:{" "}
              <a href={`mailto:${SITE.bookingEmail}`} className="font-bold text-acid hover:text-milk">
                {SITE.bookingEmail}
              </a>
            </p>
            <SelloMedalla
              id="propon"
              text="PROPÓN TU NOCHE · BARULLO · "
              className="mt-8 size-32 rotate-6 sm:size-40"
            />
          </div>
          <BookingForm
            tipos={["Noche de colectivo", "Showcase de sello", "Directo o sesión", "Presentación o rodaje", "Otro"]}
            submitLabel="Enviar propuesta"
          />
        </div>
      </Section>

      <Section>
        <SectionHeading title="Dudas" />
        <Faq items={FAQ_PRIVADOS} />
      </Section>
    </>
  );
}
