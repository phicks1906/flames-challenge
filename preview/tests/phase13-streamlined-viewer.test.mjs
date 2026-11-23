import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const file=resolve(dirname(fileURLToPath(import.meta.url)),'../a36-phase13-streamlined-viewer.html');
const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
const widths=[{width:393,height:852},{width:320,height:700},{width:375,height:667},{width:844,height:390}];
let assertions=0;
const check=(v,m)=>{assert.ok(v,m);assertions++};
const eq=(a,b,m)=>{assert.equal(a,b,m);assertions++};
try{
 for(const viewport of widths){
  const page=await browser.newPage({viewport,hasTouch:true,deviceScaleFactor:1});
  try{
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded'});
   await page.evaluate(()=>{
    const c=fc7Real();if(c?.entries?.length!==6)throw Error('Six verified source entries expected');
    c.mediaType='video';c.previewPhase='voting';
    openChallenge(c.id);
   });
   await page.waitForSelector('#viewer.show.fc17-compact.fc18-minimal');
   eq((await page.locator('#viewerMeta').textContent()).trim(),'Photography','No duplicate count in header');
   eq(await page.locator('#viewerPhase').evaluate(e=>getComputedStyle(e).display),'none','Voting chip hidden');
   eq(await page.locator('#fc18Results').isVisible(),true,'Recorded results accessible from header');
   eq(await page.locator('#fc14BallotNote').isVisible(),false,'Duplicate results strip removed');
   eq((await page.locator('.fc15-position').textContent()).trim(),'1 / 6','Compact competitor location');
   eq((await page.locator('.fc18-name-row h2').textContent()).trim(),'Rae Hicks','Competitor name correct');
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'VOTE','Default action remains vote');
   eq((await page.locator('#nextEntry span').textContent()).trim(),'→','Next navigation reduced to arrow');
   eq((await page.locator('#prevEntry span').textContent()).trim(),'←','Previous navigation reduced to arrow');
   const dims=await page.evaluate(()=>{
    const out={};for(const id of ['viewerClose','viewerMeta','fc18Results','viewerDetail','viewerActions','nextEntry','prevEntry']){
     const e=byId(id),r=e.getBoundingClientRect();out[id]={x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height,hidden:e.hidden};}
    for(const sel of ['.fc12-flame-ballot','.fc18-name-row','.fc18-name-row h2','.fc15-position']){
     const r=document.querySelector(sel).getBoundingClientRect();
     out[sel]={x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height};}
    return out;
   });
   const a=dims['.fc12-flame-ballot'],b=dims['.fc18-name-row'];
   check(a.x>=b.right-1,'Name/count and Vote do not overlap: '+JSON.stringify({viewport,a,b}));
   check(a.right<=viewport.width+1&&a.x>=0,'Vote within viewport');
   check(b.width>=105,'Name row remains legible');
   check(Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>13,'Name and vote share the same horizontal band');
   check(dims.nextEntry.y>=a.bottom-3,'Navigation below voting row');
   check(dims.nextEntry.height>=44,'Next touch target');
   check(dims.fc18Results.height>=44,'Results touch target');
   check(dims.fc18Results.right<=viewport.width+1,'Results inside viewport');
   const voteLabel=await page.locator('.fc12-ballot-label').evaluate(e=>({
     whiteSpace:getComputedStyle(e).whiteSpace,
     scrollWidth:e.scrollWidth,
     clientWidth:e.clientWidth
   }));
   eq(voteLabel.whiteSpace,'nowrap','Vote label does not wrap');
   check(voteLabel.scrollWidth<=voteLabel.clientWidth+2,'Vote label fits');
   await page.screenshot({path:'phase13-'+viewport.width+'x'+viewport.height+'.png'});
   await page.locator('#fc18Results').click();
   check(await page.locator('#sheet').isVisible(),'Real recorded result opens');
   check((await page.locator('#sheet').textContent()).includes('Official recorded result'),'Authoritative result panel');
   await page.locator('#sheet button[data-act=closeSheet]').click();
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[0].id);
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'SAVED','Saved state visible');
   await page.locator('#nextEntry').click();
   eq((await page.locator('.fc15-position').textContent()).trim(),'2 / 6','Competitor position updates');
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'CHANGE VOTE','Change vote remains clear');
   eq((await page.locator('.fc18-name-row h2').textContent()).trim(),'Izzy','Second competitor maps correctly');
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[1].id);
   check(await page.evaluate(()=>Object.keys(JSON.parse(localStorage.getItem(fc10Key))).length===1),'Only one saved local choice');
   await page.locator('#prevEntry').click();
   eq((await page.locator('.fc15-position').textContent()).trim(),'1 / 6','Previous remains accessible');
   await page.locator('#viewerClose').click();
   eq(await page.locator('#viewer.show').count(),0,'Close exits viewer');
   eq(errors.length,0,'No page exceptions: '+errors.join(';'));
  } finally {await page.close()}
 }
 console.log('PASS '+assertions+' Phase 13 streamlined viewer assertions on 4 phone/landscape viewports.');
}finally{await browser.close()}
