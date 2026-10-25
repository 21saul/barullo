"use client";

import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import useEmblaCarousel from "embla-carousel-react";
import type { EmblaCarouselType } from "embla-carousel";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Icon } from "@/components/ui/Icon";
import { StatusBadge } from "@/components/events/StatusBadge";
import type { StripDay, StripNight } from "./month-strip-data";
import { cn } from "@/lib/utils";

/** Cada noche se queda 5 s; al tocar algo, el pase automático para 7 s. */
const AUTOPLAY_MS = 5000;
const IDLE_MS = 7000;

/**
 * Tira del mes: junta los antiguos «Tickets» y «Este mes». Arriba, una
 * entrada grande por noche que se desliza con el dedo (Embla, en bucle); al
 * soltar, las de los lados quedan algo giradas, como un mazo repartido.
 * Debajo, la regla de los próximos 30 días con cada noche colgada en su
 * fecha: se desplaza en horizontal con el dedo (scroll nativo) y al tocar una
 * miniatura salta a esa entrada.
 *
 * Pasa sola de noche en noche mientras la sección está a la vista, con una
 * barrita de progreso bajo la miniatura activa. Con «reducir movimiento» no
 * pasa sola ni gira nada.
 */
export function MonthStrip({ nights, days, total }: { nights: StripNight[]; days: StripDay[]; total: number }) {
  const [viewportRef, api] = useEmblaCarousel({ align: "center", loop: nights.length > 2 });
  const [selected, setSelected] = useState(0);
  const [paused, setPaused] = useState(false);
  const [visible, setVisible] = useState(false);
  const [reduced, setReduced] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);
  const rulerRef = useRef<HTMLDivElement>(null);
  const idle = useRef<ReturnType<typeof setTimeout>>(undefined);
  const rulerBusy = useRef<ReturnType<typeof setTimeout>>(undefined);
  const rulerTouched = useRef(false);

  const hold = useCallback(() => {
    setPaused(true);
    clearTimeout(idle.current);
    idle.current = setTimeout(() => setPaused(false), IDLE_MS);
  }, []);

  // Las entradas de los lados se giran y encogen según lo lejos que estén.
  const tween = useCallback((embla: EmblaCarouselType) => {
    const engine = embla.internalEngine();
    const scroll = embla.scrollProgress();
    const snaps = embla.scrollSnapList();
    const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    embla.slideNodes().forEach((node, i) => {
      let diff = snaps[i] - scroll;
      if (engine.options.loop) {
        engine.slideLooper.loopPoints.forEach((p) => {
          if (p.index === i && p.target() !== 0) diff = snaps[i] + Math.sign(p.target()) - scroll;
        });
      }
      const slides = diff * snaps.length;
      const t = Math.min(Math.abs(slides), 1);
      const inner = node.firstElementChild as HTMLElement | null;
      if (!inner) return;
      inner.style.transform = still ? "" : `rotate(${Math.max(-1, Math.min(1, slides)) * 5}deg) scale(${1 - t * 0.07})`;
      inner.style.opacity = String(1 - t * 0.4);
    });
  }, []);

  useEffect(() => {
    if (!api) return;
    const onSelect = () => setSelected(api.selectedScrollSnap());
    const raf = requestAnimationFrame(() => tween(api));
    api.on("select", onSelect).on("scroll", tween).on("reInit", tween).on("pointerDown", hold);
    return () => {
      cancelAnimationFrame(raf);
      api.off("select", onSelect).off("scroll", tween).off("reInit", tween).off("pointerDown", hold);
    };
  }, [api, tween, hold]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const sync = () => setReduced(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    const io = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting), { threshold: 0.35 });
    if (sectionRef.current) io.observe(sectionRef.current);
    return () => {
      mq.removeEventListener("change", sync);
      io.disconnect();
      clearTimeout(idle.current);
      clearTimeout(rulerBusy.current);
    };
  }, []);

  const running = visible && !paused && !reduced && nights.length > 1;

  useEffect(() => {
    if (!api || !running) return;
    const t = setTimeout(() => api.scrollNext(), AUTOPLAY_MS);
    return () => clearTimeout(t);
  }, [api, running, selected]);

  // La regla sigue a la entrada, salvo mientras alguien la está arrastrando.
  useEffect(() => {
    const ruler = rulerRef.current;
    const btn = ruler?.querySelector<HTMLElement>(`[data-night="${selected}"]`);
    if (!ruler || !btn || rulerTouched.current) return;
    ruler.scrollTo({
      left: btn.offsetLeft - ruler.clientWidth / 2 + btn.offsetWidth / 2,
      behavior: reduced ? "auto" : "smooth",
    });
  }, [selected, reduced]);

  const touchRuler = () => {
    rulerTouched.current = true;
    hold();
    clearTimeout(rulerBusy.current);
    rulerBusy.current = setTimeout(() => (rulerTouched.current = false), IDLE_MS);
  };

  return (
    <Section className="pt-8 md:pt-14">
      <div ref={sectionRef}>
        <SectionHeading title="Este mes" action={{ href: "/agenda", label: `Agenda · ${total}` }} />

        <div
          className="relative -mx-4 sm:-mx-8"
          role="region"
          aria-roledescription="carrusel"
          aria-label="Próximas noches"
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
        >
          <div ref={viewportRef} className="overflow-hidden px-4 sm:px-8">
            <ul className="flex touch-pan-y">
              {nights.map((n, i) => (
                <li
                  key={n.slug}
                  className="min-w-0 shrink-0 grow-0 basis-[86%] px-1.5 sm:basis-[58%] lg:basis-[38%] xl:basis-[31%]"
                  aria-roledescription="diapositiva"
                  aria-label={`${i + 1} de ${nights.length}`}
                >
                  <div className="h-full origin-bottom will-change-transform">
                    <MonthTicket night={n} priority={i < 2} />
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <p className="mt-3 flex items-center justify-center gap-2 text-xs font-extrabold text-dust md:hidden">
          <Icon name="ArrowLeft" size={14} />
          Desliza para cambiar de noche
          <Icon name="ArrowRight" size={14} />
        </p>

        {/* Regla de días: scroll nativo en horizontal, también con el dedo. */}
        <div
          ref={rulerRef}
          className="no-scrollbar -mx-4 mt-5 overflow-x-auto overscroll-x-contain px-4 [mask-image:linear-gradient(90deg,transparent,#000_16px,#000_calc(100%-16px),transparent)] sm:-mx-8 sm:px-8"
          onPointerDown={touchRuler}
          onWheel={touchRuler}
          onTouchStart={touchRuler}
        >
          <ol className="flex w-max pt-1.5" aria-label="Días del mes">
            {days.map((d) => {
              const n = d.night !== undefined ? nights[d.night] : undefined;
              const on = d.night === selected;
              const inner = (
                <>
                  {d.month && (
                    <span className="absolute left-0.5 top-0 text-[10px] font-black tracking-[0.12em] text-acid">{d.month}</span>
                  )}
                  {n && (
                    <>
                      <span
                        className={cn(
                          "absolute bottom-11 aspect-[4/5] w-10 overflow-hidden rounded-[6px] bg-slate ring-1 ring-edge transition-transform duration-300 ease-[cubic-bezier(.34,1.5,.64,1)]",
                          on && "-translate-y-2 scale-115 ring-2 ring-acid",
                        )}
                      >
                        <Image
                          src={n.flyer.src}
                          alt=""
                          fill
                          sizes="48px"
                          className={cn("object-cover transition-[filter] duration-300", !on && "brightness-75 grayscale-70")}
                        />
                      </span>
                      <span className="absolute bottom-9 h-[3px] w-10 overflow-hidden rounded-pill bg-rule" aria-hidden="true">
                        {on && running && (
                          <span
                            key={selected}
                            className="block h-full origin-left bg-acid motion-safe:animate-[fill-x_5s_linear_forwards]"
                          />
                        )}
                      </span>
                    </>
                  )}
                  <span aria-hidden="true" className={cn("w-px", d.clubDay ? "h-3.5 bg-ash" : "h-2 bg-edge")} />
                  <span
                    className={cn(
                      "text-[11px] font-black leading-none tabular-nums",
                      on ? "text-acid" : n ? "text-milk" : d.month ? "text-acid" : "text-dust",
                    )}
                  >
                    {d.day}
                  </span>
                  <span aria-hidden="true" className="text-[8px] font-black leading-none tracking-[0.08em] text-edge">
                    {d.initial}
                  </span>
                </>
              );
              const cell = "relative flex h-[7.25rem] w-9 flex-col items-center justify-end gap-1";
              return (
                <li key={d.key} className="shrink-0">
                  {n && d.night !== undefined ? (
                    <button
                      type="button"
                      data-night={d.night}
                      aria-label={`${n.title}, ${n.label}`}
                      aria-current={on ? "true" : undefined}
                      onClick={() => {
                        hold();
                        api?.scrollTo(d.night!);
                      }}
                      className={cn(cell, "cursor-pointer")}
                    >
                      {inner}
                    </button>
                  ) : (
                    <div className={cell}>{inner}</div>
                  )}
                </li>
              );
            })}
          </ol>
        </div>
      </div>
    </Section>
  );
}

/**
 * La entrada del carrusel: cartel cuadrado con el día gordo en rojo, el
 * troquel y la matriz con la hora y el botón de compra. Toda la tarjeta lleva
 * a la ficha (enlace estirado); el botón de entradas va encima y sale directo
 * al proveedor.
 */
function MonthTicket({ night: n, priority }: { night: StripNight; priority: boolean }) {
  const canBuy = n.ticketUrl && n.status !== "agotado" && n.status !== "cancelado";
  return (
    <article className="group relative flex h-full select-none flex-col overflow-hidden rounded-md bg-coal ring-1 ring-rule">
      <div className="relative aspect-square overflow-hidden bg-slate">
        <Image
          src={n.flyer.src}
          alt={n.flyer.alt}
          fill
          sizes="(min-width: 1280px) 31vw, (min-width: 1024px) 38vw, (min-width: 640px) 58vw, 86vw"
          priority={priority}
          draggable={false}
          className="object-cover transition-transform duration-500 ease-[var(--ease-soft)] group-hover:scale-[1.04]"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-coal via-coal/45 via-35% to-transparent to-70%" />
        {n.status !== "anunciado" && (
          <div className="absolute left-3 top-3">
            <StatusBadge status={n.status} />
          </div>
        )}
        <div className="absolute inset-x-4 bottom-3">
          <p className="flex items-center gap-2.5">
            <span className="data text-[3rem] font-black leading-[0.85] text-acid">{n.day}</span>
            <span className="text-xs font-black leading-tight tracking-[0.1em] text-ash">
              {n.today ? "HOY" : n.weekday}
              <br />
              {n.month}
            </span>
          </p>
          <h3 className="caps mt-2 text-xl leading-tight text-milk text-balance">
            <Link href={`/eventos/${n.slug}`} draggable={false} className="after:absolute after:inset-0 after:content-['']">
              {n.title}
            </Link>
          </h3>
          {n.lineup && <p className="mt-1 line-clamp-1 text-sm font-bold text-ash">{n.lineup}</p>}
        </div>
      </div>

      {/* Troquel: muescas del color del fondo + línea de puntos. */}
      <div className="relative h-0" aria-hidden="true">
        <span className="absolute -left-2.5 -top-2.5 size-5 rounded-full bg-void ring-1 ring-rule" />
        <span className="absolute -right-2.5 -top-2.5 size-5 rounded-full bg-void ring-1 ring-rule" />
        <span className="absolute inset-x-4 top-0 border-t-2 border-dotted border-edge" />
      </div>

      <div className="flex items-center justify-between gap-3 px-4 py-3.5">
        <p className="data min-w-0 truncate text-[13px] font-bold text-ash">
          {n.doors} · {n.room}
        </p>
        {canBuy ? (
          <a
            href={n.ticketUrl}
            target="_blank"
            rel="noopener noreferrer"
            draggable={false}
            className="relative z-10 inline-flex h-10 shrink-0 items-center gap-1.5 rounded-pill bg-acid px-4 text-sm font-black text-void transition-colors hover:bg-milk"
          >
            Entradas
            {n.priceFrom ? <span className="font-bold text-void/70">· {n.priceFrom} €</span> : null}
          </a>
        ) : (
          <span className="relative z-10 shrink-0 rounded-pill border border-edge px-4 py-2 text-sm font-bold text-ash">
            {n.status === "gratis" ? "Entrada libre" : n.status === "agotado" ? "Agotado" : "Ver noche"}
          </span>
        )}
      </div>
    </article>
  );
}
