const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const url = process.argv[2] || 'http://localhost:3000/';
  const out = process.argv[3] || '/tmp/shot';
  // iPhone 14 Pro
  const m = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await m.newPage();
  const errs=[]; p.on('console',c=>{if(c.type()==='error')errs.push(c.text())}); p.on('pageerror',e=>errs.push(String(e)));
  await p.goto(url,{waitUntil:'networkidle',timeout:60000});
  await p.waitForTimeout(1200);
  await p.screenshot({path:out+'-movil.jpg',fullPage:true,quality:72,type:'jpeg'});
  await p.screenshot({path:out+'-movil-fold.jpg',quality:80,type:'jpeg'});
  const d = await b.newContext({ viewport:{width:1440,height:900}, deviceScaleFactor:1 });
  const p2 = await d.newPage();
  await p2.goto(url,{waitUntil:'networkidle',timeout:60000});
  await p2.waitForTimeout(1200);
  await p2.screenshot({path:out+'-desktop.jpg',quality:72,type:'jpeg'});
  await b.close();
  if(errs.length) console.log('ERRORES CONSOLA:\n'+errs.slice(0,10).join('\n')); else console.log('sin errores de consola');
})();
