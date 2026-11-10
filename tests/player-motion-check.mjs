import {chromium,expect} from '@playwright/test';import {writeFileSync} from 'node:fs';
const b=await chromium.launch({channel:'chrome',headless:true}),p=await b.newPage({viewport:{width:1280,height:720}}),errors=[];
p.on('pageerror',e=>errors.push(e.message));
await p.addInitScript(()=>localStorage.setItem('survivor-runs.profile.v2',JSON.stringify({version:2,settings:{quality:'low',volume:0}})));
try{
 await p.goto('http://127.0.0.1:5190/?qa=1');await p.waitForFunction(()=>!!window.__SURVIVOR,null,{timeout:120000});await p.locator('[data-start=""]').click();
 const evidence=await p.evaluate(()=>{
  const q=window.__SURVIVOR,r=q.run,v=q.view,a=v.player;r.entities=[];r.nextRow=Infinity;r.invulnerable=999;
  const skin=(()=>{let s;a.object.traverse(o=>{if(o.isSkinnedMesh)s=o;});return s;})(),V=skin.position.constructor;
  const summary={clips:Object.keys(a.actions),bounds:{},contacts:[]};
  // A deterministic exported-skin fixture: bypass transitions, sample full cycles.
  // Verify deformed sole VERTICES in fixed world coordinates, not just bone motion.
  const sample=(label,phase)=>{a.mixer.stopAllAction();const ac=a.actions[label];ac.reset().play();ac.setEffectiveWeight(1);ac.paused=true;ac.time=phase*ac.getClip().duration;a.mixer.update(0);a.object.updateMatrixWorld(true);skin.skeleton.update();};
  const bindFoot=skin.skeleton.bones.findIndex(b=>b.name==='footL'),inds=skin.geometry.attributes.skinIndex,weights=skin.geometry.attributes.skinWeight,vs=[];
  // Find actual fully-rigid left sole points in rest space, using the original
  // mesh's very lowest weighted vertices. glTF keeps the supplied UV topology.
  const pos=skin.geometry.attributes.position;
  for(let i=0;i<pos.count;i++){let w=0;for(let j=0;j<4;j++)if(inds.array[i*4+j]===bindFoot)w+=weights.array[i*4+j];if(w>.999&&pos.getY(i)<.055)vs.push(i);}
  if(!vs.length)throw new Error('No actual weighted sole samples');
  summary.soleSamples=vs.length;
  for(const [label,stride,stance]of [['walk',1.1,.62],['run',2.4,.4],['sprint',3,.31],['walk_back',1.1,.62],['run_right',2.4,.4]]){
   let origin;const values=[];a.object.rotation.set(0,Math.PI,0);
   for(let i=0;i<8;i++){const phase=.045+i*(stance-.09)/7;sample(label,phase);
    // World forward is -Z, backward +Z, body-right +X at this root heading.
    a.object.position.set(label.endsWith('right')?stride*phase:0,-.024,label.endsWith('back')?stride*phase:label.endsWith('right')?0:-stride*phase);a.object.updateMatrixWorld(true);
    const ps=vs.map(j=>skin.localToWorld(skin.getVertexPosition(j,new V()))),contact=ps.reduce((a,b)=>a.add(b),new V()).multiplyScalar(1/ps.length);
    if(!origin)origin=contact.clone();values.push(contact.distanceTo(origin));
   }
   summary.contacts.push({clip:label,maxSoleDriftMm:Math.max(...values)*1000});
  }
  a.object.position.set(0,-.024,0);a.object.rotation.set(0,Math.PI,0);
  for(const [label,phase]of [['slide',.5],['jump',.5],['walk',.25],['run',.25]]){
   sample(label,phase);let min=Infinity,max=-Infinity;for(let i=0;i<pos.count;i++){const pt=skin.localToWorld(skin.getVertexPosition(i,new V()));min=Math.min(min,pt.y);max=Math.max(max,pt.y);}
   summary.bounds[label]={minYmm:min*1000,maxYmm:max*1000};
   if(label==='jump'){const l=a.object.getObjectByName('footL').getWorldPosition(new V()),right=a.object.getObjectByName('footR').getWorldPosition(new V());summary.jumpFeet={left:l.toArray(),right:right.toArray(),foreAftSeparationMm:Math.abs(l.z-right.z)*1000,heightDifferenceMm:Math.abs(l.y-right.y)*1000};}
  }
  // Restore a fresh actor so this fixture's explicit mixer resets cannot affect play.
  v.start(r);return summary;
 });
 for(const c of evidence.contacts)expect(c.maxSoleDriftMm,c.clip).toBeLessThan(3);
 expect(evidence.jumpFeet.foreAftSeparationMm).toBeGreaterThan(300);expect(evidence.jumpFeet.heightDifferenceMm).toBeGreaterThan(100);
 expect(evidence.bounds.slide.maxYmm).toBeLessThan(900);
 console.log(JSON.stringify(evidence,null,2));writeFileSync('artifacts/player-motion/exported-contact.json',JSON.stringify(evidence,null,2));
 await p.keyboard.down('w');await p.waitForTimeout(1200);await p.keyboard.up('w');await p.waitForTimeout(350);await p.screenshot({path:'artifacts/player-motion/game-grounded.png'});
 expect(errors).toEqual([]);
}finally{await b.close();}
