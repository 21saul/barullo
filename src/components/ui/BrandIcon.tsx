/**
 * Logotipos de marca.
 *
 * Lucide no trae iconos de marca: los retiró en la v1 porque son marcas
 * registradas y no puede mantenerlas. Van aparte, y además son **macizos**
 * (trazados rellenos, rejilla de 256) mientras el resto del set es de trazo:
 * un logotipo no se puede redibujar a trazo sin dejar de ser el logotipo.
 *
 * Están dibujados con el peso `bold` de Phosphor (MIT), que a 256 equivale a
 * un trazo de ~2,25 sobre 24: el mismo grosor óptico que `Icon`, así que en la
 * fila de redes del pie no se nota el cambio de familia.
 *
 * Son cuatro y no cambian nunca: no hay generador, se edita a mano.
 */
import type { SVGProps } from "react";

const PATHS = {
  Instagram: ["M128,80a48,48,0,1,0,48,48A48.05,48.05,0,0,0,128,80Zm0,72a24,24,0,1,1,24-24A24,24,0,0,1,128,152ZM176,20H80A60.07,60.07,0,0,0,20,80v96a60.07,60.07,0,0,0,60,60h96a60.07,60.07,0,0,0,60-60V80A60.07,60.07,0,0,0,176,20Zm36,156a36,36,0,0,1-36,36H80a36,36,0,0,1-36-36V80A36,36,0,0,1,80,44h96a36,36,0,0,1,36,36ZM196,76a16,16,0,1,1-16-16A16,16,0,0,1,196,76Z"],
  TikTok: ["M224,68a44.05,44.05,0,0,1-44-44,12,12,0,0,0-12-12H128a12,12,0,0,0-12,12V156a16,16,0,1,1-22.85-14.47A12,12,0,0,0,100,130.69V88A12,12,0,0,0,85.9,76.19a79.35,79.35,0,0,0-47.08,27.74A81.84,81.84,0,0,0,20,156a80,80,0,0,0,160,0V122.67A107.47,107.47,0,0,0,224,132a12,12,0,0,0,12-12V80A12,12,0,0,0,224,68Zm-12,39.15a83.05,83.05,0,0,1-37-14.91A12,12,0,0,0,156,102v54a56,56,0,0,1-112,0,57.86,57.86,0,0,1,32-51.56V124a40,40,0,1,0,64,32V36h17.06A68.21,68.21,0,0,0,212,90.94Z"],
  SoundCloud: ["M32,120v48a12,12,0,0,1-24,0V120a12,12,0,0,1,24,0ZM60,84A12,12,0,0,0,48,96v96a12,12,0,0,0,24,0V96A12,12,0,0,0,60,84Zm40-40A12,12,0,0,0,88,56V192a12,12,0,0,0,24,0V56A12,12,0,0,0,100,44Zm122.34,59.33A84,84,0,0,0,140,36a12,12,0,0,0,0,24,59.78,59.78,0,0,1,59.7,53.93,12,12,0,0,0,9.66,10.58A28,28,0,0,1,204,180H140a12,12,0,0,0,0,24h64a52,52,0,0,0,18.34-100.67Z"],
  Spotify: ["M128,20A108,108,0,1,0,236,128,108.12,108.12,0,0,0,128,20Zm0,192a84,84,0,1,1,84-84A84.09,84.09,0,0,1,128,212Zm66.59-84.36a12,12,0,0,1-16.24,4.93,106.7,106.7,0,0,0-100.7,0A11.83,11.83,0,0,1,72,134a12,12,0,0,1-5.66-22.58,130.61,130.61,0,0,1,123.3,0A12,12,0,0,1,194.59,127.64Zm-16,36a12,12,0,0,1-16.23,5,73,73,0,0,0-68.72,0,12,12,0,0,1-11.28-21.18,97,97,0,0,1,91.28,0A12,12,0,0,1,178.59,163.64Z"],
} as const;

export type BrandName = keyof typeof PATHS;

/** Logotipo de red social. Decorativo salvo que se le pase `title`. */
export function BrandIcon({
  name,
  size = 20,
  title,
  ...rest
}: { name: BrandName; size?: number; title?: string } & Omit<SVGProps<SVGSVGElement>, "name">) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 256 256"
      fill="currentColor"
      role={title ? "img" : undefined}
      aria-hidden={title ? undefined : true}
      focusable="false"
      {...rest}
    >
      {title ? <title>{title}</title> : null}
      {PATHS[name].map((d) => (
        <path key={d} d={d} />
      ))}
    </svg>
  );
}
