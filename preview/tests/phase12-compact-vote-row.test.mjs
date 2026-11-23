import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { dirname,resolve } from 'node:path';
import { fileURLToPath,pathToFileURL } from 'node:url';
const html=resolve(dirname(fileURLToPath(import.meta.url)),'../a36-phase12-compact-vote-row.html');
const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
let assertions=0;
const check=(v,m)=>{assert.ok(v,m);assertions++};
const equal=(a,b,m)=>{assert.equal(a,b,m);assertions++};
try{
 for(const viewport of [{width:393,height:852},{width:320,height:700},{width:375,height:667},{width:844,height:390}]){
  const page=await browser.newPage({viewport,deviceScaleFactor:1,hasTouch:true});
  try{
   const errs=[];page.on('pageerror',e=>errs.push(e.message));
   await page.goto(pathToFileURL(html).href,{waitUntil:'domcontentloaded'});
   await page.evaluate(()=>{
    const c=fc7Real();
    if(!c?.entries||c.entries.length<2)throw Error('Missing approved source');
    c.mediaType='video';c.previewPhase='voting';
    openChallenge(c.id);
   });
   await page.waitForSelector('#viewer.show.fc17-compact');
   equal(await page.locator('#viewerPhase').evaluate(el=>getComputedStyle(el).display),'none','No redundant local-voting badge');
   check((await page.locator('#viewerMeta').textContent()).includes('competitors'),'Header shows field size');
   equal((await page.locator('.fc12-ballot-label').textContent()).trim(),'VOTE','Vote button concise');
   const rect=await page.evaluate(()=>{
     const ids=['viewerDetail','viewerActions','viewerClose','mediaControl','prevEntry','nextEntry','fc14BallotNote'];
     const res={};
     for(const id of ids){
      const e=byId(id),r=e.getBoundingClientRect();
      res[id]={x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height};
     }
     let r=document.querySelector('.fc12-flame-ballot').getBoundingClientRect();
     res.vote={x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height};
     return res;
   });
   check(rect.viewerDetail.right<rect.vote.x+1,'Competitor and vote have separate columns: '+JSON.stringify(rect));
   check(Math.min(rect.viewerDetail.bottom,rect.vote.bottom)-Math.max(rect.viewerDetail.y,rect.vote.y)>18,
     'Competitor info and Vote share a horizontal band: '+JSON.stringify(rect));
   check(rect.vote.right<=viewport.width+1&&rect.vote.x>=0,'Vote fits viewport');
   check(rect.viewerDetail.x>=0&&rect.viewerDetail.width>=120,'Name is not clipped to zero');
   check(rect.vote.y>=rect.viewerClose.bottom-2,'Vote stays away from close');
   check(rect.nextEntry.y>=rect.vote.bottom-4,'Next below primary action');
   check(rect.fc14BallotNote.y>=rect.vote.bottom-4,'Results below primary action');
   equal(await page.locator('#viewerDetail h2').textContent(),'Rae Hicks','Correct competitor name retained');
   await page.screenshot({path:'phase12-'+viewport.width+'x'+viewport.height+'.png'});
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[0].id);
   equal((await page.locator('.fc12-ballot-label').textContent()).trim(),'SAVED','Saving is acknowledged');
   check((await page.locator('#toast').textContent()).includes('Saved in this browser'),'No official vote claim');
   await page.locator('#nextEntry').click();
   equal((await page.locator('.fc12-ballot-label').textContent()).trim(),'CHANGE VOTE','Changing is explicit');
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[1].id);
   check(await page.evaluate(()=>Object.keys(JSON.parse(localStorage.getItem(fc10Key))).length===1),'One local choice per challenge');
   equal(await page.locator('#viewerDetail h2').textContent(),'Izzy','Correct second competitor');
   await page.locator('#prevEntry').click();
   equal(await page.locator('#viewerDetail h2').textContent(),'Rae Hicks','Previous navigates');
   await page.locator('#viewerClose').click();
   equal(await page.locator('#viewer.show').count(),0,'Exit is functional');
   equal(errs.length,0,'No browser runtime errors: '+errs.join(';'));
  }finally{await page.close()}
 }
 console.log('PASS '+assertions+' Phase 12 compact row assertions, 4 viewport sizes, two vote selections, source participants preserved.');
}finally{await browser.close()}
