// Bounded local A* for companion routing. No teleporting through cars/barricades.
import {bounds} from '../collision.js';
export function findPath(start,goal,entities){
 const cell=.8,minX=Math.min(start.x,goal.x)-5,maxX=Math.max(start.x,goal.x)+5,minS=Math.min(start.s,goal.s)-5,maxS=Math.max(start.s,goal.s)+5;
 const width=Math.ceil((maxX-minX)/cell)+1,height=Math.min(80,Math.ceil((maxS-minS)/cell)+1);
 const grid=p=>({x:Math.max(0,Math.min(width-1,Math.round((p.x-minX)/cell))),y:Math.max(0,Math.min(height-1,Math.round((p.s-minS)/cell)))}),pos=(x,y)=>({x:minX+x*cell,s:minS+y*cell});
 const blocks=entities.filter(e=>e.type==='obstacle'&&!['overhead','low_log'].includes(e.kind));
 const blocked=(x,y)=>{const p=pos(x,y);return blocks.some(e=>{const b=bounds(e);return b&&Math.abs(p.x-e.x)<b.x+.36&&Math.abs(p.s-e.s)<b.z+.36;});};
 const a=grid(start),g=grid(goal),key=(x,y)=>y*width+x,open=[{...a,g:0,f:0}],cost=new Map([[key(a.x,a.y),0]]),parent=new Map();let last=null,iterations=0;
 while(open.length&&iterations++<1400){open.sort((a,b)=>a.f-b.f);const q=open.shift(),k=key(q.x,q.y);if(q.g>cost.get(k))continue;last=q;if(Math.hypot(q.x-g.x,q.y-g.y)<1.5)break;
  for(const [dx,dy]of [[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,-1],[-1,1],[1,1]]){const x=q.x+dx,y=q.y+dy;if(x<0||x>=width||y<0||y>=height||blocked(x,y))continue;if(dx&&dy&&(blocked(q.x+dx,q.y)||blocked(q.x,q.y+dy)))continue;const nk=key(x,y),ng=q.g+(dx&&dy?1.414:1);if(ng>=(cost.get(nk)??Infinity))continue;cost.set(nk,ng);parent.set(nk,k);open.push({x,y,g:ng,f:ng+Math.hypot(x-g.x,y-g.y)});}
 }
 if(!last||Math.hypot(last.x-g.x,last.y-g.y)>2)return [];
 const path=[];let k=key(last.x,last.y),guard=0;while(k!==key(a.x,a.y)&&guard++<500){path.push(pos(k%width,Math.floor(k/width)));k=parent.get(k);if(k===undefined)return [];}
 return path.reverse();
}
