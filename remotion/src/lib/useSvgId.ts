import { useId } from 'react';

/** useId() de React 19 trae caracteres que rompen `url(#id)` en SVG. */
export const useSvgId = (prefix: string) =>
  `${prefix}-${useId().replace(/[^a-zA-Z0-9]/g, '')}`;
