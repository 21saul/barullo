import { SITE } from "./site";
import COMMONS from "../../public/media/demo/commons/credits.json";

/**
 * Textos legales. PLANTILLA, no asesoramiento jurídico: antes de publicar hay
 * que completar los datos marcados como [PENDIENTE] y que los revise alguien
 * que sepa. Faltan, como mínimo, razón social real, CIF, domicilio fiscal y
 * datos registrales.
 */
export interface LegalDoc {
  slug: string;
  title: string;
  description: string;
  updated: string;
  sections: { heading: string; body: string[] }[];
}

export const LEGAL_DOCS: LegalDoc[] = [
  {
    slug: "aviso-legal",
    title: "Aviso legal",
    description: `Información legal y condiciones de uso del sitio web de ${SITE.legalName}.`,
    updated: "2026-10-20",
    sections: [
      {
        heading: "Titular del sitio web",
        body: [
          `Denominación social: ${SITE.legalName} [PENDIENTE: razón social completa].`,
          "CIF: [PENDIENTE].",
          `Domicilio: ${SITE.address.street}, ${SITE.address.postalCode} ${SITE.address.city}, ${SITE.address.region}.`,
          `Correo electrónico: ${SITE.email}. Teléfono: ${SITE.phone}.`,
          "Datos registrales: [PENDIENTE: Registro Mercantil, tomo, folio y hoja].",
        ],
      },
      {
        heading: "Objeto",
        body: [
          `Este aviso regula el acceso y uso del sitio ${SITE.url}, propiedad del titular indicado. El acceso implica la aceptación de estas condiciones.`,
          "El titular se reserva el derecho a modificar en cualquier momento la presentación, configuración y contenidos del sitio.",
        ],
      },
      {
        heading: "Condiciones de uso",
        body: [
          "La persona usuaria se compromete a hacer un uso adecuado de los contenidos y a no emplearlos para actividades ilícitas, lesivas de derechos de terceros o que dañen el sitio.",
          "El titular no se responsabiliza del uso que terceros hagan de la información publicada ni de los daños derivados de ese uso.",
        ],
      },
      {
        heading: "Propiedad intelectual e industrial",
        body: [
          "Los contenidos del sitio (textos, fotografías, diseño gráfico, código fuente, logotipos y marcas) son titularidad del club o de terceros que han autorizado su uso.",
          "Queda prohibida su reproducción, distribución o transformación sin autorización expresa y por escrito.",
        ],
      },
      {
        heading: "Enlaces a terceros",
        body: [
          "La venta de entradas se gestiona a través de plataformas externas. Al pulsar en los enlaces de compra se abandona este sitio y se aplican las condiciones y la política de privacidad del proveedor correspondiente.",
          "El titular no controla ni responde del contenido de los sitios enlazados.",
        ],
      },
      {
        heading: "Legislación aplicable",
        body: [
          "Esta relación se rige por la legislación española. Para cualquier controversia, las partes se someten a los juzgados y tribunales de Vigo, salvo que la normativa de consumo establezca otro fuero.",
        ],
      },
    ],
  },
  {
    slug: "privacidad",
    title: "Política de privacidad",
    description: `Cómo trata ${SITE.legalName} los datos personales recogidos a través de la web.`,
    updated: "2026-10-20",
    sections: [
      {
        heading: "Responsable del tratamiento",
        body: [
          `${SITE.legalName} [PENDIENTE: razón social], CIF [PENDIENTE], con domicilio en ${SITE.address.street}, ${SITE.address.postalCode} ${SITE.address.city}.`,
          `Contacto en materia de protección de datos: ${SITE.email}.`,
        ],
      },
      {
        heading: "Qué datos recogemos y para qué",
        body: [
          "Formulario de contacto: nombre, correo, asunto y mensaje, con la finalidad de atender tu consulta. Base jurídica: consentimiento.",
          "Formularios de reserva y eventos privados: nombre, teléfono, correo, fecha, número de personas y detalles del evento, para gestionar la solicitud. Base jurídica: ejecución de un contrato o medidas precontractuales.",
          "Newsletter: correo electrónico, para enviarte información sobre la programación del club. Base jurídica: consentimiento, revocable en cualquier momento.",
          "Navegación: datos técnicos agregados de uso del sitio, con fines estadísticos. Ver la política de cookies.",
        ],
      },
      {
        heading: "Plazo de conservación",
        body: [
          "Los datos se conservan mientras dure la relación y, después, durante los plazos legales de prescripción.",
          "Los datos de la newsletter se conservan hasta que solicites la baja.",
        ],
      },
      {
        heading: "Destinatarios",
        body: [
          "No se ceden datos a terceros salvo obligación legal.",
          "Se utilizan proveedores que actúan como encargados del tratamiento: alojamiento web, plataforma de envío de correos y plataformas de venta de entradas. [PENDIENTE: enumerar los proveedores concretos una vez contratados.]",
        ],
      },
      {
        heading: "Tus derechos",
        body: [
          `Puedes ejercer los derechos de acceso, rectificación, supresión, oposición, limitación y portabilidad escribiendo a ${SITE.email}, acreditando tu identidad.`,
          "Si consideras que el tratamiento no se ajusta a la normativa, puedes reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).",
        ],
      },
    ],
  },
  {
    slug: "cookies",
    title: "Política de cookies",
    description: "Qué cookies utiliza este sitio y cómo puedes gestionarlas.",
    updated: "2026-10-20",
    sections: [
      {
        heading: "Qué son las cookies",
        body: [
          "Las cookies son pequeños archivos que un sitio web guarda en tu dispositivo para recordar información sobre tu visita.",
        ],
      },
      {
        heading: "Cookies que usamos",
        body: [
          "Cookies técnicas: imprescindibles para que el sitio funcione. No requieren consentimiento.",
          "Analítica sin cookies: usamos medición agregada y anónima que no instala cookies ni permite identificarte, por lo que no necesita banner de consentimiento.",
          "Contenido incrustado: el mapa de la página de contacto lo sirve Google Maps, que puede instalar sus propias cookies al cargarse. Se carga de forma diferida y sólo si llegas a esa sección.",
          "[PENDIENTE: si se añade píxel de Meta, Google Ads o cualquier herramienta de marketing, hay que incorporar un banner de consentimiento previo y actualizar esta tabla.]",
        ],
      },
      {
        heading: "Cómo gestionarlas",
        body: [
          "Puedes bloquear o eliminar las cookies desde la configuración de tu navegador. Bloquear las técnicas puede impedir el funcionamiento correcto del sitio.",
        ],
      },
    ],
  },
  {
    slug: "admision",
    title: "Política de admisión",
    description: `Condiciones de acceso al local de ${SITE.legalName} en ${SITE.city}.`,
    updated: "2026-10-20",
    sections: [
      {
        heading: "Edad mínima",
        body: [
          `El acceso está reservado a mayores de ${SITE.minAge} años. Es obligatorio presentar DNI, NIE o pasaporte en vigor; no se admiten fotocopias ni fotografías del documento.`,
          "En conciertos concretos la edad mínima puede ser distinta: siempre se indica en la ficha del evento.",
        ],
      },
      {
        heading: "Derecho de admisión",
        body: [
          "El local se reserva el derecho de admisión conforme a la normativa autonómica vigente en materia de espectáculos públicos y actividades recreativas de Galicia.",
          "Este derecho se ejerce siempre por motivos objetivos y nunca por razón de origen, etnia, sexo, orientación sexual, identidad de género, religión, discapacidad o cualquier otra condición personal o social.",
        ],
      },
      {
        heading: "Motivos de denegación de entrada",
        body: [
          "No se permitirá el acceso a personas en evidente estado de embriaguez o bajo los efectos de sustancias, ni a quienes porten objetos peligrosos.",
          "Tampoco a quienes hayan mostrado previamente conductas violentas, de acoso o de falta de respeto hacia el público o el personal.",
          "El aforo es limitado. Alcanzado el máximo, se detiene el acceso aunque se disponga de entrada.",
        ],
      },
      {
        heading: "Convivencia",
        body: [
          "Barullo es un espacio libre de acoso. Cualquier comportamiento de acoso, agresión o discriminación supone la expulsión inmediata y sin derecho a reembolso.",
          "Si te sientes incómoda o insegura en cualquier momento, dirígete a cualquier persona del equipo: estamos para eso.",
        ],
      },
      {
        heading: "Normas del local",
        body: [
          "No está permitido introducir bebidas ni comida del exterior.",
          "Está prohibido fumar en el interior. La terraza es la zona habilitada.",
          "La grabación profesional de vídeo requiere autorización previa.",
        ],
      },
    ],
  },
  {
    slug: "creditos",
    title: "Créditos de fotos",
    description: "Autoría y licencia de las fotografías de demostración de la web.",
    updated: "2026-10-21",
    sections: [
      {
        heading: "Fotos de demostración",
        body: [
          "Mientras el club no publique su propio material, parte de las fotos de la web son de Unsplash (licencia Unsplash) y de Wikimedia Commons, con las licencias que se indican abajo.",
        ],
      },
      {
        heading: "Wikimedia Commons",
        body: COMMONS.map(
          (c) => `${c.title.replace(/^File:/, "")}. Autoría: ${c.author || "desconocida"}. Licencia: ${c.license}. Fuente: ${c.source}`,
        ),
      },
    ],
  },
];

export const getLegalDoc = (slug: string) => LEGAL_DOCS.find((d) => d.slug === slug) ?? null;
