import {WEAPONS,ENEMIES} from '../config.js';import {relative,rayEllipsoid,coverDistance,occluded} from '../collision.js';
export function zones(r,e){const p=relative(r,e),s=ENEMIES[e.kind],crawl=e.state==='crawl'||e.kind==='stalker'&&e.state!=='lunge',h=crawl?.80:s.height;
 return [{name:'head',center:[p[0],h-.13,p[2]],r:[.12*(s.height/1.82),.145,.13]},{name:'torso',center:[p[0],crawl?.43:1.16*(h/1.82),p[2]],r:[s.radius,.39*(h/1.82),.20]},{name:'leg',center:[p[0],.43,p[2]],r:[s.radius*.90,.36,.15]}];}
export function acquire(r){const yaw=r.viewYaw||0;return r.entities.filter(e=>{if(e.type!=='zombie'||e.hp<=0||e.state==='emerge')return false;const dx=e.x-r.x,ds=e.s-r.s,d=Math.hypot(dx,ds);return d<r.spec.range&&d>.5&&(dx*Math.sin(yaw)+ds*Math.cos(yaw))/d>.94&&!occluded(r,e);}).sort((a,b)=>Math.hypot(a.x-r.x,a.s-r.s)-Math.hypot(b.x-r.x,b.s-r.s))[0]||null;}
export function aimAt(r,e,zone='torso'){const z=zones(r,e).find(z=>z.name===zone),origin=[r.x,1.32+r.y,0],v=z.center.map((a,i)=>a-origin[i]),length=Math.hypot(...v);return {origin,direction:v.map(a=>a/length)};}
export function trace(r,origin,direction){
 let best={distance:Math.min(r.spec.range,coverDistance(r,origin,direction)),entity:null,zone:null};
 for(const e of r.entities){if(e.type!=='zombie'||e.hp<=0||e.state==='emerge')continue;for(const z of zones(r,e)){const t=rayEllipsoid(origin,direction,z.center,z.r);if(t<best.distance)best={distance:t,entity:e,zone:z.name};}}
 return best;
}
export function fire(r,assist=false){
 if(r.phase!=='running'||r.reload>0||r.cooldown>0||r.stumble>.4)return false;
 if(r.ammo.mag<=0){r.cooldown=.28;r.emit('empty');return false;}
 let aim=r.aim;if(assist){const e=acquire(r);if(!e)return false;aim=aimAt(r,e);}
 r.heading=Math.atan2(aim.direction[0],-aim.direction[2]);r.ammo.mag--;r.shots++;r.cooldown=r.spec.interval;r.shotPulse=.15;r.recoil+=r.spec.recoil;
 const hits=new Map();let endpoint=null;const pellets=r.spec.pellets||1;
 const sight=trace(r,aim.origin,aim.direction),point=aim.origin.map((v,i)=>v+aim.direction[i]*Math.min(r.spec.range,sight.distance));
 const origin=r.muzzle||[r.x-.10,1.31+r.y,-.49-r.spec.muzzle],base=point.map((v,i)=>v-origin[i]),baseLength=Math.hypot(...base);for(let i=0;i<3;i++)base[i]/=baseLength;
 for(let i=0;i<pellets;i++){
  const spread=r.spec.spread*(r.aimed?.42:1)*(Math.abs(r.vx)>1?1.4:1);const d=[base[0]+(r.random()-.5)*spread,base[1]+(r.random()-.5)*spread,base[2]],length=Math.hypot(...d);for(let j=0;j<3;j++)d[j]/=length;
  const hit=trace(r,origin,d);endpoint=origin.map((v,j)=>v+d[j]*hit.distance);
  if(hit.entity){const current=hits.get(hit.entity)||{damage:0,zone:hit.zone};const armor=hit.entity.kind==='military'&&hit.zone==='torso'?ENEMIES.military.armor:1;
   current.damage+=r.spec.damage*(hit.zone==='head'?2.5:hit.zone==='leg'?.58:1)*armor*(1+.12*r.profile.upgrades.weapon);if(hit.zone==='head')current.zone='head';hits.set(hit.entity,current);}
 }
 r.emit('shot',{weapon:r.weapon,end:endpoint,recoil:r.spec.recoil});if(hits.size)r.hits++;
 for(const [e,hit]of hits)hurt(r,e,hit.damage,'gun',hit.zone);return true;
}
export function hurt(r,e,damage,source,zone='torso'){
 if(e.hp<=0)return;e.hp=Math.max(0,e.hp-damage);e.hit=.32;e.hitZone=zone;
 if(zone==='leg'){e.slow=2.2;e.reaction='hit_leg';}else e.reaction=zone==='head'?'hit_head':'hurt';
 r.emit('hit',{id:e.id,x:e.x,s:e.s,source,zone,damage});
 if(!e.hp){e.state='die';e.timer=1.5;r.kills++;if(source==='dog')r.dogKills++;if(zone==='head')r.headshots++;r.emit('kill',{id:e.id,source,zone});}
}
export function reloadGun(r){if(r.phase!=='running'||r.reload>0||r.ammo.mag>=r.spec.mag||r.ammo.reserve<=0)return false;r.reload=r.spec.reload;r.reloadWeapon=r.weapon;r.sprinting=false;r.emit('reload',{duration:r.reload});return true;}
export function updateReload(r,dt){r.recoil=Math.max(0,r.recoil-dt*.14);if(r.reload<=0)return;r.reload=Math.max(0,r.reload-dt);if(r.reload===0){const a=r.weapons[r.reloadWeapon],spec=WEAPONS[r.reloadWeapon],n=Math.min(spec.mag-a.mag,a.reserve);a.mag+=n;a.reserve-=n;r.reloadWeapon=null;r.emit('loaded');}}
