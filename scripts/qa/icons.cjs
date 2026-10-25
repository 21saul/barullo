const { chromium } = require('playwright');
const SP='/tmp/claude-1000/-home-ddev-www-barullo/f45e6cc5-3753-4078-b9a7-66b6c83f0e3e/scratchpad';
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:3, isMobile:true, hasTouch:true });
  const p = await ctx.newPage();
  // Pie: iconos de contacto (Lucide) + logos de marca (Phosphor) juntos.
  await p.goto('http://localhost:3100/contacto', { waitUntil:'networkidle', timeout:60000 });
  await p.waitForTimeout(800);
  const h = await p.evaluate(()=>document.body.scrollHeight);
  await p.evaluate((y)=>window.scrollTo(0,y), h);
  await p.waitForTimeout(900);
  await p.screenshot({ path: SP+'/pie.png' });
  // Entradas: la tira de iconos a 20px sobre tarjeta
  await p.goto('http://localhost:3100/entradas', { waitUntil:'networkidle', timeout:60000 });
  await p.waitForTimeout(800);
  await p.screenshot({ path: SP+'/entradas.png', fullPage:false });
  // Menú móvil abierto: flechas + logos
  await p.goto('http://localhost:3100/', { waitUntil:'networkidle', timeout:60000 });
  await p.getByRole('button', { name:/Abrir men/ }).click();
  await p.waitForTimeout(600);
  await p.screenshot({ path: SP+'/menu.png' });
  console.log('ok');
  await b.close();
})();
