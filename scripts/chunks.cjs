const http=require('http');
const getText=(p)=>new Promise((res)=>{http.get({host:'localhost',port:3100,path:p},r=>{let s='';r.on('data',c=>s+=c);r.on('end',()=>res(s));});});
const head=(p)=>new Promise((res)=>{http.get({host:'localhost',port:3100,path:p,headers:{'Accept-Encoding':'gzip'}},r=>{let n=0;r.on('data',c=>n+=c.length);r.on('end',()=>res({n,enc:r.headers['content-encoding']||'identity'}));});});
(async()=>{
 const html=await getText('/');
 const srcs=[...new Set([...html.matchAll(/<script[^>]+src="([^"]+)"/g)].map(m=>m[1]))];
 for(const s of srcs){const r=await head(s);console.log(String(Math.round(r.n/1024)).padStart(5)+' KB  '+r.enc.padEnd(10)+s);}
})();
