import * as THREE from 'three';import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';import {ShaderPass} from 'three/addons/postprocessing/ShaderPass.js';import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {Countryside} from './environment.js';import {ShoulderCamera} from './camera.js';import {WEAPONS,pathCenter} from './config.js';
import {PlayerMotion,GROUND_Y} from './player-motion.js';
const worldX=(r,x,s)=>x+pathCenter(s+r.locationOffset);
const angle=(a,b,t)=>a+Math.atan2(Math.sin(b-a),Math.cos(b-a))*Math.min(1,t);
export class GameView {
 constructor(canvas,lib,settings){
  this.lib=lib;this.settings=settings;this.scene=new THREE.Scene();this.scene.fog=new THREE.FogExp2(0x293c38,.019);
  this.renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});this.renderer.info.autoReset=false;this.renderer.shadowMap.enabled=settings.quality==='high';this.renderer.shadowMap.type=THREE.PCFSoftShadowMap;this.renderer.toneMapping=THREE.ACESFilmicToneMapping;this.renderer.toneMappingExposure=1.18;
  this.rigCamera=new ShoulderCamera();this.camera=this.rigCamera.camera;
  // Original procedural overcast panorama: cold cloud layers, no copied screenshot background.
  const sky=document.createElement('canvas');sky.width=512;sky.height=512;const ctx=sky.getContext('2d'),grad=ctx.createLinearGradient(0,0,0,512);grad.addColorStop(0,'#16232b');grad.addColorStop(.45,'#46585a');grad.addColorStop(.75,'#6e7b73');grad.addColorStop(1,'#293c38');ctx.fillStyle=grad;ctx.fillRect(0,0,512,512);
  for(let i=0;i<50;i++){ctx.fillStyle='rgba(15,25,27,.035)';ctx.beginPath();ctx.ellipse(Math.random()*512,Math.random()*300,70+Math.random()*180,12+Math.random()*28,-.2,0,Math.PI*2);ctx.fill();}this.scene.background=new THREE.CanvasTexture(sky);this.scene.background.colorSpace=THREE.SRGBColorSpace;
  this.scene.add(new THREE.HemisphereLight(0x9bb8bf,0x29271e,1.85));
  this.sun=new THREE.DirectionalLight(0xd2d5b2,2.3);this.sun.position.set(-25,38,-42);this.sun.castShadow=true;this.sun.shadow.mapSize.set(1024,1024);Object.assign(this.sun.shadow.camera,{left:-20,right:20,top:30,bottom:-20,near:1,far:110});this.sun.shadow.bias=-.0004;this.sun.shadow.normalBias=.04;this.sun.target.position.set(0,0,-15);this.scene.add(this.sun,this.sun.target);
  this.fill=new THREE.DirectionalLight(0xa8b4b4,2.0);this.fill.position.set(2,4,8);this.scene.add(this.fill,this.fill.target);
  this.env=new Countryside(this.scene,lib);this.actors=new Map();this.pool=new Map();this.player=null;this.dog=null;this.gun=null;this.weaponKey='';this.time=0;this.fx=[];this.tracers=[];this.frame=0;
  // Contact cue also remains visible on Low, where expensive real shadows are off.
  const sc=document.createElement('canvas');sc.width=sc.height=64;const sx=sc.getContext('2d'),sg=sx.createRadialGradient(32,32,3,32,32,31);sg.addColorStop(0,'rgba(0,0,0,.48)');sg.addColorStop(1,'rgba(0,0,0,0)');sx.fillStyle=sg;sx.fillRect(0,0,64,64);
  this.contactShadow=new THREE.Mesh(new THREE.PlaneGeometry(1,1.35),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(sc),transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1}));this.contactShadow.rotation.x=-Math.PI/2;this.scene.add(this.contactShadow);
  this.flash=new THREE.PointLight(0xffb65a,0,8,2);this.scene.add(this.flash);this.ember=new THREE.PointLight(0xff9b50,0,13,2);this.scene.add(this.ember);
  this.buildParticles();this.buildWeather();this.buildPost();this.resize();window.addEventListener('resize',()=>this.resize());
 }
 buildPost(){
  this.composer=new EffectComposer(this.renderer);this.composer.addPass(new RenderPass(this.scene,this.camera));this.bloom=new UnrealBloomPass(new THREE.Vector2(512,288),.17,.5,.9);this.composer.addPass(this.bloom);
  this.grade=new ShaderPass({uniforms:{tDiffuse:{value:null},time:{value:0},strength:{value:.028}},vertexShader:'varying vec2 vUv; void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:'uniform sampler2D tDiffuse;uniform float time;uniform float strength;varying vec2 vUv;void main(){vec3 c=texture2D(tDiffuse,vUv).rgb;float lum=dot(c,vec3(.2126,.7152,.0722));c=mix(vec3(lum),c,.82);c*=vec3(.95,1.0,1.015);float v=smoothstep(.25,.85,distance(vUv,vec2(.52,.48)));c*=1.0-v*.24;float grain=fract(sin(dot(vUv+fract(time),vec2(12.9898,78.233)))*43758.5453)-.5;c+=grain*strength*.12;gl_FragColor=vec4(max(c,vec3(0.0)),1.0);}'});this.composer.addPass(this.grade);this.composer.addPass(new OutputPass());
 }
 buildParticles(){
  const count=420;this.particleSlots=Array.from({length:count},()=>({life:0}));const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(count*3),3));g.setAttribute('tint',new THREE.BufferAttribute(new Float32Array(count*4),4));g.setAttribute('size',new THREE.BufferAttribute(new Float32Array(count),1));
  const mat=new THREE.ShaderMaterial({uniforms:{sprite:{value:this.lib.particle},fogColor:{value:new THREE.Color(0x293c38)}},transparent:true,depthWrite:false,vertexShader:'attribute vec4 tint;attribute float size;varying vec4 vTint;varying float depth;void main(){vTint=tint;vec4 mv=modelViewMatrix*vec4(position,1.0);depth=-mv.z;gl_PointSize=clamp(size*230.0/max(1.0,-mv.z),1.0,95.0);gl_Position=projectionMatrix*mv;}',fragmentShader:'uniform sampler2D sprite;uniform vec3 fogColor;varying vec4 vTint;varying float depth;void main(){float a=texture2D(sprite,gl_PointCoord).a*vTint.a;if(a<.008)discard;vec3 c=mix(vTint.rgb,fogColor,1.0-exp(-.00036*depth*depth));gl_FragColor=vec4(c,a);#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}'});
  // Chunk directives must start on a new GLSL line.
  mat.fragmentShader=mat.fragmentShader.replace(';#include',';\n#include');this.particles=new THREE.Points(g,mat);this.particles.frustumCulled=false;this.scene.add(this.particles);
 }
 buildWeather(){
  const pos=new Float32Array(720);for(let i=0;i<240;i++){pos[i*3]=(Math.random()-.5)*34;pos[i*3+1]=Math.random()*13;pos[i*3+2]=-Math.random()*90;}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(pos,3));this.rain=new THREE.Points(geo,new THREE.PointsMaterial({color:0xb6c6c3,size:.024,transparent:true,opacity:.35,depthWrite:false}));this.scene.add(this.rain);
 }
 resize(){const budget=this.settings.quality==='high'?1280*720:900*506,ratio=Math.min(devicePixelRatio,Math.sqrt(budget/(innerWidth*innerHeight)));this.renderer.setPixelRatio(ratio);this.renderer.setSize(innerWidth,innerHeight,false);this.composer?.setPixelRatio(ratio);this.composer?.setSize(innerWidth,innerHeight);this.camera.aspect=innerWidth/innerHeight;this.camera.updateProjectionMatrix();}
 applySettings(s){this.settings=s;this.renderer.shadowMap.enabled=s.quality==='high';this.bloom.enabled=s.quality==='high';this.resize();}
 obtain(name){const list=this.pool.get(name);if(list?.length){const a=list.pop();a.object.visible=true;return a;}return name.startsWith('zombie_')||name.startsWith('survivor_')?this.lib.actor(name):{name,object:this.lib.prop(name)};}
 release(a){a.object.removeFromParent();const list=this.pool.get(a.name)||[];if(list.length<12){a.reset?.();a.lastState=null;list.push(a);this.pool.set(a.name,list);}else a.dispose?.();}
 start(run){
  for(const a of this.actors.values())this.release(a);this.actors.clear();for(const a of [this.player,this.dog,this.gun]){a?.object.removeFromParent();a?.dispose?.();}for(const p of this.particleSlots)p.life=0;
  this.player=this.lib.actor('survivor_'+run.profile.character);this.dog=this.lib.actor('dog_'+run.profile.dog);this.scene.add(this.player.object,this.dog.object);this.player.object.rotation.y=Math.PI;this.player.object.updateMatrixWorld(true);
  this.playerMotion=new PlayerMotion(this.player,run);
  this.socket=this.player.object.getObjectByName('weapon_socket');if(!this.socket)throw new Error('Skinned survivor is missing the authored weapon socket');
  const rootQ=this.player.object.getWorldQuaternion(new THREE.Quaternion()),socketQ=this.socket.getWorldQuaternion(new THREE.Quaternion());this.socketCorrection=rootQ.invert().multiply(socketQ).invert();
  this.gun=null;this.weaponKey='';this.env.reset();this.rigCamera.yaw=0;this.rigCamera.ready=false;this.time=0;this.syncWeapon(run);
 }
 syncWeapon(run){if(this.weaponKey===run.weapon)return;this.gun?.object.removeFromParent();this.gun?.dispose?.();this.gun=this.lib.actor(WEAPONS[run.weapon].asset);this.socket.add(this.gun.object);this.gun.object.position.set(0,0,0);this.gun.object.quaternion.copy(this.socketCorrection);this.weaponKey=run.weapon;}
 muzzle(run){const p=this.gun.object.localToWorld(new THREE.Vector3(0,.017,run.spec.muzzle));return [p.x-pathCenter(run.distance+run.locationOffset),p.y,p.z];}
 aimFromPointer(run,x,y){this.rigCamera.pointer={x:x/innerWidth,y:y/innerHeight};const ray=this.rigCamera.ray(run);ray.muzzle=this.muzzle(run);return ray;}
 emitParticles(kind,x,s,y=1,count=8){
  if(kind==='blood'&&!this.settings.blood)return;
  const colors={smoke:0x777d76,blood:0x541713,dust:0x71654c,flash:0xffc477,spark:0xeac785,explosion:0xf4973f};let made=0;
  for(const p of this.particleSlots){if(p.life>0)continue;const c=new THREE.Color(colors[kind]||0xffffff);Object.assign(p,{x,s,y,vx:(Math.random()-.5)*(kind==='smoke'?.5:3),vy:kind==='smoke'?.55:Math.random()*2.8,vz:(Math.random()-.5)*1.3,life:kind==='smoke'?2:kind==='flash'?.07:.5,max:kind==='smoke'?2:kind==='flash'?.07:.5,size:kind==='smoke'?1.3:kind==='explosion'?.9:kind==='flash'?.5:.12,color:c,kind});if(++made>=count)break;}
 }
 event(e,run){
  const center=pathCenter(run.distance+run.locationOffset);
  if(e.type==='shot'){
   this.player.upper('shoot',.15);this.gun.play('fire',true,1);this.gun.actions.fire?.reset().play();this.flash.intensity=11;this.rigCamera.kick(e.recoil*.5);
   const muzzle=this.muzzle(run);this.emitParticles('flash',muzzle[0]+center,run.s-muzzle[2],muzzle[1],2);this.emitParticles('smoke',muzzle[0]+center,run.s-muzzle[2],muzzle[1],2);this.emitParticles('spark',muzzle[0]+center+.12,run.s-.1,1.2,1);
   if(e.end){const geo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(muzzle[0]+center,muzzle[1],muzzle[2]),new THREE.Vector3(e.end[0]+center,e.end[1],e.end[2])]);const line=new THREE.Line(geo,new THREE.LineBasicMaterial({color:0xe9be7c,transparent:true,opacity:.3}));this.scene.add(line);this.tracers.push({line,life:.045});}
  }
  if(e.type==='reload'){this.player.upper('reload',e.duration);this.gun.play('reload',true,this.gun.actions.reload.getClip().duration/e.duration);}
  if(e.type==='switch'){this.syncWeapon(run);this.player.stopUpper();}
  if(e.type==='hit'){this.emitParticles('blood',worldX(run,e.x,e.s),e.s,e.zone==='head'?1.66:e.zone==='leg'?.45:1.1,7);if(this.settings.blood)this.env.addBlood(e.x,e.s);}
  if(e.type==='damage'){this.player.upper('hurt',.45);this.rigCamera.kick(.035);}
  if(e.type==='impact'){this.emitParticles('dust',worldX(run,e.x,e.s),e.s,.5,12);this.emitParticles('spark',worldX(run,e.x,e.s),e.s,.8,5);if(e.kind==='barrel'){this.emitParticles('explosion',worldX(run,e.x,e.s),e.s,.8,15);this.emitParticles('smoke',worldX(run,e.x,e.s),e.s,1.2,15);}this.rigCamera.kick(.06);}
  if(e.type==='loaded')this.player.stopUpper();
 }
 updateParticles(run,dt){
  const g=this.particles.geometry,p=g.attributes.position,c=g.attributes.tint,size=g.attributes.size;
  this.particleSlots.forEach((a,i)=>{if(a.life<=0){c.setW(i,0);return;}a.life-=dt;a.x+=a.vx*dt;a.s-=a.vz*dt;a.y+=a.vy*dt;if(a.kind!=='smoke')a.vy-=dt*4;a.y=Math.max(.02,a.y);p.setXYZ(i,a.x,a.y,run.s-a.s);c.setXYZW(i,a.color.r,a.color.g,a.color.b,Math.max(0,a.life/a.max)*(a.kind==='smoke'?.25:.85));size.setX(i,a.size*(a.kind==='smoke'?1+(a.max-a.life):1));});p.needsUpdate=true;c.needsUpdate=true;size.needsUpdate=true;
  this.tracers=this.tracers.filter(t=>{t.life-=dt;t.line.material.opacity=Math.max(0,t.life/.045)*.3;if(t.life<=0){t.line.removeFromParent();t.line.geometry.dispose();t.line.material.dispose();return false;}return true;});
 }
 update(run,dt,menu=false){
  this.time+=dt;this.frame++;this.syncWeapon(run);const section=this.env.update(run);this.rigCamera.update(run,dt,menu,this.settings);const px=run.x;
  const visible=new Set(),near=run.entities.filter(e=>!e.scenery&&Math.hypot(e.x-run.x,e.s-run.s)<65&&!(e.hp<=0&&e.timer<0)&&!(e.passed&&['pickup','civilian'].includes(e.type))).sort((a,b)=>Math.hypot(a.x-run.x,a.s-run.s)-Math.hypot(b.x-run.x,b.s-run.s));
  for(const e of near){visible.add(e.id);let a=this.actors.get(e.id);const name=e.type==='zombie'?'zombie_'+e.kind:e.type==='civilian'?e.kind:e.type==='pickup'?(e.kind==='med'?'med_crate':'supply_crate'):e.kind;if(!a){a=this.obtain(name);this.actors.set(e.id,a);this.scene.add(a.object);}
   a.object.position.set(e.x,e.type==='pickup'?.02:0,run.s-e.s);a.object.visible=e.state!=='emerge';a.object.traverse(o=>{if(o.isMesh)o.castShadow=Math.hypot(e.x-run.x,e.s-run.s)<20;});
   if(e.type==='zombie'){
    const yaw=Math.atan2(px-a.object.position.x,-a.object.position.z);a.object.rotation.y=angle(a.object.rotation.y,yaw,dt*4);a.object.scale.setScalar(e.kind==='brute'?1.98/1.82:e.kind==='military'?1.86/1.82:1);
    const label=e.hp<=0?'die':e.hit>0?e.reaction:e.state==='crawl'?'crawl':e.state==='attack'||e.state==='grab'?e.state:['run','lunge'].includes(e.state)?'run':e.state==='wander'||e.state==='emerge'?'wander':'walk';
    // stopAllAction on pooled actors requires resetting their previous action identity.
    if(a.lastState!==label){a.play(label,['die','hurt','hit_head','hit_leg'].includes(label),e.kind==='runner'?1.1:1);a.lastState=label;}if(Math.hypot(e.x-run.x,e.s-run.s)<30||this.frame%2===0)a.mixer.update(dt*(Math.hypot(e.x-run.x,e.s-run.s)<30?1:2));
   }else if(e.type==='civilian'){a.play('idle');a.mixer.update(dt);a.object.rotation.y=Math.PI*.75;}
  }
  for(const [id,a]of this.actors)if(!visible.has(id)){this.release(a);this.actors.delete(id);}
  const player=this.player;player.object.position.set(px,run.y+GROUND_Y+.001,0);player.object.rotation.y=menu?Math.PI-.25:Math.PI-run.heading;
  this.playerMotion.update(run,dt,menu);this.gun.mixer.update(dt);
  this.contactShadow.position.set(px,GROUND_Y+.002,0);this.contactShadow.rotation.z=run.heading;this.contactShadow.scale.set(run.slide>0?1.2:1,run.slide>0?1.45:1,1);this.contactShadow.material.opacity=1/(1+run.y*2);
  const d=run.dog;this.dog.object.position.set(menu?px+1.3:d.x,d.jump>0?Math.sin(d.jump/.7*Math.PI)*.50:0,menu?.2:run.s-d.s);this.dog.object.scale.setScalar(.85);this.dog.object.rotation.y=menu?-.2:angle(this.dog.object.rotation.y,d.facing,dt*7);
  this.dog.play(menu||d.state==='follow'&&run.moveSpeed<.1?'idle':d.state==='down'?'down':d.react>0?'react':d.jump>0?'jump':d.bite>0?'bite':d.state==='attack'?(d.stateTime<.3?'bark':'attack'):'run');this.dog.mixer.update(dt);
  const muzzle=this.muzzle(run);this.flash.position.set(muzzle[0]+pathCenter(run.distance+run.locationOffset),muzzle[1],muzzle[2]);this.flash.intensity=Math.max(0,this.flash.intensity-dt*100);
  const weather=this.settings.weather&&Math.floor((run.distance+run.locationOffset)/210)%3===1;this.rain.visible=weather;this.rain.position.x=px;const rain=this.rain.geometry.attributes.position;if(weather){for(let i=0;i<rain.count;i++){rain.array[i*3+1]-=dt*14;rain.array[i*3+2]+=dt*6;if(rain.array[i*3+1]<0){rain.array[i*3+1]=13;rain.array[i*3+2]=-Math.random()*70;}}rain.needsUpdate=true;}
  const fog=.018+(weather?.005:0)+Math.sin(run.time*.06)*.001;this.scene.fog.density=fog;
  this.sun.position.x=px-25;this.sun.target.position.x=px;this.fill.position.set(this.camera.position.x+2,4,this.camera.position.z+2);this.fill.target.position.set(px,1,0);
  this.ember.intensity=this.env.section===5?2.8+Math.sin(this.time*13)*.4:0;this.ember.position.set(px+5,1,-8);if(this.ember.intensity&&this.frame%8===0)this.emitParticles('smoke',px+5,run.s+8,1.6,1);
  this.updateParticles(run,dt);this.grade.uniforms.time.value=this.time;this.bloom.enabled=this.settings.quality==='high';this.renderer.info.reset();this.composer.render();return section;
 }
 stats(){return {calls:this.renderer.info.render.calls,triangles:this.renderer.info.render.triangles,geometries:this.renderer.info.memory.geometries,textures:this.renderer.info.memory.textures,actors:this.actors.size,pooled:[...this.pool.values()].reduce((s,a)=>s+a.length,0),segments:this.env.tiles.length,skinned:true};}
}
