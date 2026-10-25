"use client";

import Image from "next/image";
import { useEffect, useId } from "react";
import PhotoSwipeLightbox from "photoswipe/lightbox";
import "photoswipe/style.css";
import SIZES from "@/content/photo-sizes.json";
import { Icon } from "@/components/ui/Icon";

const sizeOf = (src: string): [number, number] => {
  const s = (SIZES as Record<string, number[]>)[src];
  return s ? [s[0], s[1]] : [1600, 1067];
};

/**
 * Mosaico de fotos (columnas de alto natural, sin recortar) que se abre en
 * PhotoSwipe a pantalla completa: se pasa con el dedo, se hace zoom con dos
 * dedos y se cierra deslizando hacia abajo, como en la galería del móvil.
 *
 * El visor (PhotoSwipe) se descarga sólo al tocar la primera foto.
 */
export function PhotoGrid({ photos, title }: { photos: string[]; title: string }) {
  const id = `g${useId().replace(/[^a-zA-Z0-9]/g, "")}`;

  useEffect(() => {
    const lightbox = new PhotoSwipeLightbox({
      gallery: `#${id}`,
      children: "a",
      pswpModule: () => import("photoswipe"),
      bgOpacity: 0.96,
      wheelToZoom: true,
      showHideAnimationType: "zoom",
      paddingFn: (vp) => (vp.x < 640 ? { top: 56, bottom: 56, left: 0, right: 0 } : { top: 72, bottom: 72, left: 72, right: 72 }),
    });
    lightbox.init();
    return () => lightbox.destroy();
  }, [id]);

  return (
    <ul id={id} className="columns-2 gap-2 sm:columns-3 sm:gap-3 lg:columns-4">
      {photos.map((src, i) => {
        const [w, h] = sizeOf(src);
        return (
          <li key={`${src}-${i}`} className="mb-2 break-inside-avoid sm:mb-3">
            <a
              href={src}
              data-pswp-width={w}
              data-pswp-height={h}
              target="_blank"
              rel="noreferrer"
              className="group relative block overflow-hidden rounded-md bg-slate"
              aria-label={`Ampliar foto ${i + 1} de ${title}`}
            >
              <Image
                src={src}
                alt={`Foto ${i + 1} de ${title} en Barullo`}
                width={w}
                height={h}
                sizes="(min-width: 1024px) 25vw, (min-width: 640px) 33vw, 50vw"
                className="h-auto w-full transition-transform duration-500 ease-[var(--ease-soft)] group-hover:scale-[1.03]"
              />
              <span className="absolute right-2 top-2 flex size-8 items-center justify-center rounded-full bg-void/70 text-milk opacity-0 backdrop-blur transition-opacity group-hover:opacity-100">
                <Icon name="Maximize" size={14} />
              </span>
            </a>
          </li>
        );
      })}
    </ul>
  );
}
