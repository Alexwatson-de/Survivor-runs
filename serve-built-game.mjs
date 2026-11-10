// Standalone local static host for the included optimized game. No npm dependencies.
import {createServer} from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {spawn} from 'node:child_process';
const root=path.resolve(fileURLToPath(new URL('./dist/',import.meta.url)));
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.gltf':'model/gltf+json','.bin':'application/octet-stream','.json':'application/json','.glb':'model/gltf-binary','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'};
const server=createServer(async(req,res)=>{
 try{
  const requested=decodeURIComponent(new URL(req.url,'http://localhost').pathname);const file=path.resolve(root,'.'+(requested==='/'?'/index.html':requested));
  if(!file.startsWith(root+path.sep)&&file!==path.join(root,'index.html')){res.writeHead(403);res.end('Forbidden');return;}
  if(!(await stat(file)).isFile())throw new Error('Not a file');
  const bytes=await readFile(file);res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Length':bytes.length});res.end(req.method==='HEAD'?undefined:bytes);
 }catch{res.writeHead(404,{'Content-Type':'text/plain'});res.end('Not found');}
});
let port=Number(process.env.PORT)||5189;
server.on('error',error=>{if(error.code==='EADDRINUSE'&&port<5199){server.listen(++port,'127.0.0.1');}else{console.error(error.message);process.exitCode=1;}});
server.on('listening',()=>{const url='http://127.0.0.1:'+port;console.log('SURVIVOR RUNS — '+url+'\nPress Ctrl+C to stop.');if(process.argv.includes('--open')){const command=process.platform==='darwin'?'open':process.platform==='win32'?'cmd':'xdg-open';const args=process.platform==='win32'?['/c','start','',url]:[url];spawn(command,args,{stdio:'ignore'}).on('error',()=>console.log('Open the URL above in your browser.'));}});
server.listen(port,'127.0.0.1');
