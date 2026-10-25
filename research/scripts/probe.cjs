// Uso: node probe.cjs out_dir name=url [name=url ...]
// Captura fold móvil + página completa (recortada) y extrae huella técnica.
const { chromium } = require('playwright');
const fs = require('fs');
const [out, ...pairs] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const results = {};
  for (const pair of pairs) {
    const i = pair.indexOf('=');
    const name = pair.slice(0, i), url = pair.slice(i + 1);
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true,
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1' });
    const p = await ctx.newPage();
    const reqs = [];
    p.on('request', r => reqs.push(r.url()));
    try {
      await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await p.waitForTimeout(5000);
      // cerrar banners de cookies comunes
      for (const sel of ['#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll','#CybotCookiebotDialogBodyButtonAccept','#onetrust-accept-btn-handler','button:has-text("Permitir todas")','button:has-text("Aceptar todas las cookies")','button:has-text("ACCETTA TUTTO")','button:has-text("Allow all cookies")','button:has-text("ALLOW ALL COOKIES")','button:has-text("Allow all")', 'button:has-text("Accept")', 'button:has-text("Accept all")', 'button:has-text("Aceptar")', 'button:has-text("Akzeptieren")', 'button:has-text("Agree")', 'button:has-text("OK")']) {
        try { const el = p.locator(sel).first(); if (await el.isVisible({ timeout: 300 })) { await el.click({ timeout: 1000 }); } } catch {}
      }
      await p.waitForTimeout(1200);
      await p.screenshot({ path: `${out}/${name}-fold.jpg`, type: 'jpeg', quality: 60 });
      const info = await p.evaluate(() => {
        const q = s => [...document.querySelectorAll(s)];
        const fonts = new Set();
        q('h1,h2,h3,nav a,button,p,a').slice(0, 300).forEach(el => fonts.add(getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim()));
        const w = window;
        const fw = [];
        if (w.__NEXT_DATA__ || document.querySelector('script[src*="/_next/"]')) fw.push('Next.js');
        if (w.__NUXT__ || document.querySelector('script[src*="/_nuxt/"]')) fw.push('Nuxt');
        if (document.querySelector('[data-reactroot],#root,#__next')) fw.push('React-root');
        if (document.querySelector('[data-v-app],[data-server-rendered]')) fw.push('Vue');
        if (document.querySelector('script[src*="wp-content"],link[href*="wp-content"]')) fw.push('WordPress');
        if (document.querySelector('[data-wf-site]')) fw.push('Webflow');
        if (document.querySelector('script[src*="squarespace"]')) fw.push('Squarespace');
        if (document.querySelector('script[src*="shopify"]')) fw.push('Shopify');
        if (document.querySelector('[class*="svelte-"]')) fw.push('Svelte');
        if (document.querySelector('astro-island,[data-astro-cid]') || document.querySelector('[class*="astro-"]')) fw.push('Astro');
        if (w.gsap) fw.push('GSAP'); if (w.Swiper || document.querySelector('.swiper')) fw.push('Swiper');
        if (w.lenis || document.documentElement.classList.contains('lenis')) fw.push('Lenis');
        if (w.THREE || document.querySelector('canvas')) fw.push('canvas/WebGL?');
        if (document.querySelector('video')) fw.push('video');
        if (w.jQuery) fw.push('jQuery');
        const gen = document.querySelector('meta[name=generator]')?.content;
        const navs = q('header a, nav a').map(a => a.textContent.trim().replace(/\s+/g, ' ')).filter(t => t && t.length < 40);
        const headings = q('h1,h2,h3').map(h => h.textContent.trim().replace(/\s+/g, ' ')).filter(Boolean).slice(0, 30);
        return { title: document.title, gen, fw, fonts: [...fonts].slice(0, 8), navs: [...new Set(navs)].slice(0, 30), headings,
          height: document.documentElement.scrollHeight, imgs: q('img').length, bg: getComputedStyle(document.body).backgroundColor };
      });
      info.thirdParty = [...new Set(reqs.map(u => { try { return new URL(u).hostname; } catch { return ''; } }))].filter(Boolean).slice(0, 40);
      info.fontFiles = [...new Set(reqs.filter(u => /\.(woff2?|ttf|otf)(\?|$)/.test(u)).map(u => u.split('/').pop().split('?')[0]))].slice(0, 12);
      info.libs = [...new Set(reqs.filter(u => /\.js(\?|$)/.test(u)).map(u => u.split('/').pop().split('?')[0]).filter(f => /gsap|swiper|lenis|three|barba|locomotive|splide|flickity|photoswipe|lightgallery|glide|slick|framer|motion|lottie|vimeo|youtube|mux|dice|shotgun|ra\.|fourvenues|xceed|eventbrite|ticket/i.test(f)))];
      // página completa, limitada a 6000px de alto
      const h = Math.min(info.height, 6000);
      await p.setViewportSize({ width: 390, height: 844 });
      await p.screenshot({ path: `${out}/${name}-full.jpg`, type: 'jpeg', quality: 45, fullPage: true, clip: { x: 0, y: 0, width: 390, height: h } }).catch(() => {});
      results[name] = { url, ...info };
      console.log('OK', name, info.title);
    } catch (e) { results[name] = { url, error: String(e).slice(0, 200) }; console.log('FAIL', name, String(e).slice(0, 120)); }
    await ctx.close();
  }
  const f = `${out}/results.json`;
  const prev = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f)) : {};
  fs.writeFileSync(f, JSON.stringify({ ...prev, ...results }, null, 1));
  await b.close();
})();
