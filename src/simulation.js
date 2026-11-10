// Survivor Runs authoritative local simulation. Continuous movement, not lane indices.
import {WEAPONS,DOGS,CHARACTERS,MISSIONS,LOCATIONS,clamp} from './config.js';
import {overlap,occluded} from './collision.js';import {movement,jump,slide,dodge,approach} from './systems/movement.js';
import {fire,hurt,reloadGun,updateReload,acquire} from './systems/combat.js';
import {updateInfected} from './systems/infected.js';import {updateCompanion} from './systems/companion.js';
import {rng,create,generate} from './systems/encounters.js';import {objectivesMet,settle} from './systems/missions.js';
import {SPAWNS} from './systems/world.js';
export {rng,approach};
export class Run {
 constructor(profile,{seed=Date.now(),mission=null}={}){
  this.profile=profile;this.random=rng(seed);this.seed=seed;this.mission=MISSIONS.find(m=>m.id===mission)||null;this.locationOffset=Math.max(0,LOCATIONS.findIndex(l=>l.id===profile.location))*240;
  this.phase='running';this.distance=0;this.time=0;this.x=0;this.vx=0;this.y=0;this.vy=0;this.steer=0;this.stamina=100;this.aimed=false;this.sprinting=false;this.dodgeDir=1;
  [this.x,this.s]=SPAWNS[this.locationOffset/240];this.vs=0;this.moveSpeed=0;this.heading=0;this.viewYaw=0;this.sectors=new Map();this.activeSector=null;
  this.groundTravel=0;this.jumpActive=false;this.jumpElapsed=0;this.landing=0;
  for(const k of ['slide','stumble','dodgeTime','invulnerable','shotPulse','cooldown','reload','recoil','dogCommandTimer'])this[k]=0;
  this.maxHp=CHARACTERS[profile.character].hp;this.hp=this.maxHp;this.kills=0;this.dogKills=0;this.headshots=0;this.shots=0;this.hits=0;this.supplies=0;this.rescues=0;this.damageTaken=0;this.score=0;this.medkits=0;
  this.weapon=profile.weapon;this.weapons={};this.grant(this.weapon);this.reloadWeapon=null;this.aim={origin:[0,1.32,0],direction:[0,0,-1]};
  this.entities=[];this.events=[];this.id=0;this.nextRow=34;this.nextSupply=46;this.nextMissionSupply=45;this.safeGap=0;this.rescueSpawned=false;
  const cfg=DOGS[profile.dog];this.dog={x:this.x-1.2,s:this.s-.7,hp:cfg.hp,maxHp:cfg.hp,state:'follow',target:null,cooldown:0,bite:0,react:0,jump:0,downTime:0,lastHurt:-10,stateTime:0,path:[],navTimer:0,facing:0};this.result=null;this.generate();
 }
 get spec(){return WEAPONS[this.weapon];}get ammo(){return this.weapons[this.weapon];}
 get speed(){return 4.7*(this.sprinting?1.65:1)*(this.reload>0?.82:1)*(this.aimed?.33:1)*(this.stumble>0?.5:1);}
 emit(type,data={}){this.events.push({type,...data});if(this.events.length>180)this.events.shift();}
 grant(key){if(!WEAPONS[key])return false;if(!this.weapons[key])this.weapons[key]={mag:WEAPONS[key].mag,reserve:WEAPONS[key].reserve};else this.weapons[key].reserve=Math.min(999,this.weapons[key].reserve+WEAPONS[key].mag*2);return true;}
 add(type,x,s,kind,extra={}){return create(this,type,x,s,kind,extra);}generate(){generate(this);}
 jump(){return jump(this);}crouch(){return slide(this);}dodge(dir){return dodge(this,dir);}
 fire(assisted=false){return fire(this,assisted);}reloadGun(){return reloadGun(this);}hurtZombie(e,d,source,zone){hurt(this,e,d,source,zone);}
 target(){return acquire(this);}blocked(e){return occluded(this,e);}
 setAim(ray){if(ray&&ray.direction.every(Number.isFinite)&&ray.origin.every(Number.isFinite)){this.aim=ray;this.muzzle=ray.muzzle;}}
 switchWeapon(key){const keys=Object.keys(this.weapons);key=key||keys[(keys.indexOf(this.weapon)+1)%keys.length];if(this.phase!=='running'||!this.weapons[key])return false;this.weapon=key;this.reload=0;this.reloadWeapon=null;this.cooldown=Math.max(this.cooldown,.18);this.emit('switch');return true;}
 damage(n,reason){if(this.invulnerable>0||this.phase!=='running')return;const amount=Math.min(this.hp,n);this.hp=Math.max(0,this.hp-n);this.damageTaken+=amount;this.invulnerable=.85;this.stumble=reason==='grab'?.8:.42;this.dog.react=.5;this.emit('damage',{reason,amount});if(!this.hp)this.finish(false);}
 collect(e){
  if(e.passed)return;this.supplies++;e.passed=true;
  if(e.kind==='med'){this.hp=Math.min(this.maxHp,this.hp+35);this.medkits=Math.min(3,this.medkits+1);this.dog.hp=Math.min(this.dog.maxHp,this.dog.hp+45);if(this.dog.state==='down')this.dog.state='return';}
  else if(e.kind==='weapon'){const keys=Object.keys(WEAPONS),next=keys[(keys.indexOf(this.weapon)+1)%keys.length];this.grant(next);this.switchWeapon(next);}
  else for(const k of Object.keys(this.weapons))this.weapons[k].reserve=Math.min(999,this.weapons[k].reserve+Math.max(10,WEAPONS[k].mag*2));
  this.emit('pickup',{kind:e.kind});
 }
 interact(){
  if(this.phase!=='running')return false;const person=this.entities.find(e=>e.type==='civilian'&&!e.passed&&Math.hypot(e.s-this.s,e.x-this.x)<3);
  if(person){person.passed=true;this.rescues++;this.emit('rescue');return true;}
  if(this.medkits>0&&this.dog.hp<this.dog.maxHp){this.medkits--;this.dog.hp=Math.min(this.dog.maxHp,this.dog.hp+60);this.dog.state='return';this.dog.downTime=0;this.emit('dogRecover');return true;}
  return false;
 }
 commandDog(){if(this.dog.hp<=0)return false;this.dog.cooldown=0;this.dog.state='follow';this.dog.target=null;this.dogCommandTimer=3;this.emit('command');return true;}
 step(dt,input={}){if(this.phase!=='running')return;dt=clamp(dt,0,.12);while(dt>1e-7){const s=Math.min(dt,1/60);this.tick(s,input);dt-=s;}}
 tick(dt,input){
  if(this.phase!=='running')return;this.time+=dt;movement(this,dt,input);updateReload(this,dt);updateInfected(this,dt);updateCompanion(this,dt);
  if(input.fire)this.fire(false);else if(input.auto&&this.target())this.fire(true);
  for(const e of this.entities){if(e.passed)continue;
   if(e.type==='pickup'&&Math.hypot(e.s-this.s,e.x-this.x)<1.1&&this.y<1.2)this.collect(e);
  }
  // Sector-owned records persist on backtracking. No forward-only despawn plane.
  this.generate();this.score=Math.floor(this.distance)+this.kills*60+this.headshots*25+this.supplies*25+this.rescues*250;
  if(objectivesMet(this))this.finish(true);
 }
 finish(success){settle(this,success);}
}
