const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const url = process.argv[2], name = process.argv[3];
  // Móvil
  const m = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true, hasTouch:true,
    userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
  const p = await m.newPage();
  try {
    await p.goto(url, { waitUntil:'domcontentloaded', timeout:60000 });
    await p.waitForTimeout(6000);
    await p.screenshot({ path:`/tmp/ref-${name}-fold.jpg`, quality:78, type:'jpeg' });
    await p.evaluate(()=>window.scrollTo(0, window.innerHeight*0.9));
    await p.waitForTimeout(2500);
    await p.screenshot({ path:`/tmp/ref-${name}-2.jpg`, quality:78, type:'jpeg' });
    console.log(name, 'ok');
  } catch(e){ console.log(name, 'FALLO', e.message.slice(0,90)); }
  await m.close();
  await b.close();
})();
