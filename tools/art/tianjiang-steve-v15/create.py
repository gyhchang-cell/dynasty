"""Authoritative Nine-Heaven General export: six unchanged Steve proportions.

User's 2026-10-12 direction supersedes prior anti-Steve/body-enrichment templates.
Only original pixel painting is exported; no external artwork is read here.
"""
from pathlib import Path
import sys, json, math, hashlib, copy, importlib.util
import numpy as np
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[3]
A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/tianjiang-steve-v15'
ID='nine_heaven_general';SCALE=1.35
sys.path.insert(0,str(R/'tools/art/secondary-cuboid'))
from rig_bounds import vertices
spec=importlib.util.spec_from_file_location('minimal_rig',R/'tools/art/boss-structure-v13/create.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
FACES=['north','south','east','west','up','down']
# V16 is the authoritative pixel painter; legacy body/UV/animation exporter retained.
pspec=importlib.util.spec_from_file_location('tianjiang_materials',R/'tools/art/tianjiang-texture-v16/paint.py')
painter=importlib.util.module_from_spec(pspec);pspec.loader.exec_module(painter)
PAL=painter.PAL
TARGETS=[A/f'{f}/{ID}{e}' for f,e in [('geo/boss_cuboid','.geo.json'),('animations/boss_cuboid','.animation.json'),('textures/entity/boss_cuboid','.png')]]
def hashes():return {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in TARGETS}
def build():
 g=mod.Rig(ID);g.bone('body','root',[0,12,0])
 def box(n,c,s,role,rot=None):
  q=g.box(n,c,s,rot);q['_role']=role;return q
 # Exactly the classic six Cuboids. Never widen shoulders/chest/limbs or add feet.
 g.bone('chest','body',[0,12,0]);box('chest',[0,18,0],[8,12,4],'torso')
 g.bone('head','chest',[0,24,0]);box('head',[0,28,0],[8,8,8],'head')
 for side,sign in [('right',-1),('left',1)]:
  n=g.bone(side+'_arm','chest',[sign*6,22,0]);box(n,[sign*6,18,0],[4,12,4],'arm')
  g.bone(side+'_grip',n,[sign*6,13,-2.1])
  n=g.bone(side+'_leg','body',[sign*2.4,12,0]);box(n,[sign*2.4,6,0],[4,12,4],'leg')
  # A shallow, short thigh plate is the only addition to the leg silhouette.
  box(n,[sign*2.4,9.5,-2.3],[4.2,3,.6],'thigh')
 g.bone('crest','head',[0,32,0]);box('crest',[0,32.3,0],[8.4,.6,8.4],'crown')
 box('crest',[0,33.8,1],[1.5,3,2.5],'crest')
 # Original folded-moon command halberd, its shaft passes through the actual palm.
 # The unusual weapon supplies the large secondary silhouette, NOT a hulking body.
 g.bone('weapon','right_grip',[-6,13,-2.1])
 def wb(c,s,role,rot=None):box('weapon',c,s,role,rot)
 wb([-6,19,-2.1],[1.25,34,1.25],'shaft')
 wb([-6,13,-2.1],[1.7,5,1.7],'grip')
 wb([-6,35.5,-2.1],[2.8,4,2.4],'socket')
 # A stepped open crescent has a real central void; adjoining tiles never
 # overlap coplanar faces. Its large negative space survives distant views.
 wb([-11,39.5,-2.1],[4,10,1.2],'blade_body')
 wb([-14.5,39.5,-2.1],[3,8,1.2],'blade_edge')
 wb([-7.5,43,-2.1],[3,3,1.2],'blade_tip')
 wb([-4.5,45,-2.1],[3,3,1.2],'blade_tip')
 wb([-3.75,48,-2.1],[1.5,3,1.2],'blade_tip_end')
 wb([-7.5,36,-2.1],[3,3,1.2],'blade_hook')
 wb([-4.5,34,-2.1],[3,3,1.2],'blade_hook')
 wb([-3.75,31,-2.1],[1.5,3,1.2],'blade_hook_end')
 wb([-2.5,35,-2.1],[5,1.5,1.6],'crossbar')
 wb([-.2,37,-2.1],[1.5,5,1.2],'rear_tine',[0,0,18])
 for b in g.bones:
  for c in b['cubes']:c.pop('_segment',None)
 return g

def paint(role,face,w,h,context=None):
 return painter.paint(role,face,w,h,context)

def atlas(g):
 islands=[]
 for b in g.bones:
  for j,c in enumerate(b['cubes']):
   x,y,z=[max(1,round(v*2)) for v in c['size']]
   for f,(w,h) in zip(FACES,[(x,y),(x,y),(z,y),(z,y),(x,z),(x,z)]):
    islands.append({'bone':b['name'],'cube':j,'face':f,'w':w,'h':h,'role':c['_role']})
 # Compact non-rotating MaxRects placement keeps direction intact and avoids
 # wasting a 256 atlas just because narrow shaft faces are unusually tall.
 for size in [128,256]:
  free=[(0,0,size,size)];ok=True
  for i in sorted(islands,key=lambda a:(-max(a['h'],a['w']),-a['h']*a['w'])):
   iw,ih=i['w']+2,i['h']+2
   candidates=[f for f in free if f[2]>=iw and f[3]>=ih]
   if not candidates:ok=False;break
   x,y,fw,fh=min(candidates,key=lambda f:(min(f[2]-iw,f[3]-ih),max(f[2]-iw,f[3]-ih)))
   i['rect']=[x+1,y+1,i['w'],i['h']];new=[]
   for fx,fy,fww,fhh in free:
    if fx>=x+iw or fx+fww<=x or fy>=y+ih or fy+fhh<=y:new.append((fx,fy,fww,fhh));continue
    if fx<x:new.append((fx,fy,x-fx,fhh))
    if fx+fww>x+iw:new.append((x+iw,fy,fx+fww-x-iw,fhh))
    if fy<y:new.append((fx,fy,fww,y-fy))
    if fy+fhh>y+ih:new.append((fx,y+ih,fww,fy+fhh-y-ih))
   free=[]
   for j,f in enumerate(new):
    if not any(j!=k and f[0]>=o[0] and f[1]>=o[1] and f[0]+f[2]<=o[0]+o[2] and f[1]+f[3]<=o[1]+o[3] for k,o in enumerate(new)):free.append(f)
  if ok:break
 assert ok
 tex=Image.new('RGB',(size,size),PAL['ink'])
 for i in islands:
  x,y,w,h=i['rect'];tex.paste(paint(i['role'],i['face'],w,h,g.by[i['bone']]['cubes'][i['cube']]),(x,y))
  g.by[i['bone']]['cubes'][i['cube']]['uv'][i['face']]={'uv':[x,y],'uv_size':[w,h]}
 return tex,islands

def animation(g):
 old=json.loads((D/'before'/f'{ID}.animation.json').read_text())['animations'];out={}
 for clip,prior in old.items():
  L=prior['animation_length'];ch={};a={'animation_length':L,'loop':prior.get('loop',False),'bones':ch};out[clip]=a
  def r(n,v):ch.setdefault(n,{})['rotation']=v
  def keys(n,times,vs):r(n,{format(t,'.8g'):v for t,v in zip(times,vs)})
  r('right_arm',[-8,0,5]);r('left_arm',[0,0,-3]);r('head',[2,-2,0]);r('weapon',[0,0,-28])
  if clip=='idle':
   keys('head',[0,L/2,L],[[2,-2,0],[3,1,0],[2,-2,0]])
   keys('right_arm',[0,L/2,L],[[-8,0,5],[-9,0,5],[-8,0,5]])
  elif clip=='walk':
   ts=[0,L/4,L/2,L*3/4,L]
   for s,sign in [('right',-1),('left',1)]:
    keys(s+'_leg',ts,[[sign*v,0,0] for v in [17,0,-17,0,17]])
   keys('left_arm',ts,[[v,0,-3] for v in [-12,0,12,0,-12]])
   keys('right_arm',ts,[[v,0,5] for v in [-10,-7,-4,-7,-10]])
  elif clip=='attack':
   # Existing six-tick swing and middle contact. No new server timing/weapon rules.
   ts=[0,.09,.15,L]
   keys('right_arm',ts,[[-8,0,5],[28,-12,12],[-84,8,7],[-8,0,5]])
   keys('weapon',ts,[[0,0,-28],[8,0,-35],[180,0,-10],[0,0,-28]])
   keys('chest',ts,[[0,0,0],[0,-8,0],[3,8,0],[0,0,0]])
   keys('left_arm',ts,[[0,0,-3],[-15,0,-6],[-25,0,-6],[0,0,-3]])
  elif clip=='cast':
   keys('left_arm',[0,.35,.85,L],[[0,0,-3],[-80,0,-8],[-76,0,-8],[0,0,-3]])
   keys('head',[0,.35,.85,L],[[2,-2,0],[0,-6,0],[1,-6,0],[2,-2,0]])
  elif clip=='hurt':keys('chest',[0,L/2,L],[[0,0,0],[-6,0,4],[0,0,0]])
  elif clip=='death':
   keys('body',[0,L*.3,L*.7,L],[[0,0,0],[0,0,-12],[0,0,-75],[0,0,-90]])
   keys('right_arm',[0,L*.5,L],[[-8,0,5],[5,0,-12.5],[0,0,-30]])
   keys('weapon',[0,L*.5,L],[[0,0,-28],[0,75,20],[0,90,20]])
  # Ground from bearing body, never let a long weapon jack the whole body upward.
  support=[b for b in g.bones if b['name']!='weapon']
  # Dense compensation uses the full hierarchy; weapon removed, grips retained.
  ch['root']={'position':{format(t,'.8g'):[0,round(.02-min(v[1] for v in vertices(support,ch,float(t))),6),0] for t in np.linspace(0,L,121)}}
 return {'format_version':'1.8.0','animations':out}

def export():
 # V17 owns the accepted helmet; legacy commands must not restore the flat face.
 import runpy
 runpy.run_path(str(R/'tools/art/tianjiang-helmet-v17/export.py'),run_name='__main__')
if __name__=='__main__':export()
