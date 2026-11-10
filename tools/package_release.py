"""Package current Survivor Runs source, optimized game and editable artwork.
No credentials, node_modules, skin-pack download cache, full redundant GLBs or unrelated
workspace files are included. Verifies all archived bytes and executable launcher mode.
"""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'artifacts'/'releases';OUT.mkdir(parents=True,exist_ok=True)
files=[ROOT/n for n in ['README.md','TESTING.md','TESTING_0.2.md','DEVELOPMENT.md','UPGRADE_0.2.md','THIRD_PARTY_NOTICES.md','package.json','package-lock.json','index.html','vite.config.js','playwright.overhaul.config.js','Play-Survivor-Runs.command','Play-ASHFALL-RUN.command','serve-built-game.mjs']]
for folder in ['src','dist','tests/overhaul','tools','public/assets/runtime','public/assets/ui']:
    files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(ROOT/'public/assets'/n for n in ['manifest.json','particle-smoke.png'])
files.extend(ROOT/'blender'/n for n in ['survivor-runs-production.blend','ashfall-asset-workshop.blend'])
files.extend(p for p in (ROOT/'blender/upgrade').glob('*') if p.suffix in ['.py','.md'])
files.extend(p for p in (ROOT/'blender/upgrade/reference-base').iterdir() if p.suffix in ['.obj','.png','.mhmat','.md','.txt'])
for name in ['survivor-unit-tests.txt','survivor-final-browser-tests.txt','survivor-browser-results.json','survivor-effects-repeat.txt','survivor-focused-tests.txt','survivor-standalone-verification.json','survivor-asset-audit.json','survivor-build.txt','survivor-dependency-audit.txt','survivor-final-menu.png','survivor-final-gameplay.png','survivor-mobile-gameplay.png','survivor-runs-blender-world.png']:
    files.append(ROOT/'artifacts'/name)
extracted=OUT/'survivor-extracted-verification.json'
if extracted.exists():files.append(extracted)
files=sorted(set(files));manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
archive=OUT/'Survivor-Runs-0.2.0-game-and-source.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for p in files:z.write(p,'Survivor-Runs/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for p,digest in manifest.items():assert hashlib.sha256(z.read('Survivor-Runs/'+p)).hexdigest()==digest,p
    assert (z.getinfo('Survivor-Runs/Play-Survivor-Runs.command').external_attr>>16)&0o111
report={'archive':str(archive.relative_to(ROOT)),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'fileCount':len(files),'verified':True,'files':manifest}
(OUT/'survivor-release-manifest.json').write_text(json.dumps(report,indent=2))
(OUT/'Survivor-Runs-SHA256.txt').write_text(report['sha256']+'  '+archive.name+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
