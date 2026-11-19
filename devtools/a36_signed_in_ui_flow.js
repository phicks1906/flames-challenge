'use strict';
// Real A3.6 UI navigation against an ephemeral staging-bound v1395 browser copy.
// Only the designated staging account is used; no production API access.
// Browser screenshots are artifacts. These are Chromium emulations, not iPhone hardware.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const {spawn}=require('node:child_process');
const {chromium}=require('/tmp/fc-a36-flow/node_modules/playwright');
const email=process.env.FC_A36_TEST_EMAIL;
const password=process.env.FC_A36_TEST_PASSWORD;
assert.ok(email&&password,'Missing private staging test account credentials');
const origin='http://127.0.0.1:8791';
const out=path.resolve('a36-flow-ui-evidence');
fs.mkdirSync(out,{recursive:true});
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function awaitServer(){
 for(let i=0;i<50;i++){
  const ok=await new Promise(resolve=>{
   const req=http.get(origin+'/index.html',r=>{r.destroy();resolve(r.statusCode===200)});
   req.on('error',()=>resolve(false));
  });
  if(ok)return;
  await delay(120);
 }
 throw Error('Staging-only local HTML preview server failed');
}
(async()=>{
 const server=spawn('python3',['-m','http.server','8791','--bind','127.0.0.1','--directory','/tmp/fc-a36-staging-browser'],{stdio:'ignore'});
 let browser;
 try{
  await awaitServer();
  browser=await chromium.launch({channel:'chrome',headless:true,args:['--disable-dev-shm-usage']});
  const report=[];
  for(const width of [390,375,430]){
   const context=await browser.newContext({viewport:{width,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
   const page=await context.newPage();
   const pageErrors=[],blockedProduction=[];
   page.on('pageerror',error=>pageErrors.push(error.message.slice(0,190)));
   await page.route('**/*',route=>{
    const url=route.request().url();
    if(url.includes('sioalvawzayfphwzqctq.supabase.co')&&!url.includes('/storage/v1/object/public/')){
     blockedProduction.push(new URL(url).pathname);
     return route.abort();
    }
    return route.continue();
   });
   await page.goto(origin+'/index.html',{waitUntil:'domcontentloaded',timeout:50000});
   const login=await page.evaluate(async({email,password})=>{
    const {data,error}=await db.auth.signInWithPassword({email,password});
    return error?{error:error.message}:{userId:data?.user?.id};
   },{email,password});
   assert.ok(login.userId,'Real staging sign-in failed: '+String(login.error||'unknown'));
   await page.reload({waitUntil:'domcontentloaded',timeout:50000});
   await page.waitForFunction(expected=>typeof state!=='undefined'&&state.profile?.id===expected,login.userId,{timeout:25000});
   // Preserve forced onboarding: run the actual two-step appearance/interest
   // user experience if this staging account has not completed v1103 setup.
   const beforeSetup=await page.evaluate(()=>({
     complete:Number(state.profile?.onboarding_version||0)>=1103,
     hasInterest:Array.isArray(state.profile?.interests)&&state.profile.interests.length>0
   }));
   if(!beforeSetup.complete){
     const overlay=page.locator('#fcOnboardingV1103.open');
     await overlay.waitFor({timeout:20000});
     await page.screenshot({path:path.join(out,'onboarding-'+width+'.png')});
     await overlay.locator('[data-ob-theme="dark"]').click({timeout:10000});
     await overlay.locator('#fcObNextV1103').click({timeout:10000});
     // Existing Music interest is preselected by the app; clicking it again
     // would remove the only interest and correctly fail required onboarding.
     if(!beforeSetup.hasInterest) await overlay.locator('[data-ob-interest="Music"]').click({timeout:10000});
     await overlay.locator('#fcObNextV1103').click({timeout:15000});
     try {
       await page.waitForFunction(()=>Number(state.profile?.onboarding_version||0)>=1103,null,{timeout:9000});
     } catch(error){
       const diagnostic=await page.evaluate(()=>({profileVersion:Number(state.profile?.onboarding_version||0),overlayOpen:document.getElementById('fcOnboardingV1103')?.classList.contains('open'),status:document.getElementById('fcObStatusV1103')?.innerText||'',nextLabel:document.getElementById('fcObNextV1103')?.innerText||'',nextDisabled:document.getElementById('fcObNextV1103')?.disabled}));
       console.warn('A36_REQUIRED_SETUP_DIAGNOSTIC '+JSON.stringify(diagnostic));
       await page.screenshot({path:path.join(out,'onboarding-error-'+width+'.png')});
       throw error;
     }
     console.log('PASS A3.6 actual first-run appearance and Music interest onboarding '+width+'px');
   }
   // Required setup has to finish before Community Guidelines acceptance.
   await page.waitForFunction(()=>!document.getElementById('fcOnboardingV1103')?.classList.contains('open'),null,{timeout:15000});
   const hasAgreed=await page.evaluate(()=>guidelinesAcked());
   if(!hasAgreed){
     const guidelines=page.locator('#guidelinesModal.open');
     await guidelines.waitFor({timeout:20000});
     await page.screenshot({path:path.join(out,'guidelines-before-accept-'+width+'.png')});
     const agreeHit=await page.evaluate(()=>{
       const e=[...document.querySelectorAll('#guidelinesModal button')].find(x=>x.textContent.includes('I Agree'));
       const overlay=document.getElementById('guidelinesModal'),r=e.getBoundingClientRect(),o=overlay.getBoundingClientRect();
       const h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2),c=getComputedStyle(overlay);
       const chain=[];for(let n=e;n&&chain.length<8;n=n.parentElement){const st=getComputedStyle(n);
         chain.push({tag:n.tagName,id:n.id,klass:String(n.className).slice(0,65),display:st.display,visibility:st.visibility,pointerEvents:st.pointerEvents,z:st.zIndex,inert:n.inert});
       }
       return {buttonRect:{x:r.x,y:r.y,w:r.width,h:r.height},modalRect:{x:o.x,y:o.y,w:o.width,h:o.height},
         hit:h?.tagName+'#'+h?.id,hitStack:document.elementsFromPoint(r.left+r.width/2,r.top+r.height/2).slice(0,5).map(n=>n.tagName+'#'+n.id),
         modalOpen:overlay.classList.contains('open'),modalStyle:{display:c.display,visibility:c.visibility,z:c.zIndex,pointerEvents:c.pointerEvents},
         inertNodes:[...document.querySelectorAll('[inert]')].slice(0,10).map(n=>n.id||n.tagName),
         onboardingOpen:document.getElementById('fcOnboardingV1103')?.classList.contains('open'),
         nativeDialogs:[...document.querySelectorAll('dialog')].map(d=>({id:d.id,open:d.open,isModal:d.matches(':modal'),rect:{x:d.getBoundingClientRect().x,y:d.getBoundingClientRect().y,w:d.getBoundingClientRect().width,h:d.getBoundingClientRect().height},label:d.getAttribute('aria-label'),buttons:[...d.querySelectorAll('button')].slice(0,8).map(b=>({text:(b.textContent||'').trim().slice(0,35),label:b.getAttribute('aria-label')}))})).filter(d=>d.open),
         modalLayer:[...document.querySelectorAll(':modal')].map(d=>d.id||d.tagName),
         bodyInert:document.body.inert,htmlInert:document.documentElement.inert,
         chain,viewport:{w:innerWidth,h:innerHeight,scale:visualViewport?.scale}};
     });
     console.log('A36_GUIDELINES_TAP_HITTEST '+JSON.stringify(agreeHit));
     // Playwright mobile emulation reports HTML as the hit target despite the
     // visible button. Invoke the real button handler via DOM event for the
     // staging test account; this does NOT certify a physical tap.
     await guidelines.locator('button:has-text("I Agree")').dispatchEvent('click');
     console.log('A36_GUIDELINES_HANDLER_DISPATCHED (pointer acceptance still pending)');
     await page.waitForFunction(()=>!document.getElementById('guidelinesModal')?.classList.contains('open'),null,{timeout:15000});
     console.log('PASS A3.6 mandatory Guidelines handler persisted staging account consent '+width+'px');
   }
   // The guide appears shortly after Guidelines acceptance; use Skip normally.
   // Never remove overlays or bypass required onboarding in test code.
   await page.waitForTimeout(1650);
   const guide=page.locator('#fcOnboardingV1103.open');
   if(await guide.count()){
     const skip=guide.locator('#fcObSkipV1103');
     await skip.waitFor({timeout:11000});
     const guideProbe=await page.evaluate(()=>{
       const e=document.getElementById('fcObSkipV1103'),r=e.getBoundingClientRect();
       const hit=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
       const chain=[];for(let n=e;n&&chain.length<10;n=n.parentElement){
         const cs=getComputedStyle(n);chain.push({tag:n.tagName,id:n.id,klass:String(n.className).slice(0,60),pointerEvents:cs.pointerEvents,display:cs.display,zIndex:cs.zIndex,position:cs.position});
       }
       const overlay=document.getElementById('fcOnboardingV1103');
       const os=getComputedStyle(overlay);
       const overRect=overlay.getBoundingClientRect();
       const cs=getComputedStyle(e);
       return {rect:{x:r.x,y:r.y,w:r.width,h:r.height},hit:hit?.tagName+'.'+String(hit?.className||'').slice(0,90),
         hitStack:document.elementsFromPoint(r.left+r.width/2,r.top+r.height/2).slice(0,5).map(n=>n.tagName+'#'+n.id),
         overlayOpen:overlay.classList.contains('open'),modalMatches:[...document.querySelectorAll('dialog[open],[popover]:popover-open')].slice(0,8).map(n=>n.id),
         inert:[...document.querySelectorAll('[inert]')].slice(0,8).map(n=>n.id+'|'+n.className),
         bodyInert:document.body.inert,htmlInert:document.documentElement.inert,
         overlayStyle:{display:os.display,visibility:os.visibility,opacity:os.opacity,pointerEvents:os.pointerEvents,transform:os.transform,clipPath:os.clipPath},
         overlayRect:{x:overRect.x,y:overRect.y,w:overRect.width,h:overRect.height},
         buttonStyle:{visibility:cs.visibility,opacity:cs.opacity,pointerEvents:cs.pointerEvents},
         chain,viewport:{w:innerWidth,h:innerHeight,visualW:visualViewport?.width,visualH:visualViewport?.height,scale:visualViewport?.scale},
         hitAtCorner:document.elementFromPoint(20,20)?.tagName,hitAtCenter:document.elementFromPoint(innerWidth/2,innerHeight/2)?.tagName};
     });
     console.log('A36_GUIDE_TAP_HITTEST '+JSON.stringify(guideProbe));
     await page.screenshot({path:path.join(out,'guide-before-skip-'+width+'.png')});
     await skip.dispatchEvent('click');
     console.log('A36_OPTIONAL_GUIDE_HANDLER_DISPATCHED (pointer acceptance still pending)');
     await page.waitForFunction(()=>!document.getElementById('fcOnboardingV1103')?.classList.contains('open'),null,{timeout:15000});
     console.log('PASS A3.6 optional guide Skip handler persisted');
   }
   // Native Ember is the intended once-per-day briefing *after* consent and guide.
   // Dismiss it through its real Minimize control before exploring the app.
   await page.waitForTimeout(1800);
   const ember=page.locator('dialog#fcEmberDailyBriefingV1221:modal');
   if(await ember.count()){
     await page.screenshot({path:path.join(out,'ember-daily-'+width+'.png')});
     const emberHit=await page.evaluate(()=>{
       const d=document.getElementById('fcEmberDailyBriefingV1221'),
             b=d?.querySelector('[aria-label="Minimize Ember"]');
       if(!d||!b)return {missing:true};
       const r=b.getBoundingClientRect(), x=r.left+r.width/2,y=r.top+r.height/2;
       const st=getComputedStyle(d);
       return {button:{x:r.x,y:r.y,w:r.width,h:r.height},hitStack:document.elementsFromPoint(x,y).slice(0,7).map(n=>n.tagName+'#'+n.id),
         dialogOpen:d.open,dialogModal:d.matches(':modal'),dialogInert:d.inert,inertParent:!!d.closest('[inert]'),
         dialogStyle:{display:st.display,pointerEvents:st.pointerEvents,visibility:st.visibility,zIndex:st.zIndex},
         otherOpen:[...document.querySelectorAll('.modal-backdrop.open,.cd-sheet.open')].map(n=>n.id).slice(0,12),
         allModal:[...document.querySelectorAll(':modal')].map(n=>n.id),
         inertTopLevel:[...document.body.children].filter(n=>n.inert).slice(0,20).map(n=>n.id||n.tagName),
         bodyInert:document.body.inert};
     });
     console.log('A36_EMBER_TAP_HITTEST '+JSON.stringify(emberHit));
     await ember.locator('[aria-label="Minimize Ember"]').click({timeout:7500});
     await page.waitForFunction(()=>!document.querySelector('#fcEmberDailyBriefingV1221:modal'),null,{timeout:10000});
     console.log('PASS A3.6 once-daily Ember minimized using actual control '+width+'px');
   }
   // A one-time Get App nudge may appear after the user minimizes Ember.
   // Dismiss it via the actual Not now control; never bypass modal handlers.
   await page.waitForTimeout(900);
   const getApp=page.locator('#getAppPrompt.open');
   if(await getApp.count()){
     await page.screenshot({path:path.join(out,'get-app-prompt-'+width+'.png')});
     await getApp.locator('button.ga-later').click({timeout:10000});
     await page.waitForFunction(()=>!document.getElementById('getAppPrompt')?.classList.contains('open'),null,{timeout:10000});
     console.log('PASS A3.6 one-time Get App prompt dismissed using real Not now control '+width+'px');
   }
   assert.equal(await page.evaluate(()=>document.querySelector('meta[name="fc-build"]')?.content.startsWith('v1399')),true);
   // Open the actual profile sheet using the app's own navigation function.
   await page.evaluate(async()=>await openUserProfile(state.profile.id));
   await page.locator('#fcA36VotesTab:visible').waitFor({timeout:18000});
   await page.screenshot({path:path.join(out,'votes-before-'+width+'.png')});
   const geometry=await page.evaluate(()=>{
    const button=document.getElementById('fcA36VotesTab'),sheet=document.getElementById('profileSheet');
    const rect=button.getBoundingClientRect(),box=sheet.getBoundingClientRect();
    const x=rect.x+rect.width/2,y=rect.y+rect.height/2,hit=document.elementFromPoint(x,y);
    return {rect:{x:Math.round(rect.x),y:Math.round(rect.y),width:Math.round(rect.width),height:Math.round(rect.height)},
      viewport:{w:innerWidth,h:innerHeight},sheetOpen:sheet.classList.contains('open'),
      sheetRect:{x:Math.round(box.x),y:Math.round(box.y),width:Math.round(box.width),height:Math.round(box.height)},
      hit:hit?.tagName+'.'+String(hit?.className||'').slice(0,120),
      hitInsideTab:button===hit||button.contains(hit),
      onboardingOpen:document.getElementById('fcOnboardingV1103')?.classList.contains('open'),
      otherOpen:[...document.querySelectorAll('.modal-backdrop.open,.cd-sheet.open')].map(el=>el.id).slice(0,10)};
   });
   console.log('A36_VOTES_TAP_GEOMETRY '+JSON.stringify(geometry));
   try {await page.locator('#fcA36VotesTab').click({timeout:9000});}
   catch(e){await page.screenshot({path:path.join(out,'votes-click-blocked-'+width+'.png')});throw e;}
   await page.waitForFunction(()=>{
    const txt=document.getElementById('psContent')?.innerText||'';
    return typeof psState!=='undefined'&&psState.tab==='votes'&&txt.includes('FC_A36_V1395_LIVE')&&txt.includes('FC_A36_V1395_SETTLED');
   },null,{timeout:30000});
   const votes=await page.evaluate(()=>({
    ownTab:document.getElementById('fcA36VotesTab')?.hidden===false,
    profileOpen:document.getElementById('profileSheet')?.classList.contains('open'),
    labels:document.getElementById('psContent')?.innerText.slice(0,1800)||'',
    overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1
   }));
   assert.ok(votes.ownTab,'Own profile Votes tab missing');
   assert.ok(!votes.overflow,'Votes page horizontally overflows');
   assert.match(votes.labels,/FC_A36_V1395_LIVE/);
   assert.match(votes.labels,/FC_A36_V1395_SETTLED/);
   await page.screenshot({path:path.join(out,'votes-'+width+'.png')});
   // Navigate into the actual app Following sheet; verifies live Follow relation
   // and the off-feed entry button, not a mock component.
   await page.evaluate(async()=>{closeProfileSheet();await openFollowingSheet()});
   await page.locator('#followingSheet.open #followingList').waitFor({timeout:15000});
   await page.locator('#followingList .fc-a36-following-entry-v1393').waitFor({timeout:30000});
   const following=await page.evaluate(()=>{
    const nav=document.getElementById('bottomNav');
    const action=document.querySelector('#followingList .fc-a36-following-entry-v1393');
    const rect=action?.getBoundingClientRect();
    const hit=rect?document.elementFromPoint(rect.left+rect.width/2,rect.top+rect.height/2):null;
    return {
      open:document.getElementById('followingSheet')?.classList.contains('open'),
      text:document.getElementById('followingList')?.innerText.slice(0,1300)||'',
      offFeedButtons:document.querySelectorAll('#followingList .fc-a36-following-entry-v1393').length,
      overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,
      navVisibility:getComputedStyle(nav).visibility,
      navPointerEvents:getComputedStyle(nav).pointerEvents,
      actionInViewport:!!rect&&rect.bottom<=innerHeight-1&&rect.top>=0,
      actionReceivesTap:!!action&&(hit===action||action.contains(hit))
    };
   });
   const cssProbe=await page.evaluate(()=>{
     const sheet=document.getElementById('followingSheet'),
           nav=document.getElementById('bottomNav'),
           style=document.getElementById('fc-a36-following-nav-v1399');
     return {styleExists:!!style,ruleText:(style?.textContent||'').slice(0,600),
       bodyHasFollowing:document.body.matches('body:has(#followingSheet.open)'),
       followingOpen:sheet.classList.contains('open'),
       sheetInBody:document.body.contains(sheet),
       sheetComputedZ:getComputedStyle(sheet).zIndex,
       navComputedZ:getComputedStyle(nav).zIndex,
       navComputedVisibility:getComputedStyle(nav).visibility,
       navComputedPointerEvents:getComputedStyle(nav).pointerEvents,
       navInlineVisibility:nav.style.getPropertyValue('visibility'),
       navInlineVisibilityPriority:nav.style.getPropertyPriority('visibility'),
       navClass:nav.className,bodyClass:document.body.className.slice(0,160),
       rules:(()=>{
         const hits=[];
         for(const sheet of document.styleSheets){
           let rules;try{rules=sheet.cssRules}catch{continue}
           function walk(items){
             for(const rule of items){
               if(rule.cssRules){walk(rule.cssRules);continue}
               if(!rule.selectorText||!rule.style)continue;
               if(!/bottomNav|bottom-nav|fc-dialog-open-v1100/.test(rule.selectorText))continue;
               let match=false;try{match=nav.matches(rule.selectorText)}catch{}
               if(match && ['visibility','pointer-events','z-index'].some(k=>rule.style.getPropertyValue(k))){
                 hits.push({selector:rule.selectorText.slice(0,190),
                   visibility:rule.style.getPropertyValue('visibility'),
                   visibilityPriority:rule.style.getPropertyPriority('visibility'),
                   pointer:rule.style.getPropertyValue('pointer-events'),
                   zIndex:rule.style.getPropertyValue('z-index'),
                   styleId:sheet.ownerNode?.id||null});
               }
             }
           }
           walk(rules);
         }
         return hits.slice(-25);
       })()};
   });
   console.log('A36_FOLLOWING_CSS_DIAGNOSTIC '+JSON.stringify(cssProbe));
   console.log('A36_FOLLOWING_LAYOUT_CHECK '+JSON.stringify({width,navVisibility:following.navVisibility,actionInViewport:following.actionInViewport,actionReceivesTap:following.actionReceivesTap}));
   assert.ok(following.open,'Following sheet failed to open');
   assert.equal(following.navVisibility,'hidden','Following must cover persistent bottom navigation');
   assert.equal(following.navPointerEvents,'none','Hidden bottom navigation must not intercept taps');
   assert.ok(following.actionInViewport,'View Entry action clipped at bottom of Following');
   assert.ok(following.actionReceivesTap,'View Entry action obscured by another layer');
   assert.ok(following.offFeedButtons>=1,'Followed competitor has no off-feed entry link');
   assert.match(following.text,/A3\.6 Staging Competitor/);
   assert.ok(!following.overflow,'Following horizontally overflows');
   await page.screenshot({path:path.join(out,'following-'+width+'.png')});
   await page.locator('#followingList .fc-a36-following-entry-v1393').first().click();
   await page.waitForFunction(()=>!document.getElementById('followingSheet')?.classList.contains('open'),null,{timeout:12000});
   await page.waitForTimeout(700);
   const viewer=await page.evaluate(()=>({
    sheetClosed:!document.getElementById('followingSheet')?.classList.contains('open'),
    challengeHydrated:(state.challenges||[]).some(ch=>ch.title==='FC_A36_V1395_FOLLOW_NEXT'||ch.title==='FC_A36_V1395_LIVE'),
    scrollWidth:document.documentElement.scrollWidth,
    viewport:document.documentElement.clientWidth
   }));
   assert.ok(viewer.sheetClosed,'Following sheet did not close when View Entry clicked');
   assert.ok(viewer.challengeHydrated,'Off-feed competition not hydrated after View Entry click');
   assert.ok(viewer.scrollWidth<=viewer.viewport+1,'Entry viewer horizontal overflow');
   await page.screenshot({path:path.join(out,'entry-viewer-'+width+'.png')});
   assert.equal(blockedProduction.length,0,'Production API request detected');
   assert.deepEqual(pageErrors,[],'Uncaught JS errors');
   report.push({width,signedIn:true,votesRendered:true,officialResultsVisible:true,followingRendered:true,offFeedViewerHydrated:true,noProductionAPI:true,noOverflow:true,noJSRuntimeError:true});
   console.log('PASS A3.6 real UI flow '+width+'px — own Votes, official result, Following, off-feed viewer');
   await page.evaluate(async()=>{try{await db.auth.signOut()}catch{}});
   await context.close();
  }
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({scope:'real staging v1395 signed-in app UI, mobile Chromium',physicalIphone:false,report},null,2));
  console.log('PASS A3.6 signed-in v1399 UI navigation at 375/390/430px; physical iPhone still separate');
 }finally{if(browser)await browser.close();server.kill('SIGTERM');}
})().catch(e=>{console.error('A36_FLOW_UI_FAILED '+String(e.message||e).slice(0,450));process.exitCode=1;});
