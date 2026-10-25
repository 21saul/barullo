import { ImageResponse } from "next/og";
import { SITE } from "@/content/site";
import { getNextEvent } from "@/lib/events";
import { shortDate } from "@/lib/dates";

export const alt = `${SITE.name} · ${SITE.tagline}`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

/** Previsualización de la home. Incluye la próxima fecha: da un motivo para entrar. */
async function loadFont() {
  try {
    const css = await fetch("https://fonts.googleapis.com/css2?family=Syne:wght@800", {
      headers: { "User-Agent": "Mozilla/4.0" },
    }).then((r) => r.text());
    const url = css.match(/https:\/\/fonts\.gstatic\.com\/[^)]+\.ttf/)?.[0];
    if (!url) return null;
    const res = await fetch(url);
    return res.ok ? res.arrayBuffer() : null;
  } catch {
    return null;
  }
}

export default async function Image() {
  const [font, next] = await Promise.all([loadFont(), getNextEvent()]);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          background: "linear-gradient(135deg, #0b0410 0%, #241038 55%, #4a1060 100%)",
          color: "#fff1f7",
          fontFamily: font ? "Syne" : "sans-serif",
          padding: 64,
        }}
      >
        <div style={{ fontSize: 170, fontWeight: 800, letterSpacing: -6, lineHeight: 1 }}>
          BARULLO
        </div>
        <div style={{ fontSize: 34, color: "#b9a8ff", marginTop: 18, textAlign: "center" }}>
          {SITE.tagline}
        </div>
        {next && (
          <div
            style={{
              display: "flex",
              marginTop: 40,
              background: "#ff4fd8",
              color: "#0b0410",
              borderRadius: 999,
              padding: "14px 32px",
              fontSize: 26,
              fontWeight: 700,
            }}
          >
            {`Próxima noche · ${shortDate(next.date).toUpperCase()} · ${next.title}`}
          </div>
        )}
      </div>
    ),
    {
      ...size,
      fonts: font ? [{ name: "Syne", data: font, style: "normal", weight: 800 }] : undefined,
    },
  );
}
