import { addDays, nextFriday, setHours, setMinutes, startOfDay } from "date-fns";
import type { RamaId } from "./ramas";

export type TicketProvider = "fourvenues" | "dice" | "xceed" | "entradium" | "taquilla";
export type EventStatus = "anunciado" | "ultimas" | "agotado" | "cancelado" | "gratis";
export type EventKind = "club" | "directo" | "showcase";

export interface Artist {
  name: string;
  /** "b2b", "live", "warm up"... se pinta junto al nombre */
  role?: string;
  isHeadliner?: boolean;
  soundcloud?: string;
  instagram?: string;
}

export interface ClubEvent {
  slug: string;
  title: string;
  /** Frase corta de cartel. Sale en la home y en el OG. */
  tagline?: string;
  kind: EventKind;
  /** Inicio real del evento (apertura de puertas) */
  date: Date;
  /** Hora de cierre, para schema.org endDate */
  endDate: Date;
  room: string;
  lineup: Artist[];
  genres: string[];
  flyer: { src: string; alt: string };
  gallery?: string[];
  priceFrom?: number;
  ticketUrl?: string;
  ticketProvider?: TicketProvider;
  status: EventStatus;
  minAge: number;
  /** Párrafos. El primero se usa como meta description si no hay tagline. */
  description: string[];
  featured?: boolean;
  /** Rama de marca. Si no se pone, se deduce de `genres` (ver ramas.ts). */
  rama?: RamaId;
}

// --- Helpers de fechas demo -------------------------------------------------
// Las fechas se calculan desde HOY para que la plantilla nunca se vea caducada.
const base = startOfDay(new Date());
const night = (d: Date, h = 23, m = 59) => setMinutes(setHours(d, h), m);
const friday = (weeksFromNow: number) => addDays(nextFriday(base), weeksFromNow * 7);
const saturday = (weeksFromNow: number) => addDays(friday(weeksFromNow), 1);
const thursday = (weeksFromNow: number) => addDays(friday(weeksFromNow), -1);

/** Nochevieja del año en curso. */
const nye = new Date(base.getFullYear(), 11, 31);

const img = (name: string) => `/media/demo/${name}.jpg`;
/** Fotos de Wikimedia Commons (CC): créditos en /legal/creditos. */
const com = (name: string) => `/media/demo/commons/${name}.jpg`;

/** Fotos reales de cada noche: /public/media/fotos/<fecha>/NN.jpg */
const fotos = (day: string, order: number[]) => order.map((n) => `/media/fotos/${day}/${String(n).padStart(2, "0")}.jpg`);
const range = (n: number) => Array.from({ length: n }, (_, i) => i + 1);
/** Las primeras van delante (portada del álbum); el resto, en orden de la noche. */
const lead = (first: number[], total: number) => [...first, ...range(total).filter((n) => !first.includes(n))];

/** Noche de viernes pasada: puertas 23:59, cierre 05:30. */
const pastNight = (iso: string) => {
  const d = new Date(`${iso}T23:59:00`);
  return { date: d, endDate: night(addDays(startOfDay(d), 1), 5, 30) };
};

const PAST_NIGHTS: ClubEvent[] = [
  {
    slug: "barullo-07-11-2025",
    title: "Barullo 07·11",
    kind: "club",
    ...pastNight("2025-11-07"),
    room: "Kingston Club · Vigo",
    lineup: [{ name: "Barullo Club", isHeadliner: true }],
    genres: ["Urbano", "Club"],
    flyer: { src: "/media/fotos/2025-11-07/01.jpg", alt: "DJ con capucha pinchando bajo el neón de Barullo" },
    gallery: fotos("2025-11-07", lead([2, 1], 8)),
    status: "anunciado",
    minAge: 18,
    description: ["Primera noche de noviembre en Barullo. Capuchas, pared de pavés y el neón encendido toda la noche."],
  },
  {
    slug: "barullo-10-10-2025",
    title: "Barullo 10·10",
    kind: "club",
    ...pastNight("2025-10-10"),
    room: "Kingston Club · Vigo",
    lineup: [{ name: "Barullo Club", isHeadliner: true }],
    genres: ["Urbano", "Club"],
    flyer: { src: "/media/fotos/2025-10-10/03.jpg", alt: "DJ con camiseta roja de Barullo en la cabina" },
    gallery: fotos("2025-10-10", lead([3, 7, 1], 20)),
    status: "anunciado",
    minAge: 18,
    description: ["Fotos de Irene y Adán: cabina, pista y la calle a la salida."],
  },
  {
    slug: "barullo-05-09-2025",
    title: "Barullo 05·09",
    kind: "club",
    ...pastNight("2025-09-05"),
    room: "Kingston Club · Vigo",
    lineup: [{ name: "Barullo Club", isHeadliner: true }],
    genres: ["Urbano", "Club"],
    flyer: { src: "/media/fotos/2025-09-05/03.jpg", alt: "DJ pinchando entre humo con el público alrededor de la cabina" },
    gallery: fotos("2025-09-05", lead([3, 7, 9], 20)),
    status: "anunciado",
    minAge: 18,
    description: ["La vuelta del verano. Fotos de Irene y Adán."],
  },
  {
    slug: "barullo-25-07-2025",
    title: "Barullo 25·07",
    kind: "club",
    ...pastNight("2025-07-25"),
    room: "Kingston Club · Vigo",
    lineup: [{ name: "Barullo Club", isHeadliner: true }],
    genres: ["Urbano", "Club"],
    flyer: { src: "/media/fotos/2025-07-25/01.jpg", alt: "Dos DJs en la cabina bajo el neón de Barullo" },
    gallery: fotos("2025-07-25", range(14)),
    status: "anunciado",
    minAge: 18,
    description: ["Noche de julio con la sala llena, en fotos de cámara compacta."],
  },
  {
    slug: "barullo-18-07-2025",
    title: "Barullo 18·07",
    kind: "club",
    ...pastNight("2025-07-18"),
    room: "Kingston Club · Vigo",
    lineup: [{ name: "Barullo Club", isHeadliner: true }],
    genres: ["Urbano", "Club"],
    flyer: { src: "/media/fotos/2025-07-18/01.jpg", alt: "DJ en la cabina bajo el neón rojo de Barullo" },
    gallery: fotos("2025-07-18", range(22)),
    status: "anunciado",
    minAge: 18,
    description: ["Fotos de Irene. Cabina con alfombra, humo y el neón de Barullo al fondo."],
  },
];

/**
 * DATOS DEMO. Sustituir por contenido real (o por el fetch al CMS en
 * src/lib/events.ts). Las fotos son de Unsplash y de Wikimedia Commons (ver
 * /legal/creditos) y están pensadas para reemplazarse por material del club.
 */
export const EVENTS: ClubEvent[] = [
  {
    slug: "barullo-sessions-hector-oaks",
    title: "Barullo Sessions: Héctor Oaks",
    tagline: "Seis horas de vinilo y nada más.",
    kind: "club",
    date: night(friday(0)),
    endDate: night(addDays(friday(0), 1), 6, 30),
    room: "Sala Principal",
    lineup: [
      { name: "Héctor Oaks", role: "all night long", isHeadliner: true, soundcloud: "https://soundcloud.com/hector-oaks" },
      { name: "Nëro", role: "warm up" },
    ],
    genres: ["Techno", "Hard Groove"],
    flyer: { src: img("nave-techno"), alt: "Nave industrial con luces estroboscópicas y público bailando" },
    priceFrom: 15,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "ultimas",
    minAge: 18,
    description: [
      "Héctor Oaks vuelve a Vigo para una sesión sin relevos: abre a las 00:30 y no suelta los platos hasta el cierre. Solo vinilo, como siempre.",
      "Aforo reducido en Sala Principal. Las entradas anticipadas se agotaron en las dos ediciones anteriores, así que no lo dejes para la puerta.",
    ],
    featured: true,
  },
  {
    slug: "ruido-blanco-live",
    title: "Ruido Blanco · Live",
    tagline: "Directo de electrónica gallega con tres bandas.",
    kind: "directo",
    date: night(saturday(0), 21, 30),
    endDate: night(saturday(0), 3, 0),
    room: "Sala Principal",
    lineup: [
      { name: "Ruido Blanco", role: "live", isHeadliner: true },
      { name: "Marea Baixa", role: "live" },
      { name: "Chavasqueira", role: "dj set" },
    ],
    genres: ["Post-punk", "Electrónica"],
    flyer: { src: img("banda-directo"), alt: "Banda tocando en directo sobre el escenario" },
    priceFrom: 12,
    ticketUrl: "https://dice.fm/",
    ticketProvider: "dice",
    status: "anunciado",
    minAge: 16,
    description: [
      "Noche de directos con tres propuestas de la escena gallega. Puertas a las 21:30, primer pase a las 22:00.",
      "Al acabar los conciertos la sala se reconvierte en club hasta las 03:00 con sesión de Chavasqueira.",
    ],
  },
  {
    slug: "sotano-afrohouse",
    title: "Sótano: Afrohouse",
    tagline: "Amapiano, afrobeat y percusión en directo.",
    kind: "club",
    date: night(thursday(1)),
    endDate: night(addDays(thursday(1), 1), 5, 30),
    room: "Sótano",
    lineup: [
      { name: "Dama Kosi", isHeadliner: true },
      { name: "Lema", role: "b2b" },
      { name: "Tamborada", role: "percusión en vivo" },
    ],
    genres: ["Afrohouse", "Amapiano"],
    flyer: { src: img("multitud-violeta"), alt: "Público bailando bajo luces violetas" },
    priceFrom: 0,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "gratis",
    minAge: 18,
    description: [
      "Los jueves el Sótano cambia de ritmo. Afrohouse, amapiano y afrobeat con percusión en directo sobre la cabina.",
      "Entrada libre hasta la 01:30 apuntándote en lista. Después, 8 € con consumición.",
    ],
  },
  {
    slug: "barullo-x-mondo-takeover",
    title: "Barullo x Mondo · Takeover",
    tagline: "Dos salas, dos clubes, una noche.",
    kind: "club",
    date: night(friday(1)),
    endDate: night(addDays(friday(1), 1), 6, 30),
    room: "Sala Principal + Sótano",
    lineup: [
      { name: "Paula Tape", isHeadliner: true },
      { name: "Oni Ayhun", role: "b2b", isHeadliner: true },
      { name: "Residentes Barullo", role: "sótano" },
    ],
    genres: ["House", "Electro"],
    flyer: { src: img("laseres"), alt: "Lásers de colores sobre una multitud en un club" },
    priceFrom: 18,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "anunciado",
    minAge: 18,
    description: [
      "Intercambio de residentes con Mondo. Ellos traen cabina a la Sala Principal, nosotros abrimos el Sótano con los nuestros.",
      "Dos espacios funcionando en paralelo toda la noche, con acceso libre entre salas.",
    ],
    featured: true,
  },
  {
    slug: "madrugada-dub",
    title: "Madrugada Dub",
    tagline: "Sound system, bajo profundo y humo.",
    kind: "club",
    date: night(saturday(1)),
    endDate: night(addDays(saturday(1), 1), 6, 30),
    room: "Sótano",
    lineup: [
      { name: "Kalakuta Sound", role: "sound system", isHeadliner: true },
      { name: "Selecta Moa" },
    ],
    genres: ["Dub", "Dubstep", "Jungle"],
    flyer: { src: img("humo-manos"), alt: "Persona con los brazos en alto entre humo y luces" },
    priceFrom: 10,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "anunciado",
    minAge: 18,
    description: [
      "Montamos sound system propio en el Sótano. Dub, jungle y todo lo que pida subgraves hasta el cierre.",
    ],
  },
  {
    slug: "showcase-sello-ria",
    title: "Showcase: Sello Ría",
    tagline: "El sello vigués presenta su catálogo al completo.",
    kind: "showcase",
    date: night(friday(2)),
    endDate: night(addDays(friday(2), 1), 6, 0),
    room: "Sala Principal",
    lineup: [
      { name: "Ría Rec.", role: "label showcase", isHeadliner: true },
      { name: "Antela", role: "live" },
      { name: "Cíes", role: "dj set" },
      { name: "Mar de Fóra", role: "dj set" },
    ],
    genres: ["Electro", "Breakbeat"],
    flyer: { src: img("mesa-dj"), alt: "Primer plano de unas manos mezclando en una mesa de DJ" },
    priceFrom: 12,
    ticketUrl: "https://dice.fm/",
    ticketProvider: "dice",
    status: "anunciado",
    minAge: 18,
    description: [
      "Ría Rec. cumple cinco años y lo celebra en casa con todo su roster sobre la cabina.",
    ],
  },
  {
    slug: "nochevieja-barullo",
    title: "Fin de Año en Barullo",
    tagline: "Las dos salas abiertas y los residentes hasta las siete.",
    kind: "club",
    date: night(nye),
    endDate: night(addDays(nye, 1), 7, 0),
    room: "Sala Principal + Sótano",
    lineup: [
      { name: "Residentes Barullo", role: "all night", isHeadliner: true },
      { name: "Invitado por anunciar" },
    ],
    genres: ["House", "Techno", "Hits"],
    flyer: { src: img("confeti-noche"), alt: "Confeti cayendo sobre el público de un concierto nocturno" },
    priceFrom: 25,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "anunciado",
    minAge: 18,
    description: [
      "La noche más larga del año con las dos salas abiertas y los residentes repartidos entre la Sala Principal y el Sótano.",
      "El invitado se anuncia a primeros de diciembre. Las anticipadas tienen precio fijo hasta entonces.",
    ],
    featured: true,
  },
  {
    slug: "residentes-b2b",
    title: "Residentes: B2B",
    tagline: "Los cuatro residentes, por parejas y sin horario.",
    kind: "club",
    date: night(saturday(2)),
    endDate: night(addDays(saturday(2), 1), 6, 30),
    room: "Sala Principal",
    lineup: [
      { name: "Nëro", role: "b2b", isHeadliner: true },
      { name: "Lúa Vidal", role: "b2b", isHeadliner: true },
      { name: "Dama Kosi", role: "b2b" },
      { name: "Selecta Moa", role: "b2b" },
    ],
    genres: ["Techno", "Electro"],
    flyer: { src: com("cabina-10"), alt: "Cabina de DJ con controladora y luces de sala" },
    priceFrom: 10,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "anunciado",
    minAge: 18,
    description: [
      "Una vez al trimestre la cabina es solo de la casa. Los cuatro residentes se emparejan por sorteo y se van turnando hasta el cierre.",
    ],
  },
  {
    slug: "breaks-electro-jueves",
    title: "Jueves de Breaks",
    tagline: "Electro, breakbeat y bajos rotos en el Sótano.",
    kind: "club",
    date: night(thursday(3)),
    endDate: night(addDays(thursday(3), 1), 5, 30),
    room: "Sótano",
    lineup: [
      { name: "Cíes", isHeadliner: true },
      { name: "Antela", role: "live" },
    ],
    genres: ["Breakbeat", "Electro"],
    flyer: { src: com("sala-06"), alt: "Focos de colores y humo sobre la pista" },
    priceFrom: 0,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "gratis",
    minAge: 18,
    description: ["Jueves de entrada libre con lista. Electro y breakbeat de la escena local, con directo de Antela a la 01:00."],
  },
  {
    slug: "lunar-drum-and-bass",
    title: "Lunar · Drum & Bass",
    tagline: "174 bpm hasta que salga el sol.",
    kind: "club",
    date: night(friday(3)),
    endDate: night(addDays(friday(3), 1), 6, 30),
    room: "Sala Principal",
    lineup: [
      { name: "Kessler", isHeadliner: true },
      { name: "Bruma", role: "mc" },
      { name: "Selecta Moa", role: "warm up" },
    ],
    genres: ["Drum & Bass", "Jungle"],
    flyer: { src: com("pista-02"), alt: "Pista a oscuras con un foco azul sobre el público" },
    priceFrom: 14,
    ticketUrl: "https://dice.fm/",
    ticketProvider: "dice",
    status: "anunciado",
    minAge: 18,
    description: ["Lunar trae su noche de drum & bass a Barullo con sistema de sonido reforzado en la Sala Principal."],
  },
  {
    slug: "vinilo-selector",
    title: "Selector: solo vinilo",
    tagline: "Cuatro horas de discos de la colección del invitado.",
    kind: "club",
    date: night(saturday(3)),
    endDate: night(addDays(saturday(3), 1), 5, 0),
    room: "Sótano",
    lineup: [{ name: "Marta Toxo", role: "selector", isHeadliner: true }],
    genres: ["Disco", "House"],
    flyer: { src: com("platos-07"), alt: "Brazo de un tocadiscos sobre un vinilo girando" },
    priceFrom: 8,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "anunciado",
    minAge: 18,
    description: ["Formato íntimo en el Sótano: una sola persona, una maleta de discos y nada de pantallas."],
  },
  {
    slug: "afterwork-terraza-invierno",
    title: "Terraza de invierno",
    tagline: "Sesión de tarde con mantas y estufas.",
    kind: "club",
    date: night(saturday(5), 18, 0),
    endDate: night(saturday(5), 23, 30),
    room: "Terraza",
    lineup: [{ name: "Sunset Crew", isHeadliner: true }, { name: "Lúa Vidal" }],
    genres: ["Balearic", "Disco"],
    flyer: { src: com("platos-01"), alt: "Vinilo de color girando en un tocadiscos" },
    priceFrom: 0,
    ticketUrl: "https://www.fourvenues.com/",
    ticketProvider: "fourvenues",
    status: "gratis",
    minAge: 18,
    description: ["Abrimos la terraza en enero con estufas, mantas y una sesión de tarde para empezar el año despacio."],
  },
  {
    slug: "noche-electronica-gallega",
    title: "Electrónica gallega",
    tagline: "Seis proyectos de aquí, dos salas.",
    kind: "showcase",
    date: night(friday(6)),
    endDate: night(addDays(friday(6), 1), 6, 30),
    room: "Sala Principal + Sótano",
    lineup: [
      { name: "Antela", role: "live", isHeadliner: true },
      { name: "Ruido Blanco", role: "dj set", isHeadliner: true },
      { name: "Mar de Fóra" },
      { name: "Cíes" },
    ],
    genres: ["Electrónica", "Techno"],
    flyer: { src: com("sala-01"), alt: "Escenario con láseres verdes sobre el público" },
    priceFrom: 12,
    ticketUrl: "https://dice.fm/",
    ticketProvider: "dice",
    status: "anunciado",
    minAge: 18,
    description: ["Una noche dedicada a la electrónica hecha en Galicia, con directos en la Sala Principal y DJs en el Sótano."],
  },
  // --- Pasados: noches reales de Barullo con fotos del Drive (MULTIMEDIA/FOTOS) ---
  ...PAST_NIGHTS,
];

