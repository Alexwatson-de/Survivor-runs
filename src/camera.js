import * as THREE from 'three';import {clamp} from './config.js';import {coverDistance} from './collision.js';
export class ShoulderCamera {
 constructor(){this.camera=new THREE.PerspectiveCamera(57,1,.08,180);this.shock=0;this.pointer={x:.5,y:.46};this.yaw=0;this.pitch=.10;this.ready=false;}
 kick(strength){this.shock=Math.min(.11,this.shock+strength);}
 look(dx,dy,sensitivity=1){this.yaw-=dx*.003*sensitivity;this.pitch=clamp(this.pitch+dy*.002*sensitivity,-.45,.65);}
 update(run,dt,menu,settings){
  run.viewYaw=this.yaw;const aim=run.aimed&&!menu,mobile=this.camera.aspect<.8,yaw=menu?Math.PI+.25:this.yaw;
  const forward=new THREE.Vector3(Math.sin(yaw),0,-Math.cos(yaw)),right=new THREE.Vector3(Math.cos(yaw),0,Math.sin(yaw)),target=new THREE.Vector3(run.x,1.38+run.y*.7,0);
  const desired=target.clone().addScaledVector(forward,-(menu?4.4:mobile?6:aim?2.8:4.6)).addScaledVector(right,menu?.5:mobile?.35:.66);desired.y+=menu?.28:.75+Math.sin(this.pitch)*3;
  const delta=desired.clone().sub(target),length=delta.length(),dir=delta.clone().normalize(),hit=coverDistance(run,target.toArray(),dir.toArray());
  if(!menu&&hit<length)desired.copy(target).addScaledVector(dir,Math.max(.7,hit-.25));
  if(!this.ready){this.camera.position.copy(desired);this.ready=true;}else this.camera.position.lerp(desired,1-Math.exp(-dt*10));
  this.shock=Math.max(0,this.shock-dt*.35);const shake=settings.shake?this.shock:0;
  const focus=target.clone().addScaledVector(forward,menu?0:12);focus.y-=menu?0:Math.sin(this.pitch)*6;focus.y+=Math.sin(run.time*48)*shake;
  this.camera.lookAt(focus);this.camera.rotateZ(settings.shake?Math.sin(run.time*31)*shake*.15:0);
  const fov=mobile?64:aim?(run.weapon==='hunting'?43:49):57;this.camera.fov+=(fov-this.camera.fov)*(1-Math.exp(-dt*8));this.camera.updateProjectionMatrix();this.camera.updateMatrixWorld();
 }
 ray(run,u=this.pointer.x,v=this.pointer.y){const vector=new THREE.Vector3(u*2-1,-v*2+1,.5).unproject(this.camera),direction=vector.sub(this.camera.position).normalize();return {origin:this.camera.position.toArray(),direction:direction.toArray()};}
}