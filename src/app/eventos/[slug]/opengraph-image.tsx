import { ImageResponse } from "next/og";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { getEventBySlug } from "@/lib/events";
import { longDate, time } from "@/lib/dates";
import { SITE } from "@/content/site";

export const alt = "Evento en Barullo, Vigo";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/**
 * Imagen de previsualización por evento.
 *
 * Es la pieza con más retorno de toda la web: cuando alguien pega el enlace de
 * una fiesta en WhatsApp o en una story, esto es lo que ve el grupo entero.
 * Ninguno de los clubes que miramos como referencia lo genera por evento.
 */

async function loadFont() {
  // Satori necesita el binario de la fuente, y no entiende woff2. Se resuelve
  // la URL del .ttf contra la API de Google en lugar de fijarla a pelo: así no
  // se rompe cuando Google sube la versión de la familia.
  try {
    const css = await fetch("https://fonts.googleapis.com/css2?family=Syne:wght@800", {
      headers: { "User-Agent": "Mozilla/4.0" }, // UA antiguo => devuelve ttf
    }).then((r) => r.text());

    const url = css.match(/https:\/\/fonts\.gstatic\.com\/[^)]+\.ttf/)?.[0];
    if (!url) return null;

    const res = await fetch(url);
    return res.ok ? res.arrayBuffer() : null;
  } catch {
    // Sin fuente la imagen sigue generándose con la de sistema: peor, no rota.
    return null;
  }
}

/** El cartel se lee del disco: evita depender de que el dominio esté vivo. */
async function loadFlyer(src: string) {
  try {
    const file = await readFile(path.join(process.cwd(), "public", src));
    return `data:image/jpeg;base64,${file.toString("base64")}`;
  } catch {
    return null;
  }
}

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const event = await getEventBySlug(slug);

  if (!event) {
    return new ImageResponse(
      (
        <div
          style={{
            width: "100%",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "#0b0410",
            color: "#fff1f7",
            fontSize: 90,
            fontWeight: 800,
          }}
        >
          BARULLO
        </div>
      ),
      size,
    );
  }

  const [font, flyer] = await Promise.all([loadFont(), loadFlyer(event.flyer.src)]);
  const headliners = event.lineup.filter((a) => a.isHeadliner).map((a) => a.name);
  const names = (headliners.length ? headliners : event.lineup.map((a) => a.name)).join(" · ");

  // Satori falla si un div tiene más de un hijo sin `display` explícito, así
  // que las líneas compuestas se montan aquí y bajan como una sola cadena.
  const meta = [
    `${time(event.date)} · ${event.room}`,
    event.priceFrom ? `desde ${event.priceFrom} €` : null,
  ]
    .filter(Boolean)
    .join(" · ");
  const wordmark = `Barullo · ${SITE.city}`;
  // En español sólo va en mayúscula la primera letra, no cada palabra: por eso
  // se capitaliza aquí y no con `textTransform: capitalize`.
  const fecha = longDate(event.date);
  const fechaLarga = fecha.charAt(0).toUpperCase() + fecha.slice(1);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          background: "#0b0410",
          color: "#fff1f7",
          fontFamily: font ? "Syne" : "sans-serif",
        }}
      >
        {/* Mitad izquierda: el cartel tal cual, recortado. */}
        {flyer && (
          <div style={{ display: "flex", width: 470, height: "100%", position: "relative" }}>
            <img
              src={flyer}
              alt=""
              width={470}
              height={630}
              style={{ objectFit: "cover", width: 470, height: 630 }}
            />
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "linear-gradient(90deg, rgba(11,4,16,0) 55%, #0b0410 100%)",
              }}
            />
          </div>
        )}

        {/* Mitad derecha: los datos que deciden si se hace clic. */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            padding: "56px 56px 48px 44px",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div
              style={{
                display: "flex",
                alignSelf: "flex-start",
                background: "#ff4fd8",
                color: "#0b0410",
                borderRadius: 999,
                padding: "8px 20px",
                fontSize: 22,
                fontWeight: 700,
                letterSpacing: 1,
                textTransform: "uppercase",
              }}
            >
              {event.status === "agotado"
                ? "Agotado"
                : event.status === "ultimas"
                  ? "Últimas entradas"
                  : event.status === "gratis"
                    ? "Entrada libre"
                    : "Entradas a la venta"}
            </div>

            <div
              style={{
                marginTop: 28,
                fontSize: event.title.length > 34 ? 44 : event.title.length > 22 ? 52 : 62,
                fontWeight: 800,
                lineHeight: 1.03,
                letterSpacing: -1.5,
              }}
            >
              {event.title}
            </div>

            <div style={{ marginTop: 16, fontSize: 30, color: "#ff4fd8", lineHeight: 1.2 }}>
              {names}
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ fontSize: 23, color: "#b9a8ff" }}>{fechaLarga}</div>
            <div style={{ fontSize: 23, color: "#b9a8ff" }}>
              {meta}
            </div>
            <div
              style={{
                marginTop: 14,
                fontSize: 36,
                fontWeight: 800,
                letterSpacing: -1,
                textTransform: "uppercase",
              }}
            >
              {wordmark}
            </div>
          </div>
        </div>
      </div>
    ),
    {
      ...size,
      fonts: font ? [{ name: "Syne", data: font, style: "normal", weight: 800 }] : undefined,
    },
  );
}
