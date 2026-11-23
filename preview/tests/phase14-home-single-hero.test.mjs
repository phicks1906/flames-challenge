import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const file=resolve(dirname(fileURLToPath(import.meta.url)),'../a36-phase14-home-single-hero.html');
const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
let count=0;
const eq=(a,b,m)=>{assert.equal(a,b,m);count++};
const check=(x,m)=>{assert.ok(x,m);count++};
try{
 for(const viewport of [{width:393,height:852},{width:320,height:700},{width:375,height:667},{width:844,height:390}]){
  const page=await browser.newPage({viewport,hasTouch:true,deviceScaleFactor:1});
  try{
   let errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded'});
   await page.waitForSelector('#screen .fc19-home .fc19-watch');
   const home=page.locator('#screen .fc19-home');
   eq(await home.locator('.fc19-head h1').count(),1,'One main title on Home');
   eq(await home.locator('.fc19-head h1').textContent(),'Coolest video','Correct real challenge title');
   eq(await home.getByText('Coolest video',{exact:true}).count(),1,'Challenge title not duplicated on hero');
   eq(await home.locator('.fc19-head p').textContent(),'Must be a video of anything cool (concerts, pet tricks, cars, etc.)','Use original challenge rules');
   eq(await home.locator('.fc19-kicker').getByText('Featured challenge').count(),1,'One featured marker');
   eq(await home.locator('.fc19-category').textContent(),'PHOTOGRAPHY','Use recorded challenge category');
   eq(await home.locator('.fc19-entrant-count').textContent(),'6 competitors','Count displayed once');
   eq(await home.locator('.fc19-stage').count(),1,'One media stage');
   eq(await home.locator('.fc19-stage .hybrid-hit').count(),1,'Media opens challenge');
   eq(await home.locator('.fc19-watch').count(),1,'One primary CTA');
   eq(await home.locator('.fc10-hero-phase').count(),0,'No fake voting phase badge');
   eq(await home.locator('.fc11-featured').count(),0,'No repeated featured label in media');
   eq(await home.getByText(/preview|sample|demo/i).count(),0,'No gratuitous prototype wording in Home');
   check(await home.locator('.fc19-stage video, .fc19-stage img').count()===1,'Real entry media remains visible');
   const state=await page.evaluate(()=>{
    const c=fc10Lead(), h=document.querySelector('.fc19-home'),stage=h.querySelector('.fc19-stage'),cta=h.querySelector('.fc19-watch');
    const media=stage.querySelector('video,img'),nav=document.querySelector('[data-nav="home"]');
    const sr=stage.getBoundingClientRect(),cr=cta.getBoundingClientRect(),nr=nav.getBoundingClientRect();
    return {
     challenge:c.id,selectedEntry:c.entries?.[selectedIndexByChallenge[c.id]||0]?.id,
     ctaAction:cta.dataset.act,mediaAction:stage.querySelector('.hybrid-hit').dataset.act,
     mediaSrc:media?.getAttribute('src'),entryVideo:c.entries?.[0]?.video,
     entryPoster:c.entries?.[0]?.photo,
     stage:{top:sr.top,bottom:sr.bottom,height:sr.height},
     cta:{top:cr.top,bottom:cr.bottom},
     nav:{top:nr.top,bottom:nr.bottom},
     hasFourCards:h.querySelectorAll('.fc19-tile').length<=4,
     otherTitles:[...h.querySelectorAll('.fc19-tile strong')].map(e=>e.textContent),
     appNav:[...document.querySelectorAll('[data-nav]')].map(e=>e.dataset.nav),
    };
   });
   check(state.ctaAction==='open:'+state.challenge&&state.mediaAction===state.ctaAction,'Stage and CTA open same challenge');
   check(!!state.selectedEntry,'Actual approved entry selected');
   check(state.mediaSrc===state.entryVideo||state.mediaSrc===state.entryPoster,'Home media is selected challenge entrant, not unrelated placeholder');
   check(state.stage.height>=(viewport.width>viewport.height?170:220),'Media retains prominent stage');
   check(state.cta.top>=state.stage.bottom-2,'CTA directly follows one stage');
   check(state.hasFourCards,'Keep discovery compact');
   check(new Set(state.otherTitles).size===state.otherTitles.length,'Discovery repeats no identical challenge');
   check(['home','compete','create','titles','you'].every(k=>state.appNav.includes(k)),'Preserve five navigation sections');
   if(viewport.width<500){
    check(state.cta.bottom<=state.nav.top+4,'Primary action visible above tab navigation '+JSON.stringify({viewport,state}));
   }
   await page.screenshot({path:'phase14-home-'+viewport.width+'x'+viewport.height+'.png',fullPage:false});
   await page.locator('.fc19-watch').click();
   await page.waitForSelector('#viewer.show');
   eq(await page.locator('#viewerTitle').textContent(),'Coolest video','CTA opens same challenge in immersive viewer');
   eq(await page.locator('#viewerDetail h2').textContent(),'Rae Hicks','Hero opens matching entry');
   check(await page.locator('#viewer.show.immersive-viewer').count()>0,'Full-screen viewer retained');
   await page.locator('#viewerClose').click();
   eq(await page.locator('#viewer.show').count(),0,'Close restores Home');
   eq(await page.locator('#screen .fc19-home .fc19-watch').count(),1,'Home rehydrated after close');
   await page.locator('.fc19-stage .hybrid-hit').click();
   await page.waitForSelector('#viewer.show');
   eq(await page.locator('#viewerTitle').textContent(),'Coolest video','Media click opens same challenge');
   await page.locator('#viewerClose').click();
   eq(errors.length,0,'No browser exception: '+errors.join('; '));
  }finally{await page.close()}
 }
 console.log('PASS '+count+' Phase 14 Home assertions across four viewports, real media, single title, CTA and full-screen navigation.');
}finally{await browser.close()}
