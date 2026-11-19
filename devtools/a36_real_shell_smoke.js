'use strict';
/* A3.6 staging v1395: smoke check the REAL root index.html in headless phone-sized
   Chromium. Guest-only, no authentication; all outbound non-GET requests blocked.
   Never writes production data or declares iPhone hardware acceptance. */
const {chromium}=require('/tmp/fc-a36-shell/node_modules/playwright');
const {spawn}=require('node:child_process');
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const OUT=path.resolve('a36-real-shell-evidence');
fs.mkdirSync(OUT,{recursive:true});
const HOST='http://127.0.0.1:8765';
async function reachable(){
 for(let i=0;i<40;i++){
  const ok=await new Promise(resolve=>{
   const req=http.get(HOST+'/index.html',resp=>{resp.destroy();resolve(resp.statusCode===200)});
   req.on('error',()=>resolve(false));req.setTimeout(1000,()=>{req.destroy();resolve(false)});
  });
  if(ok)return;
  await new Promise(r=>setTimeout(r,150));
 }
 throw new Error('Local staging app server did not start');
}
function isVisible(el){
 const cs=getComputedStyle(el),r=el.getBoundingClientRect();
 return cs.display!=='none'&&cs.visibility!=='hidden'&&Number(cs.opacity)!==0&&r.width>0&&r.height>0;
}
(async()=>{
 const server=spawn('python3',['-m','http.server','8765','--bind','127.0.0.1'],{stdio:'ignore'});
 let browser;
 try{
  await reachable();
  browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-dev-shm-usage']});
  const summary=[];
  for(const width of [375,390,430]){
   const context=await browser.newContext({viewport:{width,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
   const page=await context.newPage();
   const errors=[],rejectedWrites=[],blockedBackends=[];
   page.on('pageerror',e=>errors.push(String(e.message).slice(0,260)));
   await page.route('**/*',route=>{
    const req=route.request(),url=req.url();
    if(url.startsWith(HOST))return route.continue();
    if(req.method()!=='GET'){
     rejectedWrites.push(req.method()+' '+new URL(url).hostname);
     return route.fulfill({status:204,body:''});
    }
    // Block live Supabase data even when current index points at production.
    if(/supabase\.co|supabase\.in/.test(url)){
     blockedBackends.push('GET '+new URL(url).pathname.slice(0,80));
     return route.fulfill({status:200,contentType:'application/json',body:'[]'});
    }
    if(['media','image'].includes(req.resourceType()))return route.abort();
    return route.continue();
   });
   await page.goto(HOST+'/index.html',{waitUntil:'domcontentloaded',timeout:45000});
   await page.waitForTimeout(1700);
   const status=await page.evaluate((visFn)=>{
     const isVisible=eval('('+visFn+')');
     const visible=[...document.querySelectorAll('button,a,h1,h2,h3,[role="dialog"]')]
       .filter(isVisible).map(e=>(e.innerText||e.getAttribute('aria-label')||'').trim()).filter(Boolean).slice(0,18);
     return {build:document.querySelector('meta[name="fc-build"]')?.content||null,
       htmlWidth:document.documentElement.scrollWidth,
       viewportWidth:document.documentElement.clientWidth,
       bodyWidth:document.body.getBoundingClientRect().width,
       visibleText:visible,visibleCount:visible.length,
       bodyExists:!!document.body,screenHeight:window.innerHeight};
   },isVisible.toString());
   await page.screenshot({path:path.join(OUT,'root-'+width+'-guest.png'),fullPage:false});
   assert.match(status.build||'',/^v1395\b/,'Expected staged build v1395');
   assert.ok(status.bodyExists&&status.bodyWidth>0,'No app body');
   assert.ok(status.visibleCount>0,'Guest app has no visible controls/text');
   // Interpret any overflow as evidence rather than certifying it without inspection:
   if(status.htmlWidth>status.viewportWidth+1)console.warn('GUEST_OVERFLOW '+width+'px '+(status.htmlWidth-status.viewportWidth)+'px');
   summary.push({width,build:status.build,htmlWidth:status.htmlWidth,viewportWidth:status.viewportWidth,
     visibleCount:status.visibleCount,visibleText:status.visibleText,
     pageErrors:errors,blockedBackendReads:blockedBackends.length,blockedExternalWrites:rejectedWrites.length});
   await context.close();
  }
  fs.writeFileSync(path.join(OUT,'report.json'),JSON.stringify({
    scope:'real staged index guest shell, Chrome emulated mobile',signedIn:false,realIphone:false,
    backendRequestsMocked:true,productionWritesBlocked:true,summary
  },null,2));
  console.log('STAGED_ROOT_GUEST_SUMMARY '+JSON.stringify(summary));
  if(summary.some(s=>s.pageErrors.length))console.warn('GUEST_BOOTSTRAP_ERRORS: See captured summary; backend reads blocked for safety');
  console.log('PASS: staged v1395 root HTML rendered visible guest controls at all phone widths; production writes blocked');
 }finally{
  if(browser)await browser.close();
  server.kill('SIGTERM');
 }
})().catch(e=>{console.error(e);process.exitCode=1;});
