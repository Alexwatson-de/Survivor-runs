import {ENEMIES} from '../config.js';import {OBSTACLES,bounds} from '../collision.js';
import {CHUNK,chunkLayout,seeded,worldKey,SPAWNS} from './world.js';
export const rng=seeded;
export function create(r,type,x,s,kind,extra={}){const cfg=ENEMIES[kind];const e={id:++r.id,type,kind,x,s,hp:cfg?.hp||1,state:type==='zombie'?'wander':'idle',timer:0,hit:0,slow:0,attackCooldown:0,windup:0,reaction:'hurt',passed:false,...extra};r.entities.push(e);return e;}
export function generate(r){
 if(r.nextRow===Infinity)return; // Explicit isolated-system fixtures only.
 const cx=Math.floor(r.x/CHUNK),cs=Math.floor(r.s/CHUNK),key=worldKey(cx,cs);if(r.activeSector===key)return;
 r.activeSector=key;const active=[];
 for(let x=cx-1;x<=cx+1;x++)for(let s=cs-1;s<=cs+1;s++){
  if(x< -3||x>2||s< -3||s>2)continue;const k=worldKey(x,s);
  if(!r.sectors.has(k)){
   const layout=chunkLayout(x,s),random=rng(r.seed+x*9311+s*17167),list=[];r.entities=list;
   for(const p of layout.props)if(p.box||OBSTACLES[p.name])create(r,'obstacle',p.x,p.s,p.name,{box:p.box,rot:p.rot,scenery:true});
   const clear=(a,b)=>list.every(e=>{const c=bounds(e);return !c||Math.abs(a-e.x)>c.x+1.2||Math.abs(b-e.s)>c.z+1.2;});
   for(let i=0;i<6;i++){
    const a=x*48+5+random()*38,b=s*48+5+random()*38;if(!clear(a,b)||SPAWNS.some(([px,ps])=>Math.hypot(a-px,b-ps)<14))continue;
    const n=random(),kind=n<.4?'walker':n<.65?'runner':n<.8?'military':n<.91?'brute':'stalker';create(r,'zombie',a,b,kind,{state:'wander',wake:28});
   }
   for(let i=0;i<3;i++){const a=x*48+7+random()*34,b=s*48+7+random()*34;if(clear(a,b))create(r,'pickup',a,b,i===0?'med':i===1?'ammo':'weapon');}
   if((x+s)%3===0){let a=x*48+8,b=s*48+8;if(clear(a,b))create(r,'civilian',a,b,'survivor_ellis');}
   r.sectors.set(k,list);
  }
  active.push(...r.sectors.get(k));
 }
 r.entities=active;
}