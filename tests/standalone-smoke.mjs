import {chromium} from '@playwright/test';import fs from 'node:fs';import assert from 'node:assert/strict';
const url=process.env.ASHFALL_URL||'http://127.0.0.1:5190/';
const browser=await chromium.launch({channel:'chrome'});
try{
 const page=await browser.newPage({viewport:{width:1440,height:900}}),errors=[],remote=[];let embeddedBlobs=0;
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{const u=new URL(r.url());if(u.protocol==='blob:')embeddedBlobs++;else if(['http:','https:'].includes(u.protocol)&&u.origin!==new URL(url).origin)remote.push(u.href);});
 await page.goto(url);await page.waitForSelector('#menu:not([hidden])');assert.equal(await page.evaluate(()=>typeof window.__ASHFALL),'undefined');await page.screenshot({path:'artifacts/final-menu.png'});
 await page.getByRole('button',{name:'BEGIN YOUR RUN'}).click();await page.keyboard.press('d');await page.keyboard.press('f');await page.mouse.click(760,350);
 await page.waitForFunction(()=>Number(document.getElementById('mag').textContent)<12);await page.keyboard.press('r');await page.waitForFunction(()=>document.getElementById('reloadLabel').textContent.includes('RELOADING'));await page.waitForFunction(()=>document.getElementById('reloadLabel').textContent==='');await page.waitForTimeout(1400);
 await page.screenshot({path:'artifacts/final-gameplay.png'});const distance=await page.locator('#distance').innerText();assert.ok(Number(distance.replaceAll(',',''))>10);await page.keyboard.press('Escape');await page.getByRole('button',{name:'KEEP RUNNING'}).waitFor();assert.deepEqual(errors,[]);assert.deepEqual(remote,[]);
 const report={url,production:true,qaHooks:false,distance,realInput:true,fireReloadPause:true,pageErrors:errors,remoteRequests:remote,embeddedTextureBlobs:embeddedBlobs};fs.writeFileSync('artifacts/standalone-verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
