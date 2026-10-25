/**
 * Genera src/content/photo-sizes.json con el ancho y alto de cada foto de
 * public/media. El visor de la galería (PhotoSwipe) necesita las medidas
 * reales antes de cargar la imagen para animar la apertura sin saltos.
 *
 * Para regenerar después de añadir fotos:  npm run photos
 */
const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const ROOT = path.join(__dirname, "..", "public");
const DIRS = ["media/demo", "media/demo/commons"];
const OUT = path.join(__dirname, "..", "src/content/photo-sizes.json");

(async () => {
  const sizes = {};
  for (const dir of DIRS) {
    for (const f of fs.readdirSync(path.join(ROOT, dir))) {
      if (!/\.(jpe?g|png|webp|avif)$/i.test(f)) continue;
      const { width, height } = await sharp(path.join(ROOT, dir, f)).metadata();
      sizes[`/${dir}/${f}`] = [width, height];
    }
  }
  fs.writeFileSync(OUT, JSON.stringify(sizes, null, 1) + "\n");
  console.log(`ok: ${Object.keys(sizes).length} fotos -> src/content/photo-sizes.json`);
})();
