// Preserve Blender albedo, normal, roughness and metallic response while reducing
// GPU material switches. Native skin weights/bones/animation tracks remain intact.
import * as THREE from 'three';import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
export function atlasAssets(templates,materials){
 const list=[...materials.values()],cols=6,rows=Math.ceil(list.length/cols),tile=512,pad=3;
 const make=(n)=>{const c=document.createElement('canvas');c.width=cols*n;c.height=rows*n;return [c,c.getContext('2d',{willReadFrequently:true})];};
 const [color,cx]=make(tile),[normal,nx]=make(128),[orm,rx]=make(64);nx.fillStyle='rgb(128,128,255)';nx.fillRect(0,0,normal.width,normal.height);
 const map=new Map();list.forEach((m,i)=>{
  const x=i%cols,y=Math.floor(i/cols);map.set(m,i);cx.fillStyle='#ffffff';cx.fillRect(x*tile,y*tile,tile,tile);if(m.map?.image)cx.drawImage(m.map.image,x*tile,y*tile,tile,tile);
  if(m.normalMap?.image)nx.drawImage(m.normalMap.image,x*128,y*128,128,128);
  rx.fillStyle='#ffffff';rx.fillRect(x*64,y*64,64,64);if(m.roughnessMap?.image)rx.drawImage(m.roughnessMap.image,x*64,y*64,64,64);
  const data=rx.getImageData(x*64,y*64,64,64);for(let k=0;k<data.data.length;k+=4){data.data[k]=255;data.data[k+1]=Math.round(data.data[k+1]*(m.roughness??1));data.data[k+2]=Math.round((m.metalness||0)*255);data.data[k+3]=255;}rx.putImageData(data,x*64,y*64);
 });
 const texture=(canvas,srgb=false)=>{const t=new THREE.CanvasTexture(canvas);t.flipY=false;t.colorSpace=srgb?THREE.SRGBColorSpace:THREE.NoColorSpace;t.anisotropy=4;return t;};
 const atlas=new THREE.MeshStandardMaterial({map:texture(color,true),normalMap:texture(normal),roughnessMap:texture(orm),roughness:1,metalness:1,side:THREE.DoubleSide});atlas.metalnessMap=atlas.roughnessMap;atlas.name='SR_PBR_runtime_atlas';
 for(const {object}of templates.values()){
  object.traverse(o=>{if(!o.isMesh)return;if(Array.isArray(o.material))throw new Error('Expected glTF material primitives before atlas merge');const index=map.get(o.material);if(index===undefined)throw new Error('Atlas material not registered');const g=o.geometry.clone(),uv=g.attributes.uv;if(!uv)throw new Error('Authored mesh lacks UVs');
   const wrap=v=>v>=0&&v<=1?v:((v%1)+1)%1;
   for(let i=0;i<uv.count;i++){const u=wrap(uv.getX(i)),v=wrap(uv.getY(i));uv.setXY(i,(index%cols*tile+pad+u*(tile-pad*2))/(cols*tile),(Math.floor(index/cols)*tile+pad+v*(tile-pad*2))/(rows*tile));}o.geometry=g;o.material=atlas;
  });
  const parents=[];object.traverse(p=>{const children=p.children.filter(c=>c.isSkinnedMesh);if(children.length>1&&children.every(c=>c.skeleton===children[0].skeleton))parents.push([p,children]);});
  for(const [parent,children]of parents){const geometries=children.map(c=>c.geometry.index?c.geometry.toNonIndexed():c.geometry.clone()),geometry=mergeGeometries(geometries,false);if(!geometry)throw new Error('Skinned atlas merge failed');for(const g of geometries)g.dispose();const first=children[0],skin=new THREE.SkinnedMesh(geometry,atlas);skin.name=first.name+'_batched';skin.bindMode=first.bindMode;skin.bind(first.skeleton,first.bindMatrix);skin.castShadow=true;skin.receiveShadow=true;parent.add(skin);for(const c of children)c.removeFromParent();}
 }
 // Close discarded decoded images after the atlas is uploaded from canvases.
 const textures=new Set(),images=new Set();for(const m of list){for(const key of ['map','normalMap','roughnessMap','metalnessMap'])if(m[key]){textures.add(m[key]);images.add(m[key].image);}m.dispose();}for(const t of textures)t.dispose();THREE.Cache.clear();for(const im of images)im?.close?.();materials.clear();materials.set(atlas.name,atlas);
 return {material:atlas,sourceMaterials:list.length,textureSize:[color.width,color.height]};
}
