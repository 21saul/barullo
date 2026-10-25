import Image from "next/image";
import type { CSSProperties } from "react";

/**
 * Fondo del héroe de /galería: las fotos de verdad, en un muro inclinado
 * que se desliza (columnas alternas en sentidos contrarios). Van viradas al
 * rojo del club y, cada poco, a una le salta el flash y se ve en color.
 *
 * Todo es CSS (cero JS). Cada columna repite su tira dos veces y se desplaza
 * un 50 %, así el bucle no tiene costura. Con prefers-reduced-motion la regla
 * global para las animaciones y queda un muro quieto.
 */
export function GalleryScene({ photos }: { photos: string[] }) {
  const COLS = 5;
  const PER = Math.max(4, Math.ceil(Math.min(photos.length, 30) / COLS));
  const cols = Array.from({ length: COLS }, (_, c) =>
    Array.from({ length: PER }, (_, i) => photos[(c + i * COLS) % photos.length]),
  );

  return (
    <div className="absolute inset-0 overflow-hidden bg-void">
      <div className="gwall">
        {cols.map((col, c) => (
          <div
            key={c}
            className={c >= 3 ? "gwall-col hidden sm:flex" : "gwall-col"}
            style={{ "--dur": `${70 + c * 9}s`, "--dir": c % 2 ? "reverse" : "normal" } as CSSProperties}
          >
            {[...col, ...col].map((src, i) => (
              <div
                key={i}
                className="gwall-photo"
                // Cada foto tiene su turno de flash: un retardo distinto
                // dentro del mismo ciclo, repartido entre columnas.
                style={{ "--flash": `${((c * 7 + i * 3) % 23) * 1.3}s` } as CSSProperties}
              >
                <Image src={src} alt="" fill sizes="(min-width: 640px) 18vw, 34vw" className="object-cover" />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
