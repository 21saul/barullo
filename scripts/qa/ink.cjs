const { chromium } = require('playwright');
const SP='/tmp/claude-1000/-home-ddev-www-barullo/f45e6cc5-3753-4078-b9a7-66b6c83f0e3e/scratchpad';
(async()=>{
  const b=await chromium.connectOverCDP('http://localhost:9222');
  const ctx=await b.newContext({viewport:{width:393,height:852},deviceScaleFactor:4,isMobile:true,hasTouch:true});
  const p=await ctx.newPage();
  await p.goto('http://localhost:3100/',{waitUntil:'networkidle',timeout:60000});
  await p.waitForTimeout(1500);
  const t=p.locator('.ink').first();
  await t.scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
  const bx=await t.boundingBox();
  await p.screenshot({path:SP+'/ink-hero.png',clip:{x:bx.x-4,y:bx.y-6,width:Math.min(bx.width+8,393),height:bx.height+12}});
  // Un titular de sección con ink-light
  await p.goto('http://localhost:3100/entradas',{waitUntil:'networkidle',timeout:60000});
  await p.waitForTimeout(800);
  const s=p.locator('.ink-light').first();
  await s.scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
  const sb=await s.boundingBox();
  await p.screenshot({path:SP+'/ink-seccion.png',clip:{x:sb.x-4,y:sb.y-6,width:Math.min(sb.width+8,393),height:sb.height+12}});
  console.log('ok'); await b.close();
})();
