const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push('JS: '+String(e).slice(0,110)));
  p.on('console', c => { if (c.type()==='error') errs.push('CONSOLA: '+c.text().slice(0,110)); });

  const routes = ['/agenda','/eventos/barullo-sessions-hector-oaks','/entradas','/reservas','/club','/galeria','/eventos-privados','/contacto','/links','/legal/aviso-legal'];
  for (const r of routes) {
    await p.goto('http://localhost:3000'+r, { waitUntil:'networkidle', timeout:60000 });
    await p.waitForTimeout(700);
    const info = await p.evaluate(() => {
      const de = document.documentElement;
      // Elementos que todavía arrastran radios del sistema viejo
      const redondeados = [...document.querySelectorAll('body *')]
        .filter(el => { const r = parseFloat(getComputedStyle(el).borderRadius); return r > 2 && r < 500; }).length;
      // Texto que quedó sin color al desaparecer los tokens viejos
      return { over: de.scrollWidth > de.clientWidth, redondeados, alto: de.scrollHeight };
    });
    const name = r.replace(/\//g,'-').replace(/^-/,'');
    await p.screenshot({ path:`/tmp/qa-${name}.jpg`, fullPage:true, quality:70, type:'jpeg' });
    console.log(`${r.padEnd(40)} ${info.over?'⚠ DESBORDA':'ok'}  radios:${String(info.redondeados).padStart(3)}  alto:${info.alto}`);
  }
  if (errs.length) console.log('\n'+[...new Set(errs)].slice(0,8).join('\n'));
  await b.close();
})();
