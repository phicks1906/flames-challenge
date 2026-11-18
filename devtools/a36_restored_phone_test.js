'use strict';
const {chromium}=require('/tmp/fc-a36-restore/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true,args:['--autoplay-policy=no-user-gesture-required','--disable-dev-shm-usage']});
 const context=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  const file=path.join(process.cwd(),'preview/a36-restored.html');
  await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>document.querySelector('#demoPosition')?.textContent.includes('ENTRY 1 OF 5'),{timeout:15000});
  assert.equal(await page.locator('#demoMedia .videoSlide').count(),5,'five dancer slides');
  assert.equal(await page.locator('#demo').isVisible(),true,'full-screen demo visible');
  assert.equal(await page.locator('#profileSheet').count(),0,'rejected profile card absent');
  assert.equal(await page.locator('.demo-banner').count(),0,'rejected debug banner absent');
  assert.equal(await page.locator('#demoPosition').innerText(),'ENTRY 1 OF 5');
  fs.mkdirSync('a36-restored-evidence',{recursive:true});
  await page.screenshot({path:'a36-restored-evidence/iphone-start.png',fullPage:true});
  await page.locator('#demoNext').click();
  assert.equal(await page.locator('#demoPosition').innerText(),'ENTRY 2 OF 5','next dancer works');
  await page.screenshot({path:'a36-restored-evidence/iphone-second.png',fullPage:true});
  await page.locator('#demoVote').click();
  assert.equal(await page.locator('#sheet').isVisible(),true,'ballot opens');
  assert.equal(await page.locator('#sheetBody [data-practice]').count(),5,'ballot shows all five');
  await page.screenshot({path:'a36-restored-evidence/iphone-ballot.png',fullPage:true});
  await page.locator('#sheetBody [data-practice="1"]').click();
  assert.match(await page.locator('#sheetTitle').innerText(),/You made the call/);
  await page.screenshot({path:'a36-restored-evidence/iphone-result.png',fullPage:true});
  assert.deepEqual(errors,[],'no JS runtime errors');
  console.log('PASS: A3.5 approved source, 390x844 mobile viewport; five slide navigation, ballot, sample result, no rejected profile page. This is Chromium emulation, NOT a real iPhone test.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});