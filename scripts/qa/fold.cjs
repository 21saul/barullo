const { chromium } = require('playwright');
const SP='/tmp/claude-1000/-home-ddev-www-barullo/f45e6cc5-3753-4078-b9a7-66b6c83f0e3e/scratchpad';
(async()=>{
  const b=await chromium.connectOverCDP('http://localhost:9222');
  const ctx=await b.newContext({viewport:{width:393,height:852},deviceScaleFactor:3,isMobile:true,hasTouch:true});
  const p=await ctx.newPage();
  await p.goto('http://localhost:3100/',{waitUntil:'networkidle',timeout:60000});
  await p.waitForTimeout(1800);
  await p.screenshot({path:SP+'/fold.png'});
  console.log('ok'); await b.close();
})();
