"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import type { BrandLoop } from "@/content/brand";
import { Icon } from "@/components/ui/Icon";

/**
 * Héroe animado de la home (renderizado con Remotion).
 *
 * Tres decisiones que conviene no deshacer:
 *
 * 1. El vídeo pesa más de un mega y esta página se abre desde el navegador de
 *    Instagram con 4G, así que NO se carga de entrada. Primero se pinta el
 *    póster (next/image lo sirve en AVIF) y el vídeo entra después, sólo si el
 *    dispositivo no pide menos movimiento y la conexión no es lenta ni está en
 *    ahorro de datos. Si algo falla, se queda el póster y no se nota.
 *
 * 2. Qué máster toca se decide en JS, NO con `sm:hidden`. Ocultar con CSS un
 *    <video autoPlay> no evita su descarga: se bajarían los dos másteres en
 *    todos los dispositivos. Aquí sólo se monta uno.
 *
 * 3. Qué se muestra sale de `src/content/brand.ts`, no está escrito aquí:
 *    el héroe va a pasar del wordmark al personaje y debe ser un cambio de
 *    una línea.
 *
 * 4. El marco reserva su altura con una clase literal (`loop.frame`), no
 *    componiendo `sm:` en JS. Tailwind no genera lo que no ve escrito, y el
 *    marco se quedaba a altura cero hasta que cargaba el vídeo.
 *
 * 5. Lleva botón de pausa. El bucle dura 8 s y arranca solo: cualquier
 *    animación que se mueva más de cinco segundos junto a texto tiene que
 *    poder pararse (WCAG 2.2.2). Respetar `prefers-reduced-motion` cubre a
 *    quien lo lleva activado en el sistema, no a quien simplemente no puede
 *    leer con algo moviéndose al lado.
 */

function useDeferredVideo() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const conn = (
      navigator as Navigator & {
        connection?: { effectiveType?: string; saveData?: boolean };
      }
    ).connection;

    if (conn?.saveData) return;
    if (conn?.effectiveType && /^(slow-)?2g$/.test(conn.effectiveType)) return;

    // Se espera a que el hilo esté libre: el vídeo nunca compite con el LCP.
    // Safari no tiene requestIdleCallback, de ahí el respaldo con setTimeout.
    const ric = window.requestIdleCallback;
    if (ric) {
      const id = ric(() => setShow(true), { timeout: 2500 });
      return () => window.cancelIdleCallback?.(id);
    }
    const id = window.setTimeout(() => setShow(true), 1200);
    return () => window.clearTimeout(id);
  }, []);

  return show;
}

export function BrandHero({ loop, alt }: { loop: BrandLoop; alt: string }) {
  const show = useDeferredVideo();
  const [wide, setWide] = useState<boolean | null>(null);
  const [ready, setReady] = useState(false);
  const [paused, setPaused] = useState(false);
  const video = useRef<HTMLVideoElement>(null);

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

  useEffect(() => {
    const mq = window.matchMedia("(min-width: 640px)");
    const sync = () => setWide(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);

  // Antes de que corra el JS no sabemos el ancho, así que el póster estrecho
  // es el que se pinta: es el caso mayoritario (viene de Instagram) y el que
  // menos pesa. El marco ya tiene su altura reservada, así que no hay salto.
  const src = wide === null ? loop.narrow : wide ? loop.wide : loop.narrow;

  return (
    <div className="relative">
      {/* En pantallas muy anchas el 21:9 sale más alto que la ventana: se
          limita la altura y el vídeo (object-cover) recorta arriba y abajo. */}
      <div className={`relative w-full overflow-hidden bg-void sm:max-h-[min(82dvh,58rem)] ${loop.frame}`}>
        <Image
          src={src.poster}
          alt={alt}
          fill
          priority
          sizes="(max-width: 640px) 100vw, 1400px"
          className="object-cover"
        />
        {show && wide !== null && (
          <video
            ref={video}
            autoPlay
            muted
            loop
            playsInline
            preload="none"
            aria-hidden="true"
            onCanPlay={() => setReady(true)}
            className={`absolute inset-0 size-full object-cover transition-opacity duration-700 ${
              ready ? "opacity-100" : "opacity-0"
            }`}
          >
            <source src={src.webm} type="video/webm" />
            <source src={src.mp4} type="video/mp4" />
          </video>
        )}

        {/* El render sale sobre negro puro y el fondo de la página es pizarra:
            sin esto se ve una raya horizontal justo donde acaba el vídeo. */}
        <div
          className="pointer-events-none absolute inset-x-0 bottom-0 h-20 bg-gradient-to-b from-transparent to-void"
          aria-hidden="true"
        />

        {/* Sólo aparece cuando hay algo que parar: si el vídeo nunca llegó a
            cargar, el botón sería mentira. */}
        {ready && (
          <button
            type="button"
            onClick={togglePlay}
            aria-label={paused ? "Reanudar la animación" : "Pausar la animación"}
            className="absolute bottom-4 right-4 flex size-11 items-center justify-center rounded-pill border border-rule bg-void/70 text-ash backdrop-blur-md transition-colors duration-150 hover:border-acid hover:text-acid"
          >
            <Icon name={paused ? "Play" : "Pause"} size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
