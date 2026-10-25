const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.connectOverCDP('http://localhost:9222');
  const ctx=await b.newContext({viewport:{width:393,height:852},deviceScaleFactor:2,isMobile:true,hasTouch:true});
  const p=await ctx.newPage();
  await p.goto('http://localhost:3100/',{waitUntil:'networkidle',timeout:60000});
  await p.getByRole('button',{name:/Abrir men/}).click();
  await p.waitForTimeout(600);
  const r=await p.evaluate(()=>{
    const menu=document.getElementById('menu-movil');
    const out={menuScroll:menu.scrollWidth,menuClient:menu.clientWidth,items:[]};
    menu.querySelectorAll('nav a').forEach(a=>{
      const span=a.querySelector('span:nth-of-type(2)');
      out.items.push({t:span.textContent.trim(),spanW:Math.round(span.getBoundingClientRect().width),aW:Math.round(a.getBoundingClientRect().width),overflowRight:Math.round(span.getBoundingClientRect().right)});
    });
    const cta=menu.querySelector('a[href="/entradas"]');
    out.cta={h:Math.round(cta.getBoundingClientRect().height),w:Math.round(cta.getBoundingClientRect().width)};
    return out;
  });
  console.log(JSON.stringify(r,null,1));
  await b.close();
})();
