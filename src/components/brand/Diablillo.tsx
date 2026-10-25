"use client";

import { useEffect, useRef, useState } from "react";

/**
 * La mascota: el diablillo de cromo (Blender, bocetos/disenos/mascota/) flotando en
 * bucle, con fondo transparente para posarse sobre cualquier superficie.
 *
 * Chrome y Firefox leen el canal alfa del VP9 en WebM; Safari no (lo pinta
 * sobre negro), así que allí va el mismo bucle en WebP animado. Con
 * «reducir movimiento» se queda quieto en el póster. Siempre decorativo.
 */
const SRC = "/media/brand/diablillo";

export function Diablillo({ className = "", priority = false }: { className?: string; priority?: boolean }) {
  const [mode, setMode] = useState<"poster" | "video" | "webp">("poster");
  const ref = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const ua = navigator.userAgent;
    const safari = /Safari\//.test(ua) && !/Chrome\/|Chromium\/|Edg\/|Firefox\//.test(ua);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMode(safari ? "webp" : "video");
  }, []);

  // Fuera de pantalla no hace falta decodificar.
  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    const io = new IntersectionObserver(([e]) => (e.isIntersecting ? v.play().catch(() => {}) : v.pause()));
    io.observe(v);
    return () => io.disconnect();
  }, [mode]);

  return (
    <div aria-hidden="true" className={className}>
      {mode === "video" ? (
        <video
          ref={ref}
          className="absolute inset-0 size-full object-contain"
          poster={`${SRC}/poster.webp`}
          muted
          loop
          playsInline
          autoPlay
          preload="metadata"
        >
          <source src={`${SRC}/loop.webm`} type="video/webm" />
        </video>
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={mode === "webp" ? `${SRC}/loop.webp` : `${SRC}/poster.webp`}
          alt=""
          className="absolute inset-0 size-full object-contain"
          loading={priority ? "eager" : "lazy"}
          decoding="async"
        />
      )}
    </div>
  );
}
