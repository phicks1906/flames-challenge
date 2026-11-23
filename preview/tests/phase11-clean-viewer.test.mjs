import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const file=resolve(dirname(fileURLToPath(import.meta.url)),'../a36-phase11-clean-viewer.html');
const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
let checks=0;
const ok=(v,m)=>{assert.ok(v,m);checks++};
const eq=(a,b,m)=>{assert.equal(a,b,m);checks++};
try{
 for(const viewport of [{width:393,height:852},{width:320,height:700},{width:844,height:390}]){
  const page=await browser.newPage({viewport,deviceScaleFactor:1,hasTouch:true});
  try{
   const errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded'});
   await page.evaluate(()=>{
    const c=fc7Real();
    if(c.entries.length<2)throw Error('Need real source entries for test');
    // Test-only state: a local choice, never an official ballot or production write.
    c.mediaType='video';
    c.previewPhase='voting';
    openChallenge(c.id);
   });
   await page.waitForSelector('#viewer.show.fc16-clean');
   eq(await page.locator('#viewerPhase').textContent(),'LOCAL VOTING','Local vote clearly distinguished');
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'VOTE','Plain vote label');
   ok((await page.locator('#viewerMeta').textContent()).includes('competitors'),'Correct count in challenge header');
   ok(!(await page.locator('#viewerMeta').textContent()).includes('Preview'),'No redundant preview copy');
   eq((await page.locator('#fc14BallotNote').textContent()).trim(),'RESULTS','Result link without demo clutter');
   for(const id of ['fc11CompetitorDock','fitControl','fc14Playback']){
    eq(await page.locator('#'+id).evaluate(e=>getComputedStyle(e).display),'none',id+' removed from visible chrome');
   }
   eq(await page.locator('#fc16PlaybackFlash').count(),1,'Transient playback acknowledgement present');
   await page.waitForTimeout(300);
   eq(await page.locator('#fc16PlaybackFlash').evaluate(e=>getComputedStyle(e).opacity),'0','Playback icon hidden before tap');
   eq(await page.locator('#viewerDetail .fc15-position').textContent(),'Competitor 1 of 6','Entrant position retained in lower text');
   eq((await page.locator('#nextEntry span').textContent()).trim(),'NEXT →','Text next control replaces overlay arrow icon');
   eq(await page.locator('.fc12-flame-ballot').evaluate(e=>getComputedStyle(e).borderRadius),'13px','Simple rectangular vote button');
   eq(await page.locator('.fc12-flame-ballot').evaluate(e=>getComputedStyle(e,'::before').content),'none','Ornamental polygon frame removed');
   const rectangles=await page.evaluate(()=>{
     const result={};
     for(const id of ['viewerClose','mediaControl','prevEntry','nextEntry','viewerPhase','viewerDetail','fc14BallotNote']){
      const el=byId(id),r=el.getBoundingClientRect();
      result[id]={x:r.x,y:r.y,right:r.right,bottom:r.bottom,w:r.width,h:r.height,hidden:el.hidden};
     }
     const a=document.querySelector('#viewerActions .fc12-flame-ballot').getBoundingClientRect();
     result.vote={x:a.x,y:a.y,right:a.right,bottom:a.bottom,w:a.width,h:a.height};
     return result;
   });
   for(const [id,r] of Object.entries(rectangles)){
     if(r.hidden)continue;
     ok(r.x>=-1&&r.y>=-1&&r.right<=viewport.width+1&&r.bottom<=viewport.height+1,
      id+' inside '+JSON.stringify(viewport)+': '+JSON.stringify(r));
   }
   ok(rectangles.nextEntry.y>=rectangles.vote.bottom-4,'Next button below vote rather than over middle of video');
   ok(rectangles.prevEntry.y>=rectangles.vote.bottom-4,'Previous button below vote');
   await page.evaluate(()=>{
     const video=byId('stageVideo');
     let paused=false;
     Object.defineProperty(video,'paused',{configurable:true,get:()=>paused});
     video.pause=()=>{paused=true;video.dispatchEvent(new Event('pause'))};
     video.play=()=>{paused=false;video.dispatchEvent(new Event('play'));return Promise.resolve()};
     video.muted=true;fc14Sync();
   });
   await page.locator('#stageVideo').click({force:true});
   await page.waitForTimeout(60);
   const pauseState=await page.evaluate(()=>({flash:byId('fc16PlaybackFlash').className,paused:byId('stageVideo').paused,hidden:byId('stageVideo').hidden,playbtn:byId('fc14Playback').dataset.playing}));
   ok(pauseState.flash.includes('show')&&pauseState.flash.includes('paused'),'Pause flashes only on user tap: '+JSON.stringify(pauseState));
   await page.waitForTimeout(800);
   ok(!(await page.locator('#fc16PlaybackFlash').evaluate(e=>e.classList.contains('show'))),'Pause flash disappears');
   await page.locator('#stageVideo').click({force:true});
   await page.waitForTimeout(60);
   ok(await page.locator('#fc16PlaybackFlash').evaluate(e=>e.classList.contains('show')&&!e.classList.contains('paused')),'Tap resumes and flashes play state');
   eq(await page.locator('#mediaControl').getAttribute('aria-label'),'Turn on sound','Sound toggle accessible');
   await page.locator('#mediaControl').click();
   eq(await page.locator('#mediaControl').getAttribute('aria-label'),'Mute video','Sound state changes');
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[0].id);
   await page.locator('#nextEntry').click();
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'CHANGE VOTE','Changing entrant is explicit');
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[1].id);
   ok(await page.evaluate(()=>Object.keys(JSON.parse(localStorage.getItem(fc10Key))).length===1),'Local ballot has only one selection');
   await page.evaluate(()=>{
     const stage=byId('stage');
     const event=(type,x)=>{const touch=new Touch({identifier:1,target:stage,clientX:x,clientY:300});return new TouchEvent(type,{bubbles:true,touches:type==='touchend'?[]:[touch],changedTouches:[touch]})};
     stage.dispatchEvent(event('touchstart',65));
     stage.dispatchEvent(event('touchend',300));
   });
   eq(await page.evaluate(()=>currentEntry),0,'Horizontal swipe navigates back');
   await page.screenshot({path:'phase11-'+viewport.width+'x'+viewport.height+'.png'});
   await page.locator('#viewerClose').click();
   eq(await page.locator('#viewer.show').count(),0,'Close exits viewer');
   eq(await page.locator('body.modal-open').count(),0,'Close restores scroll');
   eq(errors.length,0,'No page errors: '+errors.join(' | '));
  }finally{await page.close()}
 }
 console.log('PASS '+checks+' Phase 11 viewer assertions across portrait, narrow and landscape.');
}finally{await browser.close()}
