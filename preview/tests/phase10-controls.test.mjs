import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const file=resolve(dirname(fileURLToPath(import.meta.url)),'../a36-phase10-immersive-controls.html');
const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
const viewports=[{width:393,height:852},{width:320,height:700},{width:844,height:390}];
let checks=0;
const check=(v,msg)=>{assert.ok(v,msg);checks++};
const eq=(a,b,msg)=>{assert.equal(a,b,msg);checks++};
try{
 for(const viewport of viewports){
  const page=await browser.newPage({viewport,deviceScaleFactor:1,hasTouch:true});
  try{
   const errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded'});
   await page.evaluate(()=>{
    // Real, settled source is unchanged. This test switches its UI to a local
    // practice phase only, with no production authentication or database write.
    const c=fc7Real();
    if(!c?.entries||c.entries.length<2)throw Error('Need two approved source entries');
    c.previewPhase='voting';
    openChallenge(c.id);
   });
   await page.waitForSelector('#viewer.show.fc14-fidelity');
   eq(await page.locator('#viewerPhase').textContent(),'PRACTICE VOTING','Practicing must not display live voting');
   eq(await page.locator('#viewerActions .fc12-flame-ballot').count(),1,'Flame control must render');
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'PRACTICE VOTE','First ballot is practice');
   check((await page.locator('#fc14BallotNote').textContent()).includes('NO OFFICIAL VOTE'),'Practice disclosure visible');
   check((await page.locator('#viewerDetail .fc15-position').textContent()).includes('1 of'),'Competitor position shown');
   const orig=await page.evaluate(()=>fc7Real().entries[0].id);
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[0].id);
   eq(await page.evaluate(()=>fc10Choices[fc7ID]),orig,'Initial vote saved locally');
   eq(await page.locator('#viewerActions .fc12-flame-ballot').getAttribute('data-state'),'committed','Vote confirmation state visible');
   await page.locator('#nextEntry').click();
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'CHANGE VOTE','Switch must announce replacement');
   check((await page.locator('#viewerHint').textContent()).includes('replaces your previous practice vote'),'Replacement warning');
   check((await page.locator('.fc12-flame-ballot').getAttribute('aria-label')).includes('Replace your previous practice choice'),'Replacement spoken label');
   check((await page.locator('#viewerDetail .fc15-position').textContent()).includes('2 of'),'Next competitor shown');
   const second=await page.evaluate(()=>fc7Real().entries[1].id);
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[1].id);
   eq(await page.evaluate(()=>fc10Choices[fc7ID]),second,'Replacement saved locally');
   check(await page.evaluate(()=>Object.keys(JSON.parse(localStorage.getItem(fc10Key))).length===1),'Exactly one practice choice per challenge');
   await page.locator('#prevEntry').click();
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'CHANGE VOTE','Previous entrant shows replacement, not new ballot');
   await page.evaluate(()=>{
     const v=byId('stageVideo');
     Object.defineProperty(v,'play',{configurable:true,value:()=>Promise.resolve()});
     v.pause();v.muted=true;fc14Sync();
   });
   await page.waitForTimeout(40);
   eq(await page.locator('#mediaControl').getAttribute('aria-label'),'Turn on sound','Mute icon correctly labeled');
   await page.locator('#mediaControl').click();
   await page.waitForTimeout(40);
   eq(await page.locator('#mediaControl').getAttribute('aria-label'),'Mute video','Unmuted icon correctly labeled');
   eq(await page.locator('#mediaControl').getAttribute('aria-pressed'),'true','Sound toggle state accessible');
   await page.locator('#mediaControl').click();
   eq(await page.locator('#mediaControl').getAttribute('aria-label'),'Turn on sound','Mute again works');
   const positions=await page.evaluate(()=>{
     const ids=['viewerClose','fc11CompetitorToggle','fc14Playback','mediaControl','fitControl','nextEntry'];
     const out={};
     for(const id of ids){
       const el=byId(id),r=el.getBoundingClientRect();
       out[id]={x:r.x,y:r.y,right:r.right,bottom:r.bottom,w:r.width,h:r.height,hidden:el.hidden};
     }
     const a=document.querySelector('#viewerActions .fc12-flame-ballot').getBoundingClientRect();
     out.flame={x:a.x,y:a.y,right:a.right,bottom:a.bottom,w:a.width,h:a.height};
     return out;
   });
   for(const [name,r] of Object.entries(positions)){
     if(r.hidden)continue;
     check(r.x>=-1&&r.y>=-1&&r.right<=viewport.width+1&&r.bottom<=viewport.height+1,
       name+' stays in viewport '+JSON.stringify(viewport)+': '+JSON.stringify(r));
   }
   if(viewport.width<500){
    const overlap=(a,b)=>a.x<b.right&&a.right>b.x&&a.y<b.bottom&&a.bottom>b.y;
    check(!overlap(positions.fc11CompetitorToggle,positions.fc14Playback),'Competitor and playback controls do not overlap');
    check(!overlap(positions.fc14Playback,positions.mediaControl),'Playback and sound controls do not overlap');
    check(!overlap(positions.mediaControl,positions.fitControl),'Sound and fit controls do not overlap');
   }
   await page.screenshot({path:'phase10-'+viewport.width+'x'+viewport.height+'.png',fullPage:false});
   await page.locator('#viewerClose').click();
   eq(await page.locator('#viewer.show').count(),0,'Close exits immersive viewer');
   eq(await page.locator('body.modal-open').count(),0,'Close restores scrolling');
   eq(errors.length,0,'No uncaught page exceptions: '+errors.join(' | '));
  } finally{await page.close()}
 }
 console.log('PASS '+checks+' Phase 10 source-backed browser assertions across 3 phone/landscape viewports.');
}finally{await browser.close()}
