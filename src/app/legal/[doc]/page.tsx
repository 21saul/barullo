import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { LEGAL_DOCS, getLegalDoc } from "@/content/legal";
import { longDate } from "@/lib/dates";
import { breadcrumbJsonLd, JsonLd } from "@/lib/seo";
import { Section } from "@/components/ui/Section";

export function generateStaticParams() {
  return LEGAL_DOCS.map((d) => ({ doc: d.slug }));
}

export async function generateMetadata({ params }: PageProps<"/legal/[doc]">): Promise<Metadata> {
  const { doc } = await params;
  const legal = getLegalDoc(doc);
  if (!legal) return {};
  return {
    title: legal.title,
    description: legal.description,
    alternates: { canonical: `/legal/${doc}` },
    // Las páginas legales no aportan nada al índice y diluyen el presupuesto
    // de rastreo, pero sí deben ser rastreables para pasar enlace.
    robots: { index: false, follow: true },
  };
}

export default async function LegalPage({ params }: PageProps<"/legal/[doc]">) {
  const { doc } = await params;
  const legal = getLegalDoc(doc);
  if (!legal) notFound();

  return (
    <>
      <JsonLd
        data={breadcrumbJsonLd([
          { name: "Inicio", href: "/" },
          { name: legal.title, href: `/legal/${doc}` },
        ])}
      />

      <Section className="pt-10">
        <div className="max-w-2xl">
          <h1 className="wide uppercase text-[clamp(1.75rem,8vw,3rem)] leading-[0.98] text-milk text-balance">
            {legal.title}
          </h1>
          <p className="mt-4 text-sm text-ash">
            Última actualización: {longDate(new Date(legal.updated))}
          </p>

          <div className="mt-12 space-y-10">
            {legal.sections.map((s) => (
              <section key={s.heading}>
                <h2 className="caps text-base leading-tight text-milk">{s.heading}</h2>
                <div className="mt-3 space-y-3 text-sm leading-relaxed text-ash">
                  {s.body.map((p, i) => (
                    <p key={i}>{p}</p>
                  ))}
                </div>
              </section>
            ))}
          </div>

          <nav aria-label="Otros documentos legales" className="mt-16 border-t border-rule pt-8">
            <ul className="flex flex-wrap gap-x-5 gap-y-2">
              {LEGAL_DOCS.filter((d) => d.slug !== doc).map((d) => (
                <li key={d.slug}>
                  <Link
                    href={`/legal/${d.slug}`}
                    className="text-sm text-ash transition-colors hover:text-acid"
                  >
                    {d.title}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </Section>
    </>
  );
}
