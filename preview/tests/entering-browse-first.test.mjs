/**
 * Browse-first entry-window acceptance test for the isolated FlamesChallenge prototype.
 * Run with Playwright installed: node preview/tests/entering-browse-first.test.mjs
 */
import assert from 'node:assert/strict';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, resolve } from 'node:path';
import { chromium } from 'playwright';

const file=resolve(dirname(fileURLToPath(import.meta.url)),'../flameschallenge-p1.html');
const browser=await chromium.launch({headless:true});
let checks=0;
try{
 const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
 await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded'});
 const disclaimer=await page.locator('.hybrid-disclosure').textContent();
 assert.match(disclaimer,/Prototype preview · Sample competitions, not live records/);checks++;
 assert.ok(!(await page.locator('.hybrid-disclosure').evaluate(el=>getComputedStyle(el).borderTopWidth!=='0px')),'Prominent warning border must not return');checks++;
 await page.locator('.hybrid-tile[data-act="open:art"]').click();
 assert.equal(await page.locator('#viewer').evaluate(el=>el.classList.contains('show')),true,'Art opens viewer, not submission');checks++;
 assert.equal(await page.locator('#overlay').evaluate(el=>el.classList.contains('show')),false,'Entry form must remain closed');checks++;
 assert.equal(await page.locator('#stageNumber').textContent(),'SAMPLE ENTRY 1 OF 2');checks++;
 assert.match(await page.locator('#viewerDetail').textContent(),/Example entrant/);checks++;
 await page.locator('#nextEntry').click();
 assert.equal(await page.locator('#stageNumber').textContent(),'SAMPLE ENTRY 2 OF 2');checks++;
 assert.match(await page.locator('#viewerDetail').textContent(),/Sample Maker B/);checks++;
 await page.locator('#viewerActions [data-act="entrants:art"]').click();
 assert.equal(await page.locator('.option-row[data-act^="previewentry:art:"]').count(),2);checks++;
 assert.equal(await page.locator('#entryForm').count(),0,'Details must not show upload form');checks++;
 await page.locator('#sheet [data-act="enter:art"]').click();
 assert.equal(await page.locator('#entryForm').count(),1,'Only explicit Enter action starts submission');checks++;
 await page.locator('#overlay').evaluate(el=>el.classList.remove('show'));
 await page.locator('#viewerClose').click();
 await page.locator('[data-nav="compete"]').click();
 await page.locator('button[data-act="filter:enter"]').click();
 await page.locator('[data-act="open:freestyle"]').first().click();
 assert.equal(await page.locator('#stageNumber').textContent(),'NO ENTRIES YET');checks++;
 assert.match(await page.locator('#viewerDetail').textContent(),/No entries yet/);checks++;
 assert.equal(await page.locator('#entryForm').count(),0,'Empty challenge must not force submission');checks++;
 assert.match(await page.locator('#viewerActions [data-act="enter:freestyle"]').textContent(),/Enter challenge/);checks++;
 console.log('PASS '+checks+' checks: disclaimer is discreet; sample entrants can be browsed before entering; empty challenges have honest state; upload requires explicit Enter.');
 await page.close();
}finally{await browser.close();}
