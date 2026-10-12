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
PAL={
 'ink':(24,37,48),'navy':(38,57,72),'cloth':(51,77,91),'cloth_hi':(74,100,111),
 'iron_dark':(57,77,87),'iron':(94,119,130),'iron_hi':(151,175,181),'edge':(212,226,222),
 'gold_dark':(119,87,44),'gold':(184,142,65),'gold_hi':(230,200,125),
 'skin_dark':(137,96,73),'skin':(184,143,112),'skin_hi':(211,177,140),
 'jade_dark':(37,84,88),'jade':(76,140,143),'jade_hi':(137,203,194),
}
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

def paint(role,face,w,h):
 p=PAL;im=Image.new('RGB',(w,h),p['iron']);d=ImageDraw.Draw(im)
 def rect(coords,col):
  x0,y0,x1,y1=map(int,coords)
  if x1>=x0 and y1>=y0:d.rectangle((x0,y0,x1,y1),fill=p[col])
 def line(coords,col,width=1):d.line(coords,fill=p[col],width=width)
 front=face=='north';back=face=='south';side=face in ['east','west']
 if role=='head':
  im=Image.new('RGB',(w,h),p['skin']);d=ImageDraw.Draw(im)
  if face in ['up','down']:
   rect((0,0,w-1,h-1),'navy');return im
  # Helmet upper band and side/back coif are painted onto the unchanged 8px head.
  rect((0,0,w-1,3),'navy');line((0,3,w-1,3),'gold')
  if front:
   rect((0,4,1,h-1),'iron_dark');rect((w-2,4,w-1,h-1),'iron_dark')
   for cx in [4,w-5]:
    line([(cx-2,5),(cx+1,6)],'ink');rect((cx-1,7,cx+1,8),'skin_dark')
    line((cx-1 if cx<w//2 else cx,7,cx if cx<w//2 else cx+1,7),'edge');d.point((cx,7),fill=p['ink'])
   rect((w//2-1,9,w//2,10),'skin_dark');d.point((w//2-1,9),fill=p['skin_hi'])
   line((w//2-3,h-5,w//2+2,h-5),'skin_dark')
   line((w//2-2,h-3,w//2+1,h-3),'ink')
   line((w//2-2,h-2,w//2+1,h-2),'skin_dark')
  elif back:
   rect((0,4,w-1,h-1),'navy');rect((3,5,w-4,h-3),'iron_dark');line((3,5,w-4,5),'iron')
  else:
   rect((0,4,w-1,h-1),'iron_dark');rect((w//3,5,w*2//3,9),'iron');rect((w//3,10,w*2//3,h-2),'navy')
 elif role=='torso':
  rect((0,0,w-1,h-1),'cloth' if side else 'navy')
  if front or back:
   # One broad cuirass field; small cloud/command mark, no frame on every Cuboid.
   d.polygon([(2,4),(w-3,4),(w-3,14),(w//2,17),(2,14)],fill=p['iron'])
   d.polygon([(2,5),(w//2-1,5),(w//2-1,16),(2,14)],fill=p['iron_dark'])
   line((3,4,w-4,4),'iron_hi');line([(3,14),(w//2,17),(w-4,14)],'cloth')
   if front:
    line([(4,0),(w//2,4),(w-5,0)],'gold',2)
    d.polygon([(w//2+2,6),(w//2-2,10),(w//2,10),(w//2-2,14),(w//2+3,9),(w//2+1,9)],fill=p['gold_hi'])
   else:
    line([(w//2-3,7),(w//2,5),(w//2+3,7)],'iron_hi')
    line([(w//2-2,10),(w//2+2,10),(w//2+2,12),(w//2-2,12)],'gold_dark')
  elif side:
   rect((0,4,1,16),'ink');rect((w-2,4,w-1,16),'cloth_hi')
  if face not in ['up','down']:
   rect((0,h-6,w-1,h-4),'gold_dark');line((0,h-6,w-1,h-6),'gold')
   if front:rect((w//2-1,h-6,w//2+1,h-4),'gold_hi')
   rect((0,h-3,w-1,h-1),'navy')
 elif role=='arm':
  rect((0,0,w-1,h-1),'cloth');rect((0,0,w-1,6),'iron_dark')
  if front or back:
   rect((1,1,w-2,5),'iron');line((1,1,w-2,1),'iron_hi')
   rect((1,11,w-2,17),'iron_dark');line((1,11,w-2,11),'iron')
  if face not in ['up','down']:
   line((0,7,w-1,7),'gold_dark');line((0,8,w-1,8),'gold')
   line((0,18,w-1,18),'gold_dark');rect((0,20,w-1,h-1),'skin_dark')
   if front:rect((1,20,w-2,h-2),'skin');line((1,h-2,w-2,h-2),'skin_hi')
 elif role=='leg':
  rect((0,0,w-1,h-1),'navy')
  if front or back:
   rect((1,2,w-2,10),'cloth');rect((1,13,w-2,h-4),'iron_dark')
   line((1,13,w-2,13),'iron');line((2,15,2,h-5),'iron')
  elif side:rect((w//2,2,w-2,11),'cloth')
  if face not in ['up','down']:
   line((0,11,w-1,11),'gold_dark');rect((0,h-3,w-1,h-1),'ink')
   line((1,h-4,w-2,h-4),'iron')
 elif role=='thigh':
  rect((0,0,w-1,h-1),'iron_dark');rect((1,0,w-2,h-2),'iron');line((1,0,w-2,0),'gold')
 elif role in ['crown','socket','crossbar']:
  rect((0,0,w-1,h-1),'gold_dark');rect((0,0,w-1,max(0,h//2)),'gold')
  if front or face=='up':line((0,0,w-1,0),'gold_hi')
  if role=='socket' and front and w>=4:rect((w//2-1,h//2-1,w//2,h//2),'jade')
 elif role=='crest':
  rect((0,0,w-1,h-1),'navy');rect((0,0,w-1,max(0,h//3)),'iron');line((0,0,w-1,0),'gold')
 elif role=='shaft':
  rect((0,0,w-1,h-1),'navy');line((0,0,0,h-1),'iron_dark')
  for y in [4,h-9]:line((0,y,w-1,y),'gold_dark',2)
 elif role=='grip':
  rect((0,0,w-1,h-1),'ink')
  for y in range(1,h,3):line((0,y,w-1,y),'cloth')
 else:
  # Connected blade field: no bright frame on each tile of the crescent.
  rect((0,0,w-1,h-1),'iron_dark')
  if front or back:
   rect((0,0,w-1,h-1),'iron')
   if role=='blade_edge':
    x=0 if front else w-1;line((x,0,x,h-1),'edge');line((1 if front else w-2,0,1 if front else w-2,h-1),'iron_hi')
   elif role=='blade_body':
    line((w//2,2,w//2,h-3),'jade_dark');line([(w//2,6),(w//2+1,6),(w//2+1,9)],'gold_dark')
   elif role=='blade_tip_end':rect((0,0,w-1,1),'edge')
   elif role=='blade_hook_end':rect((0,h-2,w-1,h-1),'edge')
   elif role=='rear_tine':line((0,0,0,h-1),'iron_hi')
  elif face=='up':rect((0,0,w-1,h-1),'iron_hi')
 return im

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
  x,y,w,h=i['rect'];tex.paste(paint(i['role'],i['face'],w,h),(x,y))
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
 D.mkdir(parents=True,exist_ok=True);owner=D/'export-owner.json'
 expected=json.loads((owner if owner.exists() else D/'before-hashes.json').read_text())
 assert hashes()==expected,'Concurrent/manual edit; export refused before touching production'
 g=build();tex,islands=atlas(g);an=animation(g)
 for b in g.bones:
  b['pivot']=[round(x*SCALE,6) for x in b['pivot']]
  for c in b['cubes']:
   for k in ['origin','size','pivot']:
    if k in c:c[k]=[round(x*SCALE,6) for x in c[k]]
   c.pop('_role',None)
 for a in an['animations'].values():
  for channels in a['bones'].values():
   if 'position' in channels:channels['position']={t:[round(x*SCALE,6) for x in v] for t,v in channels['position'].items()}
 desc={'identifier':'geometry.'+ID,'texture_width':tex.width,'texture_height':tex.height,'visible_bounds_width':9,'visible_bounds_height':6,'visible_bounds_offset':[0,2,0]}
 geo={'format_version':'1.12.0','minecraft:geometry':[{'description':desc,'bones':g.bones}]}
 TARGETS[0].write_text(json.dumps(geo,indent=2)+'\n');TARGETS[1].write_text(json.dumps(an,indent=2)+'\n');tex.save(TARGETS[2])
 dst=D/ID;dst.mkdir(exist_ok=True);tex.save(dst/'texture.png');tex.resize((tex.width*4,tex.height*4),Image.Resampling.NEAREST).save(dst/'texture-4x.png')
 (dst/'islands.json').write_text(json.dumps(islands,indent=2)+'\n')
 owner.write_text(json.dumps(hashes(),indent=2)+'\n')
 print('Exported exact six-block Steve proportions x1.35; four small decorations; original large halberd;',tex.size)
if __name__=='__main__':export()
