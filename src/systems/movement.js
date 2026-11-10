import {CHARACTERS,clamp} from '../config.js';
import {WORLD_HALF} from './world.js';
import {overlap} from '../collision.js';
export const approach=(a,b,s)=>a+clamp(b-a,-s,s);
export function movement(r,dt,input){
 if(r.stamina<=2)r.sprintExhausted=true;if(!input.sprint||r.stamina>25)r.sprintExhausted=false;
 r.aimed=!!input.aim;
 let ax=clamp(Number(input.axis)||0,-1,1),f=clamp(Number(input.forward)||0,-1,1),len=Math.hypot(ax,f);if(len>1){ax/=len;f/=len;}
 const moving=len>.01||r.dodgeTime>0;
 r.sprinting=moving&&!!input.sprint&&!r.sprintExhausted&&r.stamina>2&&r.reload<=0&&!r.aimed&&r.slide<=0&&r.stumble<=0;
 if(r.sprinting)r.stamina=Math.max(0,r.stamina-dt*21);else r.stamina=Math.min(100,r.stamina+dt*CHARACTERS[r.profile.character].regen);
 const yaw=r.viewYaw||0,dx=ax*Math.cos(yaw)+f*Math.sin(yaw),ds=-ax*Math.sin(yaw)+f*Math.cos(yaw);
 const burst=r.dodgeTime>0,tx=burst?r.dodgeDir*10*Math.cos(yaw):dx*r.speed,ts=burst?-r.dodgeDir*10*Math.sin(yaw):ds*r.speed;
 // A real slide coasts along its entry direction and slows, rather than playing
 // a crouch pose over the ordinary walking controller. Other movement is unchanged.
 const sliding=r.slide>0,slideSpeed=sliding?(r.slideEntrySpeed||4.6)*(.35+.65*r.slide/.92):0;
 const targetX=sliding?r.slideDirX*slideSpeed:tx,targetS=sliding?r.slideDirS*slideSpeed:ts;
 r.steer=ax;const dvx=targetX-r.vx,dvs=targetS-r.vs,delta=Math.hypot(dvx,dvs),blend=delta?Math.min(1,dt*(sliding?45:moving?24:34)/delta):0;r.vx+=dvx*blend;r.vs+=dvs*blend;
 const oldX=r.x,oldS=r.s;
 // Axis-separated capsule sweeps; contacts block motion, never erase the solid prop.
 r.x=clamp(r.x+r.vx*dt,-WORLD_HALF+.5,WORLD_HALF-.5);
 if(r.entities.some(e=>e.type==='obstacle'&&overlap(r,e))){r.x=oldX;r.vx=0;}
 r.s=clamp(r.s+r.vs*dt,-WORLD_HALF+.5,WORLD_HALF-.5);
 if(r.entities.some(e=>e.type==='obstacle'&&overlap(r,e))){r.s=oldS;r.vs=0;}
 const travelled=Math.hypot(r.x-oldX,r.s-oldS);r.moveSpeed=travelled/dt;r.distance+=travelled;
 if(!r.jumpActive&&!sliding&&r.dodgeTime<=0)r.groundTravel+=travelled;
 // Keep the gun facing the look direction during backward/sideways firing.
 if(r.aimed||input.fire)r.heading=yaw;else if(r.moveSpeed>.15)r.heading=Math.atan2(r.vx,r.vs);
 if(r.jumpActive)r.jumpElapsed+=dt;
 r.landing=Math.max(0,r.landing-dt);r.vy-=17*dt;r.y=Math.max(0,r.y+r.vy*dt);
 if(!r.y){r.vy=0;if(r.jumpActive){r.jumpActive=false;r.landing=.22;r.emit('land');}}
 for(const key of ['slide','stumble','dodgeTime','invulnerable','shotPulse','cooldown','dogCommandTimer'])r[key]=Math.max(0,r[key]-dt);
}
export function jump(r){if(r.phase!=='running'||r.jumpActive||r.y>.02||r.slide>0||r.stumble>.2)return false;r.vy=6.8;r.jumpActive=true;r.jumpElapsed=0;r.landing=0;r.stamina=Math.max(0,r.stamina-5);r.emit('jump');return true;}
export function slide(r){if(r.phase!=='running'||r.jumpActive||r.y>.02||r.slide>0)return false;r.slide=.92;r.landing=0;const speed=Math.hypot(r.vx,r.vs);r.slideDirX=speed>.1?r.vx/speed:Math.sin(r.heading);r.slideDirS=speed>.1?r.vs/speed:Math.cos(r.heading);r.slideEntrySpeed=Math.max(6.0,speed);r.stamina=Math.max(0,r.stamina-7);r.emit('slide');return true;}
export function dodge(r,dir){if(r.phase!=='running'||r.stamina<18||r.dodgeTime>0||r.slide>0)return false;r.dodgeDir=dir<0?-1:1;r.dodgeTime=.25;r.stamina-=18;r.emit('dodge');return true;}