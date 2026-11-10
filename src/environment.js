import * as THREE from 'three';import {THEMES} from './config.js';
import {CHUNK,chunkLayout,district,seeded,worldKey} from './systems/world.js';
// 0.3: camera-centered TWO-dimensional chunks, deterministic on return. No road-edge
// mirroring; the exact same layout records define solid scenery in the simulation.
export class Countryside {
 constructor(scene,lib){this.scene=scene;this.lib=lib;this.tiles=[];this.section=0;this.center=null;this.makeMaterials();}
 makeMaterials(){
  const canvas=document.createElement('canvas');canvas.width=canvas.height=512;const ctx=canvas.getContext('2d'),rand=seeded(7201),im=ctx.createImageData(512,512);
  for(let y=0;y<512;y++)for(let x=0;x<512;x++){const n=(rand()-.5)*23,moss=Math.sin(x*.017)*Math.sin(y*.026)*7,k=(y*512+x)*4;im.data[k]=61+n+moss;im.data[k+1]=60+n+moss*1.7;im.data[k+2]=43+n*.7;im.data[k+3]=255;}
  ctx.putImageData(im,0,0);for(let i=0;i<1600;i++){ctx.fillStyle=i%3?'#6a6251':'#262c22';ctx.beginPath();ctx.ellipse(rand()*512,rand()*512,rand()*2+.4,rand()*4+.5,rand()*6,0,6.28);ctx.fill();}
  const map=new THREE.CanvasTexture(canvas);map.colorSpace=THREE.SRGBColorSpace;map.wrapS=map.wrapT=THREE.RepeatWrapping;map.repeat.set(10,10);map.anisotropy=4;
  this.groundMaterial=new THREE.MeshStandardMaterial({map,roughness:1});this.groundGeometry=new THREE.PlaneGeometry(CHUNK,CHUNK);this.groundGeometry.rotateX(-Math.PI/2);
  const blood=document.createElement('canvas');blood.width=blood.height=256;const b=blood.getContext('2d');
  for(let i=0;i<44;i++){b.fillStyle=i<12?'rgba(62,9,7,.6)':'rgba(85,13,9,.62)';b.beginPath();b.ellipse(128+(rand()-.5)*135,128+(rand()-.5)*100,5+rand()*35,3+rand()*17,rand()*6.28,0,6.28);b.fill();}
  const stainMap=new THREE.CanvasTexture(blood);stainMap.colorSpace=THREE.SRGBColorSpace;this.stainMaterial=new THREE.MeshStandardMaterial({map:stainMap,transparent:true,depthWrite:false,roughness:.65,polygonOffset:true,polygonOffsetFactor:-2});this.stainGeometry=new THREE.PlaneGeometry(3.4,2.5);this.stainGeometry.rotateX(-Math.PI/2);
  this.stains=new THREE.Group();this.scene.add(this.stains);this.dynamicStains=[];
 }
 instances(group,name,placements){
  const src=this.lib.templates.get(name)?.object;if(!src||!placements.length)return;src.updateMatrixWorld(true);const dummy=new THREE.Object3D();
  src.traverse(o=>{if(!o.isMesh)return;const mesh=new THREE.InstancedMesh(o.geometry,o.material,placements.length);mesh.castShadow=false;mesh.receiveShadow=true;
   placements.forEach((p,i)=>{dummy.position.set(p.x,0,-p.s);dummy.scale.setScalar(p.scale||1);dummy.rotation.y=p.rot||0;dummy.updateMatrix();mesh.setMatrixAt(i,new THREE.Matrix4().multiplyMatrices(dummy.matrix,o.matrixWorld));});mesh.computeBoundingSphere();group.add(mesh);
  });
 }
 populate(cx,cs){
  const layout=chunkLayout(cx,cs),group=new THREE.Group(),ground=new THREE.Mesh(this.groundGeometry,this.groundMaterial);ground.position.set(cx*CHUNK+24,-.025,-cs*CHUNK-24);ground.receiveShadow=true;group.add(ground);
  const buckets=new Map();for(const p of layout.props){if(p.name==='blood_stain'){const o=new THREE.Mesh(this.stainGeometry,this.stainMaterial);o.position.set(p.x,.006,-p.s);o.rotation.y=p.rot;o.scale.setScalar(p.scale);o.userData.blood=true;group.add(o);continue;}const a=buckets.get(p.name)||[];a.push(p);buckets.set(p.name,a);}
  for(const [name,ps]of buckets)this.instances(group,name,ps);
  this.scene.add(group);return {group,cx,cs,key:layout.key,theme:layout.theme};
 }
 addBlood(x,s){if(this.dynamicStains.length>=45){const old=this.dynamicStains.shift();old.removeFromParent();}const o=new THREE.Mesh(this.stainGeometry,this.stainMaterial);o.position.set(x,.008,-s);o.scale.setScalar(.35+Math.random()*.3);o.rotation.y=Math.random()*6.28;this.stains.add(o);this.dynamicStains.push(o);}
 update(run){
  const cx=Math.floor(run.x/CHUNK),cs=Math.floor(run.s/CHUNK),key=worldKey(cx,cs);
  if(this.center!==key){this.center=key;const wanted=new Set();for(let x=cx-1;x<=cx+1;x++)for(let s=cs-1;s<=cs+1;s++){if(x< -3||x>2||s< -3||s>2)continue;const k=worldKey(x,s);wanted.add(k);if(!this.tiles.some(t=>t.key===k))this.tiles.push(this.populate(x,s));}
   this.tiles=this.tiles.filter(t=>{if(wanted.has(t.key))return true;t.group.traverse(o=>{if(o.isInstancedMesh)o.dispose();});t.group.removeFromParent();return false;});
  }
  for(const t of this.tiles){t.group.position.z=run.s;t.group.traverse(o=>{if(o.userData.blood)o.visible=run.profile.settings.blood;});}
  this.stains.position.z=run.s;this.stains.visible=run.profile.settings.blood;this.section=district(run.x,run.s);return THEMES[this.section];
 }
 reset(){this.center=null;for(const o of this.dynamicStains)o.removeFromParent();this.dynamicStains=[];}
}
