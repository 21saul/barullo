/**
 * Residentes del club. DATOS DEMO: nombres inventados y fotos de manos y
 * cabina (sin caras) de Wikimedia Commons, hasta tener retratos propios.
 */
export interface Resident {
  slug: string;
  name: string;
  /** Lo que pincha, en dos o tres palabras. */
  sound: string;
  since: number;
  photo: { src: string; alt: string };
  bio: string;
  instagram?: string;
  soundcloud?: string;
}

const com = (name: string) => `/media/demo/commons/${name}.jpg`;

export const RESIDENTS: Resident[] = [
  {
    slug: "nero",
    name: "Nëro",
    sound: "Techno y hard groove",
    since: 2019,
    photo: { src: com("platos-03"), alt: "Manos poniendo la aguja sobre un vinilo" },
    bio: "Abre casi todas las noches grandes y sabe leer una pista vacía mejor que nadie. Pincha solo vinilo y guarda los discos rápidos para el final.",
    instagram: "https://instagram.com/",
    soundcloud: "https://soundcloud.com/",
  },
  {
    slug: "lua-vidal",
    name: "Lúa Vidal",
    sound: "House, electro y disco",
    since: 2020,
    photo: { src: com("platos-06"), alt: "Plato Technics con un vinilo girando bajo luz azul" },
    bio: "La residente de los viernes. Mezcla house de Chicago con electro de aquí y es responsable de la mitad de los cierres que la gente recuerda.",
    instagram: "https://instagram.com/",
    soundcloud: "https://soundcloud.com/",
  },
  {
    slug: "dama-kosi",
    name: "Dama Kosi",
    sound: "Afrohouse y amapiano",
    since: 2022,
    photo: { src: com("platos-04"), alt: "Vinilo girando en primer plano con el brazo del tocadiscos" },
    bio: "Lleva los jueves del Sótano. Trae percusionistas a la cabina y convierte una noche entre semana en la más llena del mes.",
    instagram: "https://instagram.com/",
  },
  {
    slug: "selecta-moa",
    name: "Selecta Moa",
    sound: "Dub, jungle y drum & bass",
    since: 2021,
    photo: { src: com("platos-10"), alt: "Cápsula de un tocadiscos sobre un vinilo en movimiento" },
    bio: "Monta el sound system del Sótano pieza a pieza. Si hay subgraves, está ella detrás.",
    soundcloud: "https://soundcloud.com/",
  },
];
