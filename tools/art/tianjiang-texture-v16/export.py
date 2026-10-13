"""Texture-only export onto the approved per-face UVs. Never writes JSON assets."""
import sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'tools/art/tianjiang-steve-v15'))
from create import build,paint,PAL,TARGETS,hashes,D as PREV
from PIL import Image
D=R/'docs/art/tianjiang-texture-v16';ID='nine_heaven_general'
def export():
 owner=D/'export-owner.json';baseline=json.loads((owner if owner.exists() else D/'before-hashes.json').read_text())
 assert hashes()==baseline,'Concurrent edit: refuse to overwrite'
 locked={p:p.read_bytes() for p in TARGETS[:2]}
 actual=json.loads(TARGETS[0].read_text())['minecraft:geometry'][0]
 rig=build();by={b['name']:b for b in actual['bones']}
 tex=Image.new('RGB',(128,128),PAL['ink']);islands=[]
 for b in rig.bones:
  for i,c in enumerate(b['cubes']):
   for f,u in by[b['name']]['cubes'][i]['uv'].items():
    x,y=u['uv'];w,h=u['uv_size'];tex.paste(paint(c['_role'],f,w,h,c),(x,y))
    islands.append({'bone':b['name'],'cube':i,'face':f,'w':w,'h':h,'role':c['_role'],'rect':[x,y,w,h]})
 # The legacy full exporter must produce exactly the same pixels and UVs too.
 from create import atlas
 rebuilt,newislands=atlas(rig)
 assert rebuilt.tobytes()==tex.tobytes()
 for b in rig.bones:
  for i,c in enumerate(b['cubes']):assert c['uv']==by[b['name']]['cubes'][i]['uv']
 TARGETS[2].parent.mkdir(parents=True,exist_ok=True);tex.save(TARGETS[2])
 assert all(p.read_bytes()==data for p,data in locked.items()),'Locked geometry/animation changed'
 for n in ['texture','after']:
  tex.save(D/(n+'.png'));tex.resize((512,512),Image.Resampling.NEAREST).save(D/(n+'-4x.png'))
 before=Image.open(D/'before'/f'{ID}.png');before.save(D/'before.png');before.resize((512,512),Image.Resampling.NEAREST).save(D/'before-4x.png')
 owner.write_text(json.dumps(hashes(),indent=2)+'\n')
 # Keep the pre-existing export guard current; its geometry code is untouched.
 (PREV/'export-owner.json').write_text(json.dumps(hashes(),indent=2)+'\n')
 (D/'islands.json').write_text(json.dumps(islands,indent=2)+'\n')
 print('Updated only production PNG: 128x128, existing UV unchanged; legacy re-export identical.')
if __name__=='__main__':export()
