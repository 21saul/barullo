const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await ctx.newPage();
  await p.goto('http://localhost:3000/', { waitUntil:'networkidle', timeout:60000 });
  await p.waitForTimeout(1500);
  await p.screenshot({ path:'/tmp/fold.png' });
  // Sección de galería
  const gal = p.locator('section', { hasText: 'Cómo se vive' }).first();
  await gal.scrollIntoViewIfNeeded();
  await p.waitForTimeout(800);
  await gal.screenshot({ path:'/tmp/galeria.png' });
  // Contar imágenes rotas
  const broken = await p.evaluate(()=>[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.currentSrc||i.src));
  console.log('imagenes rotas:', broken.length, broken.slice(0,5));
  await b.close();
})();
