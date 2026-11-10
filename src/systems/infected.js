import {ENEMIES,clamp} from '../config.js';import {bounds} from '../collision.js';import {findPath} from './navigation.js';
export function updateInfected(r,dt){
 for(const e of r.entities){
  if(e.type!=='zombie')continue;e.hit=Math.max(0,e.hit-dt);e.slow=Math.max(0,e.slow-dt);e.attackCooldown=Math.max(0,e.attackCooldown-dt);const spec=ENEMIES[e.kind],playerDistance=Math.hypot(e.x-r.x,e.s-r.s);
  if(e.hp<=0){e.timer-=dt;continue;}
  if(e.state==='emerge'){if(playerDistance>(e.wake||28))continue;e.timer-=dt;if(e.timer>0)continue;e.state='wander';r.emit('emerge',{id:e.id,x:e.x,s:e.s});}
  const dogDistance=Math.hypot(e.x-r.dog.x,e.s-r.dog.s),targetsDog=r.dog.hp>0&&dogDistance<1.2&&dogDistance<playerDistance;
  const tx=targetsDog?r.dog.x:r.x,ts=targetsDog?r.dog.s:r.s;
  if(e.windup>0){
   e.windup-=dt;e.state=e.kind==='military'?'grab':'attack';
   if(e.windup<=0){const d=Math.hypot(e.x-tx,e.s-ts),ducked=!targetsDog&&r.slide>0&&['walker','military'].includes(e.kind);if(d<1.65&&!ducked){if(targetsDog){r.dog.hp=Math.max(0,r.dog.hp-spec.damage);r.dog.react=.6;r.dog.lastHurt=r.time;r.emit('dogHurt',{amount:spec.damage,x:e.x,s:e.s});}else r.damage(spec.damage,e.kind==='military'?'grab':'infected');}e.attackCooldown=1.25;e.state='chase';}continue;
  }
  if(playerDistance>28){e.state='wander';continue;}
  e.state=e.kind==='stalker'?(playerDistance<10?'lunge':'crawl'):e.kind==='runner'?'run':'chase';
  const speed=spec.speed*(e.slow>0?.38:1)*(e.hit>0?.25:1)*(e.state==='lunge'?1.7:1);
  e.navTimer=(e.navTimer||0)-dt;
  if(e.navTimer<=0){e.path=findPath(e,{x:tx,s:ts},r.entities);e.navTimer=.9+(e.id%5)*.07;}
  let w=e.path?.[0];if(w&&Math.hypot(e.x-w.x,e.s-w.s)<.45){e.path.shift();w=e.path[0];}
  if(!w&&Math.hypot(e.x-tx,e.s-ts)<1.6)w={x:tx,s:ts};
  if(w){const dx=w.x-e.x,ds=w.s-e.s,d=Math.hypot(dx,ds),step=Math.min(d,speed*dt);if(d>.001){const nx=e.x+dx/d*step,ns=e.s+ds/d*step;
   const blocked=r.entities.some(o=>{if(o.type!=='obstacle')return false;const b=bounds(o);return b&&Math.abs(nx-o.x)<b.x+spec.radius&&Math.abs(ns-o.s)<b.z+spec.radius;});
   if(!blocked){e.x=nx;e.s=ns;}
  }}
  e.x=clamp(e.x,-143,143);e.s=clamp(e.s,-143,143);
  if(Math.hypot(e.x-tx,e.s-ts)<1.35&&e.attackCooldown<=0){e.windup=e.kind==='brute'?.8:e.kind==='runner'?.32:.52;e.state='attack';r.emit('threat',{id:e.id,x:e.x,s:e.s,kind:e.kind});}
 }
}