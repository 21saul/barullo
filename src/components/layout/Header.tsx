"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { NAV, SITE } from "@/content/site";
import { Icon } from "@/components/ui/Icon";
import { BrandIcon } from "@/components/ui/BrandIcon";
import { Wordmark } from "./Wordmark";
import { cn } from "@/lib/utils";

const SOCIALS = [
  { href: SITE.socials.instagram, label: "Instagram", icon: "Instagram" },
  { href: SITE.socials.tiktok, label: "TikTok", icon: "TikTok" },
  { href: SITE.socials.soundcloud, label: "SoundCloud", icon: "SoundCloud" },
  { href: SITE.socials.spotify, label: "Spotify", icon: "Spotify" },
] as const;

export function Header() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();

  // Bloquear el scroll del fondo mientras el menú está abierto.
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  // Cerrar con Escape: el menú ocupa la pantalla entera y hay que poder salir
  // sin buscar la equis con el pulgar.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  /** Activo = la ruta actual cuelga de este enlace. "/" nunca es prefijo. */
  const isActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  return (
    <>
      {/* Cabecera mínima, como en todas las webs de club que funcionan:
          logo · Entradas · menú. Siempre maciza: transparente sobre el vídeo
          el texto se mezclaba con la imagen. */}
      <header
        className={cn(
          "pt-safe fixed inset-x-0 top-0 z-40 border-b bg-void transition-colors duration-200",
          scrolled || open ? "border-rule" : "border-transparent",
        )}
      >
        <div className="mx-auto flex h-16 w-full max-w-6xl 2xl:max-w-7xl 3xl:max-w-[100rem] items-center gap-4 px-4 sm:px-8">
          <Wordmark size={34} className="shrink-0" />

          <nav className="mx-auto hidden items-center gap-1 lg:flex" aria-label="Principal">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive(item.href) ? "page" : undefined}
                className={cn(
                  "rounded-pill px-4 py-2 text-[15px] font-extrabold transition-colors duration-150",
                  isActive(item.href) ? "bg-milk text-void" : "text-ash hover:bg-slate hover:text-milk",
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="ml-auto flex shrink-0 items-center gap-1 lg:ml-0">
            {/* En móvil también: es el acceso directo que más se pulsa. */}
            <Link
              href="/entradas"
              className="inline-flex h-10 items-center gap-2 rounded-pill bg-acid px-4 text-sm font-black text-void transition-colors duration-150 hover:bg-milk sm:px-5"
            >
              <Icon name="Ticket" size={16} />
              Entradas
            </Link>
            {/* El icono solo, sin recuadro: la zona táctil sigue siendo de
                44 px aunque no se dibuje. */}
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              aria-expanded={open}
              aria-controls="menu-movil"
              aria-label={open ? "Cerrar menú" : "Abrir menú"}
              className="-mr-2 flex size-11 items-center justify-center text-milk transition-colors duration-150 hover:text-acid lg:hidden"
            >
              <Icon name={open ? "X" : "Menu"} size={26} weight={2} />
            </button>
          </div>
        </div>
      </header>

      {/* Menú móvil a pantalla completa. dvh, no vh: en el navegador de
          Instagram el 100vh se cuela por debajo de la barra del sistema. */}
      <div
        id="menu-movil"
        hidden={!open}
        className="min-h-screen-safe pt-safe overscroll-lock fixed inset-0 z-30 flex flex-col justify-between overflow-y-auto bg-void px-4 pb-10 lg:hidden"
      >
        <nav className="mt-24 flex flex-col gap-1" aria-label="Principal móvil">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive(item.href) ? "page" : undefined}
              // Se cierra al pulsar y no en un efecto sobre `pathname`: así el
              // menú no se queda abierto encima de la página nueva.
              onClick={() => setOpen(false)}
              className="group flex items-center justify-between py-1"
            >
              <span
                className={cn(
                  // Escala con el ancho: la palabra más larga cabe en 360 px.
                  "wide text-[clamp(3rem,17vw,5rem)] uppercase leading-[0.95] transition-colors",
                  isActive(item.href) ? "text-acid" : "text-milk group-hover:text-acid",
                )}
              >
                {item.label}
              </span>
              <Icon
                name="ArrowUpRight"
                size={28}
                className="text-edge transition-colors group-hover:text-acid"
              />
            </Link>
          ))}
        </nav>

        <div className="mt-10 space-y-6">
          <Link
            href="/entradas"
            onClick={() => setOpen(false)}
            className="flex min-h-14 items-center justify-between rounded-pill bg-acid pl-6 pr-2 text-lg font-black text-void"
          >
            Entradas
            <span className="flex size-10 items-center justify-center rounded-full bg-void text-acid">
              <Icon name="Ticket" size={18} />
            </span>
          </Link>
          <p className="text-sm font-semibold leading-relaxed text-ash">
            Jueves a sábado, de 23:59 al cierre. Solo mayores de {SITE.minAge}.
          </p>
          <ul className="flex gap-2">
            {SOCIALS.map((s) => (
              <li key={s.label}>
                <a
                  href={s.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={s.label}
                  className="flex size-12 items-center justify-center rounded-full bg-coal text-milk ring-1 ring-rule transition-colors hover:bg-acid hover:text-void"
                >
                  <BrandIcon name={s.icon} size={20} />
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
}
