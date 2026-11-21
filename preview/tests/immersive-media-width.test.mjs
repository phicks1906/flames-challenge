/**
 * Immersive media-width regression. Run in a checkout with Playwright installed:
 *   node preview/tests/immersive-media-width.test.mjs
 * Tests actual on-screen pixels, not just the dimensions of .stage or <video>.
 * Includes both portrait and landscape viewports, source media and fit toggle.
 */
import assert from 'node:assert/strict';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { chromium } from 'playwright';

const file=resolve(dirname(fileURLToPath(import.meta.url)),'../flameschallenge-p1.html');
const browser=await chromium.launch({headless:true});
const photo=(w,h,color)=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'"><rect width="100%" height="100%" fill="'+color+'"/></svg>'
);
const magenta=photo(256,448,'#ff00ff');
const black=photo(256,448,'#050505');
const videoURL='data:video/webm;base64,GkXfo59ChoEBQveBAULygQRC84EIQoKEd2VibUKHgQJChYECGFOAZwEAAAAAAALmEU2bdLpNu4tTq4QVSalmU6yBoU27i1OrhBZUrmtTrIHWTbuMU6uEElTDZ1OsggElTbuMU6uEHFO7a1OsggLQ7AEAAAAAAABZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVSalmsCrXsYMPQkBNgIxMYXZmNjEuNy4xMDNXQYxMYXZmNjEuNy4xMDNEiYhAeQAAAAAAABZUrmvKrgEAAAAAAABB14EBc8WIcUJ88/OBy+2cgQAitZyDdW5kiIEAhoVWX1ZQOYOBASPjg4QCYloA4JKwggEAuoIBwJqBAlW5gQESVMNnQH9zc59jwIBnyJlFo4dFTkNPREVSRIeMTGF2ZjYxLjcuMTAzc3PaY8CLY8WIcUJ88/OBy+1nyKVFo4dFTkNPREVSRIeYTGF2YzYxLjE5LjEwMSBsaWJ2cHgtdnA5Z8ihRaOIRFVSQVRJT05Eh5MwMDowMDowMC40MDAwMDAwMDAAH0O2dUEg54EAo7mBAACAgkmDQgAP8Bv2ADgkHBiwAAAwcAAAfJBDx2Df//8viD///H4OOebZRdS5ekH5g54Yg088KQCjmIEAKACGAECSnABWAAAEJqwAAF6McjWagKOXgQBQAIYAQJIcAFoAAAMgAABejHI1moCjl4EAeACGAECSnABRoAADIAAAXoxyNZqAo5eBAKAAhgBAkpwAT8AAAyAAAF6McjWagKOXgQDIAIYAQJKcAE8gAAMgAABejHI1moCjl4EA8ACGAECSnABOQAADIAAAXoxyNZqAo5eBARgAhgBAkpwATYAAAyAAAF6McjWagKOXgQFAAIYAQJKcAEzAAAMgAABejHI1moCjl4EBaACGAECSnABMIAADIAAAXoxyNZqAHFO7a5G7j7OBALeK94EB8YIBqvCBAw=='; // 256 x 448, original untracked test media

async function setup(page,kind){
  await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded'});
  await page.evaluate(kind=>{
    openChallenge(kind==='photo'?'photo':'music');
  },kind);
  await page.waitForSelector('#viewer.show.immersive-viewer');
  await page.evaluate(async({kind,magenta,black,videoURL})=>{
    const bg=document.getElementById('stageBlur');
    bg.src=black;bg.style.opacity='1';
    const image=document.getElementById('stagePhoto');
    image.src=magenta;image.style.opacity='1';
    await image.decode();
    if(kind==='video'){
      const v=document.getElementById('stageVideo');
      v.pause();v.src=videoURL;v.muted=true;v.hidden=false;
      await new Promise((resolve,reject)=>{if(v.readyState>=2)resolve();else{v.addEventListener('loadeddata',resolve,{once:true});v.addEventListener('error',reject,{once:true})}});
      assertVideoDimensions(v);
      await v.play();
    }else document.getElementById('stageVideo').hidden=true;
    function assertVideoDimensions(v){
      if(v.videoWidth!==256||v.videoHeight!==448)throw Error('Video fixture dimensions not loaded');
    }
  },{kind,magenta,black,videoURL});
}

async function visiblePixels(page){
  const info=await page.evaluate(()=>{
    const stage=document.getElementById('stage'), media=document.getElementById('stageVideo').hidden?document.getElementById('stagePhoto'):document.getElementById('stageVideo');
    const r=stage.getBoundingClientRect(), computed=getComputedStyle(media);
    return {rect:{x:r.x,y:r.y,width:r.width,height:r.height}, fit:computed.objectFit, mediaW:media.tagName==='VIDEO'?media.videoWidth:media.naturalWidth, mediaH:media.tagName==='VIDEO'?media.videoHeight:media.naturalHeight};
  });
  assert.ok(info.mediaW>0&&info.mediaH>0,'Source media must load; a blank stage cannot pass');
  const screenshot=(await page.screenshot()).toString('base64');
  const probes=await page.evaluate(async({png,r})=>{
    const bitmap=new Image();bitmap.src='data:image/png;base64,'+png;await bitmap.decode();
    const canvas=document.createElement('canvas');canvas.width=bitmap.naturalWidth;canvas.height=bitmap.naturalHeight;
    const context=canvas.getContext('2d',{willReadFrequently:true});context.drawImage(bitmap,0,0);
    return [.12,.88].map(f=>{
      const d=context.getImageData(Math.round(r.x+r.width*f),Math.round(r.y+r.height*.39),1,1).data;
      return {magenta:d[0]>95&&d[2]>95&&d[1]<d[0]*.65&&d[1]<d[2]*.65,rgba:Array.from(d)};
    });
  },{png:screenshot,r:info.rect});
  return {info,probes};
}

let assertions=0;
try{
  for(const viewport of [{width:844,height:390},{width:390,height:844}]){
    for(const kind of ['photo','video']){
      const page=await browser.newPage({viewport,deviceScaleFactor:1});
      try{
        await setup(page,kind);
        const result=await visiblePixels(page);
        assert.equal(result.info.fit,'cover',kind+' must use full-bleed sizing');
        assert.ok(result.probes.every(p=>p.magenta),
          kind+' visible pixels must reach both stage edges at '+viewport.width+'x'+viewport.height+': '+JSON.stringify(result));
        assertions+=2;
        await page.getByRole('button',{name:/show the entire entry/i}).click();
        const contained=await visiblePixels(page);
        assert.equal(contained.info.fit,'contain','Member must be able to show full uncropped entry');
        if(viewport.width>viewport.height){
          assert.ok(contained.probes.some(p=>!p.magenta),'In landscape, contained portrait media must show its side margins');
        }
        assertions+=viewport.width>viewport.height?2:1;
      } finally {await page.close()}
    }
  }
  process.stdout.write('PASS '+assertions+' assertions: rendered photo/video pixels reach both sides in portrait and landscape; uncropped toggle works.\n');
} finally {await browser.close()}
