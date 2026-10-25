import type { ClubEvent } from "./events";

/**
 * Ramas de la marca: «un emblema, muchas frecuencias». Cada noche pertenece a
 * una, y la rama le da su color en el chip de la agenda y en la barra de datos.
 * Es el equivalente de las salas de Berghain o de BASEMENT/STUDIO en Basement:
 * permite leer la agenda de reojo por estilo.
 *
 * Fuente de verdad del color: REBRANDING BARULLO/CLAUDE.md §3. Aquí sólo se
 * usan los acentos; el fondo y la tinta de la web no cambian por rama.
 */
export type RamaId = "B/00" | "B/01" | "B/02" | "B/03";

export interface Rama {
  id: RamaId;
  name: string;
  /** Clases del chip: fondo macizo y tinta con contraste AA. */
  chip: string;
  /** Color del filete o del punto. */
  dot: string;
}

export const RAMAS: Record<RamaId, Rama> = {
  "B/00": { id: "B/00", name: "Mix", chip: "bg-acid text-void", dot: "bg-acid" },
  "B/01": { id: "B/01", name: "Techno", chip: "bg-r1 text-void", dot: "bg-r1" },
  "B/02": { id: "B/02", name: "Urbano", chip: "bg-r2 text-milk", dot: "bg-r2" },
  "B/03": { id: "B/03", name: "DnB · Afro", chip: "bg-r3 text-void", dot: "bg-r3" },
};

/** Géneros que deciden la rama. Lo que no encaja en ninguna es MIX. */
const MATCH: [RamaId, RegExp][] = [
  ["B/01", /techno|hard groove|electro|breakbeat|industrial|trance|acid/i],
  ["B/02", /reggaet|trap|dembow|urbano|perreo|hip.?hop|r&b|latin/i],
  ["B/03", /drum|dnb|jungle|dub|afro|amapiano|bass|garage/i],
];

export function ramaOf(event: Pick<ClubEvent, "genres" | "rama">): Rama {
  if (event.rama) return RAMAS[event.rama];
  const genres = event.genres.join(" ");
  for (const [id, re] of MATCH) if (re.test(genres)) return RAMAS[id];
  return RAMAS["B/00"];
}
