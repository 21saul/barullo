"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

/**
 * Medallas del catálogo (bocetos/disenos/logo/estilos) que tiran a rojo, negro y
 * plata, las que pegan con el plato rojo del CTA. Se elige una al montar: cada
 * recarga o cada vez que se vuelve a la página sale otra, nunca la misma dos
 * veces seguidas. Mientras no hay elección (SSR) sólo se ve el plato.
 */
const MEDALS = [
  "negro-rubi-plata",
  "oro-girih-rubi",
  "plata-rosetas-rojo",
  "plata-joya-rubi",
  "oro-rosa-arabesco",
  "cromo-negro-guilloche",
];
const LAST_KEY = "barullo:medalla";

function pick() {
  let last: string | null = null;
  try {
    last = sessionStorage.getItem(LAST_KEY);
  } catch {}
  const pool = MEDALS.filter((m) => m !== last);
  const next = pool[Math.floor(Math.random() * pool.length)];
  try {
    sessionStorage.setItem(LAST_KEY, next);
  } catch {}
  return next;
}

export function RandomMedal({ className, sizes }: { className?: string; sizes: string }) {
  const [medal, setMedal] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    // Aleatorio sólo en cliente: en el servidor daría un desajuste de hidratación.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMedal(pick());
  }, []);

  return (
    <div aria-hidden="true" className={className}>
      {medal && (
        <Image
          src={`/media/brand/medallas/${medal}.webp`}
          alt=""
          fill
          sizes={sizes}
          onLoad={() => setLoaded(true)}
          className={`object-contain drop-shadow-[0_24px_40px_rgb(0_0_0/0.55)] transition-[opacity,scale] duration-700 ease-out motion-safe:animate-[spin_60s_linear_infinite] ${loaded ? "scale-100 opacity-100" : "scale-90 opacity-0"}`}
        />
      )}
    </div>
  );
}
