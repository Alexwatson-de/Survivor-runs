// Original procedural audio. Distance/HRTF threat cues; six weapon signatures, surface
// footsteps, breath, handling, companion calls and an adaptive low-level tension score.
export class Soundscape {
 constructor(settings){this.settings=settings;this.ctx=null;this.lastStep=0;this.lastGrowl=0;this.lastBeat=0;this.lastCreak=0;this.counts={};}
 async unlock(){
  if(!this.ctx){
   this.ctx=new AudioContext();this.master=this.ctx.createGain();this.master.gain.value=this.settings.volume;this.limiter=this.ctx.createDynamicsCompressor();this.limiter.threshold.value=-3;this.limiter.knee.value=5;this.limiter.ratio.value=8;this.master.connect(this.limiter).connect(this.ctx.destination);
   this.noise=this.ctx.createBuffer(1,this.ctx.sampleRate*2,this.ctx.sampleRate);const d=this.noise.getChannelData(0);let n=325;for(let i=0;i<d.length;i++){n=n*16807%2147483647;d[i]=n/2147483647*2-1;}
   const wind=this.ctx.createBufferSource();wind.buffer=this.noise;wind.loop=true;const filter=this.ctx.createBiquadFilter();filter.type='lowpass';filter.frequency.value=260;this.wind=this.ctx.createGain();this.wind.gain.value=.04;wind.connect(filter).connect(this.wind).connect(this.master);wind.start();
   this.score=this.ctx.createGain();this.score.gain.value=.006;this.score.connect(this.master);for(const f of [43.65,65.4,87.3]){const o=this.ctx.createOscillator();o.type='sine';o.frequency.value=f;const g=this.ctx.createGain();g.gain.value=.30;o.connect(g).connect(this.score);o.start();}
  }
  await this.ctx.resume();
 }
 set(s){this.settings=s;if(this.master)this.master.gain.setTargetAtTime(s.volume,this.ctx.currentTime,.08);}
 bus(e,r){
  if(!r||e.x===undefined||e.s===undefined)return this.master;const p=this.ctx.createPanner();p.panningModel='HRTF';p.distanceModel='inverse';p.refDistance=3;p.maxDistance=75;p.rolloffFactor=.9;const dx=e.x-r.x,dz=r.s-e.s,yaw=r.viewYaw||0;p.positionX.value=dx*Math.cos(yaw)+dz*Math.sin(yaw);p.positionY.value=.9;p.positionZ.value=-dx*Math.sin(yaw)+dz*Math.cos(yaw);p.connect(this.master);setTimeout(()=>p.disconnect(),2400);return p;
 }
 noiseBurst(duration,volume,cutoff=2500,delay=0,bus=this.master,high=0){if(!this.ctx)return;const t=this.ctx.currentTime+delay,s=this.ctx.createBufferSource(),f=this.ctx.createBiquadFilter(),g=this.ctx.createGain();s.buffer=this.noise;f.type=high?'highpass':'lowpass';f.frequency.value=high||cutoff;g.gain.setValueAtTime(volume,t);g.gain.exponentialRampToValueAtTime(.0001,t+duration);s.connect(f).connect(g).connect(bus);s.start(t);s.stop(t+duration+.02);s.onended=()=>{s.disconnect();f.disconnect();g.disconnect();};}
 tone(freq,end,dur,vol=.1,type='sine',delay=0,bus=this.master){if(!this.ctx)return;const t=this.ctx.currentTime+delay,o=this.ctx.createOscillator(),g=this.ctx.createGain();o.type=type;o.frequency.setValueAtTime(freq,t);o.frequency.exponentialRampToValueAtTime(Math.max(10,end),t+dur);g.gain.setValueAtTime(vol,t);g.gain.exponentialRampToValueAtTime(.0001,t+dur);o.connect(g).connect(bus);o.start(t);o.stop(t+dur+.02);o.onended=()=>{o.disconnect();g.disconnect();};}
 event(e,r){
  if(!this.ctx)return;this.counts[e.type]=(this.counts[e.type]||0)+1;const b=this.bus(e,r);
  if(e.type==='shot'){
   const specs={pistol:[170,3600,.30,.16],revolver:[115,2700,.42,.27],shotgun:[78,1800,.58,.43],rifle:[160,4100,.28,.15],smg:[220,4800,.22,.10],hunting:[95,3000,.43,.34]},[pitch,filter,vol,tail]=specs[e.weapon];
   this.noiseBurst(tail,vol,filter);this.noiseBurst(.025,vol*.8,9000,0,this.master,1100);this.tone(pitch,33,tail,.18);this.noiseBurst(.4,.045,650,.06);this.tone(1600,850,.065,.018,'triangle',.10);return;
  }
  switch(e.type){
   case 'reload':this.noiseBurst(.11,.12,3500);this.tone(710,220,.08,.035,'square');this.noiseBurst(.12,.12,4200,e.duration*.65);this.noiseBurst(.045,.15,5100,e.duration*.91);break;
   case 'loaded':this.noiseBurst(.045,.11,6200);break;
   case 'empty':this.tone(280,165,.04,.045,'square');break;
   case 'bark':for(const delay of [0,.17]){this.tone(165,80,.15,.14,'sawtooth',delay,b);this.noiseBurst(.13,.15,900,delay,b);}break;
   case 'bite':this.noiseBurst(.15,.13,600,0,b);this.tone(100,70,.3,.07,'sawtooth',0,b);break;
   case 'dogHurt':this.tone(440,240,.35,.085,'triangle');this.noiseBurst(.2,.06,1600);break;
   case 'emerge':case 'threat':this.tone(90+(e.id%5)*11,42,.68,.12,'sawtooth',0,b);this.noiseBurst(.65,.10,480,0,b);break;
   case 'hit':this.noiseBurst(e.zone==='head'?.14:.19,.14,750,0,b);break;
   case 'impact':this.noiseBurst(.5,.28,1100);this.tone(68,26,.4,.21);break;
   case 'damage':this.noiseBurst(.26,.12,650);this.tone(120,50,.3,.11);break;
   case 'jump':this.noiseBurst(.13,.10,900);break;
   case 'slide':this.noiseBurst(.7,.14,1500);break;
   case 'pickup':this.tone(520,780,.15,.03,'triangle');this.tone(780,1040,.18,.025,'triangle',.12);break;
   case 'rescue':this.tone(390,520,.3,.04,'triangle');this.tone(585,780,.4,.025,'triangle',.15);break;
   case 'finish':this.tone(87,32,1.1,.07);break;
  }
 }
 update(r,dt){
  if(!this.ctx)return;const nearby=r.entities.filter(e=>e.type==='zombie'&&e.hp>0&&Math.hypot(e.x-r.x,e.s-r.s)<24),pressure=Math.min(1,nearby.length/5+(r.hp<30?.4:0));this.score.gain.setTargetAtTime(r.phase==='running'?.007+pressure*.019:.004,this.ctx.currentTime,.8);this.wind.gain.setTargetAtTime(.03+(r.sprinting?.015:0),this.ctx.currentTime,.5);
  if(r.phase!=='running')return;
  const step=r.sprinting?.25:.38;if(r.moveSpeed>.3&&r.time-this.lastStep>step&&r.y<.05&&r.slide<=0){this.lastStep=r.time;const asphalt=r.x>48;this.noiseBurst(asphalt?.07:.13,asphalt?.065:.10,asphalt?1500:650);this.tone(asphalt?150:78,35,.09,.035);if(r.sprinting)this.noiseBurst(.2,.03,800,0,this.master,300);}
  if(nearby.length&&r.time-this.lastGrowl>3.7){this.lastGrowl=r.time;const e=nearby[0],b=this.bus(e,r);this.tone(82,40,.7,.09,'sawtooth',0,b);this.noiseBurst(.7,.08,360,0,b);}
  if(pressure>.3&&r.time-this.lastBeat>1.1-pressure*.45){this.lastBeat=r.time;this.tone(53,30,.2,.024+pressure*.02);this.tone(58,28,.16,.018,'sine',.17);}
  if(r.time-this.lastCreak>9){this.lastCreak=r.time;const b=this.bus({x:r.x+5,s:r.s+18},r);this.tone(650,240,1.3,.014,'triangle',0,b);this.noiseBurst(1.3,.018,700,0,b);}
 }
}
