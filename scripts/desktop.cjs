const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:1440,height:900}, deviceScaleFactor:1 });
  const p = await ctx.newPage();
  await p.goto('http://localhost:3000/club', { waitUntil:'networkidle', timeout:60000 });
  await p.waitForTimeout(5000); // el vídeo entra en requestIdleCallback
  await p.screenshot({ path:'/tmp/club-desktop.png' });
  await p.goto('http://localhost:3000/', { waitUntil:'networkidle', timeout:60000 });
  await p.waitForTimeout(5000);
  const nl = p.locator('footer').first();
  await nl.scrollIntoViewIfNeeded();
  await p.waitForTimeout(3000);
  await p.screenshot({ path:'/tmp/newsletter-desktop.png' });
  const vids = await p.evaluate(()=>[...document.querySelectorAll('video')].map(v=>({src:v.currentSrc,playing:!v.paused,w:v.videoWidth})));
  console.log('videos:', JSON.stringify(vids));
  await b.close();
})();
