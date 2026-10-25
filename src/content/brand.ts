/**
 * Assets animados de marca. Están centralizados aquí porque el héroe de la
 * home va a cambiar: ahora mismo muestra el wordmark, y pasará a mostrar el
 * personaje hyperpop en cuanto esté renderizado. Cambiando `HERO_LOOP` se
 * cambia la home entera, sin tocar componentes.
 */
export interface BrandFormat {
  webm: string;
  mp4: string;
  poster: string;
}

export interface BrandLoop {
  /** Vertical/cuadrado: el que se sirve en móvil. */
  narrow: BrandFormat;
  /** Apaisado: el que se sirve de sm en adelante. */
  wide: BrandFormat;
  /**
   * Proporción del marco, con el salto de móvil a escritorio YA escrito.
   *
   * Tiene que estar aquí como texto literal y no componerse en el componente
   * (`sm:${algo}`): Tailwind genera CSS leyendo el código fuente, y una clase
   * que sólo existe al concatenar cadenas en tiempo de ejecución nunca llega
   * a la hoja de estilos. Eso dejaba el marco en `height: 0` y el héroe
   * invisible hasta que el vídeo cargaba.
   */
  frame: string;
}

export const WORDMARK_LOOP: BrandLoop = {
  narrow: {
    webm: "/media/brand/hero-loop-vertical.webm",
    mp4: "/media/brand/hero-loop-vertical.mp4",
    poster: "/media/brand/hero-poster.jpg",
  },
  wide: {
    webm: "/media/brand/hero-loop-wide.webm",
    mp4: "/media/brand/hero-loop-wide.mp4",
    poster: "/media/brand/hero-poster-wide.jpg",
  },
  frame: "aspect-[2/1] sm:aspect-[21/9]",
};

/**
 * Personaje hyperpop. El máster estrecho se entrega en 3:2 nativo, no en 4:5
 * recortado: recortar un 4:5 a 3:2 tira el 23 % por arriba y otro 23 % por
 * abajo, se pierde media composición y además pesa más.
 */
export const CHARACTER_LOOP: BrandLoop = {
  narrow: {
    webm: "/media/brand/hero-character-v4-3x2.webm",
    mp4: "/media/brand/hero-character-v4-3x2.mp4",
    poster: "/media/brand/hero-character-v4-3x2-poster.jpg",
  },
  wide: {
    webm: "/media/brand/hero-character-v4-wide.webm",
    mp4: "/media/brand/hero-character-v4-wide.mp4",
    poster: "/media/brand/hero-character-v4-wide-poster.jpg",
  },
  // Cuadrado en móvil: el héroe tiene que dominar la pantalla como en
  // Antídoto. Más alto que esto y el botón de entradas se cae del fold.
  frame: "aspect-square sm:aspect-[21/9]",
};

/**
 * Alfombra voladora (Blender, bocetos/animaciones/alfombra/rug): el wordmark tejido en una
 * alfombra persa. El máster estrecho es cuadrado nativo, como el marco móvil.
 */
export const RUG_LOOP: BrandLoop = {
  narrow: {
    webm: "/media/brand/hero-rug-square.webm",
    mp4: "/media/brand/hero-rug-square.mp4",
    poster: "/media/brand/hero-rug-square-poster.jpg",
  },
  wide: {
    webm: "/media/brand/hero-rug-wide.webm",
    mp4: "/media/brand/hero-rug-wide.mp4",
    poster: "/media/brand/hero-rug-wide-poster.jpg",
  },
  frame: "aspect-square sm:aspect-[21/9]",
};

/**
 * Colgante plateado: el pecho de alguien con camiseta de tirantes y el logo
 * de Barullo en un medallón tipo Jäger que rebota al andar (Blender,
 * bocetos/animaciones/colgante). Pensado para el héroe de la home; la alfombra pasa a /club.
 */
export const PENDANT_LOOP: BrandLoop = {
  narrow: {
    webm: "/media/brand/hero-pendant-square.webm",
    mp4: "/media/brand/hero-pendant-square.mp4",
    poster: "/media/brand/hero-pendant-square-poster.jpg",
  },
  wide: {
    webm: "/media/brand/hero-pendant-wide.webm",
    mp4: "/media/brand/hero-pendant-wide.mp4",
    poster: "/media/brand/hero-pendant-wide-poster.jpg",
  },
  frame: "aspect-square sm:aspect-[21/9]",
};

/**
 * Lo que se ve en el héroe de la home: el colgante (2026-10-21, a petición del
 * club). La alfombra sigue en RUG_LOOP y se ve en /club.
 *
 * Los vídeos son el loop definitivo de 7 s (210 fotogramas, bocetos/animaciones/colgante):
 * placa «barullo» de plata sobre cadena cubana. Para rehacerlo, se renderiza
 * y se pasa `node bocetos/animaciones/colgante/encode.mjs`, que escribe los mismos nombres.
 */
export const HERO_LOOP: BrandLoop = PENDANT_LOOP;
