import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const filename=resolve(dirname(fileURLToPath(import.meta.url)),'../a36-phase18-visual-stage.html');
const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
const viewports=[{width:393,height:852},{width:320,height:700},{width:375,height:667},{width:844,height:390}];
let n=0;
const eq=(a,b,m)=>{assert.equal(a,b,m);n++};
const check=(v,m)=>{assert.ok(v,m);n++};
try{
 for(const viewport of viewports){
  const page=await browser.newPage({viewport,hasTouch:true,deviceScaleFactor:1});
  try{
   let errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(filename).href,{waitUntil:'domcontentloaded'});
   await page.waitForSelector('#screen .fc21-competition .fc19-watch');
   const home=page.locator('#screen .fc21-competition');
   eq((await home.locator('.fc19-head h1').textContent()).trim(),'Coolest video','Same real challenge');
   eq(await home.locator('.fc19-head h1').count(),1,'Title appears once');
   eq((await home.locator('.fc19-kicker span:first-child').textContent()).trim(),'Result settled','Archive phase shown honestly');
   eq((await home.locator('.fc19-category').textContent()).trim(),'PHOTOGRAPHY · VIDEO','Use actual video format, not mismatched Photography category');
   eq((await home.locator('.fc19-entrant-count').textContent()).trim(),'6 competitors','Real participant count');
   eq((await home.locator('.fc19-head p').textContent()).trim(),'Must be a video of anything cool (concerts, pet tricks, cars, etc.)','Real recorded challenge rule');
   eq((await home.locator('.fc20-cta-text').textContent()).trim(),'Who did it best?','Meaningful action, not passive comparison');
   eq(await home.locator('.fc21-cta-copy small').textContent(),'Watch 6 entries · See winner','Field comparison promise is concrete');
   eq(await home.locator('.fc19-watch').count(),1,'One dominant primary button');
   eq(await home.locator('.fc19-watch .fc12-ballot-icon').count(),1,'Use existing flame voting symbol');
   eq(await home.locator('.fc19-watch').getAttribute('aria-label'),
      'Watch all 6 entries in the settled Coolest video contest, choose a private favorite and see the official result','Honest accessible ballot framing');
   check(!(await home.textContent()).includes('Pick Your Winner'),'Eliminated poll-like CTA wording');
   eq(await home.locator('.fc19-stage > video, .fc19-stage > img').count(),1,'One mapped hero media stage');
   eq(await home.locator('.fc23-entrant-strip .fc23-entrant').count(),6,'All six authentic entries visible together');
   eq(await home.locator('.fc23-entrant[aria-pressed="true"]').count(),1,'Exactly one featured entrant active');
   check(await home.locator('.fc23-stage > video, .fc23-stage > img').first().evaluate(e=>getComputedStyle(e).objectFit==='contain'),'Natural video aspect preserved instead of forced cropped fill');
   eq(await home.locator('.fc23-entrant img').count(),6,'Actual media posters, no generic imagery');
   await home.locator('.fc23-entrant').nth(2).click();
   await page.waitForFunction(()=>selectedIndexByChallenge[fc10Lead().id]===2);
   eq(await page.locator('.fc23-entrant[aria-pressed="true"]').getAttribute('aria-label'),'Preview entry 3 by ehicks23','Preview selection updated');
   await home.locator('.fc23-entrant').first().click();
   await page.waitForFunction(()=>selectedIndexByChallenge[fc10Lead().id]===0);
   eq(await home.locator('.fc19-stage .hybrid-hit').count(),1,'Stage opens same challenge');
   eq(await home.locator('.fc19-entrant-count').count(),1,'Count not duplicated');
   const metrics=await page.evaluate(()=>{
     const h=document.querySelector('.fc21-competition'),c=fc10Lead();
     const call=h.querySelector('.fc19-watch'),stage=h.querySelector('.fc19-stage'),media=stage.querySelector(':scope > video,:scope > img');
     const btn=call.getBoundingClientRect(),st=stage.getBoundingClientRect(),nav=document.querySelector('[data-nav="home"]').getBoundingClientRect();
     const text=call.querySelector('.fc20-cta-text');
     return {id:c.id,count:c.entries.length,authoritativeResolved:!!c.record?.result?.is_public,
      mediaType:c.mediaType,stageAction:stage.querySelector('.hybrid-hit').dataset.act,
      buttonAction:call.dataset.act,mediaSrc:media?.getAttribute('src'),
      entryVideo:c.entries[0].video,entryPhoto:c.entries[0].photo,
      stageBottom:st.bottom,buttonTop:btn.top,buttonBottom:btn.bottom,navTop:nav.top,
      textFits:text.scrollWidth<=text.clientWidth+1,
      buttonWidth:btn.width,buttonHeight:btn.height,
      navs:[...document.querySelectorAll('[data-nav]')].map(e=>e.dataset.nav),
      topMeta:h.querySelector('.fc19-head').innerText};
   });
   check(metrics.id&&metrics.stageAction==='open:'+metrics.id,'Media linked to authoritative contest');
   eq(metrics.buttonAction,metrics.stageAction,'Both entry points use the same competition');
   check(metrics.mediaSrc===metrics.entryVideo||metrics.mediaSrc===metrics.entryPhoto,'Source-backed original media');
   check(metrics.authoritativeResolved,'Existing competition actually has a recorded outcome');
   eq(metrics.mediaType,'video','Metadata means video, independent of category');
   check(metrics.buttonTop>=metrics.stageBottom-2,'Primary action immediately follows media');
   check(metrics.textFits,'CTA label does not clip or wrap');
   check(metrics.buttonHeight>=44,'Accessible tap height');
   if(viewport.width<500)check(metrics.buttonBottom<=metrics.navTop+4,'CTA above bottom navigation');
   check(['home','compete','create','titles','you'].every(k=>metrics.navs.includes(k)),'Preserves five tabs');
   check(await home.locator('.fc19-watch').evaluate(e=>getComputedStyle(e).backgroundImage.includes('gradient')),'Purposeful CTA styling');
   check(await home.locator('.fc23-stage').evaluate(e=>e.scrollWidth<=e.clientWidth+1),'Entry lineup never causes horizontal overflow');
   await page.screenshot({path:'phase18-home-'+viewport.width+'x'+viewport.height+'.png'});
   await home.locator('.fc19-watch').click();
   await page.waitForSelector('#viewer.show.fc18-minimal');
   eq((await page.locator('#viewerTitle').textContent()).trim(),'Coolest video','Same challenge opens in viewer');
   eq((await page.locator('#viewerDetail h2').textContent()).trim(),'Rae Hicks','Correct opening entrant');
   eq((await page.locator('#viewerMeta').textContent()).trim(),'Photography · VIDEO','Viewer reflects the same category and media format');
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'PICK FAVORITE','This is not an official vote');
   check((await page.locator('#viewerHint').textContent()).includes('Official voting is closed'),'Clear settled phase and private favorite distinction');
   eq((await page.locator('#fc18Results').isVisible()),true,'Real recorded outcome accessible');
   await page.locator('#viewerActions .fc12-flame-ballot').click();
   await page.waitForFunction(()=>fc10Choices[fc7ID]===fc7Real().entries[0].id);
   check((await page.locator('#toast').textContent()).includes('Saved in this browser'),'Clear browser-only receipt, not an official vote');
   await page.evaluate(()=>showEntryIndex(1));
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'CHANGE PICK','Different entrant offers a local preference change');
   await page.evaluate(()=>showEntryIndex(0));
   eq((await page.locator('.fc12-ballot-label').textContent()).trim(),'SAVED','Current private favorite is retained');
   await page.locator('#fc18Results').click();
   check((await page.locator('#sheet').textContent()).includes('Official recorded result'),'Official settled outcome visible');
   await page.locator('#sheet button[data-act=closeSheet]').click();
   await page.locator('#viewerClose').click();
   eq(await page.locator('#viewer.show').count(),0,'Viewer closes');
   eq(await page.locator('#screen .fc21-competition').count(),1,'Returns to Home');
   eq(errors.length,0,'No page errors: '+errors.join('; '));
  }finally{await page.close()}
 }
 console.log('PASS '+n+' Phase 18 media and competition staging and Home → personal choice → authoritative outcome assertions on 4 viewports.');
}finally{await browser.close()}
