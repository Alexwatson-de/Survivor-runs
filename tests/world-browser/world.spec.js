import {test,expect} from '@playwright/test';
const boot=async page=>{await page.addInitScript(()=>localStorage.setItem('survivor-runs.profile.v2',JSON.stringify({version:2,settings:{quality:'low',volume:0}})));await page.goto('/?qa=1');await page.waitForFunction(()=>!!window.__SURVIVOR,null,{timeout:120000});};
const snap=page=>page.evaluate(()=>window.__SURVIVOR.snapshot());
const play=async page=>{await page.locator('[data-start=""]').click();await page.waitForTimeout(1000);};
const hold=async(page,key,ms)=>{await page.keyboard.down(key);await page.waitForTimeout(ms);await page.keyboard.up(key);await page.waitForTimeout(350);};
test('real keyboard: stop, forward, backward, strafe, turn, map, manual fire/reload and pause',async({page},info)=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));await boot(page);await page.waitForTimeout(800);await page.screenshot({path:`artifacts/world-${info.project.name}-menu.png`});await play(page);
 const idle=await snap(page);await page.waitForTimeout(700);const stopped=await snap(page);expect(stopped.s).toBeCloseTo(idle.s,5);expect(stopped.distance).toBeCloseTo(0,5);
 await hold(page,'w',1300);const f=await snap(page);expect(f.s).toBeGreaterThan(idle.s+3);expect(f.y).toBe(0);const walkDistance=f.distance;
 await hold(page,'s',1000);const back=await snap(page);expect(back.s).toBeLessThan(f.s-2);expect(back.distance).toBeGreaterThan(walkDistance+2);expect(back.slide).toBe(0);
 await hold(page,'d',1000);const right=await snap(page);expect(right.x).toBeGreaterThan(back.x+2);await hold(page,'a',1000);expect((await snap(page)).x).toBeLessThan(right.x-2);
 const beforeTurn=await snap(page);await hold(page,'l',600);expect(Math.abs((await snap(page)).yaw-beforeTurn.yaw)).toBeGreaterThan(.2);
 await page.keyboard.press('m');await expect(page.locator('#explorationMap')).toBeVisible();await page.keyboard.press('m');await expect(page.locator('#explorationMap')).toBeHidden();
 const mag=(await snap(page)).ammo.mag;await page.keyboard.press('Enter');await page.waitForTimeout(450);expect((await snap(page)).ammo.mag).toBe(mag-1);await page.keyboard.press('r');await expect.poll(async()=>(await snap(page)).reload,{timeout:10000}).toBe(0);expect((await snap(page)).ammo.mag).toBe(12);
 await page.keyboard.press('p');await expect(page.locator('#resume')).toBeVisible();const paused=await snap(page);await page.waitForTimeout(600);expect((await snap(page)).time).toBeCloseTo(paused.time,5);await page.locator('#resume').click();await page.waitForTimeout(400);expect((await snap(page)).time).toBeGreaterThan(paused.time);
 await page.screenshot({path:`artifacts/world-${info.project.name}-play.png`});expect(errors).toEqual([]);
});
test('actual imported actors: skin weights, separate clones, canonical clips, no missing textures',async({page},info)=>{
 const missing=[];page.on('response',r=>{if(r.status()>=400)missing.push(r.url());});await boot(page);await play(page);
 const result=await page.evaluate(async()=>{const q=window.__SURVIVOR;return {assets:q.lib.audit.slice(-3),player:q.view.player.object.getObjectByName('weapon_socket')?.name,clones:['zombie_walker','zombie_runner'].map(n=>{const a=q.lib.actor(n),b=q.lib.actor(n),skins=[];a.object.traverse(o=>{if(o.isSkinnedMesh)skins.push(o);});let other;b.object.traverse(o=>{if(o.isSkinnedMesh)other=o;});const skin=skins[0],V=skin.position.constructor,indices=Array.from({length:24},(_,i)=>Math.floor(i*(skin.geometry.attributes.position.count-1)/23));a.object.updateMatrixWorld(true);skin.skeleton.update();const before=indices.map(i=>skin.getVertexPosition(i,new V()).clone());a.play('walk');a.mixer.update(.3);a.object.updateMatrixWorld(true);skin.skeleton.update();const deformation=Math.max(...indices.map((v,i)=>skin.getVertexPosition(v,new V()).distanceTo(before[i])));let animated=0;for(const bone of skin.skeleton.bones)if(Math.abs(bone.quaternion.x)+Math.abs(bone.quaternion.y)+Math.abs(bone.quaternion.z)>.01)animated++;return {n,skins:skins.length,independent:skin.skeleton!==other.skeleton,animated,deformation,clips:Object.keys(a.actions)};})};});
 expect(result.player).toBe('weapon_socket');expect(result.assets.map(a=>a.name)).toEqual(['survivor_cowboy','zombie_grim','zombie_melty']);for(const a of result.clones){expect(a.skins).toBeGreaterThan(0);expect(a.independent).toBe(true);expect(a.animated).toBeGreaterThan(4);expect(a.deformation).toBeGreaterThan(.0001);for(const label of ['walk','run','attack','hurt','die'])expect(a.clips).toContain(label);}
 expect(missing).toEqual([]);
});
test('fixture review: connected districts, exact shared scenery collision, settings and enemy model variants',async({page},info)=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));await boot(page);await play(page);
 // Explicit spatial fixture, not claimed as a natural traversal acceptance test.
 await page.evaluate(()=>{const q=window.__SURVIVOR,r=q.run;r.x=75;r.s=55;r.vx=r.vs=0;r.hp=100;r.invulnerable=999;r.generate();r.entities=r.entities.filter(e=>e.type!=='zombie');r.nextRow=Infinity;r.add('zombie',r.x-2,r.s+6,'walker');r.add('zombie',r.x+2,r.s+6,'runner');q.view.rigCamera.ready=false;});await page.waitForTimeout(2200);
 await page.screenshot({path:`artifacts/world-${info.project.name}-wrecks-zombies.png`});const a=await snap(page);expect(a.render.segments).toBeLessThanOrEqual(9);expect(a.assets.some(a=>a.name==='zombie_melty')).toBe(true);
 const count=await page.evaluate(()=>{const q=window.__SURVIVOR;q.profile.settings.blood=false;q.view.update(q.run,.016);let shown=0;q.view.env.tiles.forEach(t=>t.group.traverse(o=>{if(o.userData.blood&&o.visible)shown++;}));return shown;});expect(count).toBe(0);
 await page.evaluate(()=>window.__SURVIVOR.home());await page.locator('[data-page="characters"]').click();await expect(page.getByRole('heading',{name:'The Drifter'})).toBeVisible();await expect(page.locator('img[src="/assets/ui/survivor_cowboy.png"]').first()).toBeVisible();expect(errors).toEqual([]);
});
test('mobile layout and independent two-axis stick / camera drag / fire / release',async({browser},info)=>{
 const context=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await boot(page);await play(page);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 const b=await page.locator('#steerpad').boundingBox(),x=b.x+b.width/2,y=b.y+b.height/2,initial=await snap(page);let forward;
 if(info.project.name==='chrome'){
  const cdp=await context.newCDPSession(page),point=(id,x,y)=>({id,x,y,radiusX:5,radiusY:5,force:1}),send=(type,points)=>cdp.send('Input.dispatchTouchEvent',{type,touchPoints:points});
  await send('touchStart',[point(11,x,y-30)]);await page.waitForTimeout(900);await send('touchEnd',[]);forward=await snap(page);expect(forward.s).toBeGreaterThan(initial.s+1);
  await send('touchStart',[point(11,x+24,y+24)]);await page.waitForTimeout(800);await send('touchStart',[point(11,x+24,y+24),point(22,280,350)]);await send('touchMove',[point(11,x+24,y+24),point(22,335,355)]);
  const f=await page.locator('[data-action="fire"]').boundingBox();await send('touchStart',[point(11,x+24,y+24),point(22,335,355),point(33,f.x+f.width/2,f.y+f.height/2)]);await page.waitForTimeout(300);await send('touchEnd',[]);
 }else{
  // WebKit's public Playwright API has taps, not multi-touch dragging. Exercise
  // its real active-pointer pad and RMB look fallback, then an actual touch tap.
  await page.mouse.move(x,y-30);await page.mouse.down();await page.waitForTimeout(900);await page.mouse.up();forward=await snap(page);expect(forward.s).toBeGreaterThan(initial.s+1);
  await page.mouse.move(x+24,y+24);await page.mouse.down();await page.waitForTimeout(1100);await page.mouse.up();await page.mouse.move(280,350);await page.mouse.down({button:'right'});await page.mouse.move(335,355,{steps:6});await page.mouse.up({button:'right'});await page.locator('[data-action="fire"]').tap();
 }
 await page.waitForTimeout(500);
 const final=await snap(page);expect(final.x).toBeGreaterThan(forward.x+.8);expect(final.s).toBeLessThan(forward.s-.5);expect(Math.abs(final.yaw)).toBeGreaterThan(.1);expect(final.shots).toBeGreaterThan(0);expect(final.moveSpeed).toBeLessThan(.01);
 await page.screenshot({path:`artifacts/world-${info.project.name}-mobile.png`});expect(errors).toEqual([]);await context.close();
});
