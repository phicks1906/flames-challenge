/**
 * Phase lifecycle acceptance checks for sample-only staging.
 * node preview/tests/challenge-phases.test.mjs
 */
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const file=resolve(dirname(fileURLToPath(import.meta.url)),'../flameschallenge-p1.html');
const browser=await chromium.launch({headless:true});
let checks=0;
const yes=(value,message)=>{assert.ok(value,message);checks++};
const equal=(a,b,message)=>{assert.equal(a,b,message);checks++};
try{
  for(const viewport of [{width:390,height:844},{width:844,height:390}]){
    const page=await browser.newPage({viewport,deviceScaleFactor:1});
    try{
      await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded'});
      await page.locator('[data-nav="compete"]').click();
      await page.locator('button[data-act="filter:processing"]').click();
      yes(await page.locator('[data-act="open:posterfinal"]').count()>0,'Processing challenge discoverable');
      await page.locator('[data-act="open:posterfinal"]').click();
      equal(await page.locator('#viewerPhase').textContent(),'PROCESSING','Processing status');
      equal(await page.locator('#stageNumber').textContent(),'SAMPLE ENTRY 1 OF 2','Processing example entry');
      equal(await page.locator('#viewerActions [data-act^="pick:"]').count(),0,'Processing cannot vote');
      equal(await page.locator('#viewerActions [data-act^="enter:"]').count(),0,'Processing cannot enter');
      yes((await page.locator('#viewerHint').textContent()).includes('no winner'),'No winner invented');
      await page.locator('#nextEntry').click();
      equal(await page.locator('#stageNumber').textContent(),'SAMPLE ENTRY 2 OF 2','Browse other settled-awaiting entry');
      await page.locator('#viewerActions [data-act="phaseinfo:posterfinal"]').click();
      equal(await page.locator('#sheet [data-act^="phaseentry:"]').count(),2,'Processing entrant details');
      equal(await page.locator('#sheet .standing').count(),0,'No standings before settlement');
      await page.locator('#sheet .sheethead [data-act="closeSheet"]').click();
      await page.locator('#viewerClose').click();

      await page.locator('button[data-act="filter:upcoming"]').click();
      yes(await page.locator('[data-act="open:openmic"]').count()>0,'Upcoming visible in filter');
      await page.locator('[data-act="open:openmic"]').click();
      equal(await page.locator('#viewerPhase').textContent(),'UPCOMING','Upcoming status');
      equal(await page.locator('#stageNumber').textContent(),'CHALLENGE PREVIEW','Not a claimed submitted entry');
      equal(await page.locator('#viewerActions [data-act^="pick:"]').count(),0,'Upcoming cannot vote');
      equal(await page.locator('#viewerActions [data-act^="enter:"]').count(),0,'Upcoming cannot enter');
      equal(await page.locator('#viewerDots button').count(),0,'No fake competitors');
      await page.locator('#viewerActions [data-act="phaseinfo:openmic"]').click();
      yes((await page.locator('#sheet').textContent()).includes('Submissions and voting are not available yet'),'Upcoming rules are truthful');
      equal(await page.locator('#entryForm').count(),0,'Upcoming never opens submission');
      await page.locator('#sheet .sheethead [data-act="closeSheet"]').click();
      await page.locator('#viewerActions [data-act="filter:live"]').click();
      equal(await page.locator('#viewer.show').count(),0,'Transition back to directory closes viewer');
      equal(await page.locator('[data-act="open:music"]').count(),1,'Voting remains available');
      await page.locator('[data-act="open:music"]').click();
      yes((await page.locator('#viewerActions').textContent()).includes('Choose'),'Voting allows practice comparison');
      await page.locator('#viewerClose').click();

      await page.locator('button[data-act="filter:results"]').click();
      await page.locator('[data-act="open:cooking"]').first().click();
      yes((await page.locator('#viewerActions').textContent()).includes('Final standings'),'Results expose standings');
      await page.locator('#viewerActions [data-act="result:cooking"]').click();
      yes((await page.locator('#sheet').textContent()).includes('not a settled competition record'),'Sample winner clearly marked');
      await page.locator('#sheet .sheethead [data-act="closeSheet"]').click();
    }finally{await page.close();}
  }
  console.log('PASS '+checks+' lifecycle assertions across portrait and landscape phone viewports.');
}finally{await browser.close();}
