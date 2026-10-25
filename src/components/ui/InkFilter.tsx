/**
 * Filtros de tinta. Se montan UNA vez en el layout, no por titular.
 *
 * Por qué existen: la referencia (guías de Indigo, Sparks Edition) no cambia
 * de tipografía para los titulares, cambia la tinta: el mismo grotesco neutro
 * pasa de carcomido a mancha según el peso. Eso aquí es un filtro SVG sobre
 * texto de verdad —sigue siendo seleccionable, buscable y legible por un
 * lector de pantalla—, no una imagen.
 *
 * Tres grados:
 *   #ink-light   sólo el borde, mordido
 *   #ink-medium  borde mordido + neblina de tinta alrededor
 *   #ink-heavy   la mancha empieza a comerse la letra (carteles, no interfaz)
 *
 * CUIDADO: `filter: url(#id)` apuntando a un filtro que no existe no se
 * ignora, **oculta el elemento**. Estos defs tienen que estar siempre en el
 * árbol: por eso van en el layout raíz y no en la página que los usa.
 */

/**
 * Un grado de tinta.
 *
 * La cadena son dos capas:
 *
 *  1. EL NÚCLEO. `feTurbulence` + `feDisplacementMap` empujan el contorno con
 *     ruido: ahí sale el borde mordido, como de sello mal entintado. `bite`
 *     es cuántos píxeles se mueve el borde.
 *  2. LA NEBLINA. Una copia desenfocada del texto recortada (`operator="in"`)
 *     por una máscara de ruido. Sin el recorte sería una sombra; con él es
 *     polvo de tinta. `haze` es el radio y `dust` la frecuencia del grano.
 *
 * La neblina va DEBAJO del núcleo en el `feMerge`: la letra tiene que quedar
 * nítida por dentro o deja de leerse.
 */
function Ink({
  id,
  bite,
  haze,
  dust,
  cut,
}: {
  id: string;
  bite: number;
  haze: number;
  dust: number;
  /** Cuánta neblina sobrevive. Más alto = menos polvo y más limpio. */
  cut: number;
}) {
  return (
    <filter
      id={id}
      x="-25%"
      y="-25%"
      width="150%"
      height="150%"
      colorInterpolationFilters="sRGB"
    >
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" seed="11" result="n" />
      <feDisplacementMap
        in="SourceGraphic"
        in2="n"
        scale={bite}
        xChannelSelector="R"
        yChannelSelector="G"
        result="core"
      />

      <feTurbulence type="fractalNoise" baseFrequency={dust} numOctaves="2" seed="4" result="g" />
      <feColorMatrix in="g" type="luminanceToAlpha" result="gA" />
      <feComponentTransfer in="gA" result="mask">
        <feFuncA type="linear" slope="2.4" intercept={-cut} />
      </feComponentTransfer>
      <feGaussianBlur in="SourceGraphic" stdDeviation={haze} result="halo" />
      <feComposite in="halo" in2="mask" operator="in" result="mist" />

      <feMerge>
        <feMergeNode in="mist" />
        <feMergeNode in="core" />
      </feMerge>
    </filter>
  );
}

export function InkFilter() {
  return (
    <svg
      aria-hidden="true"
      focusable="false"
      // Fuera de la vista pero no `display:none`: un SVG oculto con display
      // none no siempre resuelve las referencias de filtro.
      style={{ position: "absolute", width: 0, height: 0, overflow: "hidden" }}
    >
      <defs>
        <Ink id="ink-light" bite={1.6} haze={1.2} dust={1.6} cut={1.05} />
        <Ink id="ink-medium" bite={2} haze={2.4} dust={1.1} cut={0.95} />
        <Ink id="ink-heavy" bite={2.6} haze={4} dust={0.8} cut={0.8} />
      </defs>
    </svg>
  );
}
