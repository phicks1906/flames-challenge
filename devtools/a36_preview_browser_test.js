'use strict';
/* Offline browser checks for the actual staged A3.6 votes component.
   Emulated phone viewports in Chromium, not a real iPhone nor live Supabase. */
const { chromium } = require('/tmp/fc-a36-test/node_modules/playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');

(async () => {
  const browser = await chromium.launch({headless:true,channel:'chrome'});
  const dir=path.resolve('a36-browser-evidence');
  fs.mkdirSync(dir,{recursive:true});
  const pageUrl=pathToFileURL(path.resolve('preview/a36-votes.html')).href;
  const evidence=[];
  try{
    for(const width of [375,390,430]){
      const page=await browser.newPage({viewport:{width,height:812},deviceScaleFactor:3,isMobile:true,hasTouch:true});
      const errors=[];
      page.on('pageerror',e=>errors.push(String(e)));
      await page.goto(pageUrl,{waitUntil:'load'});
      await page.locator('#fcA36VotesTab').waitFor();
      assert.equal(await page.locator('#fcA36VotesTab').isVisible(),true,'Own Votes tab visible');
      await page.locator('#fcA36VotesTab').click();
      await page.getByText('Live Vocal Challenge').waitFor();
      assert.equal(await page.getByText('Street Photography Showdown').count(),1);
      assert.equal(await page.getByText('Aria Wells').count(),1);
      assert.equal(await page.locator('[data-fc-a36-ch]').count(),3,'Three sample owned votes');
      assert.equal(await page.evaluate(()=>state.myVotes.poll_example),true,'Poll state preserved');
      const overflow=await page.evaluate(()=>({
        html:document.documentElement.scrollWidth,viewport:document.documentElement.clientWidth
      }));
      assert.ok(overflow.html<=overflow.viewport+1,'Horizontal overflow at '+width+': '+JSON.stringify(overflow));
      await page.screenshot({path:path.join(dir,'votes-'+width+'-dark.png'),fullPage:true});
      await page.locator('[data-fc-a36-ch]').first().click();
      await page.locator('#demoViewer').waitFor({state:'visible'});
      assert.equal(await page.locator('#viewerTitle').textContent(),'Live Vocal Challenge');
      await page.locator('#viewerClose').click();
      await page.locator('#demoViewer').waitFor({state:'hidden'});
      assert.equal(await page.locator('#fcA36VotesTab').isVisible(),true);
      await page.locator('#themeSwitch').click();
      await page.screenshot({path:path.join(dir,'votes-'+width+'-light.png'),fullPage:true});
      assert.equal(await page.locator('body').evaluate(el=>el.classList.contains('light')),true);
      await page.locator('#viewSwitch').click();
      assert.equal(await page.locator('#fcA36VotesTab').isVisible(),false,'Other profile hides Votes');
      await page.screenshot({path:path.join(dir,'other-profile-'+width+'.png'),fullPage:true});
      await page.locator('#viewSwitch').click();
      assert.equal(await page.locator('#fcA36VotesTab').isVisible(),true,'Own Votes restored');
      assert.deepEqual(errors,[],'Browser errors at '+width);
      evidence.push({width,render:'pass',sampleVotes:3,viewer:'pass',theme:'pass',profileIsolation:'pass',overflow:overflow.html-overflow.viewport,errors:0});
      await page.close();
    }
    fs.writeFileSync(path.join(dir,'report.json'),JSON.stringify({
      test:'A3.6 offline Chromium phone-view preview',data:'sample only',realDevice:false,liveSupabase:false,evidence
    },null,2));
    console.log('PASS A3.6 rendered browser tests: '+JSON.stringify(evidence));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
