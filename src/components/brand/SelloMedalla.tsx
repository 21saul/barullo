import { Stamp } from "@/components/brand/Stamp";
import { RandomMedal } from "@/components/home/RandomMedal";

/**
 * Sello de los formularios: la pegatina dentada color hueso con una de las
 * medallas en el centro, otra en cada recarga.
 *
 * `stamped` es la versión del envío: entra de golpe, como un tampón sobre el
 * papel (animación `sello-golpe` en globals.css), y el texto dice que ha llegado.
 */
export function SelloMedalla({
  id,
  text = "BARULLO · TE LEEMOS · BARULLO · TE LEEMOS · ",
  stamped = false,
  className = "",
}: {
  id: string;
  text?: string;
  stamped?: boolean;
  className?: string;
}) {
  return (
    <div aria-hidden="true" className={`relative ${stamped ? "sello-golpe" : ""} ${className}`}>
      <Stamp id={id} shape="scallop" text={text} bg="var(--color-milk)" fg="var(--color-void)" className="size-full" />
      <RandomMedal className="absolute inset-[20%]" sizes="10rem" />
    </div>
  );
}
