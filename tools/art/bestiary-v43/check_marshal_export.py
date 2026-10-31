"""Check actual actor UV/materials and re-export only in a disposable mirror."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, tempfile, zipfile
import numpy as np
from PIL import Image
from wood_kite_materials import geometry_signature

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/art/bestiary-v43/marshal'
BUILD=ROOT/'build/bestiary-v43'
ASSET=Path('src/main/resources/assets/dynasty')
IDS=('gongsun_wuwang','gongsun_wuwang_foot')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 report={'status':'PASS','forms':{},'protected_resources':{}}
 for ident in IDS:
  gp=ASSET/f'geo/blueprint/boss/{ident}.geo.json'
  geo=json.loads((ROOT/gp).read_text())['minecraft:geometry'][0]
  before=json.loads((OUT/'before'/f'{ident}.geo.json').read_text())['minecraft:geometry'][0]
  assert geometry_signature(geo)==geometry_signature(before)
  ap=ASSET/f'animations/blueprint/boss/{ident}.animation.json'
  assert (ROOT/ap).read_bytes()==(OUT/'before'/f'{ident}.animation.json').read_bytes()
  png=np.array(Image.open(ROOT/ASSET/f'textures/entity/blueprint/boss/{ident}_body.png').convert('RGB'))
  assert png.shape==(512,512,3)
  occupied=np.zeros((512,512),bool)
  islands=json.loads((OUT/ident/'uv-islands.json').read_text())
  for q in islands:
   x,y,w,h=q['rect'];assert x>=1 and y>=1 and x+w<512 and y+h<512
   assert not occupied[y-1:y+h+1,x-1:x+w+1].any(),q
   occupied[y-1:y+h+1,x-1:x+w+1]=True
   tile=png[y:y+h,x:x+w]
   assert np.array_equal(np.pad(tile,((1,1),(1,1),(0,0)),mode='edge'),png[y-1:y+h+1,x-1:x+w+1])
  report['forms'][ident]={'geometry_except_uv':'UNCHANGED','animation_bytes':'UNCHANGED','face_islands':len(islands),'UV_bounds_overlap_gutters':'PASS','body_png_sha256':digest(ROOT/ASSET/f'textures/entity/blueprint/boss/{ident}_body.png')}
 for p,sha in json.loads((OUT/'protected-before.json').read_text()).items():
  assert digest(ROOT/p)==sha,p
  report['protected_resources'][p]=sha
 renderer=(ROOT/'src/main/java/com/dynasty/blueprint/boss/client/BlindMarshalRenderer.java').read_text()
 assert 'form(e)+"_body",".png"' in renderer
 assert 'getTextureResource(MarshalProjectile e){return resource("textures/entity/blueprint/boss/",BlindMarshal.ID,".png");}' in renderer
 with tempfile.TemporaryDirectory(prefix='marshal-export-',dir=BUILD) as td:
  mirror=Path(td)
  for p in ['textures/entity/blueprint/boss','textures/item']:(mirror/ASSET/p).mkdir(parents=True,exist_ok=True)
  for p in ['tools/blueprint/generate_blind_marshal.py','tools/blueprint/generate_tide_yasha.py',
            'tools/art/secondary-cuboid/review_models.py','tools/art/inventory-refresh/transparent.py','docs/art/inventory-refresh-v1/white-backgrounds.json',
            'tools/art/bestiary-v43/marshal_materials.py','tools/art/bestiary-v43/wood_kite_materials.py',
            'tools/art/bestiary-v43/marshal-material-map.json','docs/art/bestiary-v43/marshal-reference-review.json']:
   dest=mirror/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,dest)
  # The legacy exporter finishes with global icon cleanup. Supply its inputs in
  # the disposable checkout only; it never runs against the shared worktree.
  for ident in json.loads((ROOT/'docs/art/inventory-refresh-v1/white-backgrounds.json').read_text()):
   p=ASSET/f'textures/item/{ident}.png';shutil.copyfile(ROOT/p,mirror/p)
  run=subprocess.run([os.sys.executable,str(mirror/'tools/blueprint/generate_blind_marshal.py')],cwd=mirror,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  (BUILD/'marshal-isolated-export.log').write_text(run.stdout+run.stderr)
  assert run.returncode==0,(run.stdout+run.stderr)[-4000:]
  paths=[]
  for ident in IDS:
   paths.extend([ASSET/f'geo/blueprint/boss/{ident}.geo.json',ASSET/f'animations/blueprint/boss/{ident}.animation.json',ASSET/f'textures/entity/blueprint/boss/{ident}.png',ASSET/f'textures/entity/blueprint/boss/{ident}_body.png'])
  for p in paths:
   assert (mirror/p).read_bytes()==(ROOT/p).read_bytes(),('Reexport mismatch',str(p))
  report['isolated_reexport']={'status':'PASS','matching_runtime_files':len(paths),'production_checkout_overwritten':False}
 (OUT/'resource-verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: two forms geometry/actions, twelve protected resources, UV bounds/gutters and eight byte-identical reexports.')
 if '--native' in os.sys.argv:native()

def native(ids=IDS,counts=((37,80),(39,86)),doc=OUT,tag='marshal'):
 # Adapt the existing headless harness, keeping use of the installed native loader.
 source=(ROOT/'tools/art/bestiary-v43/NativeKiteCheck.java').read_text()
 classname='Native'+tag.title()+'Check'
 source=source.replace('NativeKiteCheck',classname).replace('"luban_yisha", "luban_yisha_metal"',', '.join('"'+i+'"' for i in ids))
 source=source.replace('"textures/entity/blueprint/boss/"+id+".png"','"textures/entity/blueprint/boss/"+id+"_body.png"')
 source=source.replace('id.endsWith("_metal") ? 136 : 172',f'id.equals("{ids[1]}") ? {counts[1][1]} : {counts[0][1]}')
 source=source.replace('bones!=73',f'bones!=(id.equals("{ids[1]}") ? {counts[1][0]} : {counts[0][0]})')
 harness=BUILD/(classname+'.java');harness.write_text(source)
 cp=(ROOT/'build/bestiary-v41/classpath.txt').read_text().strip()
 gecko=next(Path(p) for p in cp.split(os.pathsep) if 'geckolib' in p)
 with zipfile.ZipFile(gecko) as z:
  mathjar=BUILD/'mclib-20.jar';mathjar.write_bytes(z.read('META-INF/jarjar/mclib-20.jar'))
 cp=str(mathjar)+os.pathsep+cp
 java=Path('/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin')
 classes=BUILD/(tag+'-native-classes');classes.mkdir(exist_ok=True)
 output=BUILD/(tag+'-native-bake.json');logpath=BUILD/(tag+'-native.log')
 with logpath.open('w') as log:
  for cmd in [[str(java/'javac'),'-proc:none','-cp',cp,'-d',str(classes),str(harness)],
              [str(java/'java'),'-Djava.awt.headless=true','-cp',str(classes)+os.pathsep+cp,classname,str(ROOT),str(output)]]:
   result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
   if result.returncode:
    log.flush();raise RuntimeError(logpath.read_text()[-4000:])
 data=json.loads(output.read_text())
 forms={id:{k:v for k,v in row.items() if k!='bakedFaces'} for id,row in data.items()}
 (doc/'native-bake-check.json').write_text(json.dumps({'status':'PASS','method':'Actual installed GeckoLib4.8.4 parser and Builtin mesh factory, Java17 headless; no window/world','forms':forms,'game_render_test':False,'game_test':'PENDING'},indent=2)+'\n')
 print(logpath.read_text().strip())

if __name__=='__main__':main()
