import Link from "next/link";
import { SITE, FOOTER_NAV } from "@/content/site";
import { Newsletter } from "@/components/home/Newsletter";
import { Icon, type IconName } from "@/components/ui/Icon";
import { BrandIcon, type BrandName } from "@/components/ui/BrandIcon";
import { Emblem } from "@/components/brand/Emblem";
import { Stamp } from "@/components/brand/Stamp";

const SOCIALS: { href: string; label: string; icon: BrandName }[] = [
  { href: SITE.socials.instagram, label: "Instagram", icon: "Instagram" },
  { href: SITE.socials.tiktok, label: "TikTok", icon: "TikTok" },
  { href: SITE.socials.soundcloud, label: "SoundCloud", icon: "SoundCloud" },
  { href: SITE.socials.spotify, label: "Spotify", icon: "Spotify" },
];

/**
 * Lo práctico, con su icono. Sin dirección ni «cómo llegar»: Barullo es un
 * club, no una discoteca, y el sitio de cada noche va en la ficha del evento.
 */
const INFO: { icon: IconName; label: string; value: string; href?: string }[] = [
  { icon: "ShieldCheck", label: "Acceso", value: `Mayores de ${SITE.minAge}, con DNI` },
  { icon: "Mail", label: "Correo", value: SITE.email, href: `mailto:${SITE.email}` },
];

const LEGAL = [...FOOTER_NAV.Legal, { href: "/legal/creditos", label: "Créditos de fotos" }];

/**
 * Pie «banda roja»: el boletín en rojo con la medalla, y debajo sólo lo
 * imprescindible: unos sellos de adorno, acceso y correo, las redes y una
 * línea legal. La navegación ya está en la cabecera; aquí no se repite.
 *
 * Móvil y ordenador son dos maquetas distintas que comparten piezas; el CSS
 * enseña una u otra según el ancho de pantalla (`lg`), sin JS.
 */
export function Footer() {
  return (
    <footer className="px-2 pb-2 sm:px-4 sm:pb-4">
      <div className="mx-auto w-full max-w-[90rem] 3xl:max-w-[110rem] overflow-hidden rounded-lg bg-coal ring-1 ring-rule">
        <Newsletter />

        {/* Móvil y tableta: todo en columna, centrado y a todo el ancho. */}
        <div className="flex flex-col gap-6 px-4 pb-6 pt-8 sm:px-8 lg:hidden">
          <Stamps className="justify-center" />
          <ul className="divide-y divide-rule rounded-md bg-slate px-4">
            {INFO.map((i) => (
              <InfoItem key={i.label} item={i} className="py-3.5" />
            ))}
          </ul>
          <ul className="grid grid-cols-4 gap-2">
            {SOCIALS.map((s) => (
              <SocialLink key={s.label} social={s} className="h-12" />
            ))}
          </ul>
          <div className="border-t border-rule pt-5 text-center text-sm font-semibold text-ash">
            <LegalLinks className="justify-center" />
            <Copyright className="mt-3" />
          </div>
        </div>

        {/* Ordenador: sellos, datos y redes en una fila; legal debajo. */}
        <div className="hidden px-16 lg:block">
          <div className="flex items-center gap-12 py-10">
            <Stamps />
            <ul className="mr-auto flex gap-12">
              {INFO.map((i) => (
                <InfoItem key={i.label} item={i} />
              ))}
            </ul>
            <ul className="flex gap-2">
              {SOCIALS.map((s) => (
                <SocialLink key={s.label} social={s} className="size-12" />
              ))}
            </ul>
          </div>
          <div className="flex items-center justify-between border-t border-rule py-6 text-sm font-semibold text-ash">
            <Copyright />
            <LegalLinks />
          </div>
        </div>
      </div>
    </footer>
  );
}

function InfoItem({ item: i, className = "" }: { item: (typeof INFO)[number]; className?: string }) {
  return (
    <li className={`flex items-center gap-3.5 ${className}`}>
      <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-void text-acid lg:bg-slate">
        <Icon name={i.icon} size={20} />
      </span>
      <span className="min-w-0">
        <span className="block text-sm font-bold text-ash">{i.label}</span>
        {i.href ? (
          <a href={i.href} className="block text-base font-extrabold text-milk hover:text-acid">
            {i.value}
          </a>
        ) : (
          <span className="block text-base font-extrabold text-milk">{i.value}</span>
        )}
      </span>
    </li>
  );
}

function SocialLink({ social: s, className }: { social: (typeof SOCIALS)[number]; className: string }) {
  return (
    <li>
      <a
        href={s.href}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={s.label}
        className={`flex items-center justify-center rounded-full text-milk ring-1 ring-edge ring-inset transition-colors hover:bg-acid hover:text-void hover:ring-acid ${className}`}
      >
        <BrandIcon name={s.icon} size={20} />
      </a>
    </li>
  );
}

function LegalLinks({ className = "" }: { className?: string }) {
  return (
    <ul className={`flex flex-wrap gap-x-5 gap-y-1 ${className}`}>
      {LEGAL.map((link) => (
        <li key={link.href}>
          <Link href={link.href} className="inline-flex min-h-9 items-center hover:text-milk">
            {link.label}
          </Link>
        </li>
      ))}
    </ul>
  );
}

function Copyright({ className = "" }: { className?: string }) {
  return (
    <p className={className}>
      © {new Date().getFullYear()} {SITE.legalName}, {SITE.city}.
    </p>
  );
}

/**
 * Sellos de pegatina, un poco torcidos y montados unos sobre otros. Puro
 * adorno: el dato de verdad (acceso, correo) va al lado en texto.
 */
function Stamps({ className = "" }: { className?: string }) {
  return (
    <div className={`flex shrink-0 items-center ${className}`}>
      <Stamp
        id="club"
        shape="scallop"
        text="BARULLO CLUB · VIGO · BARULLO CLUB · VIGO · "
        bg="var(--color-acid)"
        fg="var(--color-void)"
        className="size-[6.5rem] -rotate-12 lg:size-32"
      >
        <Emblem className="size-full text-void" disc="var(--color-acid)" title="" />
      </Stamp>
      <Stamp
        id="musica"
        shape="disc"
        text="MÚSICA DE CLUB · HECHO EN VIGO · "
        bg="var(--color-milk)"
        fg="var(--color-void)"
        className="-ml-2 size-[6.5rem] rotate-6 lg:-ml-4 lg:size-28"
      >
        <Icon name="Disc" size={28} className="text-void" />
      </Stamp>
      <Stamp
        id="respeto"
        shape="ring"
        text="BAILA · ESCUCHA · RESPETA · "
        bg="var(--color-coal)"
        fg="var(--color-milk)"
        className="-ml-2 size-[6.5rem] -rotate-3 lg:-ml-3 lg:size-28"
      >
        <span className="wide text-2xl text-milk lg:text-3xl">+18</span>
      </Stamp>
    </div>
  );
}
