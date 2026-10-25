/**
 * Configuración única del club. Todo lo que cambie con el negocio vive aquí:
 * NAP (nombre/dirección/teléfono) para SEO local, redes, navegación y textos base.
 */
export const SITE = {
  name: "Barullo",
  legalName: "Barullo Club",
  /** Cambiar al dominio real antes de desplegar: afecta a canonical, sitemap y OG. */
  url: "https://barulloclub.com",
  city: "Vigo",
  region: "Pontevedra",
  country: "ES",
  locale: "es-ES",

  tagline: "Fiesta de música urbana y cultura club en Galicia",
  shortDescription:
    "Barullo Club es una fiesta nacida de la música urbana, hecha de forma independiente en Vigo y con Galicia en el horizonte: sonidos nuevos, talento emergente y una pista segura para todo el mundo. Agenda, entradas y fotos de cada noche.",

  // --- NAP: debe coincidir LETRA A LETRA con Google Business Profile ---
  address: {
    street: "Rúa do Areal, 00",
    postalCode: "36201",
    city: "Vigo",
    region: "Pontevedra",
    country: "ES",
  },
  geo: { lat: 42.2374, lng: -8.7196 },
  phone: "+34 986 00 00 00",
  email: "hola@barulloclub.com",
  bookingEmail: "booking@barulloclub.com",
  privateEmail: "eventos@barulloclub.com",

  /** Horario de apertura en formato schema.org */
  openingHours: [
    { days: ["Thursday"], opens: "23:59", closes: "05:30" },
    { days: ["Friday", "Saturday"], opens: "23:59", closes: "06:30" },
  ],
  openingHoursText: "Jue 23:59–05:30 · Vie y Sáb 23:59–06:30",
  capacity: 400,
  minAge: 18,

  socials: {
    instagram: "https://instagram.com/barulloclub",
    tiktok: "https://tiktok.com/@barulloclub",
    soundcloud: "https://soundcloud.com/barulloclub",
    spotify: "https://open.spotify.com/user/barulloclub",
    youtube: "https://youtube.com/@barulloclub",
    ra: "https://ra.co/clubs/00000",
  },

  /** Proveedor de ticketing por defecto. Ver src/content/events.ts */
  defaultTicketProvider: "fourvenues" as const,
} as const;

/**
 * Navegación principal. Barullo es un club, no una discoteca: no hay reserva
 * de mesa ni reservados. Cuatro secciones y punto.
 *
 * `/entradas` NO está aquí a propósito: es el botón de acción de la cabecera.
 */
export const NAV = [
  { href: "/agenda", label: "Agenda" },
  { href: "/club", label: "El club" },
  { href: "/galeria", label: "Galería" },
  { href: "/contacto", label: "Contacto" },
] as const;

export const FOOTER_NAV = {
  Noches: [
    { href: "/agenda", label: "Agenda" },
    { href: "/entradas", label: "Entradas" },
    { href: "/galeria", label: "Galería" },
  ],
  Club: [
    { href: "/club", label: "Sobre Barullo" },
    { href: "/club#manifesto", label: "Manifesto" },
    { href: "/eventos-privados", label: "Propón una noche" },
    { href: "/contacto", label: "Contacto" },
  ],
  Legal: [
    { href: "/legal/admision", label: "Normas de acceso" },
    { href: "/legal/privacidad", label: "Privacidad" },
    { href: "/legal/cookies", label: "Cookies" },
    { href: "/legal/aviso-legal", label: "Aviso legal" },
  ],
} as const;
