import {test,expect} from '@playwright/test';
async function boot(page){await page.goto('/?qa=1');await page.waitForFunction(()=>window.__ASHFALL);await page.getByRole('button',{name:'BEGIN YOUR RUN'}).click();}
const snap=page=>page.evaluate(()=>window.__ASHFALL.snapshot());
test('controlled fixture: pickups equip shotgun and rifle, Q cycles owned guns',async({page})=>{
 await boot(page);await page.evaluate(()=>{const r=window.__ASHFALL.run;r.entities=[];r.nextRow=1e9;r.add('pickup',0,r.distance+3,'weapon');});await page.waitForFunction(()=>window.__ASHFALL.run.weapon==='shotgun');await expect(page.locator('#weaponName')).toContainText('M12');await page.evaluate(()=>{const r=window.__ASHFALL.run;r.add('pickup',0,r.distance+3,'weapon');});await page.waitForFunction(()=>window.__ASHFALL.run.weapon==='rifle');await page.keyboard.press('q');expect((await snap(page)).weapon).toBe('pistol');
});
test('controlled fixture + real jump and slide inputs clear modeled obstacles',async({page})=>{
 await boot(page);await page.evaluate(()=>{const r=window.__ASHFALL.run;r.entities=[];r.nextRow=1e9;r.add('obstacle',0,r.distance+4,'low_log');});await page.keyboard.press('Space');await page.waitForFunction(()=>window.__ASHFALL.run.entities[0].passed);expect((await snap(page)).hp).toBe(100);await page.waitForFunction(()=>window.__ASHFALL.run.y===0);await page.evaluate(()=>{const r=window.__ASHFALL.run;r.entities=[];r.add('obstacle',0,r.distance+4,'overhead');});await page.keyboard.press('s');await page.waitForFunction(()=>window.__ASHFALL.run.entities[0].passed);expect((await snap(page)).hp).toBe(100);
});
test('controlled fixture: all five biomes, rain and segment recycling remain bounded',async({page})=>{
 await boot(page);const report=[];
 for(let i=0;i<5;i++){
  await page.evaluate(i=>{const a=window.__ASHFALL,r=a.run;r.distance=i*192+25;r.dog.s=r.distance-.6;r.entities=[];r.nextRow=r.distance+50;r.generate();r.hp=100;r.invulnerable=999;},i);
  await page.waitForTimeout(300);await page.screenshot({path:'artifacts/biome-'+i+'.png'});report.push((await snap(page)).render);
 }
 await page.evaluate(()=>{const r=window.__ASHFALL.run;r.distance=290;});await page.waitForTimeout(100);expect(await page.evaluate(()=>window.__ASHFALL.view.rain.visible)).toBe(true);
 for(const r of report){expect(r.segments).toBe(7);expect(r.geometries).toBeLessThan(180);expect(r.actors).toBeLessThan(35);}
 await page.evaluate(()=>{for(let i=0;i<120;i++)window.__ASHFALL.view.env.update(i*48);});expect((await snap(page)).render.geometries).toBeLessThan(180);
});
test('controlled fixture: unlocks, upgrades, survivor and companion selections persist',async({page})=>{
 await boot(page);await page.evaluate(()=>{const a=window.__ASHFALL;a.profile.credits=3000;a.home();});
 await page.getByRole('button',{name:'SURVIVORS'}).click();await page.locator('[data-buy="character:ellis"]').click();await page.getByRole('button',{name:'BACK TO CAMP'}).click();await page.getByRole('button',{name:'COMPANIONS'}).click();await page.locator('[data-buy="dog:husky"]').click();await page.locator('[data-buy="upgrade:dog"]').click();await page.getByRole('button',{name:'BACK TO CAMP'}).click();await page.getByRole('button',{name:'ARMORY'}).click();await page.locator('[data-buy="weapon:rifle"]').click();await page.locator('[data-buy="upgrade:weapon"]').click();await page.reload();await page.waitForFunction(()=>window.__ASHFALL);await page.getByRole('button',{name:'BEGIN YOUR RUN'}).click();const s=await snap(page);expect(s.hp).toBe(125);expect(s.weapon).toBe('rifle');expect(await page.evaluate(()=>window.__ASHFALL.view.dog.name)).toBe('dog_husky');expect(await page.evaluate(()=>window.__ASHFALL.profile.upgrades.dog)).toBe(1);await page.screenshot({path:'artifacts/ellis-ghost-rifle.png'});
});
test('controlled fixture: mission completion unlocks next assignment exactly once',async({page})=>{
 await boot(page);await page.evaluate(()=>{const a=window.__ASHFALL;a.home();});await page.getByRole('button',{name:'MISSIONS'}).click();await expect(page.locator('[data-start="clearance"]')).toBeDisabled();await page.locator('[data-start="firstlight"]').click();await page.evaluate(()=>{const r=window.__ASHFALL.run;r.distance=501;});await expect(page.getByText('You made it.',{exact:true})).toBeVisible({timeout:15000});expect(await page.evaluate(()=>window.__ASHFALL.profile.completed)).toContain('firstlight');await page.getByRole('button',{name:'RETURN TO CAMP'}).click();await page.getByRole('button',{name:'MISSIONS'}).click();await expect(page.locator('[data-start="clearance"]')).toBeEnabled();
});
test('restart resets gameplay and memory inventory stays bounded',async({page})=>{
 await boot(page);for(let i=0;i<8;i++){await page.keyboard.press('Escape');await page.getByRole('button',{name:'RESTART RUN'}).click();}const s=await snap(page);expect(s.hp).toBe(100);expect(s.kills).toBe(0);expect(s.render.geometries).toBeLessThan(180);expect(s.render.pooled).toBeLessThan(100);expect(s.render.textures).toBeLessThan(30);
});
test('real-input continuous mission run: avoids obstacles without teleporting or invulnerability',async({page})=>{
 test.setTimeout(150000);await page.goto('/?qa=1');await page.waitForFunction(()=>window.__ASHFALL);await page.getByRole('button',{name:'MISSIONS'}).click();await page.locator('[data-start="firstlight"]').click();let steps=0;
 // Observe the same visible encounter state and issue ordinary key inputs; no simulation mutation.
 while(steps++<600){
  const s=await snap(page);if(s.phase!=='running')break;
  const near=s.entities.filter(e=>!e.passed&&e.hp>0&&e.s>s.distance&&e.s-s.distance<19&&e.type!=='pickup');
  const lanes=[-1,0,1].map(l=>({lane:l,clear:near.filter(e=>Math.abs(e.x-l*3)<1.5).reduce((n,e)=>n+(e.type==='obstacle'?5:2),0)})).sort((a,b)=>a.clear-b.clear||Math.abs(a.lane-s.lane)-Math.abs(b.lane-s.lane));
  if(lanes[0].lane<s.lane)await page.keyboard.press('a');if(lanes[0].lane>s.lane)await page.keyboard.press('d');
  if(s.ammo.mag<3&&s.ammo.reserve>0&&s.reload===0)await page.keyboard.press('r');
  await page.waitForTimeout(180);
 }
 const s=await snap(page);expect(s.phase).toBe('complete');expect(s.distance).toBeGreaterThanOrEqual(500);expect(s.hp).toBeGreaterThan(0);expect(s.kills).toBeGreaterThan(0);await page.screenshot({path:'artifacts/continuous-mission.png'});console.log('CONTINUOUS_RUN',JSON.stringify({distance:s.distance,hp:s.hp,kills:s.kills,dogKills:s.dogKills,frameMs:s.frameMs,render:s.render}));
});
