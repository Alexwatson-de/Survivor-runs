// Survivor Runs 0.3: the user means actual free exploration, not lateral steering.
// One connected 288 x 288 m world. X and S are independent horizontal coordinates.
// Layout is deterministic on revisit; bushes are permeable, solid trunks/wrecks are not.
export const WORLD_HALF=144,CHUNK=48;
export const SPAWNS=[[-96,-72],[0,-72],[96,-72],[-96,72],[0,72],[96,72]];
export function district(x,s){return Math.min(2,Math.max(0,Math.floor((x+144)/96)))+3*(s>=0?1:0);}
export function worldKey(x,s){return `${x},${s}`;}
export function seeded(seed){let a=seed>>>0;return ()=>{a+=0x6D2B79F5;let t=Math.imul(a^a>>>15,1|a);t^=t+Math.imul(t^t>>>7,61|t);return ((t^t>>>14)>>>0)/4294967296;};}
export function chunkLayout(cx,cs){
 const rand=seeded(7031+cx*73856093+cs*19349663),props=[],x0=cx*CHUNK,s0=cs*CHUNK;
 const theme=district(x0+24,s0+24),centers=Array.from({length:4},()=>[x0+rand()*48,s0+rand()*48]);
 const safe=(x,s)=>SPAWNS.every(([a,b])=>Math.hypot(x-a,s-b)>5);
 const add=(name,x,s,scale=1,rot=0,box=null)=>{if(safe(x,s))props.push({name,x,s,scale,rot,box});};
 // Clustered independent samples, not alternating +/- rows or mirrored roadside belts.
 for(let i=0;i<(theme===0?24:theme===5?13:9);i++){
  const c=centers[Math.floor(rand()*centers.length)],a=rand()*Math.PI*2,r=Math.sqrt(rand())*12;
  const x=Math.max(x0+1,Math.min(x0+47,c[0]+Math.cos(a)*r)),s=Math.max(s0+1,Math.min(s0+47,c[1]+Math.sin(a)*r)),scale=.65+rand()*.85;
  add(rand()<.2?'tree_dead_lod':'tree_oak_lod',x,s,scale,rand()*6.28,{x:.25*scale,z:.25*scale,y0:0,y1:2.6});
 }
 for(let i=0;i<27;i++){const c=centers[Math.floor(rand()*4)],x=Math.max(x0+.5,Math.min(x0+47.5,c[0]+(rand()-.5)*22)),s=Math.max(s0+.5,Math.min(s0+47.5,c[1]+(rand()-.5)*22));add('bush',x,s,.5+rand()*1.15,rand()*6.28);}
 for(let i=0;i<60;i++)add('grass_clump',x0+rand()*48,s0+rand()*48,.45+rand(),rand()*6.28);
 for(let i=0;i<7;i++)add('rock',x0+rand()*48,s0+rand()*48,.2+rand()*.55,rand()*6.28);
 // Recognizable opening landmark off to one side, with walkable routes around it.
 if(cx===-2&&cs===-2){add('car_wreck',-87,-57,1,Math.PI/2);add('blood_stain',-89,-59,1.1,.7);add('body_bag',-84,-55,1,.35);}
 const count=theme===4?5:theme===0?1:2;
 for(let i=0;i<count;i++){
  const x=x0+6+rand()*36,s=s0+6+rand()*36,name=rand()<.22?'truck_wreck':'car_wreck';
  // Keep collision and actual car orientation identical (axis-aligned or quarter-turn).
  add(name,x,s,1,rand()<.5?0:Math.PI/2);
  add('rubble',x+2.5,s-2,.7+rand()*.4,rand()*6.28);
  add('blood_stain',x-1,s+2.5,.7+rand()*1.5,rand()*6.28);
 }
 if(theme===1)add('house_ruin',x0+24,s0+25,1,0,{x:4.8,z:4.8,y0:0,y1:5.5});
 if(theme===3)add('warehouse',x0+22,s0+26,.8,0,{x:6.5,z:7,y0:0,y1:6});
 if(theme===2){add('military_truck',x0+31,s0+26);add('barricade',x0+18,s0+25);add('warning_sign',x0+15,s0+27,1);}
 if(theme===5)add('camp',x0+32,s0+31,.8,0,{x:3,z:3,y0:0,y1:2.4});
 for(let i=0;i<3;i++)add('blood_stain',x0+rand()*48,s0+rand()*48,.4+rand(),rand()*6.28);
 return {cx,cs,key:worldKey(cx,cs),theme,props};
}
