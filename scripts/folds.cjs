const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true });
  const p = await ctx.newPage();
  for (const r of process.argv.slice(2)) {
    await p.goto('http://localhost:3000'+r, { waitUntil:'networkidle', timeout:60000 });
    await p.waitForTimeout(900);
    const n = r.replace(/\//g,'-').replace(/^-/,'') || 'home';
    await p.screenshot({ path:`/tmp/fold-${n}.png` });
    console.log(n);
  }
  await b.close();
})();
