"""Re-export in a disposable mirror; never overwrite the shared source checkout."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, tempfile, zipfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/art/bestiary-v43/wood-kite'
BUILD=ROOT/'build/bestiary-v43'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def native_check():
 (OUT/'native-bake-check.json').unlink(missing_ok=True)
 # Use this project's existing mapped Forge/GeckoLib dependency path. Extract
 # GeckoLib's own bundled math dependency, as Forge's jar-in-jar loader would.
 cp=(ROOT/'build/bestiary-v41/classpath.txt').read_text().strip()
 gecko=next(Path(p) for p in cp.split(os.pathsep) if 'geckolib' in p)
 with zipfile.ZipFile(gecko) as z:
  math_jar=BUILD/'mclib-20.jar';math_jar.write_bytes(z.read('META-INF/jarjar/mclib-20.jar'))
 cp=str(math_jar)+os.pathsep+cp
 java=Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin')
 classes=BUILD/'native-classes';classes.mkdir(exist_ok=True)
 logpath=BUILD/'native-kite.log';output=BUILD/'native-kite.json'
 with logpath.open('w') as log:
  commands=[
   [str(java/'javac'),'-proc:none','-cp',cp,'-d',str(classes),str(ROOT/'tools/art/bestiary-v43/NativeKiteCheck.java')],
   [str(java/'java'),'-Djava.awt.headless=true','-cp',str(classes)+os.pathsep+cp,'NativeKiteCheck',str(ROOT),str(output)]]
  for command in commands:
   run=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
   if run.returncode:
    log.flush();raise RuntimeError(logpath.read_text()[-3500:])
 data=json.loads(output.read_text())
 report={id:{k:v for k,v in row.items() if k!='bakedFaces'} for id,row in data.items()}
 (OUT/'native-bake-check.json').write_text(json.dumps(dict(status='PASS',
  method='Actual installed GeckoLib4.8.4 JsonUtil.GEO_GSON and Builtin BakedModelFactory; no window/world',
  java='17',forms=report,gecko_jar_sha256=digest(gecko),
  pending='Actual game resource reload, native rendering/animations and combat'),indent=2)+'\n')
 print(logpath.read_text().strip())

def main():
 BUILD.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='wood-kite-export-',dir=BUILD) as td:
  mirror=Path(td)
  for name in ['tools/blueprint/generate_wood_kite.py','tools/blueprint/generate_tide_yasha.py',
   'tools/art/bestiary-v43/wood_kite_materials.py','tools/art/bestiary-v43/wood-kite-material-map.json',
   'docs/art/bestiary-v43/wing-reference-review.json']:
   target=mirror/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
  run=subprocess.run([os.sys.executable,str(mirror/'tools/blueprint/generate_wood_kite.py')],
   cwd=mirror,text=True,capture_output=True,check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  (BUILD/'isolated-export.log').write_text(run.stdout+run.stderr)
  matches={}
  for id in ['luban_yisha','luban_yisha_metal','wood_kite_thunder_bomb']:
   for folder,suffix in [('geo','.geo.json'),('animations','.animation.json'),('textures/entity','.png')]:
    path=Path('src/main/resources/assets/dynasty')/folder/'blueprint/boss'/(id+suffix)
    assert (mirror/path).read_bytes()==(ROOT/path).read_bytes(),('Nonreproducible export',path)
    matches[str(path)]=digest(ROOT/path)
  (OUT/'reexport-check.json').write_text(json.dumps(dict(status='PASS',
   isolated_export=True,production_not_overwritten=True,matching_files=matches),indent=2)+'\n')
  print('PASS: isolated authoritative re-export; nine runtime files byte-identical.')
  # The old diagnostic baseline is retained, including the four deferred forms.
  baseline=json.loads((ROOT/'docs/art/bestiary-v43/unfinished-registered.json').read_text())['findings']
  unchanged={}
  for id,record in baseline.items():
   checks={}
   for key,folder,suffix in [('geo','geo','.geo.json'),('texture','textures/entity','.png'),('animation','animations','.animation.json')]:
    p=ROOT/'src/main/resources/assets/dynasty'/folder/'blueprint/boss'/(id+suffix)
    expected=record['hashes'][key]
    if id.startswith('luban_yisha') and key!='animation':
     if key=='geo':
      from wood_kite_materials import geometry_signature
      before=json.loads((OUT/'before'/(id+suffix)).read_text())['minecraft:geometry'][0]
      after=json.loads(p.read_text())['minecraft:geometry'][0]
      assert geometry_signature(before)==geometry_signature(after)
      checks['geometry_except_uv']='UNCHANGED'
     continue
    assert digest(p)==expected,('Unexpected change to deferred/animation resource',p)
    checks[key]='UNCHANGED'
   unchanged[id]=checks
  (OUT/'preservation-check.json').write_text(json.dumps(dict(status='PASS',resources=unchanged),indent=2)+'\n')
  print('PASS: body geometry, actions and deferred four forms unchanged.')
 if '--native' in os.sys.argv:native_check()

if __name__=='__main__':main()
