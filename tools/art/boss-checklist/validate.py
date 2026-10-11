"""Focused resource invariants and full-clip floor/UV checks for this export."""
from refine import *
import hashlib,subprocess

def stripped(g):
 g=copy.deepcopy(g);desc=g['minecraft:geometry'][0]['description']
 for k in ['texture_width','texture_height']:desc.pop(k,None)
 for b in g['minecraft:geometry'][0]['bones']:
  for c in b.get('cubes',[]):c.pop('uv',None)
 return g
report={}
for id in IDS:
 gp=A/f'geo/boss_cuboid/{id}.geo.json';ap=A/f'animations/boss_cuboid/{id}.animation.json';tp=A/f'textures/entity/boss_cuboid/{id}.png'
 geo=json.loads(gp.read_text());g=geo['minecraft:geometry'][0];an=json.loads(ap.read_text())['animations'];old=json.loads((D/'before'/f'{id}.animation.json').read_text())['animations'];bones=g['bones'];names=[b['name'] for b in bones]
 assert len(names)==len(set(names));assert list(an)==list(old)
 for b in bones:assert not b.get('parent') or names.index(b['parent'])<names.index(b['name'])
 if id!='nine_heaven_general':
  assert stripped(geo)==stripped(json.loads((D/'before'/f'{id}.geo.json').read_text()))
  if id=='dragon_king':assert ap.read_bytes()==(D/'before'/f'{id}.animation.json').read_bytes()
  else:
   stripped_an=copy.deepcopy(an)
   for k in ['walk','attack']:stripped_an[k]['bones'].pop('root',None)
   assert stripped_an==old
 else:assert not any(n in names for n in ['left_leg','right_leg','waist','pelvis'])
 im=Image.open(tp);assert im.size==(g['description']['texture_width'],g['description']['texture_height']);occupied=np.zeros(im.size[::-1],dtype=np.uint8)
 for b in bones:
  for c in b.get('cubes',[]):
   assert min(c['size'])>0
   assert set(c['uv'])=={'north','south','east','west','up','down'}
   for uv in c['uv'].values():
    x,y=uv['uv'];w,h=uv['uv_size'];assert x>=1 and y>=1 and x+w<im.width and y+h<im.height
    assert not occupied[y:y+h,x:x+w].any();occupied[y:y+h,x:x+w]=1
 clips={}
 for clip,a in an.items():
  assert a['animation_length']==old[clip]['animation_length'] and a.get('loop')==old[clip].get('loop')
  assert set(a['bones']).issubset(names)
  for ch in a['bones'].values():
   for track in ch.values():
    for val in (track.values() if isinstance(track,dict) else [track]):assert len(val)==3 and np.isfinite(val).all()
  low=[]
  for t in np.linspace(0,a['animation_length'],161):low.append(min(p[1] for p in vertices(bones,a['bones'],float(t))))
  clips[clip]={'minY_units':round(min(low),4),'end_minY_units':round(low[-1],4),'duration':a['animation_length']}
  if id=='dragon_emperor' and clip in ['walk','attack']:assert min(low)>-.015
  if id=='nine_heaven_general' and clip=='death':assert min(low)>-.015 and abs(low[-1]-.03)<.01
 verts=np.array(vertices(bones,{},0));scale=1.4 if id=='dragon_emperor' else 1.35 if id=='dragon_king' else 1
 report[id]={'atlas':im.size,'coloredPixels':int(occupied.sum()),'modelBounds_blocks':((verts.max(0)-verts.min(0))*scale/16).round(3).tolist(),'clips':clips,'hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [gp,ap,tp]}}
# The eight approved bosses must stay byte-identical to the last art commit.
protected=[]
for folder in ['geo/boss_forms','animations/boss_forms','textures/entity/boss_forms']:
 for p in (A/folder).glob('*'):
  if p.is_file():
   before=subprocess.check_output(['git','show','bd487216:'+str(p.relative_to(R))],cwd=R);assert before==p.read_bytes();protected.append(str(p.relative_to(R)))
report['protectedApprovedResources']=len(protected)
(D/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
