const { chromium } = require('playwright');
const SP='/tmp/claude-1000/-home-ddev-www-barullo/f45e6cc5-3753-4078-b9a7-66b6c83f0e3e/scratchpad';
(async()=>{
  const b=await chromium.connectOverCDP('http://localhost:9222');
  const ctx=await b.newContext({viewport:{width:393,height:852},deviceScaleFactor:4,isMobile:true,hasTouch:true});
  const p=await ctx.newPage();
  await p.goto('http://localhost:3100/entradas',{waitUntil:'networkidle',timeout:60000});
  await p.waitForTimeout(600);
  const li=p.locator('ol > li').first();
  await li.scrollIntoViewIfNeeded(); await p.waitForTimeout(400);
  const box=await li.boundingBox();
  await p.screenshot({path:SP+'/paso.png',clip:{x:box.x,y:box.y,width:box.width,height:90}});
  console.log('ok');
  await b.close();
})();
