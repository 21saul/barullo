const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true });
  const p = await ctx.newPage();
  await p.goto('http://localhost:3000/', { waitUntil:'networkidle', timeout:60000 });
  await p.waitForTimeout(1000);
  const r = await p.evaluate(() => {
    const out = {};
    const h = document.querySelector('header');
    out.header = h ? { h: Math.round(h.getBoundingClientRect().height), pos: getComputedStyle(h).position } : null;
    const band = [...document.querySelectorAll('div')].find(d => getComputedStyle(d).backgroundColor === 'rgb(255, 47, 208)');
    out.cinta = band ? { top: Math.round(band.getBoundingClientRect().top), h: Math.round(band.getBoundingClientRect().height) } : 'NO ENCONTRADA';
    return out;
  });
  console.log(JSON.stringify(r));
  await b.close();
})();
