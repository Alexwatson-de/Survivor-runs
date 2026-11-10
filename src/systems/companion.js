import {DOGS,clamp} from '../config.js';import {hurt} from './combat.js';import {findPath} from './navigation.js';
export function updateCompanion(r,dt){
 const d=r.dog,cfg=DOGS[r.profile.dog],mode=r.profile.settings.companionMode;d.cooldown=Math.max(0,d.cooldown-dt);d.bite=Math.max(0,d.bite-dt);d.react=Math.max(0,d.react-dt);d.jump=Math.max(0,d.jump-dt);d.stateTime+=dt;d.navTimer-=dt;
 if(d.hp<=0){d.hp=0;d.state='down';d.downTime+=dt;d.target=null;if(d.downTime>15){d.hp=cfg.hp*.35;d.downTime=0;d.state='return';r.emit('dogRecover');}return;}
 d.downTime=0;const reach=cfg.reach*(mode==='scout'?1.25:mode==='aggressive'?1.15:.72);
 let target=r.entities.find(e=>e.id===d.target&&e.type==='zombie'&&e.hp>0&&e.state!=='emerge'&&Math.hypot(e.x-r.x,e.s-r.s)<reach+8);
 if(d.hp<cfg.hp*.24){target=null;d.target=null;d.state='retreat';}
 if(!target&&d.cooldown<=0&&d.state!=='retreat'){
  target=r.entities.filter(e=>e.type==='zombie'&&e.hp>0&&e.state!=='emerge'&&Math.hypot(e.x-r.x,e.s-r.s)<reach).sort((a,b)=>Math.hypot(a.x-r.x,a.s-r.s)-Math.hypot(b.x-r.x,b.s-r.s))[0];
  if(target){d.target=target.id;d.state='attack';d.stateTime=0;d.navTimer=0;r.emit('bark',{x:d.x,s:d.s});}
 }
 if(!target&&d.state==='attack'){d.target=null;d.state='return';d.navTimer=0;}
 const yaw=r.heading||0,goal=target?{x:target.x,s:target.s-.45}:{x:clamp(r.x-1.15*Math.cos(yaw)-.65*Math.sin(yaw),-142,142),s:clamp(r.s+1.15*Math.sin(yaw)-.65*Math.cos(yaw),-142,142)};
 if(d.navTimer<=0){d.path=findPath(d,goal,r.entities);d.navTimer=.35;d.pathGoal=goal;}
 // Progress along a collision-free corridor. The last small approach is bounded by the same grid.
 let waypoint=d.path[0];if(waypoint&&Math.hypot(d.x-waypoint.x,d.s-waypoint.s)<.40){d.path.shift();waypoint=d.path[0];}
 if(!waypoint&&Math.hypot(d.x-goal.x,d.s-goal.s)<1)waypoint=goal;
 if(waypoint){const dx=waypoint.x-d.x,ds=waypoint.s-d.s,length=Math.hypot(dx,ds),speed=(target?cfg.speed:r.speed+4),step=Math.min(length,speed*dt);if(length>.001){d.x+=dx/length*step;d.s+=ds/length*step;d.facing=Math.atan2(dx,-ds);}}
 if(target&&Math.hypot(target.x-d.x,target.s-d.s)<1.1&&d.bite<=0){
  hurt(r,target,cfg.damage*(1+.18*r.profile.upgrades.dog)*(mode==='aggressive'?1.12:1),'dog');d.bite=.48;d.cooldown=Math.max(.8,cfg.cooldown-.18*r.profile.upgrades.dog);d.target=null;d.state='return';d.stateTime=0;d.navTimer=0;r.emit('bite',{x:d.x,s:d.s});
 }
 if(!target&&Math.hypot(d.x-goal.x,d.s-goal.s)<1.0&&d.state!=='retreat')d.state='follow';
 if(r.time-d.lastHurt>4&&!target)d.hp=Math.min(cfg.hp,d.hp+dt*(d.state==='retreat'?5:2));
 if(d.state==='retreat'&&d.hp>cfg.hp*.55){d.state='return';d.navTimer=0;}
 if(r.entities.some(e=>e.type==='obstacle'&&e.kind==='low_log'&&Math.abs(e.x-d.x)<1.5&&Math.abs(e.s-d.s)<3)&&d.jump<=0)d.jump=.7;
 d.x=clamp(d.x,-143,143);d.s=clamp(d.s,-143,143);
}
