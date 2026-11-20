'use strict';
const {chromium}=require('/tmp/fc-a37/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {pathToFileURL}=require('node:url');
const source=fs.readFileSync('preview/a37-connected.html','utf8');
const scripts=[...source.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)]
  .filter(m=>!/(?:src=|type=["'](?:application\/json|application\/ld\+json))/i.test(m[1]));
for(const [i,m] of scripts.entries())new vm.Script(m[2],{filename:'a37-inline-'+i+'.js'});
assert.match(source,/dance\.votes=\[41,40,36,32,29\]/);
assert.doesNotMatch(source,/events\.push\(newEvent\)/);
assert.doesNotMatch(source,/images:\[imgs\.singer,imgs\.singer\]|images:\[imgs\.pasta,imgs\.pasta\]/);
assert.ok(scripts.length>0,'inline source scripts exist');
const out='a37-evidence';fs.mkdirSync(out,{recursive:true});
async function main(){
 const browser=await chromium.launch({headless:true,channel:'chrome',args:['--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required']});
 const report=[];
 const mk=async(width)=>{
  const context=await browser.newContext({viewport:{width,height:844},deviceScaleFactor:3,isMobile:true,hasTouch:true});
  const page=await context.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('preview/a37-connected.html')).href,{waitUntil:'domcontentloaded',timeout:45000});
  await page.locator('#a34Performer').waitFor();
  await page.waitForFunction(()=>document.querySelector('#a34Demo')?.hidden===false,{timeout:20000});
  return {context,page,errors};
 };
 try{
  // New spectator, practice voting, not-following, pending result, and returning fan.
  for(const width of [375,390,430]){
   const {context,page,errors}=await mk(width);
   assert.match(await page.locator('#a34Performer').innerText(),/@NyraMoves/);
   await page.screenshot({path:`${out}/${width}-first.png`,fullPage:true});
   await page.locator('#a34Next').click();
   assert.match(await page.locator('#a34Performer').innerText(),/@KeiSteps/);
   await page.locator('#a34Compare').click();
   assert.equal(await page.locator('[data-a34-pick]').count(),5,'every eligible sample choice');
   await page.screenshot({path:`${out}/${width}-ballot.png`,fullPage:true});
   await page.locator('[data-a34-pick="3"]').click();
   assert.match(await page.locator('#a34VoteSentence').innerText(),/@AvaLines/);
   assert.match(await page.locator('#a34ResultExplainer').innerText(),/No real vote, official winner/);
   await page.screenshot({path:`${out}/${width}-receipt.png`,fullPage:true});
   await page.locator('#a34VoteNotNow').click();
   await page.locator('#a34ResultExplore').click();
   assert.match(await page.locator('#a31Content').innerText(),/Street Dance Weekend/);
   assert.match(await page.locator('#a31Content').innerText(),/outcome pending/i);
   await page.screenshot({path:`${out}/${width}-votes.png`,fullPage:true});
   await page.locator('[data-a31-you="following"]').click();
   assert.match(await page.locator('#a31Content').innerText(),/No competitors followed yet/);
   await page.locator('#a31Scenario').selectOption('fan');
   assert.match(await page.locator('#a31Content').innerText(),/result pending|Voting open/i);
   assert.doesNotMatch(await page.locator('#a31Content').innerText(),/Your pick won/i);
   await page.screenshot({path:`${out}/${width}-fan.png`,fullPage:true});
   const dimensions=await page.evaluate(()=>({
     viewport:document.documentElement.clientWidth,
     fullWidth:document.documentElement.scrollWidth,
     shell:document.getElementById('shell')?.getBoundingClientRect().width
   }));
   assert.ok(dimensions.fullWidth<=dimensions.viewport+2,`horizontal overflow at ${width}: ${JSON.stringify(dimensions)}`);
   assert.deepEqual(errors,[],`browser errors at ${width}`);
   report.push({width,dimensions,checks:'spectator practice receipt, no-follow, tracking, pending fan',errors});
   await context.close();
  }
  // Independent follow-choice path. Following MUST open the selected actual entry.
  {
   const {context,page,errors}=await mk(390);
   await page.locator('#a34Compare').click();
   await page.locator('[data-a34-pick="2"]').click();
   await page.locator('#a34VoteFollow').click();
   assert.match(await page.locator('#a37FollowStatus').innerText(),/@SolRitmo/);
   await page.locator('#a34ResultExplore').click();
   await page.locator('[data-a31-you="following"]').click();
   assert.match(await page.locator('#a31Content').innerText(),/@SolRitmo/);
   await page.screenshot({path:`${out}/390-following.png`,fullPage:true});
   await page.locator('[data-a31^="follow-profile:"]').click();
   assert.equal(await page.locator('#a34Demo').isVisible(),true);
   assert.match(await page.locator('#a34Performer').innerText(),/@SolRitmo/);
   assert.match(await page.locator('#a34Position').innerText(),/3 \/ 5/);
   assert.deepEqual(errors,[],'following route browser errors');
   await context.close();
  }
  // Home and Compete point to the same viewer; Titles structure and other media remain available.
  {
   const {context,page,errors}=await mk(390);
   await page.locator('#a34Skip').click();
   await page.locator('[data-nav="home"]').click();
   assert.match(await page.locator('#a33EntryCount').innerText(),/1 OF 5/);
   await page.locator('#compareA').click();
   assert.equal(await page.locator('#a34Demo').isVisible(),true,'Home launches immersive comparison');
   await page.locator('#a34Skip').click();
   await page.locator('[data-nav="compete"]').click();
   assert.equal(await page.locator('#featuredTitle').innerText(),'Street Dance Weekend');
   assert.match(await page.locator('#featuredPhase').innerText(),/VOTING NOW/);
   await page.screenshot({path:`${out}/390-compete.png`,fullPage:true});
   await page.locator('#seeContest').click();
   assert.equal(await page.locator('#a34Demo').isVisible(),true,'Compete launches same immersive comparison');
   await page.locator('#a34Skip').click();
   await page.locator('[data-nav="titles"]').click();
   assert.match(await page.locator('#a31Content').innerText(),/Championships/);
   await page.screenshot({path:`${out}/390-titles-championships.png`,fullPage:true});
   await page.locator('[data-a31-title="standings"]').click();
   assert.match(await page.locator('#a31Content').innerText(),/Qualification race/);
   await page.screenshot({path:`${out}/390-titles-standings.png`,fullPage:true});
   await page.locator('[data-a31-title="hof"]').click();
   assert.match(await page.locator('#a31Content').innerText(),/Legend/);
   await page.screenshot({path:`${out}/390-titles-hof.png`,fullPage:true});
   await page.locator('#a31Scenario').selectOption('creator');
   assert.match(await page.locator('#a31Content').innerText(),/Your race is close/);
   assert.match(await page.locator('#a31Content').innerText(),/not a final result/);
   await page.screenshot({path:`${out}/390-creator.png`,fullPage:true});
   assert.deepEqual(errors,[],'navigation and Titles browser errors');
   await context.close();
  }
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({commit:process.env.GITHUB_SHA||null,test:'A3.7 staging illustrative only',production:false,realIphone:false,backendIntegration:false,report},null,2));
  console.log('PASS A3.7: Chromium mobile 375/390/430, practice voting, no-follow and follow, tracked pending result, coherent Home/Compete, Titles and creator examples. NOT live iPhone or authenticated Supabase.');
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
