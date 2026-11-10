import {test,expect} from '@playwright/test';
const boot=async p=>{await p.addInitScript(()=>localStorage.setItem('survivor-runs.profile.v2',JSON.stringify({version:2,settings:{quality:'low',volume:0}})));await p.goto('/?qa=1');await p.waitForFunction(()=>!!window.__SURVIVOR,null,{timeout:120000});await p.locator('[data-start=""]').click();};
test('real movement selects matching run/walk/sprint and stops stepping against cover',async({page},info)=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));await boot(page);
 // Remove combat interruptions for the labelled motion acceptance fixture only.
 await page.evaluate(()=>{const r=window.__SURVIVOR.run;r.entities=[];r.nextRow=Infinity;r.invulnerable=999;});
 await page.keyboard.down('w');await expect.poll(()=>page.evaluate(()=>window.__SURVIVOR.view.playerMotion.audit.clip)).toBe('run');
 await page.mouse.move(650,360);await page.mouse.down({button:'right'});await expect.poll(()=>page.evaluate(()=>window.__SURVIVOR.view.playerMotion.audit.clip)).toBe('walk');
 await page.mouse.up({button:'right'});await page.keyboard.down('Shift');await expect.poll(()=>page.evaluate(()=>window.__SURVIVOR.view.playerMotion.audit.clip)).toBe('sprint');await page.keyboard.up('Shift');
 await page.keyboard.up('w');await expect.poll(()=>page.evaluate(()=>window.__SURVIVOR.view.playerMotion.audit.clip)).toBe('idle');
 await page.evaluate(()=>{const q=window.__SURVIVOR,r=q.run;r.x=0;r.s=0;r.vx=r.vs=0;r.heading=0;q.view.rigCamera.yaw=0;r.add('obstacle',0,3,'car_wreck');});
 await page.keyboard.down('w');await page.waitForTimeout(1300);await expect.poll(()=>page.evaluate(()=>window.__SURVIVOR.run.moveSpeed)).toBeLessThan(.01);
 const before=await page.evaluate(()=>window.__SURVIVOR.view.playerMotion.phase);await page.waitForTimeout(400);const after=await page.evaluate(()=>window.__SURVIVOR.view.playerMotion.phase);expect(after).toBeCloseTo(before,8);await page.keyboard.up('w');expect(errors).toEqual([]);
});
test('actual space jump tracks flight, has asymmetric legs, and lands without restarting a jump loop',async({page},info)=>{
 await boot(page);await page.evaluate(()=>{const q=window.__SURVIVOR,r=q.run;r.entities=[];r.nextRow=Infinity;r.invulnerable=999;q.motionSamples=[];
  const frame=()=>{const m=q.view.playerMotion,a=q.view.player,r=q.run,V=a.object.position.constructor,L=a.object.getObjectByName('footL').getWorldPosition(new V()),R=a.object.getObjectByName('footR').getWorldPosition(new V());q.motionSamples.push({clip:m.audit.clip,phase:m.audit.phase,y:r.y,jump:r.jumpActive,separation:Math.abs(L.z-R.z),height:Math.abs(L.y-R.y)});if(q.motionSamples.length<160)requestAnimationFrame(frame);};requestAnimationFrame(frame);
 });
 await page.keyboard.press('Space');await page.waitForTimeout(1500);
 const s=await page.evaluate(()=>window.__SURVIVOR.motionSamples),air=s.filter(s=>s.clip==='jump'&&s.phase>.30&&s.phase<.65);expect(air.length).toBeGreaterThan(1);expect(Math.max(...air.map(s=>s.separation))).toBeGreaterThan(.35);expect(Math.max(...air.map(s=>s.height))).toBeGreaterThan(.12);expect(air.every(s=>s.y>.2)).toBe(true);
 const end=await page.evaluate(()=>({y:window.__SURVIVOR.run.y,jump:window.__SURVIVOR.run.jumpActive,clip:window.__SURVIVOR.view.playerMotion.audit.clip}));expect(end.y).toBe(0);expect(end.jump).toBe(false);expect(['land','idle']).toContain(end.clip);
});
test('real Ctrl slide coasts on the surface in a low reclined non-gait pose',async({page},info)=>{
 await boot(page);await page.evaluate(()=>{const q=window.__SURVIVOR;q.run.entities=[];q.run.nextRow=Infinity;q.run.invulnerable=999;q.slideSamples=[];const frame=()=>{const m=q.view.playerMotion,r=q.run;q.slideSamples.push({clip:m.audit.clip,phase:m.audit.phase,s:r.s,speed:r.moveSpeed,y:r.y});if(q.slideSamples.length<160)requestAnimationFrame(frame);};requestAnimationFrame(frame);});
 const before=await page.evaluate(()=>window.__SURVIVOR.run.s);await page.keyboard.press('Control');await page.waitForTimeout(1400);
 const s=await page.evaluate(()=>window.__SURVIVOR.slideSamples),slide=s.filter(v=>v.clip==='slide'&&v.phase>.1&&v.phase<.8);expect(slide.length).toBeGreaterThan(2);expect(slide.every(v=>v.y===0)).toBe(true);expect(slide.at(-1).s).toBeGreaterThan(before+2);expect(slide.at(-1).speed).toBeLessThan(slide[0].speed);
 expect(await page.evaluate(()=>window.__SURVIVOR.run.slide)).toBe(0);
});
test('exported skinned boots plant in world space; slide height and jump fit the collider/reference',async({page},info)=>{
 await boot(page);
 const e=await page.evaluate(()=>{
  const q=window.__SURVIVOR,a=q.lib.actor('survivor_cowboy'),V=a.object.position.constructor;let skin;a.object.traverse(o=>{if(o.isSkinnedMesh)skin=o;});const g=skin.geometry,pos=g.attributes.position,si=g.attributes.skinIndex,sw=g.attributes.skinWeight,foot=skin.skeleton.bones.findIndex(b=>b.name==='footL'),verts=[];
  for(let i=0;i<pos.count;i++){let weight=0;for(let j=0;j<4;j++)if(si.array[i*4+j]===foot)weight+=sw.array[i*4+j];if(weight>.999&&pos.getY(i)<.055)verts.push(i);}
  const sample=(name,phase)=>{a.mixer.stopAllAction();const ac=a.actions[name];ac.reset().play().setEffectiveWeight(1);ac.paused=true;ac.time=ac.getClip().duration*phase;a.mixer.update(0);a.object.updateMatrixWorld(true);skin.skeleton.update();};
  const contacts=[];
  for(const [name,stride,stance]of [['walk',1.1,.62],['run',2.4,.4],['sprint',3,.31],['walk_back',1.1,.62],['run_right',2.4,.4]]){
   let first,drift=0;a.object.rotation.set(0,Math.PI,0);
   for(let i=0;i<8;i++){const phase=.045+i*(stance-.09)/7;sample(name,phase);a.object.position.set(name.endsWith('right')?stride*phase:0,-.024,name.endsWith('back')?stride*phase:name.endsWith('right')?0:-stride*phase);a.object.updateMatrixWorld(true);const p=verts.reduce((out,j)=>out.add(skin.localToWorld(skin.getVertexPosition(j,new V()))),new V()).multiplyScalar(1/verts.length);if(!first)first=p.clone();drift=Math.max(drift,p.distanceTo(first));}
   contacts.push({name,driftMm:drift*1000});
  }
  a.object.position.set(0,-.024,0);sample('slide',.5);let top=-Infinity,bottom=Infinity;for(let i=0;i<pos.count;i++){const p=skin.localToWorld(skin.getVertexPosition(i,new V()));top=Math.max(top,p.y);bottom=Math.min(bottom,p.y);}
  sample('jump',.5);const l=a.object.getObjectByName('footL').getWorldPosition(new V()),r=a.object.getObjectByName('footR').getWorldPosition(new V());return {samples:verts.length,contacts,slideTopMm:top*1000,slideBottomMm:bottom*1000,jumpFootSeparationMm:Math.abs(l.z-r.z)*1000,jumpFootHeightDifferenceMm:Math.abs(l.y-r.y)*1000};
 });
 expect(e.samples).toBeGreaterThan(50);for(const c of e.contacts)expect(c.driftMm,c.name).toBeLessThan(3);expect(e.slideTopMm).toBeLessThan(880);expect(e.slideBottomMm).toBeGreaterThan(-26);expect(e.jumpFootSeparationMm).toBeGreaterThan(350);expect(e.jumpFootHeightDifferenceMm).toBeGreaterThan(120);
 await info.attach('exported-motion-measurements',{body:JSON.stringify(e,null,2),contentType:'application/json'});
});
