const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await ctx.newPage();
  await p.goto('http://localhost:3000/', { waitUntil:'networkidle', timeout:60000 });
  await p.waitForTimeout(1200);
  const r = await p.evaluate(() => {
    const vh = window.innerHeight;
    // Sólo el CTA del héroe: el menú móvil oculto tiene otro igual en 0,0.
    const hero = document.querySelector('main section');
    const cta = [...(hero?.querySelectorAll('a') || [])]
      .find(a => /Entradas desde|Comprar entradas|Apuntarme/i.test(a.textContent || '')
                 && a.getBoundingClientRect().height > 0);
    if (!cta) return { error:'no se encontró el CTA' };
    const b = cta.getBoundingClientRect();
    return { vh, top:Math.round(b.top), bottom:Math.round(b.bottom), visible: b.bottom <= vh, texto: cta.textContent.trim().slice(0,40) };
  });
  console.log(JSON.stringify(r));
  await p.screenshot({ path:'/tmp/fold.png' });
  await b.close();
})();
