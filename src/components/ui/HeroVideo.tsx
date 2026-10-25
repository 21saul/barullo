"use client";

import { getImageProps } from "next/image";
import { useEffect, useRef, useState } from "react";
import type { HeroBackdrop } from "@/content/heroes";
import { Icon } from "@/components/ui/Icon";

/**
 * Fondo de vídeo de un héroe de sección. Las reglas son las de BrandHero:
 *
 * - El póster se pinta primero y es el que cuenta para el LCP. Va con
 *   <picture>, así el navegador elige el vertical o el apaisado con la media
 *   query antes de que corra el JS, sin bajarse los dos.
 * - El vídeo entra después, sólo si nadie pide menos movimiento ni ahorro de
 *   datos, y sólo se monta el máster que toca (ocultar un <video autoPlay>
 *   con CSS no evita que se descargue).
 * - Botón de pausa en cuanto hay algo que parar (WCAG 2.2.2).
 */

// Qué máster toca depende de la proporción de la pantalla, no del ancho: un
// iPad en vertical necesita el vertical, y un móvil tumbado el apaisado.
const WIDE_MQ = "(min-aspect-ratio: 4/5)";

function useDeferredVideo() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const conn = (
      navigator as Navigator & { connection?: { effectiveType?: string; saveData?: boolean } }
    ).connection;
    if (conn?.saveData) return;
    if (conn?.effectiveType && /^(slow-)?2g$/.test(conn.effectiveType)) return;

    const ric = window.requestIdleCallback;
    if (ric) {
      const id = ric(() => setShow(true), { timeout: 2000 });
      return () => window.cancelIdleCallback?.(id);
    }
    const id = window.setTimeout(() => setShow(true), 1000);
    return () => window.clearTimeout(id);
  }, []);

  return show;
}

export function HeroVideo({ backdrop, alt }: { backdrop: HeroBackdrop; alt: string }) {
  const show = useDeferredVideo();
  const [wide, setWide] = useState<boolean | null>(null);
  const [ready, setReady] = useState(false);
  const [paused, setPaused] = useState(false);
  const video = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const mq = window.matchMedia(WIDE_MQ);
    const sync = () => {
      setReady(false);
      setWide(mq.matches);
    };
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);

  const togglePlay = () => {
    const el = video.current;
    if (!el) return;
    if (el.paused) {
      void el.play();
      setPaused(false);
    } else {
      el.pause();
      setPaused(true);
    }
  };

  const common = { alt, sizes: "100vw", priority: true } as const;
  const {
    props: { srcSet: wideSet },
  } = getImageProps({ ...common, src: backdrop.wide.poster, width: 1920, height: 1080 });
  const {
    props: { srcSet: narrowSet, ...img },
  } = getImageProps({ ...common, src: backdrop.narrow.poster, width: 1080, height: 1920 });

  const src = wide ? backdrop.wide : backdrop.narrow;

  return (
    <>
      {/* El `object-position` cambia con el máster: se declara como variable
          y la clase sm: la elige, sin esperar al JS. */}
      <picture>
        <source media={WIDE_MQ} srcSet={wideSet} />
        <img
          {...img}
          srcSet={narrowSet}
          alt={alt}
          className="absolute inset-0 size-full [object-fit:var(--fit-n)] [object-position:var(--focus-n)] [mask-image:var(--mask-n)] [@media(max-aspect-ratio:4/5)]:[scale:var(--zoom-n)] [@media(max-aspect-ratio:4/5)]:[translate:0_var(--shift-n)] [@media(min-aspect-ratio:4/5)]:[mask-image:none] [@media(min-aspect-ratio:4/5)]:[object-fit:var(--fit-w)] [@media(min-aspect-ratio:4/5)]:[object-position:var(--focus-w)]"
        />
      </picture>

      {backdrop.animated && show && wide !== null && (
        <video
          key={wide ? "w" : "n"}
          ref={video}
          autoPlay
          muted
          loop
          playsInline
          preload="none"
          aria-hidden="true"
          onCanPlay={() => setReady(true)}
          className={`absolute inset-0 size-full [object-fit:var(--fit-n)] [object-position:var(--focus-n)] [mask-image:var(--mask-n)] [@media(max-aspect-ratio:4/5)]:[scale:var(--zoom-n)] [@media(max-aspect-ratio:4/5)]:[translate:0_var(--shift-n)] [@media(min-aspect-ratio:4/5)]:[mask-image:none] [@media(min-aspect-ratio:4/5)]:[object-fit:var(--fit-w)] [@media(min-aspect-ratio:4/5)]:[object-position:var(--focus-w)] transition-opacity duration-700 ${
            ready ? "opacity-100" : "opacity-0"
          }`}
        >
          <source src={src.webm} type="video/webm" />
          <source src={src.mp4} type="video/mp4" />
        </video>
      )}

      {ready && (
        <button
          type="button"
          onClick={togglePlay}
          aria-label={paused ? "Reanudar la animación" : "Pausar la animación"}
          className="absolute right-4 top-4 z-20 flex size-11 items-center justify-center rounded-pill border border-rule bg-void/60 text-ash backdrop-blur-md transition-colors duration-150 hover:border-acid hover:text-acid sm:bottom-6 sm:top-auto sm:right-8"
        >
          <Icon name={paused ? "Play" : "Pause"} size={16} />
        </button>
      )}
    </>
  );
}
