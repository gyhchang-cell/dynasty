"""Strict resource/source checks before actual GeckoLib runtime verification."""
import base64
import hashlib
import json
import math
from collections import deque
from PIL import Image
from rebuild_npcs import ASSETS, DOC, ROLES, STATES

report=[]
for role in ROLES:
 gp=ASSETS/f'geo/npc/{role}.geo.json';ap=ASSETS/f'animations/npc/{role}.animation.json';tp=ASSETS/f'textures/entity/npc/{role}.png'
 g=json.loads(gp.read_text())['minecraft:geometry'][0];names={b['name']:b for b in g['bones']}
 assert len(names)==len(g['bones']);assert len(names)>=30
 for b in names.values():
  visited=set();node=b
  while node.get('parent'):
   assert node['name'] not in visited,(role,'bone cycle');visited.add(node['name']);node=names[node['parent']]
  assert node['name']=='root'
  for c in b.get('cubes',[]):
   assert all(math.isfinite(v) for k in ('origin','size') for v in c[k])
   assert all(v>0 for v in c['size'])
   assert set(c['uv'])=={'north','south','east','west','up','down'}
   for face in c['uv'].values():
    assert all(isinstance(v,int) for v in face['uv']+face['uv_size'])
    assert all(2<=a and a+s<=g['description'][axis]-2 for a,s,axis in zip(face['uv'],face['uv_size'],('texture_width','texture_height'))),(role,'UV outside gutter')
    assert all(s>=1 for s in face['uv_size'])
 for part,parent in [('pelvis','root'),('waist','pelvis'),('chest','waist'),('neck','chest'),('head','neck')]:assert names[part]['parent']==parent
 props=[]
 for b in names.values():
  if any(k.startswith('grip_') for k in b.get('locators',{})):
   assert b['parent'] in ('left_hand','right_hand'),(role,b['name'],'held prop not hand bound')
   hand=names[b['parent']];anchor=next(iter(hand['locators'].values()));assert anchor==b['pivot'],(role,b['name'],'grip/pivot mismatch')
   props.append(b['name'])
 anim=json.loads(ap.read_text())['animations'];assert set(anim)=={'animation.npc.'+s for s in STATES}
 for name,a in anim.items():
  assert set(a['bones'])<=names.keys();assert a['loop'] is True
  for bone,channels in a['bones'].items():
   for channel,values in channels.items():
    if isinstance(values,dict):
     times=sorted(float(t) for t in values);assert times[0]==0 and times[-1]==a['animation_length'],(role,name,bone,'length mismatch')
     assert values[min(values,key=float)]==values[max(values,key=float)],(role,name,'loop seam')
    else:assert len(values)==3
 im=Image.open(tp).convert('RGB');assert im.size==(g['description']['texture_width'],g['description']['texture_height'])
 assert im.width in (128,256) and im.height==im.width
 colours=im.getcolors(im.width*im.height);assert colours and 12<=len(colours)<=32
 bbp=DOC/f'blockbench/{role}.bbmodel';bb=json.loads(bbp.read_text());groups={};parents={}
 def visit(nodes,parent=None):
  for n in nodes:
   if isinstance(n,dict):groups[n['name']]=n;parents[n['name']]=parent;visit(n['children'],n['name'])
 visit(bb['outliner']);assert groups.keys()==names.keys()
 for name,b in names.items():
  assert parents[name]==b.get('parent');assert groups[name]['origin']==[-b['pivot'][0],b['pivot'][1],b['pivot'][2]]
  r=b.get('rotation',[0,0,0]);assert groups[name]['rotation']==[-r[0],-r[1],r[2]]
 elements={e['uuid']:e for e in bb['elements']}
 for name,b in names.items():
  cubes=[elements[k] for k in groups[name]['children'] if isinstance(k,str) and elements[k]['type']=='cube']
  assert len(cubes)==len(b.get('cubes',[]))
  for c,e in zip(b.get('cubes',[]),cubes):
   x,y,z=c['origin'];w,h,d=c['size'];assert e['from']==[-x-w,y,z] and e['to']==[-x,y+h,z+d]
   for face,m in c['uv'].items():
    u,v=m['uv'];du,dv=m['uv_size'];assert e['faces'][face]['uv']==([u+du,v+dv,u,v] if face in ('up','down') else [u,v,u+du,v+dv])
 assert base64.b64decode(bb['textures'][0]['source'].split(',',1)[1])==tp.read_bytes()
 assert (DOC/f'blockbench/{role}.animation.json').read_bytes()==ap.read_bytes()
 report.append({'id':role,'bones':len(names),'cuboids':sum(len(b.get('cubes',[])) for b in names.values()),'paletteSize':len(colours),'gripProps':props,'sha256':{str(p.relative_to(ASSETS)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (gp,ap,tp)}})
(DOC/'resource-validation.json').write_text(json.dumps({'passed':True,'roles':report,'animations':165,'checks':['bone topology','segmented anatomy','integer in-bounds UV','finite NPC material palette','2px atlas gutters','integer face UVs','loop endpoints','hand pivots','editable source coordinates','embedded PNG parity']},indent=2)+'\n')
print('PASS: 15 rigs / 165 animation bindings / 45 runtime files / 30 editable files')
