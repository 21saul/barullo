import type { BrandFormat } from "@/content/brand";

/**
 * Fondos animados de los héroes de cada sección (bocetos/animaciones/heroes).
 *
 * Cada uno tiene dos másteres renderizados por separado, no un recorte del
 * otro: el vertical (9:16) para móvil, con el motivo arriba y sitio abajo
 * para el título, y el apaisado (16:9) para escritorio, con el motivo a la
 * derecha y el título abajo a la izquierda. `focus` es el `object-position`
 * de cada uno: cuando la ventana no tiene la proporción del máster, el
 * recorte sacrifica el lado donde va el texto, nunca el motivo.
 */
export interface HeroBackdrop {
  narrow: BrandFormat & {
    focus?: string;
    fit?: "cover" | "contain";
    /** Máscara CSS (mask-image) para fundir los bordes de un máster que no llena. */
    mask?: string;
    /** Ampliación en móvil (por defecto 1). */
    zoom?: number;
    /**
     * Desplazamiento vertical en móvil (CSS, p. ej. "-18px"). En los teléfonos
     * la caja es más estrecha que 9:16 y el máster entra por altura, así que
     * `focus` no mueve nada en vertical: esto sí.
     */
    shift?: string;
  };
  wide: BrandFormat & { focus?: string; fit?: "cover" | "contain" };
  /** false mientras sólo exista el póster (el render todavía no está). */
  animated: boolean;
}

const loop = (
  name: string,
  focus: { narrow?: string; wide?: string } = {},
  animated = true,
): HeroBackdrop => ({
  animated,
  narrow: {
    webm: `/media/heroes/${name}-narrow.webm`,
    mp4: `/media/heroes/${name}-narrow.mp4`,
    poster: `/media/heroes/${name}-narrow-poster.jpg`,
    focus: focus.narrow,
  },
  wide: {
    webm: `/media/heroes/${name}-wide.webm`,
    mp4: `/media/heroes/${name}-wide.mp4`,
    poster: `/media/heroes/${name}-wide-poster.jpg`,
    focus: focus.wide,
  },
});

/**
 * La alfombra voladora con el logo tejido (bocetos/animaciones/heroes/club).
 * Escritorio: alfombra arriba a la derecha, título abajo a la izquierda.
 * Móvil: la alfombra entera justo encima del título, pegada a él.
 */
export const CLUB_HERO: HeroBackdrop = (() => {
  const h = loop("club", { narrow: "50% 40%", wide: "60% 35%" });
  // que el badge empiece bajo la cenefa inferior, sin tocar el logo tejido
  return { ...h, narrow: { ...h.narrow, shift: "-18px" } };
})();

/** «Te extendemos la alfombra»: un corredor persa que se desenrolla sin fin. */
export const PROPON_HERO: HeroBackdrop = (() => {
  const h = loop("propon", { narrow: "50% 50%", wide: "62% 45%" });
  // en móvil el rollo sube por encima del título; el corredor sigue detrás
  return { ...h, narrow: { ...h.narrow, shift: "-15svh" } };
})();

/** Pulseras de tela tejidas con el kufi, flotando. */
export const ENTRADAS_HERO: HeroBackdrop = (() => {
  const h = loop("entradas", { narrow: "50% 40%", wide: "62% 45%" });
  // la pulsera roja baja hasta el 62 % del máster en parte del bucle: sube
  // para que en todo momento acabe por encima del badge
  return { ...h, narrow: { ...h.narrow, shift: "-16svh" } };
})();

/** El neón de Barullo sobre la pared de pavés del club. */
export const CONTACTO_HERO = loop("contacto", { narrow: "50% 40%", wide: "62% 40%" });
