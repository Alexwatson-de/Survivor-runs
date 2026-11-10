import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync,readdirSync,existsSync} from 'node:fs';
const dir=new URL('../public/assets/',import.meta.url);
function glb(name){const b=readFileSync(new URL(name,dir));assert.equal(b.readUInt32LE(0),0x46546c67);assert.equal(b.readUInt32LE(4),2);assert.equal(b.readUInt32LE(8),b.length);return JSON.parse(b.subarray(20,20+b.readUInt32LE(12)).toString());}
for(const name of readdirSync(dir).filter(n=>n.endsWith('.glb')))test('Blender export integrity / '+name,()=>{
 const g=glb(name);assert.equal(g.scenes.length,1);assert.ok(!g.nodes.some(n=>n.name==='Cube'));assert.ok(g.meshes.length>0);
 for(const m of g.meshes)for(const p of m.primitives){assert.ok('TEXCOORD_0' in p.attributes);assert.ok('NORMAL' in p.attributes);}
 assert.ok(g.images.length>0);for(const image of g.images)assert.ok(image.bufferView!==undefined,'textures embedded, no external URLs');
});
for(const [name,expected]of [['survivor_mara',['run','shoot','reload','jump','slide','death']],['survivor_ellis',['run','shoot','reload','death']],['zombie_walker',['walk','run','attack','die']],['zombie_runner',['walk','run','attack','die']],['zombie_brute',['walk','run','attack','die']],['dog_shepherd',['run','bark','attack','bite','jump','idle','react']],['dog_husky',['run','bark','attack','bite','jump','idle','react']],['weapon_pistol',['fire','reload']],['weapon_shotgun',['fire','reload']],['weapon_rifle',['fire','reload']]])test('real animation clips / '+name,()=>{
 const g=glb(name+'.glb');for(const clip of expected){const a=g.animations.find(x=>x.name===clip);assert.ok(a,clip);assert.ok(a.channels.length>0);assert.ok(a.samplers.every(s=>g.accessors[s.input].count>1));}
});
test('editable Blender workshop and source stages exist',()=>{assert.ok(existsSync(new URL('../blender/ashfall-asset-workshop.blend',import.meta.url)));for(const stage of ['01_asset_foundation','02_characters','03_animation_weapons','04_environment','05_scene_review'])assert.ok(existsSync(new URL('../blender/'+stage+'.py',import.meta.url)));});
test('LOD triangle reduction is real',()=>{for(const n of ['tree_pine','tree_dead','car_wreck','rock']){const count=g=>g.meshes.reduce((s,m)=>s+m.primitives.reduce((a,p)=>a+g.accessors[p.indices].count/3,0),0);assert.ok(count(glb(n+'_lod.glb'))<count(glb(n+'.glb'))*.6);}});
