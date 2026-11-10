import {pathCenter} from './config.js';
// Envelopes derive from the Blender props; player capsule is 580 mm wide, not a lane.
export const OBSTACLES={
 car_wreck:{x:.96,z:2.18,y0:0,y1:1.54},truck_wreck:{x:1.08,z:2.98,y0:0,y1:2.1},military_truck:{x:1.08,z:2.98,y0:0,y1:2.35},
 barricade:{x:1.18,z:.47,y0:0,y1:1.25},low_log:{x:1.46,z:.46,y0:0,y1:.72},overhead:{x:1.28,z:.20,y0:1.42,y1:2.05},barrel:{x:.30,z:.30,y0:0,y1:.75}
};
export function relative(run,e){return [e.x,0,run.s-e.s];}
export function bounds(e){const b=e.box||OBSTACLES[e.kind];if(!b)return null;return Math.abs(Math.sin(e.rot||0))>.5?{...b,x:b.z,z:b.x}:b;}
export function overlap(run,e){
 const c=bounds(e)||{x:.45,z:.45,y0:0,y1:.55},p=relative(run,e),dx=Math.abs(run.x-p[0]);
 if(dx>c.x+.29||Math.abs(p[2])>c.z+.28)return false;
 const floor=e.kind==='overhead'&&dx>1.01?0:c.y0;return run.y+(run.slide>0?.88:1.79)>floor&&run.y<c.y1;
}
export function rayEllipsoid(origin,dir,center,radii){
 let a=0,b=0,c=-1;for(let i=0;i<3;i++){const v=(origin[i]-center[i])/radii[i],d=dir[i]/radii[i];a+=d*d;b+=2*v*d;c+=v*v;}
 const disc=b*b-4*a*c;if(disc<0)return Infinity;const t=(-b-Math.sqrt(disc))/(2*a);return t>.03?t:Infinity;
}
export function rayBox(origin,dir,min,max){
 let near=0,far=Infinity;for(let i=0;i<3;i++){if(Math.abs(dir[i])<1e-8){if(origin[i]<min[i]||origin[i]>max[i])return Infinity;continue;}let a=(min[i]-origin[i])/dir[i],b=(max[i]-origin[i])/dir[i];if(a>b)[a,b]=[b,a];near=Math.max(near,a);far=Math.min(far,b);if(near>far)return Infinity;}return far>.03?near:Infinity;
}
export function coverDistance(run,origin,dir){let hit=Infinity;for(const e of run.entities){if(e.type!=='obstacle')continue;const b=bounds(e);if(!b)continue;const p=relative(run,e);hit=Math.min(hit,rayBox(origin,dir,[p[0]-b.x,b.y0,p[2]-b.z],[p[0]+b.x,b.y1,p[2]+b.z]));}return hit;}
export function occluded(run,e){const p=relative(run,e),o=[run.x,1.3,0],delta=[p[0]-o[0],(e.kind==='stalker'?.55:1.25)-o[1],p[2]],length=Math.hypot(...delta),d=delta.map(v=>v/length);return coverDistance(run,o,d)<length-.3;}
