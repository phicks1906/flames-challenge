'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('/tmp/fc-a36-follow-browser/node_modules/playwright');
const source=fs.readFileSync('index.html','utf8');
const start=source.indexOf('async function fcA36AttachFollowingEntriesV1391(list, profiles) {');
const end=source.indexOf('\nasync function loadFollowersList() {',start);
assert.ok(start>0&&end>start,'Real Following component missing from staged index.html');
const component=source.slice(start,end);
const html=['<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>',
'*{box-sizing:border-box} :root{--ember:#ff692b;--text:#f5f3f2;--text-muted:#a9a9ad;--surface:#17181b;--border:#393b40;background:#111215;color:var(--text);font-family:-apple-system,Arial,sans-serif}',
'body{margin:0;padding:50px 12px 95px;min-height:100svh}h1{font-size:23px}p{font-size:12px;color:var(--text-muted)}',
'#followingSheet{max-width:500px;margin:auto;border:1px solid var(--border);background:var(--surface);border-radius:17px;overflow:hidden}',
'#followingList>div{display:flex;align-items:center;gap:12px;padding:14px 16px;border-bottom:1px solid var(--border)}',
'#followingList>div>div:first-child{width:44px;height:44px;border-radius:100%;display:grid;place-items:center;background:#323238;flex-shrink:0}',
'#followingList>div>div:nth-child(2){flex:1;min-width:0;font-weight:750;font-size:15px}',
'.light{--text:#202127;--text-muted:#626470;--surface:#fff;--border:#dddee2;background:#f6f6f8}',
'#theme{position:fixed;bottom:18px;left:18px;min-height:44px;background:var(--ember);border:0;border-radius:9px;padding:0 20px}',
'</style></head><body><h1>Following</h1><p>A3.6 actual staging component — sample data</p>',
'<section id="followingSheet" class="open"><div id="followingList"><div><div>A</div><div>Avery</div><div>Following</div></div><div><div>B</div><div>Blake</div><div>Following</div></div></div></section>',
'<p id="result">No entry opened yet</p><button id="theme" type="button">Light</button></body></html>'].join('');
function browserSetup(){
 const state={profile:{id:'fan'},challenges:[],feedEntries:[],myVotes:{pollVote:true}};
 const people=[{id:'followed',name:'Avery'},{id:'other',name:'Blake'}];
 const challenge={id:'challenge-new',title:'New Public Challenge',is_public:true,status:'voting',sd_round:0};
 const opened=[],errors=[];
 let discoveryQueries=0;
 function makeQuery(table){
  const q={
   select(){return q},in(){return q},eq(){return q},order(){return q},limit(){return q},
   maybeSingle(){return Promise.resolve({data:table==='challenges'?challenge:{id:'entry-new',challenge_id:challenge.id,moderation_status:'clear',sd_round:0},error:null})},
   then(ok,bad){
    discoveryQueries++;
    return Promise.resolve({data:[
     {id:'private-entry',user_id:'other',challenge_id:'private',moderation_status:'clear',sd_round:0,created_at:'2026-11-18T12:00:00Z',challenge:{id:'private',is_public:false,status:'voting',title:'Hidden'}},
     {id:'recent-closed',user_id:'other',challenge_id:'closed',moderation_status:'clear',sd_round:0,created_at:'2026-11-18T11:30:00Z',challenge:{id:'closed',title:'Closed Yesterday',is_public:true,status:'closed',sd_round:0}},
    {id:'entry-new',user_id:'followed',challenge_id:'challenge-new',moderation_status:'clear',sd_round:0,created_at:'2026-11-18T11:00:00Z',challenge}
    ],error:null}).then(ok,bad);
   }
  };
  return q;
 }
 const db={from:makeQuery};
 const fcWithTimeoutV1099=async q=>await q;
 const computeChallengeStatus=ch=>ch.status;
 function closeFollowingSheet(){document.getElementById('followingSheet').classList.remove('open')}
 async function openFeedViewer(challengeId,entryId){
  if(!state.challenges.some(c=>c.id===challengeId))throw Error('Not hydrated');
  opened.push([challengeId,entryId]);
  document.getElementById('result').textContent='Opened '+challengeId+' / '+entryId;
 }
 function renderFollowList(list,profiles,competingIds,mode){
  list.innerHTML=profiles.map(p=>'<div><div>'+p.name[0]+'</div><div>'+p.name+(competingIds.has(p.id)?'<div class="competing-label">● Competing now</div>':'')+'</div><div>Following</div></div>').join('');
 }
 function toast(s){errors.push(s)}
 document.getElementById('theme').onclick=()=>{
  const light=document.documentElement.classList.toggle('light');
  document.getElementById('theme').textContent=light?'Dark':'Light';
 };
 Object.assign(window,{state,people,challenge,opened,errors,db,fcWithTimeoutV1099,computeChallengeStatus,closeFollowingSheet,openFeedViewer,toast,renderFollowList});
 Object.defineProperty(window,'discoveryQueries',{get:()=>discoveryQueries});
}
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const out=path.resolve('a36-follow-browser-evidence');fs.mkdirSync(out,{recursive:true});
 try {
  for(const width of [375,390,430]){
   const page=await browser.newPage({viewport:{width,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
   const errs=[];page.on('pageerror',e=>errs.push(String(e)));
   await page.setContent(html);
   await page.addScriptTag({content:'('+browserSetup.toString()+')()'});
   await page.addScriptTag({content:component});
   await page.evaluate(()=>fcA36AttachFollowingEntriesV1391(document.getElementById('followingList'),people));
   await page.locator('.fc-a36-following-entry-v1393').waitFor();
   assert.equal(await page.locator('.fc-a36-following-entry-v1393').count(),1,'Only active public entry should link');
   assert.equal(await page.locator('.competing-label').count(),1,'Only verified eligible competitor has Competing now');
   assert.match(await page.locator('#followingList').innerText(),/Avery[\s\S]*Competing now[\s\S]*Blake/,'Active competitor sorted above recently-closed competitor');
   assert.equal(await page.locator('.fc-a36-following-entry-v1393').innerText(),'View entry · New Public Challenge');
   assert.deepEqual(await page.evaluate(()=>[discoveryQueries,state.feedEntries.length,state.challenges.length]),[1,0,0],'Independent discovery without feed cache');
   assert.equal(await page.locator('#followingList').evaluate(e=>e.scrollWidth<=e.clientWidth+1),true,'No Following overflow');
   await page.screenshot({path:path.join(out,'following-'+width+'-dark.png')});
   await page.locator('#theme').click();
   await page.screenshot({path:path.join(out,'following-'+width+'-light.png')});
   await page.locator('.fc-a36-following-entry-v1393').click();
   assert.equal(await page.locator('#followingSheet').evaluate(e=>e.classList.contains('open')),false);
   assert.deepEqual(await page.evaluate(()=>opened),[['challenge-new','entry-new']]);
   assert.equal(await page.evaluate(()=>state.myVotes.pollVote),true);
   assert.equal(await page.evaluate(()=>errors.length),0);
   assert.deepEqual(errs,[]);
   await page.close();
  }
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({test:'v1393 Following source in browser',type:'mocked Supabase',iphoneHardware:false,liveAuth:false,widths:[375,390,430],result:'pass'},null,2));
  console.log('PASS Following browser: 375/390/430, dark/light, off-feed link, viewer hydration, no overflow or errors');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
