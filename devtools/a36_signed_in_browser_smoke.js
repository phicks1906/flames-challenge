'use strict';
// A3.6 signed-in mobile Chromium smoke against ephemeral staging-bound v1395.
// No production APIs and no secrets in screenshots/logs. Not physical iPhone QA.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const {spawn}=require('node:child_process');
const {chromium}=require('/tmp/fc-a36-browser-auth/node_modules/playwright');
const email=process.env.FC_A36_TEST_EMAIL,password=process.env.FC_A36_TEST_PASSWORD;
assert.ok(email&&password,'Private test credentials required');
const origin='http://127.0.0.1:8780';
const out=path.resolve('a36-signed-in-browser-evidence');
fs.mkdirSync(out,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function awaitServer(){
 for(let i=0;i<40;i++){
  const ok=await new Promise(resolve=>{
   const r=http.get(origin+'/index.html',resp=>{resp.destroy();resolve(resp.statusCode===200)});
   r.on('error',()=>resolve(false));
  });
  if(ok)return;
  await sleep(150);
 }
 throw Error('Staging copy local server unavailable');
}
(async()=>{
 const server=spawn('python3',['-m','http.server','8780','--bind','127.0.0.1','--directory','/tmp/fc-a36-staging-browser'],{stdio:'ignore'});
 let browser;
 try{
  await awaitServer();
  browser=await chromium.launch({channel:'chrome',headless:true,args:['--disable-dev-shm-usage']});
  const reports=[];
  for(const width of [375,390,430]){
   const context=await browser.newContext({viewport:{width,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
   const page=await context.newPage();
   const errs=[],rejected=[];
   page.on('pageerror',e=>errs.push(String(e.message).slice(0,220)));
   await page.route('**/*',route=>{
    const req=route.request(),u=req.url();
    if(u.includes('sioalvawzayfphwzqctq.supabase.co')&&!u.includes('/storage/v1/object/public/')){
     rejected.push('blocked production backend');return route.abort();
    }
    return route.continue();
   });
   await page.goto(origin+'/index.html',{waitUntil:'domcontentloaded',timeout:45000});
   await page.waitForTimeout(1200);
   const signIn=await page.evaluate(async({email,password})=>{
    if(typeof db==='undefined'||!db?.auth?.signInWithPassword)return {error:'Supabase client not initialized'};
    const result=await db.auth.signInWithPassword({email,password});
    if(result.error)return {error:String(result.error.message)};
    return {id:result.data?.user?.id||null};
   },{email,password});
   assert.ok(signIn.id,'Real app client sign-in failed: '+String(signIn.error||'unknown'));
   await page.reload({waitUntil:'domcontentloaded',timeout:45000});
   await page.waitForTimeout(1500);
   const state=await page.evaluate(()=>({
    build:document.querySelector('meta[name="fc-build"]')?.content,
    sessionId:(typeof state==='undefined'?null:state.profile?.id||null),
    w:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,
    visibleText:(document.body?.innerText||'').slice(0,1100)
   }));
   await page.screenshot({path:path.join(out,'staging-auth-'+width+'.png'),fullPage:false});
   assert.match(state.build||'',/^v1395\b/,'Wrong app build');
   assert.equal(state.sessionId,signIn.id,'App did not restore signed-in member state');
   assert.ok(state.w<=state.cw+1,'Authenticated app overflows viewport at '+width);
   assert.ok(!rejected.length,'Browser tried to access production API');
   assert.ok(!errs.length,'Browser runtime errors: '+errs.join('; '));
   reports.push({width,authenticated:true,build:state.build,noOverflow:true,jsErrors:0});
   await page.evaluate(async()=>{try{await db.auth.signOut()}catch{}});
   await context.close();
  }
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({type:'authenticated staged v1395 browser smoke',hardwareIphone:false,reports},null,2));
  console.log('PASS A3.6 staged signed-in Chromium: '+reports.map(r=>r.width).join(',')+' px, no runtime errors or viewport overflow');
 }finally{if(browser)await browser.close();server.kill('SIGTERM')}
})().catch(e=>{console.error('A36_BROWSER_AUTH_FAILED '+String(e.message||e).slice(0,450));process.exitCode=1;});
