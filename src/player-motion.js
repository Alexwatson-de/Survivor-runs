import {clamp} from './config.js';
// Matches Blender player-motion.py: distance per FULL alternating-leg cycle.
// The old arbitrary speed/4.7 multiplier played a tiny walk stride at run speed.
export const GAIT_STRIDES={walk:1.10,run:2.40,sprint:3.00};
export const JUMP_FLIGHT=.8,LAND_DURATION=.22,SLIDE_DURATION=.92,GROUND_Y=-.025;
export function motionState(r,menu=false){
 if(menu||r.phase==='complete')return {clip:'idle'};
 if(r.phase==='dead')return {clip:'death',once:true};
 if(r.jumpActive)return {clip:'jump',phase:clamp(r.jumpElapsed/JUMP_FLIGHT,0,1)};
 if(r.slide>0)return {clip:'slide',phase:clamp(1-r.slide/SLIDE_DURATION,0,1)};
 if(r.landing>0&&r.moveSpeed<.4)return {clip:'land',phase:clamp(1-r.landing/LAND_DURATION,0,1)};
 if(r.dodgeTime>0)return {clip:'dodge',once:true};
 if(r.stumble>0)return {clip:'stumble',once:true};
 if(r.moveSpeed<.08)return {clip:'idle'};
 const base=r.moveSpeed<2.2?'walk':r.moveSpeed>6.1?'sprint':'run';
 // Normal free movement already faces its travel direction. Aim/fire can strafe
 // or backpedal; separate lower-body clips keep the gun facing the look direction.
 const forward=r.vx*Math.sin(r.heading)+r.vs*Math.cos(r.heading),right=r.vx*Math.cos(r.heading)-r.vs*Math.sin(r.heading);
 const octant=((Math.round(Math.atan2(right,forward)/(Math.PI/4))%8)+8)%8;
 const suffix=['','_fr','_right','_br','_back','_bl','_left','_fl'][octant];
 return {clip:(base==='sprint'&&suffix?'run':base)+suffix,gait:base==='sprint'&&suffix?'run':base};
}
export class PlayerMotion {
 constructor(actor,run){this.actor=actor;this.lastDistance=run.groundTravel??run.distance;this.phase=0;this.previous=null;this.clock=0;this.audit={};}
 update(run,dt,menu=false){
  const state=motionState(run,menu),distance=run.groundTravel??run.distance,travel=Math.max(0,distance-this.lastDistance);this.lastDistance=distance;
  const actor=this.actor,clip=actor.actions[state.clip]?state.clip:'idle';
  if(state.gait)this.phase=(this.phase+travel/GAIT_STRIDES[state.gait])%1;
  if(clip!==this.previous){this.clock=0;actor.play(clip,!!state.once,1,state.gait?.065:clip==='jump'||clip==='slide'?.035:.085);this.previous=clip;}
  this.clock+=dt;
  const action=actor.actions[clip];
  if(state.gait||state.phase!==undefined){action.paused=true;action.time=(state.gait?this.phase:state.phase)*action.getClip().duration;}
  else action.paused=false;
  actor.mixer.update(dt);actor.object.updateMatrixWorld(true);
  this.audit={clip,cycle:this.phase,phase:state.phase??null,travel,stride:state.gait?GAIT_STRIDES[state.gait]:null,grounded:!run.jumpActive};
 }
}
