const { chromium } = require('playwright');
(async () => {
  const b = await chromium.connectOverCDP('http://localhost:9222');
  const ctx = await b.newContext({ viewport:{width:393,height:852}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await ctx.newPage();
  const bytes = {};
  p.on('response', async r => { const u=r.url(); if(/\.(webm|mp4)$/.test(u)){ try{ bytes[u.split('/').pop()] = (await r.body()).length; }catch{} } });
  await p.goto('http://localhost:3000/', { waitUntil:'networkidle', timeout:60000 });
  await p.waitForTimeout(6000);
  const vids = await p.evaluate(()=>[...document.querySelectorAll('video')].map(v=>v.currentSrc.split('/').pop()));
  console.log('videos montados en móvil:', vids);
  console.log('vídeo descargado:', Object.entries(bytes).map(([k,v])=>`${k} ${Math.round(v/1024)} KB`).join(' | ') || 'ninguno');
  await b.close();
})();
