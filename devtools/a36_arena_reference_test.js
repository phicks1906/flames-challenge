'use strict';
const { chromium }=require('/tmp/fc-a36-arena/node_modules/playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const { pathToFileURL }=require('node:url');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required']});
 const evidence=[];
 try{
  for(const width of [375,390,430]){
   const page=await browser.newPage({viewport:{width,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
   const errors=[];page.on('pageerror',e=>errors.push(String(e)));
   const source=path.resolve('preview/a36-arena-approved-reference.html');
   await page.goto(pathToFileURL(source).href,{waitUntil:'domcontentloaded',timeout:30000});
   await page.locator('#a34Skip').waitFor({state:'visible',timeout:20000});
   assert.equal(await page.locator('#a31Scenario').count(),1,'scenario selector');
   assert.match(await page.locator('body').innerText(),/A3\.4 TEST/);
   await page.locator('#a34Skip').click();
   await page.locator('[data-nav="compete"]').click();
   await page.locator('#contestView').waitFor({state:'visible',timeout:10000});
   assert.match(await page.locator('#contestView h1').innerText(),/THE ARENA/);
   assert.match(await page.locator('#contestView').innerText(),/Street Dance Weekend/);
   assert.ok(await page.locator('#contestView .participant').count()>=2,'side by side competitors');
   const layout=await page.evaluate(()=>({
    shell:document.getElementById('shell')?.getBoundingClientRect().width,
    viewport:document.documentElement.clientWidth,
    arenaVisible:!!document.querySelector('#contestView.active'),
    challengeCards:document.querySelectorAll('#contestView .participant').length
   }));
   assert.ok(layout.shell<=layout.viewport+1,'no shell horizontal overflow');
   assert.deepEqual(errors,[],'no browser JS errors');
   fs.mkdirSync('a36-arena-evidence',{recursive:true});
   await page.screenshot({path:'a36-arena-evidence/arena-'+width+'.png',fullPage:true});
   evidence.push({width,layout,errors,staticSample:true,realDevice:false,production:false});
   await page.close();
  }
  fs.writeFileSync('a36-arena-evidence/report.json',JSON.stringify({source:'A3.4 original approved HTML preserved in A3.6 staging',evidence},null,2));
  console.log('PASS: exact A3.4 Arena reference renders and navigates in phone-sized Chromium; not a live iPhone test.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
