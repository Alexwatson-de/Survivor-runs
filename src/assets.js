import * as THREE from 'three';import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';import {clone as cloneSkeleton} from 'three/addons/utils/SkeletonUtils.js';import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';import {atlasAssets} from './atlas.js';
export let ASSET_NAMES=[];
function batch(object,provided=null){
 object.updateWorldMatrix(true,true);const inv=new THREE.Matrix4().copy(object.matrixWorld).invert(),items=provided||[];
 if(!provided)object.traverse(o=>{if(o.isMesh&&!o.isSkinnedMesh)items.push(o);});if(!items.length)return;
 const gs=items.map(o=>{const g=o.geometry.clone().applyMatrix4(new THREE.Matrix4().multiplyMatrices(inv,o.matrixWorld)),n=g.index?g.toNonIndexed():g;for(const k of Object.keys(n.attributes))if(!['position','normal','uv'].includes(k))n.deleteAttribute(k);return n;});
 const geometry=mergeGeometries(gs,false);if(!geometry)throw new Error('Static atlas geometry merge failed');for(const g of gs)g.dispose();const mesh=new THREE.Mesh(geometry,items[0].material);mesh.castShadow=true;mesh.receiveShadow=true;object.add(mesh);for(const o of items)o.removeFromParent();
}
export class Library {
 constructor(){this.templates=new Map();this.materials=new Map();this.audit=[];this.manifest=null;}
 async load(progress){
  THREE.Cache.enabled=true;const response=await fetch('/assets/manifest.json');if(!response.ok)throw new Error('Missing production asset manifest');this.manifest=await response.json();ASSET_NAMES=this.manifest.assets.filter(n=>!n.startsWith('survivor_')&&!n.startsWith('zombie_'));let loaded=0,next=0;const loader=new GLTFLoader();
  const worker=async()=>{while(next<ASSET_NAMES.length){const name=ASSET_NAMES[next++],g=await loader.loadAsync('/assets/'+(this.manifest.runtimeRoot||'')+name+(this.manifest.runtimeFormat==='gltf-separate'?'.gltf':'.glb'));let skinned=0;
   g.scene.traverse(o=>{if(!o.isMesh)return;if(o.isSkinnedMesh)skinned++;const mats=Array.isArray(o.material)?o.material:[o.material];const unified=mats.map(m=>{if(this.materials.has(m.name))return this.materials.get(m.name);m.side=THREE.DoubleSide;this.materials.set(m.name,m);return m;});o.material=Array.isArray(o.material)?unified:unified[0];o.castShadow=true;o.receiveShadow=true;});
   this.templates.set(name,{object:g.scene,clips:g.animations,skinned:!!skinned});this.audit.push({name,skinned:!!skinned,clips:g.animations.map(c=>c.name)});progress?.(++loaded/ASSET_NAMES.length,name);
  }};
  await Promise.all(Array.from({length:4},worker));progress?.(.99,'Optimizing PBR render batches');this.atlas=atlasAssets(this.templates,this.materials);
  for(const [name,t]of this.templates){if(!t.skinned&&!name.startsWith('weapon_'))batch(t.object);if(name.startsWith('weapon_')){const parents=[];t.object.traverse(p=>{if(p.children.filter(o=>o.isMesh).length>1)parents.push(p);});for(const p of parents)batch(p,p.children.filter(o=>o.isMesh));}}
  // Supplied models keep their authored UVs and PBR maps, outside the old shared atlas.
  for(const [name,url]of [['survivor_cowboy','survivor_cowboy_motion.glb'],['zombie_grim','zombie_grim.glb'],['zombie_melty','melty/scene.gltf']]){
   progress?.(.99,'Loading supplied '+name);const g=await loader.loadAsync('/assets/supplied/'+url);g.scene.updateMatrixWorld(true);
   let object=g.scene,clips=g.animations;
   if(name==='zombie_melty'){
    const b=new THREE.Box3().setFromObject(object),size=b.getSize(new THREE.Vector3()),wrapper=new THREE.Group(),scale=1.82/size.y;
    object.scale.multiplyScalar(scale);object.position.y-=b.min.y*scale;wrapper.add(object);object=wrapper;
    const labels={idle:'idle01',wander:'idle02',walk:'walk01',run:'run',attack:'attack01',grab:'attack02',hurt:'damage',hit_head:'damage',hit_leg:'damage',die:'death',crawl:'on_all_four_B'};
    clips=Object.entries(labels).map(([label,source])=>{const c=g.animations.find(c=>c.name===source).clone();c.name=label;return c;});
   }
   object.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});
   const t={object,clips,skinned:true};this.templates.set(name,t);this.audit.push({name,skinned:true,clips:clips.map(c=>c.name),source:url});
  }
  for(const [alias,source]of Object.entries({survivor_mara:'survivor_cowboy',survivor_ellis:'survivor_cowboy',zombie_walker:'zombie_melty',zombie_runner:'zombie_grim',zombie_brute:'zombie_melty',zombie_military:'zombie_grim',zombie_stalker:'zombie_melty'}))this.templates.set(alias,this.templates.get(source));
  this.particle=await new THREE.TextureLoader().loadAsync('/assets/particle-smoke.png');
 }
 prop(name){const t=this.templates.get(name);if(!t)throw new Error('Missing Blender asset '+name);return t.object.clone(true);}
 actor(name){
  const t=this.templates.get(name);if(!t)throw new Error('Missing actor '+name);const object=t.skinned?cloneSkeleton(t.object):t.object.clone(true),mixer=new THREE.AnimationMixer(object),actions={},overlays={};let current=null,upperName=null;
  for(const clip of t.clips){actions[clip.name]=mixer.clipAction(clip);if(['reload','shoot','aim','hurt','hit_head'].includes(clip.name)){const tracks=clip.tracks.filter(t=>/upper|fore|hand|chest|neck|head|weapon_socket|pack/.test(t.name));if(tracks.length)overlays[clip.name]=mixer.clipAction(new THREE.AnimationClip('upper_'+clip.name,clip.duration,tracks));}}
  return {name,object,mixer,actions,overlays,
   play(label,once=false,rate=1,blend=.20){if(label===current){actions[label]?.setEffectiveTimeScale(rate);return;}const action=actions[label]||actions.idle;if(!action)return;if(current)actions[current]?.fadeOut(blend);action.reset().setLoop(once?THREE.LoopOnce:THREE.LoopRepeat,once?1:Infinity);action.clampWhenFinished=once;action.setEffectiveTimeScale(rate).fadeIn(blend).play();current=actions[label]?label:'idle';},
   upper(label,duration){const action=overlays[label];if(!action)return;if(upperName&&upperName!==label)overlays[upperName]?.fadeOut(.10);action.reset().setLoop(THREE.LoopOnce,1);action.clampWhenFinished=false;action.setEffectiveTimeScale(duration?action.getClip().duration/duration:1).fadeIn(.075).play();upperName=label;},
   stopUpper(){if(upperName)overlays[upperName]?.fadeOut(.15);upperName=null;},get clip(){return current;},reset(){mixer.stopAllAction();current=null;upperName=null;},dispose(){mixer.stopAllAction();mixer.uncacheRoot(object);}
  };
 }
}
