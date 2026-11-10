import {test,expect} from '@playwright/test';
test('controlled audio fixture: generated gun, bark and impact signals are finite, distinct and non-silent',async({page})=>{
 await page.goto('/?qa=1');await page.waitForFunction(()=>window.__ASHFALL);await page.getByRole('button',{name:'BEGIN YOUR RUN'}).click();
 const result=await page.evaluate(async()=>{
  const a=window.__ASHFALL.audio,c=a.ctx;await c.resume();const analyser=c.createAnalyser();analyser.fftSize=2048;const mute=c.createGain();mute.gain.value=0;a.master.connect(analyser);analyser.connect(mute).connect(c.destination);
  const signals=[];
  for(const event of [{type:'shot',weapon:'pistol'},{type:'shot',weapon:'shotgun'},{type:'shot',weapon:'rifle'},{type:'bark'},{type:'impact'}]){
   let peak=0,sum=0,count=0;a.event(event);
   for(let i=0;i<10;i++){await new Promise(r=>setTimeout(r,20));const d=new Float32Array(analyser.fftSize);analyser.getFloatTimeDomainData(d);for(const x of d){peak=Math.max(peak,Math.abs(x));sum+=x*x;count++;}}
   signals.push({event:event.weapon||event.type,peak,rms:Math.sqrt(sum/count)});await new Promise(r=>setTimeout(r,450));
  }
  a.master.disconnect(analyser);analyser.disconnect();mute.disconnect();return {state:c.state,signals};
 });
 expect(result.state).toBe('running');for(const s of result.signals){expect(Number.isFinite(s.rms)).toBe(true);expect(s.peak).toBeGreaterThan(.005);expect(s.peak).toBeLessThan(1);}
 expect(new Set(result.signals.map(s=>s.rms.toFixed(4))).size).toBeGreaterThanOrEqual(4);console.log('AUDIO_SIGNAL',JSON.stringify(result));
});
