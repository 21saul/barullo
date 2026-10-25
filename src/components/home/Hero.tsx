import { SITE } from "@/content/site";
import { BrandHero } from "./BrandHero";
import { HERO_LOOP } from "@/content/brand";

/**
 * El héroe es sólo la animación de marca, a sangre, como en Antídoto. La
 * información empieza justo debajo con el carrusel de «Tickets»: así el
 * primer pantallazo es imagen y el segundo ya es la noche que buscas.
 */
export function Hero() {
  return (
    <section className="relative">
      <h1 className="sr-only">
        {SITE.name} · {SITE.tagline}
      </h1>
      <BrandHero loop={HERO_LOOP} alt={`${SITE.name} · ${SITE.tagline}`} />
    </section>
  );
}
