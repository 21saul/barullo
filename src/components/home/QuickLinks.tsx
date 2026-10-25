import Link from "next/link";
import { Icon, type IconName } from "@/components/ui/Icon";
import { Section } from "@/components/ui/Section";

/**
 * Accesos directos. Sólo lo que se busca de verdad en un club: cómo compro,
 * qué normas hay para entrar, quiénes somos y cómo fue. Sin «cómo llegar» ni
 * «reserva de mesa»: eso es de discoteca.
 */
const LINKS: { href: string; label: string; sub: string; icon: IconName }[] = [
  { href: "/entradas", label: "Entradas", sub: "Precios, venta y taquilla", icon: "Ticket" },
  { href: "/legal/admision", label: "Normas", sub: "Edad, DNI y derecho de admisión", icon: "ShieldCheck" },
  { href: "/club", label: "Nosotros", sub: "El club y sus residentes", icon: "Disc" },
  { href: "/galeria", label: "Galería", sub: "Las fotos de cada noche", icon: "Camera" },
];

export function QuickLinks() {
  return (
    <Section className="py-6 md:py-10">
      <nav aria-label="Accesos directos">
        <ul className="grid grid-cols-2 gap-3 md:grid-cols-4 md:gap-4">
          {LINKS.map((l) => (
            <li key={l.href}>
              <Link
                href={l.href}
                className="group relative flex h-full min-h-40 flex-col justify-between overflow-hidden rounded-lg bg-coal p-4 ring-1 ring-rule transition-colors duration-200 hover:bg-acid hover:ring-acid sm:min-h-48 sm:p-5"
              >
                <span className="flex size-12 items-center justify-center rounded-full bg-slate text-acid transition-colors group-hover:bg-void sm:size-14">
                  <Icon name={l.icon} size={24} />
                </span>
                <Icon
                  name="ArrowUpRight"
                  size={20}
                  className="absolute right-4 top-4 text-dust transition-colors group-hover:text-void sm:right-5 sm:top-5"
                />
                <span>
                  <span className="caps block text-xl leading-tight text-milk group-hover:text-void sm:text-2xl">
                    {l.label}
                  </span>
                  <span className="mt-1.5 block text-[13px] font-semibold leading-snug text-ash group-hover:text-void/80 sm:text-sm">
                    {l.sub}
                  </span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </Section>
  );
}
