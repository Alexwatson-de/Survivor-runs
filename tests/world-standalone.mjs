// Normal built-game smoke, no ?qa and no application instrumentation.
import {chromium,expect} from '@playwright/test';import {writeFileSync} from 'node:fs';
const browser=await chromium.launch({channel:'chrome',headless:true});let report;
try{
 const page=await browser.newPage({viewport:{width:1280,height:720}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>localStorage.setItem('survivor-runs.profile.v2',JSON.stringify({version:2,settings:{quality:'low',volume:0}})));
 await page.goto('http://127.0.0.1:5190/');await expect(page.locator('#loading')).toBeHidden({timeout:120000});
 expect(await page.evaluate(()=>typeof window.__SURVIVOR)).toBe('undefined');await page.locator('[data-start=""]').click();await page.waitForTimeout(600);
 const idle=await page.locator('#distance').textContent();await page.waitForTimeout(600);expect(await page.locator('#distance').textContent()).toBe(idle);
 await page.keyboard.down('w');await page.waitForTimeout(1100);await page.keyboard.up('w');await page.waitForTimeout(300);const f=Number(await page.locator('#distance').textContent());expect(f).toBeGreaterThan(1);
 await page.keyboard.down('s');await page.waitForTimeout(900);await page.keyboard.up('s');await page.waitForTimeout(300);expect(Number(await page.locator('#distance').textContent())).toBeGreaterThan(f);
 await page.keyboard.press('Enter');await expect(page.locator('#mag')).toHaveText('11');await page.keyboard.press('r');await expect(page.locator('#mag')).toHaveText('12',{timeout:10000});
 await page.locator('[data-action="map"]').click();await expect(page.locator('#explorationMap')).toBeVisible();await page.locator('[data-action="map"]').click();await expect(page.locator('#explorationMap')).toBeHidden();
 await page.mouse.move(600,320);await page.mouse.down({button:'right'});await page.mouse.move(850,330,{steps:15});await page.mouse.up({button:'right'});
 await page.keyboard.press('p');await expect(page.locator('#resume')).toBeVisible();await page.locator('#resume').click();
 await page.screenshot({path:'artifacts/world-standalone-no-qa.png'});expect(errors).toEqual([]);
 report={passed:true,journey:'normal production controls',qaHook:false,controls:'real keyboard, mouse and DOM buttons',rendering:'low',errors};
}catch(e){report={passed:false,error:e.message};throw e;}finally{writeFileSync('artifacts/world-standalone-results.json',JSON.stringify(report,null,2));await browser.close();}
console.log(JSON.stringify(report));
