'use strict';
const { chromium }=require('/tmp/fc-a36-test/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const link='https://htmlpreview.github.io/?https://github.com/phicks1906/flames-challenge/blob/a36-integration-v1389/preview/a36-votes.html';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
  const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const resp=await page.goto(link,{waitUntil:'domcontentloaded',timeout:35000});
  console.log('Preview external URL:',page.url(),'HTTP:',resp?.status());
  await page.locator('#fcA36VotesTab').waitFor({timeout:25000});
  await page.locator('#fcA36VotesTab').click();
  await page.getByText('Live Vocal Challenge').waitFor({timeout:15000});
  assert.equal(await page.locator('[data-fc-a36-ch]').count(),3);
  assert.deepEqual(errors,[]);
  const out=path.resolve('a36-external-evidence');
  fs.mkdirSync(out,{recursive:true});
  await page.screenshot({path:path.join(out,'external-preview-390.png'),fullPage:true});
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({url:link,status:'passed',width:390,liveData:false,realIPhone:false},null,2));
  console.log('PASS external static A3.6 preview rendered and responded to Votes tap');
 } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1)});
