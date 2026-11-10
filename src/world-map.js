import {LOCATIONS} from './config.js';import {chunkLayout} from './systems/world.js';
// Lightweight navigational map of the actual connected world, not a menu illustration.
let base;
export function drawMap(canvas,r){
 if(!base){base=document.createElement('canvas');base.width=base.height=360;const c=base.getContext('2d');c.fillStyle='#111d19';c.fillRect(0,0,360,360);
  const colors=['#283a27','#403b2d','#343c3b','#393632','#34312c','#2d382c'];
  for(let i=0;i<6;i++){const x=i%3*120,y=i<3?180:0;c.fillStyle=colors[i];c.fillRect(x,y,120,180);c.fillStyle='#cfccb7';c.font='8px sans-serif';c.fillText(LOCATIONS[i].label.toUpperCase().replace('THE ',''),x+5,y+15,110);}
  for(let x=-3;x<3;x++)for(let s=-3;s<3;s++)for(const p of chunkLayout(x,s).props){c.fillStyle=p.name.includes('tree')?'#718264':p.name.includes('wreck')?'#ada18a':'#4c5741';if(p.name.includes('tree')||p.name.includes('wreck'))c.fillRect((p.x+144)*1.25,(144-p.s)*1.25,2,2);}
 }
 const c=canvas.getContext('2d');c.clearRect(0,0,360,360);c.drawImage(base,0,0);const px=(r.x+144)*1.25,py=(144-r.s)*1.25;
 for(const e of r.entities){if(e.passed)continue;c.fillStyle=e.type==='pickup'?'#cfbc67':e.type==='civilian'?'#88b8bd':'transparent';if(['pickup','civilian'].includes(e.type))c.fillRect((e.x+144)*1.25-2,(144-e.s)*1.25-2,4,4);}
 c.save();c.translate(px,py);c.rotate(r.viewYaw);c.fillStyle='#f0e7cc';c.beginPath();c.moveTo(0,-7);c.lineTo(4,5);c.lineTo(0,3);c.lineTo(-4,5);c.closePath();c.fill();c.restore();c.fillStyle='#fff0cd';c.font='10px sans-serif';c.fillText('N ↑ / CONNECTED WORLD / 288 × 288 m',9,345);
}
