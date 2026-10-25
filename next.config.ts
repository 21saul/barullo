import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // cacheComponents (el modelo de caché nuevo de Next 16) queda desactivado a
  // propósito: es incompatible con `export const revalidate` por segmento y
  // aquí el ISR por ruta nos da un control más simple para una agenda que
  // cambia poco. Reconsiderar cuando entre un CMS con webhooks.
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  // Para probar `next dev` desde el móvil vía `cloudflared tunnel --url`.
  allowedDevOrigins: ["*.trycloudflare.com"],
  // Barullo es un club: no hay reserva de mesa. Los enlaces viejos (bio de
  // Instagram, Google) acaban en la página para proponer o alquilar una noche.
  async redirects() {
    return [{ source: "/reservas", destination: "/eventos-privados", permanent: true }];
  },
  images: {
    formats: ["image/avif", "image/webp"],
  },
};

export default nextConfig;
