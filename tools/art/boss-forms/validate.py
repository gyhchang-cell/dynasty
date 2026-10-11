"""Offline structural and sampled geometry validation. Explicitly does not validate Java/runtime."""
import json,hashlib,math,subprocess
import numpy as np
from PIL import Image
from review import r,A,D,R
models=json.loads((D/'forms.json').read_text());report={};hashes={}
for i,m in enumerate(models):
 id=m['id'];geo_path=A/'geo/boss_forms'/f'{id}.geo.json';g=json.loads(geo_path.read_text())['minecraft:geometry'][0];a=json.loads((A/'animations/boss_forms'/f'{id}.animation.json').read_text())['animations'];tex=Image.open(A/'textures/entity/boss_forms'/f'{id}.png');desc=g['description'];assert tex.size==(desc['texture_width'],desc['texture_height']);colors=len(tex.getcolors(tex.width*tex.height));assert colors<=12
 seen=set();faces=0
 for b in g['bones']:
  assert b['name'] not in seen;assert not b.get('parent') or b['parent'] in seen;seen.add(b['name'])
  for c in b.get('cubes',[]):
   assert all(math.isfinite(v) for v in c['origin']+c['size']) and min(c['size'])>0
   sx,sy,sz=c['size']
   for f,uv in c['uv'].items():
    x,y=uv['uv'];w,h=uv['uv_size'];assert min(x,y)>=0 and min(w,h)>0 and x+w<=tex.width and y+h<=tex.height
    target=(sx,sz) if f in ['up','down'] else (sz,sy) if f in ['east','west'] else (sx,sy)
    assert all(abs(v-max(1,round(t*.5)))<1e-6 for v,t in zip([w,h],target));faces+=1
 prefix='' if i<3 else 'animation.'+id+'.';assert set(prefix+c for c in ['idle','walk','hurt','death'])<=set(a)
 pose={}
 for name,clip in a.items():
  assert clip['animation_length']>0
  for bn,ch in clip['bones'].items():
   assert bn in seen,(id,name,bn)
   for kind,track in ch.items():
    assert kind in ['rotation','position','scale']
    if isinstance(track,list):track={'0':track}
    assert min(map(float,track))>=0 and max(map(float,track))<=clip['animation_length']+.00001
    assert all(len(v)==3 and all(math.isfinite(float(n)) for n in v) for v in track.values())
    if clip.get('loop'):
     first=r.sample(track,0);last=r.sample(track,clip['animation_length']);delta=last-first
     if kind=='rotation':delta=(delta+180)%360-180
     assert np.max(np.abs(delta))<.001,(id,name,bn,kind,delta)
  lows=[]
  for t in np.linspace(0,clip['animation_length'],25):
   pts=np.concatenate([q[0] for q in r.geometry(id,clip=name,tick=float(t*20))]);assert np.isfinite(pts).all();lows.append(float(pts[:,1].min()))
  assert min(lows)>=-.12,(id,name,'ground penetration',min(lows))
  if name.endswith('death'):assert -.12<=lows[-1]<=.15,(id,'ungrounded death',lows[-1])
  pose[name]={'minYModelUnits':round(min(lows),4),'finalYModelUnits':round(lows[-1],4),'samples':25}
 assert json.loads((D/'blockbench'/f'{id}.bbmodel').read_text())['animations']
 for folder,ext in [('geo','.geo.json'),('animations','.animation.json'),('textures/entity','.png')]:
  p=A/folder/'boss_forms'/(id+ext);hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 report[id]={'bones':len(g['bones']),'cuboids':sum(len(b['cubes']) for b in g['bones']),'faces':faces,'atlas':list(tex.size),'paletteColors':colors,'pixelsPerBlock':8,'animations':len(a),'poseSamples':pose}
# Existing skill contracts and drop/quest code were not rewritten.
classes=['HeadlessGeneral','Mechanist','Jinwu','FoxMatron','HammerGuardian']
for cls in classes:
 p=R/f'src/main/java/com/dynasty/blueprint/elite/{cls}.java';source=p.read_text();old=subprocess.check_output(['git','show','main:'+str(p.relative_to(R))]).decode()
 import re
 pattern=r'new SkillDefinition\([^;]+';assert re.findall(pattern,source)==re.findall(pattern,old)
result={'status':'PASS_OFFLINE_ONLY','javaBuild':'NOT_RUN_USER_EXAM_HOLD','nativeGame':'NOT_RUN_USER_EXAM_HOLD','checks':['finite transforms and acyclic rig','UV bounds, palette and consistent pixel density','animation bone references, bounds and loop seams','25 exported pose samples per clip; ground tolerance .12 model units','server skill definitions unchanged'],'models':report,'sha256':hashes}
(D/'offline-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: eight rigs, UV, loop seams, skill definitions and sampled floor contacts. Java/native NOT RUN.')
