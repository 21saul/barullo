/**
 * Genera src/components/ui/Icon.tsx a partir de los SVG de Lucide (ISC).
 *
 * Por qué no se importa `lucide-react` directamente: cada icono sería un
 * componente más en el árbol y, al usarse dentro de `Header` (que es cliente),
 * el paquete entero entra en el bundle. Aquí se copia el trazado en tiempo de
 * build y se emite un SVG plano: cero JS extra por dibujar una flecha.
 *
 * Lucide es de trazo, no macizo: el grosor lo pone `strokeWidth` (ver el
 * componente). Lucide **no trae logotipos de marca** —los quitó en la v1—, así
 * que Instagram, TikTok, SoundCloud y Spotify viven aparte en
 * `src/components/ui/BrandIcon.tsx`.
 *
 * Para regenerar:  npm run icons
 */
const fs = require("fs");
const path = require("path");

const ICONS_DIR = path.join(__dirname, "..", "node_modules/lucide-static/icons");
const OUT = path.join(__dirname, "..", "src/components/ui/Icon.tsx");

// nombre en el proyecto -> fichero de Lucide (sin .svg)
// Se mantiene el vocabulario de Lucide (Chevron, no Caret) para que buscar un
// icono en lucide.dev y usarlo aquí sea la misma palabra.
// Sólo lo que se usa: `Icon` se importa desde `Header`, que es componente de
// cliente, así que cada trazado del MAP viaja al navegador aunque nadie lo
// pinte. Para añadir uno, mételo aquí y ejecuta `npm run icons`.
const MAP = {
  ArrowLeft: "arrow-left",
  ArrowRight: "arrow-right",
  ArrowUpRight: "arrow-up-right",
  ChevronRight: "chevron-right",
  ChevronDown: "chevron-down",
  Check: "check",
  CircleCheck: "circle-check",
  Clock: "clock",
  CreditCard: "credit-card",
  Building: "building-2",
  IdCard: "id-card",
  ListChecks: "list-checks",
  Mail: "mail",
  MapPin: "map-pin",
  Martini: "martini",
  Menu: "menu",
  Music: "music",
  Phone: "phone",
  Ticket: "ticket",
  Users: "users",
  X: "x",
  Sparkles: "sparkles",
  Play: "play",
  Pause: "pause",
  ShieldCheck: "shield-check",
  Images: "images",
  CalendarPlus: "calendar-plus",
  CalendarDays: "calendar-days",
  Disc: "disc-3",
  Headphones: "headphones",
  Camera: "camera",
  ScrollText: "scroll-text",
  DoorOpen: "door-open",
  Send: "send",
  ArrowDown: "arrow-down",
  ChevronLeft: "chevron-left",
  Star: "star",
  Megaphone: "megaphone",
  MessageCircle: "message-circle",
  Maximize: "maximize-2",
  Clock3: "clock-3",
  Sparkle: "sparkle",
};

/** Devuelve el interior del <svg> de Lucide como JSX autocerrado. */
function inner(file) {
  const src = path.join(ICONS_DIR, `${file}.svg`);
  if (!fs.existsSync(src)) throw new Error(`no existe el icono lucide "${file}"`);
  const svg = fs.readFileSync(src, "utf8");
  const body = svg.slice(svg.indexOf(">", svg.indexOf("<svg")) + 1, svg.lastIndexOf("</svg>"));
  const nodes = [...body.matchAll(/<([a-z]+)\s([^>]*?)\/>/g)].map(
    ([, tag, attrs]) => `<${tag} ${attrs.trim()} />`,
  );
  if (!nodes.length) throw new Error(`${file}: sin formas`);
  // Lucide no usa atributos con guion, así que valen tal cual en JSX.
  if (/[a-z]+-[a-z]+=/.test(nodes.join(""))) throw new Error(`${file}: atributo con guion`);
  return nodes.join("");
}

const entries = Object.entries(MAP).map(([name, file]) => `  ${name}: <>${inner(file)}</>,`);

const out = `// GENERADO POR scripts/gen-icons.cjs — no editar a mano.
// Trazados de Lucide (ISC) v${require("lucide-static/package.json").version}.
// Para añadir un icono: busca su nombre en https://lucide.dev, mételo en el MAP
// del script y ejecuta \`npm run icons\`.
import type { ReactNode, SVGProps } from "react";

export type IconName =
${Object.keys(MAP)
  .map((n) => `  | "${n}"`)
  .join("\n")};

const SHAPES: Record<IconName, ReactNode> = {
${entries.join("\n")}
};

/**
 * Icono de Lucide. Es un SVG plano: no monta ningún componente de cliente.
 *
 * \`weight\` es el grosor del trazo. Lucide dibuja a 2 sobre una rejilla de 24;
 * aquí el valor por defecto es 2.25 porque la dirección visual pide un icono
 * con cuerpo, y pasar de ~2.5 empasta las formas pequeñas a 16-20 px.
 *
 * Accesibilidad: por defecto es decorativo (\`aria-hidden\`). Si el icono es la
 * única etiqueta de un control, pásale \`title\` y se anuncia.
 */
export function Icon({
  name,
  size = 20,
  weight = 2.25,
  title,
  ...rest
}: {
  name: IconName;
  size?: number;
  weight?: number;
  title?: string;
} & Omit<SVGProps<SVGSVGElement>, "name">) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={weight}
      strokeLinecap="round"
      strokeLinejoin="round"
      role={title ? "img" : undefined}
      aria-hidden={title ? undefined : true}
      focusable="false"
      {...rest}
    >
      {title ? <title>{title}</title> : null}
      {SHAPES[name]}
    </svg>
  );
}
`;

fs.writeFileSync(OUT, out);
console.log(`ok: ${Object.keys(MAP).length} iconos -> ${path.relative(process.cwd(), OUT)}`);
