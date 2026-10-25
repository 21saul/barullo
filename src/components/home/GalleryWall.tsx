"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Section, SectionHeading } from "@/components/ui/Section";
import { KufiWordmark } from "@/components/brand/KufiWordmark";
import { cn } from "@/lib/utils";

export type WallPhoto = { src: string; href: string; label: string };

/** Píxeles por segundo de cada columna; el signo alterna el sentido. */
const SPEEDS = [14, -10, 18, -13, 11, -16, 12];

/**
 * Noches pasadas como un muro de fotos visto en escorzo: columnas sobre un
 * plano tumbado y girado que corren solas, cada una a su velocidad y en
 * sentido contrario a la de al lado. En móvil van 5 columnas y en ordenador 7.
 *
 * Las fotos son pequeñas, así que la firma «barullo» va una sola vez en la
 * esquina del muro, como la mosca de una tele. Cada foto lleva a su álbum.
 *
 * Sólo corre mientras se ve; con el ratón encima va más despacio y con
 * «reducir movimiento» se queda quieto. Para no pintar de más, las columnas
 * se mueven con transform en un bucle de requestAnimationFrame, sin estado
 * de React por fotograma.
 */
export function GalleryWall({ photos, total }: { photos: WallPhoto[]; total: number }) {
  const cols = SPEEDS.map((_, c) => photos.filter((_, i) => i % SPEEDS.length === c));
  const colRefs = useRef<(HTMLDivElement | null)[]>([]);
  const boxRef = useRef<HTMLDivElement>(null);
  const [paused, setPaused] = useState(false);
  const [shown, setShown] = useState(false);
  const run = useRef({ visible: false, paused: false, reduced: false, slow: 1, target: 1 });

  useEffect(() => {
    run.current.paused = paused;
  }, [paused]);

  useEffect(() => {
    const state = run.current;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const sync = () => (state.reduced = mq.matches);
    sync();
    mq.addEventListener("change", sync);
    const io = new IntersectionObserver(
      ([entry]) => {
        state.visible = entry.isIntersecting;
        if (entry.isIntersecting) setShown(true);
      },
      { threshold: 0.15 },
    );
    if (boxRef.current) io.observe(boxRef.current);

    const pos = SPEEDS.map(() => 0);
    let prev = performance.now();
    let raf = requestAnimationFrame(function frame(now) {
      const dt = Math.min(0.05, (now - prev) / 1000);
      prev = now;
      state.slow += (state.target - state.slow) * Math.min(1, dt * 4);
      if (state.visible && !state.paused && !state.reduced) {
        colRefs.current.forEach((el, i) => {
          if (!el) return;
          // Cada columna lleva sus fotos dos veces: al llegar a la mitad, vuelve a 0 sin salto.
          const half = el.scrollHeight / 2;
          if (!half) return;
          pos[i] = (((pos[i] + SPEEDS[i] * dt * state.slow) % half) + half) % half;
          el.style.transform = `translate3d(0, ${-pos[i]}px, 0)`;
        });
      }
      raf = requestAnimationFrame(frame);
    });

    return () => {
      cancelAnimationFrame(raf);
      io.disconnect();
      mq.removeEventListener("change", sync);
    };
  }, []);

  return (
    <Section>
      <SectionHeading title="Noches pasadas" action={{ href: "/galeria", label: `Galería · ${total}` }} />

      <div
        ref={boxRef}
        className="relative -mx-4 h-[470px] overflow-hidden [perspective:760px] sm:-mx-8 md:h-[560px]"
        onMouseEnter={() => (run.current.target = 0.25)}
        onMouseLeave={() => (run.current.target = 1)}
      >
        <div
          className={cn(
            "absolute -inset-x-[30%] -inset-y-[40%] grid grid-cols-5 gap-2 transition-[transform,opacity] duration-[1300ms] ease-[var(--ease-soft)] md:grid-cols-7 md:gap-3",
            shown
              ? "opacity-100 [transform:rotateX(34deg)_rotateZ(-14deg)_translateZ(-40px)]"
              : "opacity-0 [transform:rotateX(70deg)_rotateZ(-30deg)_translateZ(-300px)]",
          )}
        >
          {cols.map((col, c) => (
            <div
              key={c}
              ref={(el) => {
                colRefs.current[c] = el;
              }}
              className={cn("grid content-start gap-2 will-change-transform md:gap-3", c >= 5 && "hidden md:grid")}
            >
              {[...col, ...col].map((p, i) => {
                const copy = i >= col.length;
                return (
                  <Link
                    key={i}
                    href={p.href}
                    draggable={false}
                    aria-label={copy ? undefined : `Fotos de ${p.label}`}
                    aria-hidden={copy || undefined}
                    tabIndex={copy ? -1 : undefined}
                    className="relative block aspect-[4/5] overflow-hidden rounded-sm bg-slate"
                  >
                    <Image
                      src={p.src}
                      alt=""
                      fill
                      sizes="(min-width: 768px) 14vw, 26vw"
                      draggable={false}
                      className="object-cover transition-transform duration-500 hover:scale-105"
                    />
                  </Link>
                );
              })}
            </div>
          ))}
        </div>

        {/* Fundidos arriba y abajo: capas encima, más baratas que una máscara. */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-void to-transparent" />
        <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-void to-transparent" />
        <KufiWordmark
          title=""
          className="pointer-events-none absolute bottom-3 right-4 w-20 text-milk/80 drop-shadow-[0_1px_3px_rgb(0_0_0/0.7)] sm:right-8 md:w-24"
        />
      </div>

      <div className="mt-4 flex items-center justify-between gap-4">
        <p className="text-sm font-bold text-ash">Toca una foto para ver su noche</p>
        <button
          type="button"
          onClick={() => setPaused((p) => !p)}
          aria-pressed={paused}
          className="h-9 shrink-0 rounded-pill border border-edge px-4 text-xs font-black text-milk transition-colors hover:border-milk"
        >
          {paused ? "Reanudar" : "Pausar"}
        </button>
      </div>
    </Section>
  );
}
