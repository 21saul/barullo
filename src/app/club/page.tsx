import type { Metadata } from "next";
import Image from "next/image";
import { CLUB_HERO } from "@/content/heroes";
import { breadcrumbJsonLd, organizationJsonLd, JsonLd } from "@/lib/seo";
import { Section, SectionHeading } from "@/components/ui/Section";
import { PageHero, HeroLink } from "@/components/ui/PageHero";
import { ProposeCta } from "@/components/home/ProposeCta";

export const metadata: Metadata = {
  title: "El club",
  description:
    "Barullo Club é unha festa nacida da música urbana española, feita de maneira independente e artesanal en Galicia: novos sons, talento emerxente e unha pista segura e inclusiva.",
  alternates: { canonical: "/club" },
  openGraph: { title: "El club · Barullo", url: "/club" },
};

/**
 * Manifesto de Barullo, en galego tal e como o escribiu o colectivo.
 * Non traducir nin reescribir sen eles.
 */
const MANIFESTO = [
  "Barullo Club é unha festa nacida da música urbana española, un movemento que experimentou un enorme crecemento nos últimos anos e que marcou a toda unha xeración. Con todo, a súa masificación e ultracomercialización fixeron que moitas propostas acabasen perdendo parte da súa identidade, repetindo fórmulas e afastándose da espontaneidade e a frescura que a caracterizaban nos seus inicios.",
  "Nese contexto nace Barullo. Un proxecto construído de maneira totalmente independente e artesanal, impulsado pola necesidade de descubrir novos sons e de recuperar a emoción de escoitar música que sorprenda. Cansos da monotonía e das tendencias repetidas ata a saciedade, buscamos explorar territorios diferentes, revisitar sons do pasado e dar espazo a propostas que, independentemente da súa etiqueta, compartan unha mesma esencia: música feita para conectar coa pista.",
  "Aínda que as nosas raíces están na música urbana, Barullo vai máis alá dese concepto. O noso interese está en todas aquelas sonoridades que achegan personalidade, enerxía e autenticidade á experiencia do club, desde influencias urbanas ata propostas máis electrónicas e experimentais.",
  "O noso obxectivo é levar esta visión por toda Galicia, creando festas que conecten cidades, escenas e persoas arredor dunha mesma paixón pola música. Apostamos polo talento emerxente, polas propostas arriscadas e pola creación dunha comunidade que valore a cultura, a creatividade e a liberdade de expresión por enriba das modas do momento.",
  "Entendemos a noite como un espazo de encontro, expresión e descubrimento. Por iso traballamos para que cada evento sexa un lugar seguro, inclusivo e respectuoso para todas as persoas, onde a música sexa a protagonista e onde cada quen poida sentirse libre de participar, bailar e expresarse sen prexuízos.",
];

/** Tira de cabina: fotos reales de las noches (ver src/content/events.ts). */
const CABINA = [
  { src: "/media/fotos/2025-10-10/07.jpg", alt: "DJ con camiseta roja de Barullo pinchando con amigos detrás" },
  { src: "/media/fotos/2025-09-05/03.jpg", alt: "DJ pinchando con aro de luz y público pegado a la cabina" },
  { src: "/media/fotos/2025-07-18/01.jpg", alt: "Cabina con alfombra persa bajo el neón rojo de Barullo" },
];

export default function ClubPage() {
  return (
    <>
      <JsonLd data={organizationJsonLd()} />
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: "El club", href: "/club" },
        ])}
      />

      <PageHero
        backdrop={CLUB_HERO}
        alt="El logo de Barullo tejido en una alfombra persa que vuela entre brasas"
        eyebrow="Barullo Club · Galicia"
        title="El club"
        lead={
          <p lang="gl">
            Barullo non nace para seguir tendencias. Nace para crear experiencias e descubrir novos
            camiños dentro da cultura club en Galicia.
          </p>
        }
      >
        <HeroLink href="#manifesto" primary>
          Ler o manifesto
        </HeroLink>
        <HeroLink href="/agenda">Próximas noches</HeroLink>
      </PageHero>

      <Section id="manifesto">
        <div className="grid gap-10 lg:grid-cols-[1fr_1.1fr] lg:gap-16">
          <div lang="gl" className="space-y-5 text-lg leading-relaxed text-ash">
            <h2 className="wide text-[2.5rem] uppercase leading-none text-milk">Manifesto</h2>
            {MANIFESTO.map((p, i) => (
              <p key={i} className={i === 0 ? "text-milk" : undefined}>
                {p}
              </p>
            ))}
          </div>
          <div className="grid grid-cols-2 content-start gap-2 sm:gap-3 lg:sticky lg:top-24 lg:self-start">
            <div className="relative row-span-2 aspect-[3/4] overflow-hidden rounded-md bg-slate">
              <Image src="/media/fotos/2025-07-18/09.jpg" alt="Dos amigas posando en la pista bajo luces rojas" fill sizes="(min-width: 1024px) 26vw, 48vw" className="object-cover" />
            </div>
            <div className="relative aspect-square overflow-hidden rounded-md bg-slate">
              <Image src="/media/fotos/2025-11-07/02.jpg" alt="DJ con sudadera negra frente a la pared de pavés y el neón de Barullo" fill sizes="(min-width: 1024px) 20vw, 48vw" className="object-cover" />
            </div>
            <div className="relative aspect-square overflow-hidden rounded-md bg-slate">
              <Image src="/media/fotos/2025-07-25/04.jpg" alt="Grupo de gente posando en la pista llena" fill sizes="(min-width: 1024px) 20vw, 48vw" className="object-cover" />
            </div>
          </div>
        </div>
      </Section>

      <Section>
        <SectionHeading title="En cabina" description="Fotos reales de nuestras noches. Hay más en la galería." action={{ href: "/galeria", label: "Galería" }} />
        <ul className="grid gap-2 sm:grid-cols-3 sm:gap-3">
          {CABINA.map((f) => (
            <li key={f.src} className="relative aspect-[4/3] overflow-hidden rounded-md bg-slate">
              <Image src={f.src} alt={f.alt} fill sizes="(min-width: 640px) 31vw, 100vw" className="object-cover" />
            </li>
          ))}
        </ul>
      </Section>

      <ProposeCta />
    </>
  );
}
