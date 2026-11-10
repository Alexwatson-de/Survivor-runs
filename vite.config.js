import {defineConfig} from 'vite';import {mkdir,cp} from 'node:fs/promises';import path from 'node:path';
// Only engine-used runtime assets ship in the website. Full Blender GLBs stay in source.
export default defineConfig(({command})=>({publicDir:command==='build'?false:'public',plugins:[{
 name:'survivor-runtime-assets',async closeBundle(){if(command!=='build')return;const out=path.resolve('dist/assets');await mkdir(out,{recursive:true});for(const name of ['runtime','supplied','ui','manifest.json','particle-smoke.png'])await cp(path.resolve('public/assets',name),path.join(out,name),{recursive:true});}
}]}));
