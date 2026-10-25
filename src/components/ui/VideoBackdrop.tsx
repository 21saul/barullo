"use client";

import { useEffect, useState } from "react";

/**
 * Fondo de vídeo decorativo.
 *
 * Sólo se carga en pantallas anchas. En móvil el efecto equivalente ya lo dan
 * los `Bloom` en CSS, que cuestan 0 KB: meter medio mega de vídeo en la ruta
 * crítica para lo mismo sería un mal negocio.
 *
 * Se respeta `prefers-reduced-motion` y el ahorro de datos.
 */
export function VideoBackdrop({
  webm,
  mp4,
  poster,
  opacity = 0.3,
}: {
  webm: string;
  mp4: string;
  poster?: string;
  opacity?: number;
}) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (!window.matchMedia("(min-width: 1024px)").matches) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const conn = (
      navigator as Navigator & {
        connection?: { effectiveType?: string; saveData?: boolean };
      }
    ).connection;
    if (conn?.saveData) return;
    if (conn?.effectiveType && /^(slow-)?2g|3g$/.test(conn.effectiveType)) return;

    const ric = window.requestIdleCallback;
    if (ric) {
      const id = ric(() => setShow(true), { timeout: 4000 });
      return () => window.cancelIdleCallback?.(id);
    }
    const id = window.setTimeout(() => setShow(true), 2000);
    return () => window.clearTimeout(id);
  }, []);

  if (!show) return null;

  return (
    <video
      autoPlay
      muted
      loop
      playsInline
      preload="none"
      poster={poster}
      aria-hidden="true"
      style={{ opacity }}
      className="pointer-events-none absolute inset-0 size-full object-cover mix-blend-screen"
    >
      <source src={webm} type="video/webm" />
      <source src={mp4} type="video/mp4" />
    </video>
  );
}
