"""Narrow resource/re-export/native check for the two existing cauldron forms."""
from pathlib import Path
import json, os, shutil, subprocess, tempfile
import numpy as np
from PIL import Image
from wood_kite_materials import geometry_signature
from check_marshal_export import native, digest
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/art/bestiary-v43/taoyan';BUILD=ROOT/'build/bestiary-v43'
A=Path('src/main/resources/assets/dynasty');IDS=('taoyan_zhishi','taoyan_zhishi_phase2')

def main():
 report={'status':'PASS','forms':{},'protected_resources':{}}
 union=json.loads((OUT/'union-islands.json').read_text());occupied=np.zeros((512,512),bool)
 for q in union:
  x,y,w,h=q['rect'];assert x>=1 and y>=1 and x+w<512 and y+h<512
  assert not occupied[y-1:y+h+1,x-1:x+w+1].any();occupied[y-1:y+h+1,x-1:x+w+1]=True
 expected={tuple(q['key']):q['rect'] for q in union}
 for ident in IDS:
  geo=json.loads((ROOT/A/f'geo/blueprint/boss/{ident}.geo.json').read_text())['minecraft:geometry'][0]
  before=json.loads((OUT/'before'/f'{ident}.geo.json').read_text())['minecraft:geometry'][0]
  assert geometry_signature(geo)==geometry_signature(before)
  assert (ROOT/A/f'animations/blueprint/boss/{ident}.animation.json').read_bytes()==(OUT/'before'/f'{ident}.animation.json').read_bytes()
  png=np.array(Image.open(ROOT/A/f'textures/entity/blueprint/boss/{ident}_body.png').convert('RGB'));assert png.shape==(512,512,3)
  for q in union:
   x,y,w,h=q['rect'];tile=png[y:y+h,x:x+w]
   assert np.array_equal(np.pad(tile,((1,1),(1,1),(0,0)),mode='edge'),png[y-1:y+h+1,x-1:x+w+1])
  islands=json.loads((OUT/ident/'uv-islands.json').read_text())
  for q in islands:
   key=(q['bone'].removeprefix('old_'),q['cube'],q['face']);assert q['rect']==expected[key]
  report['forms'][ident]={'geometry_except_UV':'UNCHANGED','animation_bytes':'UNCHANGED','actual_face_islands':len(islands),'UV_bounds_overlap_gutters':'PASS','all_union_pixels_present':len(union)}
 for p,sha in json.loads((OUT/'protected-before.json').read_text()).items():
  assert digest(ROOT/p)==sha,p
  report['protected_resources'][p]=sha
 renderer=(ROOT/'src/main/java/com/dynasty/blueprint/boss/client/TaoyanCauldronRenderer.java').read_text()
 assert 'e.form()==2&&e.transition()&&e.level().getGameTime()-e.shifted()<32?TaoyanCauldron.ID:form(e))+"_body"' in renderer
 assert 'getTextureResource(CauldronGroundSpell e){return resource("textures/entity/blueprint/boss/",TaoyanCauldron.ID,".png");}' in renderer
 report['transition']={'old32tick_timing':'UNCHANGED','both_atlases_cover_all_phase2_UVs':True,'common_cube_UVs_identical':True}
 with tempfile.TemporaryDirectory(prefix='taoyan-export-',dir=BUILD) as td:
  mirror=Path(td)
  for p in ['tools/blueprint/generate_taoyan_cauldrons.py','tools/blueprint/generate_tide_yasha.py','tools/art/secondary-cuboid/review_models.py',
   'tools/art/inventory-refresh/transparent.py','docs/art/inventory-refresh-v1/white-backgrounds.json','tools/art/bestiary-v43/taoyan_materials.py',
   'tools/art/bestiary-v43/wood_kite_materials.py','tools/art/bestiary-v43/taoyan-material-map.json','docs/art/bestiary-v43/taoyan-reference-review.json']:
   dest=mirror/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,dest)
  (mirror/A/'textures/item').mkdir(parents=True,exist_ok=True)
  for ident in json.loads((ROOT/'docs/art/inventory-refresh-v1/white-backgrounds.json').read_text()):
   p=A/f'textures/item/{ident}.png';shutil.copyfile(ROOT/p,mirror/p)
  run=subprocess.run([os.sys.executable,str(mirror/'tools/blueprint/generate_taoyan_cauldrons.py')],cwd=mirror,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  (BUILD/'taoyan-isolated-export.log').write_text(run.stdout+run.stderr);assert run.returncode==0,(run.stdout+run.stderr)[-3000:]
  paths=[]
  for ident in IDS:
   paths.extend([A/f'geo/blueprint/boss/{ident}.geo.json',A/f'animations/blueprint/boss/{ident}.animation.json',A/f'textures/entity/blueprint/boss/{ident}.png',A/f'textures/entity/blueprint/boss/{ident}_body.png'])
  for p in paths:assert (mirror/p).read_bytes()==(ROOT/p).read_bytes(),('Nonreproducible export',str(p))
  report['isolated_reexport']={'status':'PASS','byte_identical_files':len(paths),'production_overwritten':False}
 (OUT/'resource-verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS two form geometry/actions, eleven protected files, full union UVs,32tick texture compatibility, eight identical reexports.')
 if '--native' in os.sys.argv:native(IDS,((38,118),(63,153)),OUT,'taoyan')
if __name__=='__main__':main()
