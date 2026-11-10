import {Library} from './assets.js';import {GameView} from './render.js';import {Run} from './simulation.js';import {Soundscape} from './audio.js';import {Interface,$} from './ui.js';import {Controls} from './controls.js';import {normalizeProfile,MISSIONS} from './config.js';
const STORAGE='survivor-runs.profile.v2';let profile;try{profile=normalizeProfile(JSON.parse(localStorage.getItem(STORAGE)||localStorage.getItem('ashfall-run.profile.v1')));}catch{profile=normalizeProfile(null);}
if(matchMedia('(prefers-reduced-motion: reduce)').matches){profile.settings.shake=false;profile.settings.weather=false;}
let view,run,ui,controls,state='loading',last=performance.now(),mission=null,resultDelay=0;const samples=[];const audio=new Soundscape(profile.settings);
function save(){try{localStorage.setItem(STORAGE,JSON.stringify(profile));}catch{ui?.notify('SAVE UNAVAILABLE / BROWSER STORAGE IS FULL');}}
function preview(){run=new Run(profile,{seed:5042});view.start(run);}
function home(){controls?.clear();state='menu';preview();ui.render('home');}
function settings(){save();audio.set(profile.settings);view?.applySettings(profile.settings);ui?.soundLabel();}
function start(selected=null){
 if(selected){const i=MISSIONS.findIndex(m=>m.id===selected);if(i<0||i>0&&!profile.completed.includes(MISSIONS[i-1].id))return;}
 controls?.clear();if(controls)controls.aimToggle=false;mission=selected;run=new Run(profile,{mission});view.start(run);view.rigCamera.pointer={x:.5,y:.46};controls?.reticle();ui.begin();state='play';resultDelay=0;audio.lastStep=-1;audio.lastGrowl=-4;audio.unlock().catch(()=>{});last=performance.now();
}
function pause(toggle=true){if(state==='paused'){if(toggle)resume();return;}if(state!=='play'||run.phase!=='running')return;state='paused';controls?.clear();ui.pause();}
function resume(){if(state!=='paused')return;state='play';$('modal').hidden=true;controls?.clear();audio.unlock().catch(()=>{});last=performance.now();}
function leave(){run.finish(false);save();home();}
const lib=new Library();
try{
 await lib.load((p,name)=>{$('loadbar').style.width=p*100+'%';$('loadtext').textContent=name.replaceAll('_',' ')+' / '+Math.round(p*100)+'%';});
 view=new GameView($('world'),lib,profile.settings);ui=new Interface(profile,{start,pause:()=>pause(),resume,leave,home,restart:()=>start(mission),save,settings,preview});home();
 controls=new Controls({run:()=>run,state:()=>state,view,audio,pause,toggleAssist:()=>{profile.settings.autofire=!profile.settings.autofire;save();ui.notify(profile.settings.autofire?'ASSISTED FIRE ON / RELOAD IS MANUAL':'MANUAL AIM + FIRE');}});
 $('loading').hidden=true;save();
}catch(error){console.error(error);$('loadtext').textContent='World could not load: '+error.message+'. Reload to retry.';throw error;}
function frame(now){
 const elapsed=Math.max(0,(now-last)/1000),dt=Math.min(.075,elapsed);last=now;samples.push(elapsed*1000);if(samples.length>180)samples.shift();
 if(state==='play'){
  run.setAim(controls.ray());run.step(dt,{...controls.sample(),auto:profile.settings.autofire});view.syncWeapon(run);
  while(run.events.length){const e=run.events.shift();view.event(e,run);ui.event(e,run);audio.event(e,run);if(e.type==='finish')save();}
  audio.update(run,dt);
  if(run.phase!=='running'){resultDelay+=dt;if(resultDelay>1.25){state='result';controls.clear();ui.result(run);}}
 }
 const section=view.update(run,state==='paused'?0:dt,state==='menu');if(state!=='menu')ui.update(run,section,dt);requestAnimationFrame(frame);
}
last=performance.now();requestAnimationFrame(frame);
// Opt-in instrumentation only. Fixtures must remain explicitly labeled in test reports.
if(new URLSearchParams(location.search).has('qa'))window.__SURVIVOR={
 get run(){return run;},get state(){return state;},get profile(){return profile;},view,lib,audio,controls,start,home,pause,resume,save,
 snapshot(){return {state,phase:run.phase,distance:run.distance,x:run.x,s:run.s,vx:run.vx,vs:run.vs,yaw:run.viewYaw,moveSpeed:run.moveSpeed,y:run.y,slide:run.slide,stamina:run.stamina,sprint:run.sprinting,aimed:run.aimed,hp:run.hp,weapon:run.weapon,ammo:{...run.ammo},shots:run.shots,kills:run.kills,dogKills:run.dogKills,headshots:run.headshots,reload:run.reload,supplies:run.supplies,rescues:run.rescues,damage:run.damageTaken,time:run.time,dog:{...run.dog},entities:run.entities.map(e=>({...e})),render:view.stats(),frameMs:samples.reduce((a,b)=>a+b,0)/Math.max(1,samples.length),clips:{player:view.player.clip,dog:view.dog.clip},assets:lib.audit};}
};
