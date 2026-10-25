"use client";

import { Children, useCallback, useEffect, useState, type ReactNode } from "react";
import useEmblaCarousel from "embla-carousel-react";
import { WheelGesturesPlugin } from "embla-carousel-wheel-gestures";
import type { EmblaCarouselType } from "embla-carousel";
import { Icon } from "@/components/ui/Icon";
import { cn } from "@/lib/utils";

/**
 * Carrusel horizontal (Embla). Se arrastra con el dedo, con la rueda del
 * trackpad y con las flechas. Debajo, una barra de progreso que dice cuánto
 * queda por ver: en móvil sustituye a los puntitos, que no se pueden pulsar.
 *
 * `tween`: las diapositivas que no están en primer plano se encogen y se
 * apagan un poco al arrastrar. Se usa en las noches pasadas, donde la foto
 * manda; en las entradas no, porque ahí hay que poder leer todas las fechas.
 */
export function Carousel({
  children,
  label,
  slideClassName,
  tween = false,
  className,
}: {
  children: ReactNode;
  label: string;
  slideClassName: string;
  tween?: boolean;
  className?: string;
}) {
  const [viewportRef, api] = useEmblaCarousel(
    { align: "start", containScroll: "trimSnaps", skipSnaps: true },
    [WheelGesturesPlugin()],
  );
  const [progress, setProgress] = useState(0);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(false);

  const applyTween = useCallback(
    (embla: EmblaCarouselType) => {
      if (!tween) return;
      const engine = embla.internalEngine();
      const scroll = embla.scrollProgress();
      const snaps = embla.scrollSnapList();
      embla.slideNodes().forEach((node, i) => {
        // Distancia de la diapositiva a su punto de anclaje, en "pantallas".
        let diff = snaps[i] - scroll;
        if (engine.options.loop) {
          engine.slideLooper.loopPoints.forEach((p) => {
            if (p.index === i && p.target() !== 0) diff = snaps[i] + Math.sign(p.target()) - scroll;
          });
        }
        const t = Math.min(Math.abs(diff * snaps.length), 1);
        const inner = node.firstElementChild as HTMLElement | null;
        if (!inner) return;
        inner.style.transform = `scale(${1 - t * 0.08})`;
        inner.style.opacity = String(1 - t * 0.45);
      });
    },
    [tween],
  );

  const update = useCallback(
    (embla: EmblaCarouselType) => {
      setProgress(Math.max(0, Math.min(1, embla.scrollProgress())));
      setCanPrev(embla.canScrollPrev());
      setCanNext(embla.canScrollNext());
      applyTween(embla);
    },
    [applyTween],
  );

  useEffect(() => {
    if (!api) return;
    // Primera lectura en el siguiente frame: Embla ya ha medido las diapositivas.
    const raf = requestAnimationFrame(() => update(api));
    api.on("scroll", update).on("reInit", update).on("select", update);
    return () => {
      cancelAnimationFrame(raf);
      api.off("scroll", update).off("reInit", update).off("select", update);
    };
  }, [api, update]);

  // Con movimiento reducido no se encoge nada.
  useEffect(() => {
    if (!tween || !api) return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mq.matches) api.slideNodes().forEach((n) => ((n.firstElementChild as HTMLElement).style.transform = ""));
  }, [api, tween]);

  const slides = Children.toArray(children);

  return (
    <div className={cn("relative", className)} role="region" aria-roledescription="carrusel" aria-label={label}>
      <div ref={viewportRef} className="overflow-hidden">
        <ul className="-ml-3 flex touch-pan-y sm:-ml-4">
          {slides.map((slide, i) => (
            <li
              key={i}
              className={cn("min-w-0 shrink-0 grow-0 pl-3 sm:pl-4", slideClassName)}
              aria-roledescription="diapositiva"
              aria-label={`${i + 1} de ${slides.length}`}
            >
              <div className="h-full origin-center transition-[opacity] duration-200 will-change-transform">
                {slide}
              </div>
            </li>
          ))}
        </ul>
      </div>

      {(canPrev || canNext) && (
        <div className="mt-5 flex items-center gap-4">
          <div className="relative h-1 flex-1 overflow-hidden rounded-pill bg-rule" aria-hidden="true">
            <div
              className="absolute inset-y-0 left-0 rounded-pill bg-acid"
              style={{ width: `${Math.max(12, progress * 100)}%` }}
            />
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => api?.scrollPrev()}
              disabled={!canPrev}
              aria-label="Anterior"
              className="flex size-11 items-center justify-center rounded-full border border-edge text-milk transition-colors hover:border-acid hover:bg-acid hover:text-void disabled:pointer-events-none disabled:opacity-30"
            >
              <Icon name="ChevronLeft" size={20} />
            </button>
            <button
              type="button"
              onClick={() => api?.scrollNext()}
              disabled={!canNext}
              aria-label="Siguiente"
              className="flex size-11 items-center justify-center rounded-full border border-edge text-milk transition-colors hover:border-acid hover:bg-acid hover:text-void disabled:pointer-events-none disabled:opacity-30"
            >
              <Icon name="ChevronRight" size={20} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
