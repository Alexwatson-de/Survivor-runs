import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync,existsSync} from 'node:fs';import path from 'node:path';
const root=new URL('../../public/assets/',import.meta.url),manifest=JSON.parse(readFileSync(new URL('manifest.json',root)));
for(const name of manifest.assets)test('production Blender export '+name,()=>{
 const g=JSON.parse(readFileSync(new URL('runtime/'+name+'.gltf',root)));assert.equal(g.scenes.length,1);assert.ok(g.meshes.length>0);assert.ok(!g.nodes.some(n=>n.name==='Cube'));
 for(const m of g.meshes)for(const p of m.primitives){assert.ok(p.attributes.NORMAL!==undefined);assert.ok(p.attributes.TEXCOORD_0!==undefined);}
 for(const b of g.buffers)assert.ok(existsSync(new URL('runtime/'+b.uri,root)));for(const i of g.images||[])assert.ok(existsSync(new URL('runtime/'+i.uri,root)));
 if(name.startsWith('survivor_')||name.startsWith('zombie_')||name.startsWith('dog_')){
  assert.equal(g.skins.length,1);assert.ok(g.skins[0].joints.length>=18);assert.ok(g.meshes.some(m=>m.primitives.some(p=>p.attributes.JOINTS_0!==undefined&&p.attributes.WEIGHTS_0!==undefined)));
  const clips=g.animations.map(a=>a.name),required=name.startsWith('dog_')?['idle','run','bark','growl','attack','bite','jump','react','down']:name.startsWith('survivor_')?['idle','walk','run','sprint','aim','shoot','reload','jump','slide','dodge','stumble','hurt','death']:['idle','wander','walk','run','attack','grab','hurt','hit_head','hit_leg','stumble','fall','crawl','die'];for(const c of required)assert.ok(clips.includes(c),c);
  for(const a of g.animations)assert.ok(a.samplers.some(s=>g.accessors[s.input].count>3));
 }
 if(name.startsWith('weapon_'))for(const c of ['fire','reload'])assert.ok(g.animations.some(a=>a.name===c));
 assert.ok(g.materials.some(m=>m.normalTexture));assert.ok(g.materials.some(m=>m.pbrMetallicRoughness?.metallicRoughnessTexture));
});
test('42 production assets, new variants and actual selection images',()=>{assert.equal(manifest.assets.length,42);for(const n of ['zombie_military','zombie_stalker','weapon_revolver','weapon_smg','weapon_hunting','warehouse','truck_wreck','house_ruin','camp','bridge'])assert.ok(manifest.assets.includes(n));for(const n of ['survivor_mara','survivor_ellis','dog_shepherd','dog_husky','weapon_pistol','weapon_revolver','weapon_shotgun','weapon_rifle','weapon_smg','weapon_hunting'])assert.ok(existsSync(new URL('ui/'+n+'.png',root)));});
test('survivor skeleton has an actual hand/weapon attachment socket',()=>{for(const name of ['survivor_mara','survivor_ellis']){const g=JSON.parse(readFileSync(new URL('runtime/'+name+'.gltf',root)));assert.ok(g.nodes.some(n=>n.name==='weapon_socket'));}});
test('ground export has matching boundary heights and upward normals',()=>{
 const g=JSON.parse(readFileSync(new URL('runtime/terrain.gltf',root))),b=readFileSync(new URL('runtime/'+g.buffers[0].uri,root));const me=g.meshes.find(m=>m.name==='Irregular_earth');assert.ok(me);const p=me.primitives[0];const positions=g.accessors[p.attributes.POSITION],normals=g.accessors[p.attributes.NORMAL];
 const data=(a,i)=>{const v=g.bufferViews[a.bufferView],o=(v.byteOffset||0)+(a.byteOffset||0)+i*(v.byteStride||12);return [b.readFloatLE(o),b.readFloatLE(o+4),b.readFloatLE(o+8)];};const first=new Map(),last=new Map();
 for(let i=0;i<positions.count;i++){const v=data(positions,i),n=data(normals,i);assert.ok(n[1]>.85);if(Math.abs(v[2])<1e-5)first.set(v[0].toFixed(3),v[1]);if(Math.abs(v[2]-48)<1e-5)last.set(v[0].toFixed(3),v[1]);}
 assert.ok(first.size>30);assert.equal(first.size,last.size);for(const [x,y]of first)assert.ok(Math.abs(y-last.get(x))<1e-5);
});
test('CC0 base and skin provenance and saved production blend exist',()=>{assert.ok(existsSync(new URL('../../blender/survivor-runs-production.blend',import.meta.url)));const source=readFileSync(new URL('../../blender/upgrade/reference-base/makehuman-base.obj',import.meta.url),'utf8');assert.ok(source.includes('released as CC0'));assert.ok(existsSync(new URL('../../blender/upgrade/reference-base/CC0-LEGAL.txt',import.meta.url)));});
