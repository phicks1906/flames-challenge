'use strict';
// Isolated staging only. Authenticated A3.6 Home -> native video bridge ->
// authoritative vote -> actual X -> Home. Never touches production project.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('/tmp/fc-a36-integrated-auth/node_modules/playwright');
const email=process.env.FC_A36_TEST_EMAIL;
const password=process.env.FC_A36_TEST_PASSWORD;
assert.ok(email&&password,'Missing authorized staging test credentials');
const CH='a3600000-0000-4000-8000-000000000004';
const A='a3610000-0000-4000-8000-000000000006';
const B='a3610000-0000-4000-8000-000000000007';
const ownerA='a6da1fad-1ce0-47d2-83a3-29dffb724f28';
const ownerB='d1650878-3b27-4734-b49b-4456b4a28dc0';
const url='https://phicks1906.github.io/flames-challenge-staging/a36-immersive-integrated-v1400/index.html';
const out='a36-integrated-auth-evidence';fs.mkdirSync(out,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
 const browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-dev-shm-usage']});
 const results=[];
 try{
  for(const width of [375,390,430]){
   const context=await browser.newContext({viewport:{width,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
   const page=await context.newPage();
   const errors=[],production=[];
   page.on('pageerror',err=>errors.push(String(err.message).slice(0,200)));
   await page.route('**/*',route=>{
    const req=route.request(),u=req.url();
    if(u.includes('sioalvawzayfphwzqctq.supabase.co')&&!u.includes('/storage/v1/object/public/')){
     production.push(req.method()+' production request');return route.abort();
    }
    return route.continue();
   });
   const initial=await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
   assert.equal(initial.status(),200);
   await page.waitForFunction(()=>typeof db!=='undefined',null,{timeout:20000});
   const auth=await page.evaluate(async({email,password})=>{
    const {data,error}=await db.auth.signInWithPassword({email,password});
    return error?{error:error.message}:{userId:data?.user?.id};
   },{email,password});
   assert.ok(auth.userId,'Staging sign in failed: '+String(auth.error||'unknown'));
   await page.reload({waitUntil:'domcontentloaded',timeout:45000});
   await page.waitForFunction(id=>typeof state!=='undefined'&&state.profile?.id===id,auth.userId,{timeout:25000});
   // Both designated staging accounts use valid onboarding; never bypass onboarding.
   const appState=await page.evaluate(()=>({
    id:state.profile?.id,
    onboarding:Number(state.profile?.onboarding_version||0),
    interests:state.profile?.interests||[],
    active:state.currentView
   }));
   assert.ok(appState.onboarding>=1103,'Staging account requires real onboarding acceptance before this test');
   if(appState.active!=='feed')await page.evaluate(()=>switchView('feed'));
   await page.locator('#fcHomeV2:not([hidden])').waitFor({state:'visible',timeout:20000});
   await page.locator('#fcHomeV2Switcher [data-a36-entry]').first().waitFor({state:'visible',timeout:20000});
   const choice=auth.userId===ownerA?B:A;
   const spec=choice===A?'hiphop':'salsa';
   await page.locator('#fcHomeV2Switcher [data-a36-entry="'+choice+'"]').click();
   const before=await page.evaluate(()=>{
    const v=document.querySelector('#fcHomeV2Media video');
    return {title:document.querySelector('#fcHomeV2Title')?.textContent,
     video:v?.src,readyState:v?.readyState,showcaseCount:document.querySelectorAll('#fcHomeV2Switcher [data-a36-entry]').length,
     horizontalOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth};
   });
   assert.equal(before.showcaseCount,2);
   assert.ok(before.video?.includes(spec+'.mp4'),'Home not showing selected performance');
   assert.ok(before.horizontalOverflow<=1,'Horizontal overflow');
   await page.screenshot({path:out+'/home-'+width+'.png',fullPage:false});
   await page.locator('#fcHomeV2Arena').click({timeout:12000});
   await page.locator('#entryViewerSheet.open').waitFor({state:'visible',timeout:16000});
   await page.waitForFunction(videoKey=>document.querySelector('#evMedia .fc-a36-v3-media video')?.src.includes(videoKey+'.mp4'),spec,{timeout:12000});
   const viewer=await page.evaluate(()=>({
     challenge:document.getElementById('evChallenge')?.textContent,
     competitor:document.getElementById('evName')?.innerText,
     video:document.querySelector('#evMedia .fc-a36-v3-media video')?.src,
     counter:document.getElementById('evCounter')?.textContent,
     voteText:document.getElementById('evVoteBtn')?.textContent,
     visible:getComputedStyle(document.getElementById('evVoteBtn')).display!=='none'
   }));
   assert.ok(viewer.challenge?.includes('A3.6 Demo'),'Viewer wrong challenge');
   assert.ok(viewer.video.includes(spec+'.mp4'));
   assert.equal(viewer.visible,true,'Native vote action not visible');
   await page.screenshot({path:out+'/viewer-'+width+'.png',fullPage:false});
   // Vote through v1400's native click and upsert. No direct SQL or fabricated counts.
   await page.locator('#evVoteBtn').click({timeout:12000});
   await page.waitForFunction(async({uid,entry})=>{
    const {data,error}=await db.from('entry_votes').select('entry_id')
     .eq('challenge_id','a3600000-0000-4000-8000-000000000004').eq('voter_id',uid).maybeSingle();
    return !error&&data?.entry_id===entry;
   },{uid:auth.userId,entry:choice},{timeout:20000});
   const saved=await page.evaluate(async()=>{
    const {data,error}=await db.from('entry_votes').select('entry_id,voter_id')
     .eq('challenge_id','a3600000-0000-4000-8000-000000000004')
     .eq('voter_id',state.profile.id).maybeSingle();
    return {entry:data?.entry_id,error:error?.message||null,local:state.entryVoteSelectionsV1083 instanceof Map?state.entryVoteSelectionsV1083.get('a3600000-0000-4000-8000-000000000004'):null};
   });
   assert.equal(saved.entry,choice,'Vote not stored in staging');
   assert.equal(saved.local,choice,'Unified local vote selection unsynchronized');
   await page.locator('#entryViewerSheet button[aria-label="Close entry viewer"]').click({timeout:12000});
   await page.waitForFunction(()=>!document.querySelector('#entryViewerSheet')?.classList.contains('open'),null,{timeout:8000});
   assert.equal(await page.locator('#fcHomeV2:not([hidden])').count(),1,'Home did not resume after actual X');
   assert.ok(errors.length===0,'JavaScript errors: '+errors.join(' / '));
   assert.ok(production.length===0,'Production API request attempt');
   await page.screenshot({path:out+'/return-'+width+'.png',fullPage:false});
   results.push({width,backend:'staging',signedIn:true,video:spec,voted:true,returned:true,jsErrors:errors.length,overflow:before.horizontalOverflow});
   await page.evaluate(()=>db.auth.signOut());
   await context.close();
  }
  fs.writeFileSync(out+'/report.json',JSON.stringify({productionChanged:false,physicalIphone:false,tested:'authenticated staging',results},null,2));
  console.log('A36_SIGNED_IN_NATIVE_VOTE_PASS',JSON.stringify(results));
 }finally{await browser.close()}
}
main().catch(e=>{console.error('A36_SIGNED_IN_NATIVE_VOTE_FAIL',e.stack||String(e));process.exitCode=1});
