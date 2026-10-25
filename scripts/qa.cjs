const { chromium } = require('playwright');
// BASE=http://localhost:3100 para medir contra el build de producción.
const BASE = process.env.BASE || 'http://localhost:3000';
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true, hasTouch:true,
    userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
  const p = await ctx.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(String(e))); p.on('console',c=>{if(c.type()==='error')errs.push(c.text())});

  for (const route of (process.argv[2]||'/').split(',')) {
    await p.goto(BASE+route, { waitUntil:'networkidle', timeout:60000 });
    await p.waitForTimeout(900);
    const info = await p.evaluate(() => {
      const de = document.documentElement;
      const over = [...document.querySelectorAll('body *')]
        .filter(el => { const r = el.getBoundingClientRect(); return r.width>0 && (r.right > de.clientWidth + 1 || r.left < -1); })
        .slice(0,6)
        .map(el => `${el.tagName.toLowerCase()}.${(el.className&&el.className.baseVal!==undefined?el.className.baseVal:String(el.className||'')).split(' ').slice(0,3).join('.')} → ${Math.round(el.getBoundingClientRect().left)}..${Math.round(el.getBoundingClientRect().right)}`);
      return { scrollW: de.scrollWidth, clientW: de.clientWidth, over };
    });
    const name = route==='/'?'home':route.replace(/\//g,'-').replace(/^-/,'');
    await p.screenshot({ path:`/tmp/qa-${name}.png`, fullPage:true });
    console.log(`${route}  scrollWidth=${info.scrollW} clientWidth=${info.clientW} ${info.scrollW>info.clientW?'⚠ DESBORDA':'ok'}`);
    info.over.forEach(o=>console.log('     '+o));
  }
  if (errs.length) console.log('\nERRORES JS:\n'+errs.slice(0,6).join('\n'));
  await b.close();
})();
