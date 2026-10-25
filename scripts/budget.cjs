const http=require('http');
const get=(p)=>new Promise((res,rej)=>{http.get({host:'localhost',port:3100,path:p,headers:{'Accept-Encoding':'gzip','User-Agent':'Mozilla/5.0 (iPhone)'}},r=>{let n=0;r.on('data',c=>n+=c.length);r.on('end',()=>res({n,enc:r.headers['content-encoding']||'none',code:r.statusCode}));}).on('error',rej);});
const getText=(p)=>new Promise((res,rej)=>{http.get({host:'localhost',port:3100,path:p},r=>{let s='';r.on('data',c=>s+=c);r.on('end',()=>res(s));}).on('error',rej);});
(async()=>{
 for(const page of ['/','/agenda','/eventos/barullo-sessions-hector-oaks','/links','/contacto']){
  const html=await getText(page);
  const srcs=[...new Set([...html.matchAll(/<script[^>]+src="([^"]+)"/g)].map(m=>m[1]))];
  const css =[...new Set([...html.matchAll(/<link[^>]+rel="stylesheet"[^>]*href="([^"]+)"/g)].map(m=>m[1]))];
  let js=0; for(const s of srcs){ const r=await get(s); js+=r.n; }
  let cs=0; for(const c of css){ const r=await get(c); cs+=r.n; }
  const doc=await get(page);
  console.log(`${page.padEnd(42)} html ${String(Math.round(doc.n/1024)).padStart(4)} KB | js ${String(Math.round(js/1024)).padStart(4)} KB (${srcs.length}) | css ${String(Math.round(cs/1024)).padStart(3)} KB`);
 }
 console.log('\n(comprimido en origen, que es lo que viaja por la red)');
})();
