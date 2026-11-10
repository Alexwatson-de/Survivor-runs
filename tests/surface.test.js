import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync,readdirSync} from 'node:fs';import {createHash} from 'node:crypto';
test('exported ground normals face up, preventing self-shadow bands',()=>{
 const b=readFileSync(new URL('../public/assets/terrain.glb',import.meta.url)),n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n)),bin=28+n;
 const earth=j.meshes.find(m=>m.name.startsWith('earth_tile'));assert.ok(earth);
 const a=j.accessors[earth.primitives[0].attributes.NORMAL],v=j.bufferViews[a.bufferView];assert.equal(a.componentType,5126);
 for(let i=0;i<a.count;i++){const o=bin+(v.byteOffset||0)+(a.byteOffset||0)+i*(v.byteStride||12);assert.ok(b.readFloatLE(o+4)>.9,'glTF +Y normals');}
});
test('optimized build ships the exact current Blender GLB bytes',()=>{
 const names=readdirSync(new URL('../public/assets/',import.meta.url)).filter(n=>n.endsWith('.glb'));assert.equal(names.length,34);
 const hash=b=>createHash('sha256').update(b).digest('hex');
 for(const n of names)assert.equal(hash(readFileSync(new URL('../public/assets/'+n,import.meta.url))),hash(readFileSync(new URL('../dist/assets/'+n,import.meta.url))),n);
});
