"""Surface-only export on the accepted v5 bodies; animations are immutable."""
import sys,json,runpy,hashlib,base64
from PIL import Image
import presence as p
p.D=p.R/'docs/art/boss-materials-v6'
p.TARGETS=['xianzhen_duantoujiang','rebel_general']
p.SAMPLES={'rebel_general':[('idle',0),('attack',9),('attack',12),('attack',22)],
 'xianzhen_duantoujiang':[('idle',0),('roar',18),('roar',24),('roar',44)]}
p.ATTACKS.update(rebel_general='attack',xianzhen_duantoujiang='roar')
p.LABELS=('BEFORE / v5 PNG · 同一动作与形体','AFTER / v6 PNG · 同相机同比例同光照')

def export():
 p.retexture(p.TARGETS,p.D)
 runpy.run_path(str(p.R/'tools/art/boss-forms/export_bbmodel.py'),run_name='__main__')

def validate():
 p.validate()
 for id in p.IDS+['hammer_chain']:
  path=p.A/'animations/boss_forms'/(id+'.animation.json')
  assert path.read_bytes()==(p.D/'before'/path.name).read_bytes(),(id,'animation changed')
  path=p.A/'geo/boss_forms'/(id+'.geo.json')
  assert path.read_bytes()==(p.D/'before'/path.name).read_bytes(),(id,'geometry changed')
  if id not in p.TARGETS:
   path=p.A/'textures/entity/boss_forms'/(id+'.png')
   assert path.read_bytes()==(p.D/'before'/path.name).read_bytes(),(id,'non-target texture changed')
 for id in p.TARGETS:
  im=Image.open(p.A/'textures/entity/boss_forms'/(id+'.png'));g=json.loads((p.A/'geo/boss_forms'/(id+'.geo.json')).read_text())['minecraft:geometry'][0]
  boxes=[]
  for b in g['bones']:
   for c in b['cubes']:
    for f,uv in c['uv'].items():
     x,y=uv['uv'];w,h=uv['uv_size'];assert min(x,y,w,h)>0 and x+w<im.width and y+h<im.height
     assert all(x+w<=X or X+W<=x or y+h<=Y or Y+H<=y for X,Y,W,H in boxes)
     boxes.append((x,y,w,h))
  bb=json.loads((p.R/'docs/art/boss-forms-v2/blockbench'/(id+'.bbmodel')).read_text())
  assert base64.b64decode(bb['textures'][0]['source'].split(',')[1])==(p.A/'textures/entity/boss_forms'/(id+'.png')).read_bytes()
 print('PASS: every animation byte unchanged, unique in-bounds UV islands, editable PNG equals runtime',flush=True)

if __name__=='__main__':
 if '--review-only' not in sys.argv:export();validate()
 if '--export-only' not in sys.argv:p.review()
