import type { Metadata, Viewport } from "next";
import { Anton, Nunito } from "next/font/google";
import { SITE } from "@/content/site";
import { organizationJsonLd, JsonLd } from "@/lib/seo";
import { Header } from "@/components/layout/Header";
import { EventTicker } from "@/components/home/EventTicker";
import { getUpcomingEvents } from "@/lib/events";
import { Footer } from "@/components/layout/Footer";
import { Grain } from "@/components/ui/Grain";
import { InkFilter } from "@/components/ui/InkFilter";
import "./globals.css";

/**
 * v3 (2026-10-21, a petición del club):
 *
 * Anton para titulares: la Impact de Google, gorda y condensada. Sólo tiene
 * un peso, así que `wide` desactiva la negrita sintética (si no, el navegador
 * la engorda a mano y se emborrona).
 *
 * Nunito para todo lo demás: redondeada, muy legible en pantallas pequeñas y
 * con pesos hasta 900 para datos y botones.
 *
 * El «Kufi Barullo» de la marca no es una fuente: va dibujado en el logo.
 */
const anton = Anton({
  variable: "--font-anton",
  weight: "400",
  subsets: ["latin", "latin-ext"],
  display: "swap",
});

const nunito = Nunito({
  variable: "--font-nunito",
  subsets: ["latin", "latin-ext"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE.url),
  title: {
    default: `${SITE.name} · ${SITE.tagline}`,
    template: `%s · ${SITE.name} Vigo`,
  },
  description: SITE.shortDescription,
  applicationName: SITE.name,
  keywords: [
    "club Vigo",
    "club de música Vigo",
    "música electrónica Vigo",
    "conciertos Vigo",
    "salir de fiesta en Vigo",
    "techno Vigo",
    "sala de conciertos Vigo",
    "residentes Barullo",
  ],
  authors: [{ name: SITE.legalName }],
  creator: SITE.legalName,
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "es_ES",
    url: SITE.url,
    siteName: SITE.name,
    title: `${SITE.name} · ${SITE.tagline}`,
    description: SITE.shortDescription,
  },
  twitter: { card: "summary_large_image" },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1 },
  },
  category: "nightlife",
};

export const viewport: Viewport = {
  themeColor: "#0b0b0b",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
  // El navegador de Instagram es propenso al zoom accidental, pero bloquearlo
  // del todo es una barrera de accesibilidad. Se permite hasta 5x.
  maximumScale: 5,
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const upcoming = await getUpcomingEvents(8);

  return (
    <html lang="es" className={`${anton.variable} ${nunito.variable}`}>
      <body className="min-h-screen-safe flex flex-col bg-void text-milk">
        <JsonLd data={organizationJsonLd()} />
        <a
          href="#contenido"
          className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:rounded-sm focus:bg-acid focus:px-5 focus:py-3 focus:font-bold focus:text-void"
        >
          Saltar al contenido
        </a>
        <Header />
        {/* Cinta bajo la cabecera, en todas las páginas: es la pieza que más
            identidad da y la que mantiene la agenda siempre a la vista. */}
        <div className="pt-16">
          <EventTicker events={upcoming} />
        </div>
        <main id="contenido" className="flex-1">
          {children}
        </main>
        <Footer />
        {/* Barra fija de compra en móvil. El patrón "CTA en el héroe + CTA
            fijo abajo" existe porque quien llega desde Instagram hace scroll
            largo y no vuelve arriba a buscar el botón. */}
        <Grain />
        {/* Defs de los filtros de tinta. Tienen que existir siempre: un
            `filter: url(#id)` que no resuelve oculta el elemento. */}
        <InkFilter />
      </body>
    </html>
  );
}
