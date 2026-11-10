import {test,expect} from '@playwright/test';
test.use({viewport:{width:390,height:844},hasTouch:true,isMobile:true,deviceScaleFactor:1});
async function boot(page){await page.goto('/?qa=1');await page.waitForFunction(()=>window.__ASHFALL);}
test('mobile menu pages fit and all navigation is reachable',async({page})=>{
 await boot(page);await page.screenshot({path:'artifacts/mobile-menu.png'});for(const name of ['ARMORY','SURVIVORS','COMPANIONS','STATISTICS','SETTINGS','MISSIONS']){await page.getByRole('button',{name:new RegExp(name)}).tap();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.getByRole('button',{name:'BACK TO CAMP'}).tap();}
});
test('real touch: lane controls, jump, slide, fire and reload work',async({page})=>{
 await boot(page);await page.getByRole('button',{name:'BEGIN YOUR RUN'}).tap();await page.getByRole('button',{name:'Move right',exact:true}).tap();await page.waitForFunction(()=>window.__ASHFALL.run.x>2.8);await page.getByRole('button',{name:'Jump',exact:true}).tap();await page.waitForFunction(()=>window.__ASHFALL.run.y>.2);await page.waitForFunction(()=>window.__ASHFALL.run.y===0);await page.getByRole('button',{name:'Slide',exact:true}).tap();expect(await page.evaluate(()=>window.__ASHFALL.run.slide)).toBeGreaterThan(0);await page.getByRole('button',{name:'Fire weapon'}).tap();await page.waitForFunction(()=>window.__ASHFALL.run.ammo.mag<12);await page.getByRole('button',{name:'Reload',exact:true}).tap();await page.waitForFunction(()=>window.__ASHFALL.run.reload>0);await page.screenshot({path:'artifacts/mobile-gameplay.png'});
});
test('actual multi-touch: releasing movement does not cancel held fire',async({page,context})=>{
 await boot(page);await page.getByRole('button',{name:'BEGIN YOUR RUN'}).tap();await page.evaluate(()=>{window.__ASHFALL.profile.settings.autofire=false;window.touchLog=[];for(const t of ['pointerdown','pointerup','pointercancel'])window.addEventListener(t,e=>touchLog.push({type:t,id:e.pointerId,action:e.target.dataset?.action}),true);});
 const fire=await page.getByRole('button',{name:'Fire weapon'}).boundingBox(),left=await page.getByRole('button',{name:'Move left',exact:true}).boundingBox();
 const cdp=await context.newCDPSession(page),point=(b,id)=>({x:b.x+b.width/2,y:b.y+b.height/2,id});
 const f=point(fire,1),l=point(left,2);
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[f]});await page.waitForTimeout(380);await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[f,l]});await page.waitForTimeout(120);await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[l]});expect(await page.evaluate(()=>touchLog.filter(e=>e.type==='pointerup').at(-1)?.action)).toBe('left');const first=await page.evaluate(()=>window.__ASHFALL.run.shots);await page.waitForTimeout(800);const second=await page.evaluate(()=>window.__ASHFALL.run.shots);console.log('MULTITOUCH_TRACE',await page.evaluate(()=>touchLog));await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});expect(second).toBeGreaterThan(first);expect(await page.evaluate(()=>window.__ASHFALL.run.lane)).toBe(-1);
});
test('landscape touch HUD has no overlap between action pads',async({page})=>{
 await page.setViewportSize({width:844,height:390});await boot(page);await page.getByRole('button',{name:'BEGIN YOUR RUN'}).tap();const a=await page.locator('.move-pad').boundingBox(),b=await page.locator('.combat-pad').boundingBox();expect(a.x+a.width).toBeLessThan(b.x);await page.screenshot({path:'artifacts/mobile-landscape.png'});
});
