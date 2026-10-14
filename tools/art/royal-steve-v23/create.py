"""Authoritative royal pair, following the user's accepted V22 human direction.
Six canonical Steve blocks x1.35, small identity relief, large original weapons.
This latest explicit direction supersedes historic anti-Steve and 16px rules.
No external image/model is read. Exports refuse concurrent/manual asset changes.
"""
from pathlib import Path
import importlib.util,json,copy,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/royal-steve-v23'
IDS=['dragon_king','dragon_emperor'];S=1.35
spec=importlib.util.spec_from_file_location('steve',R/'tools/art/tianjiang-steve-v15/create.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
PAL={k:tuple(bytes.fromhex(v)) for k,v in {'ink':'172e38','deep':'244957','cloth':'326a76','fold':'275363','light':'68999d','metal':'799e9e','metalhi':'b9d2cd','white':'e0e6d4','gold':'b09866','goldhi':'d7c99c','golddark':'6f664c','jade':'66bbb0','jadedark':'376a6c','skin':'afc6bb','skinshade':'7f9f9b','eye':'d7f3dc','leather':'34434a'}.items()}
EM={k:tuple(bytes.fromhex(v)) for k,v in {'ink':'26232c','deep':'3b3038','cloth':'713d45','fold':'4b2e39','light':'93545a','metal':'8b714d','metalhi':'bea06a','white':'e7d4aa','gold':'b18a4f','goldhi':'d6bc7d','golddark':'705335','jade':'7bbaa4','jadedark':'356c62','skin':'b9a58c','skinshade':'84766b','eye':'f1dc9f','leather':'393034'}.items()}
CURRENT=IDS[0]
def build(id):
 g=base.mod.Rig(id);g.bone('body','root',[0,12,0]);g.bone('chest','body',[0,12,0]);g.bone('head','chest',[0,24,0])
 def box(n,c,s,role,rot=None):q=g.box(n,c,s,rot);q['_role']=role;return q
 box('chest',[0,18,0],[8,12,4],'torso');box('head',[0,28,0],[8,8,8],'head')
 for side,sign in [('right',-1),('left',1)]:
  n=g.bone(side+'_arm','chest',[sign*6,22,0]);box(n,[sign*6,18,0],[4,12,4],'arm');g.bone(side+'_grip',n,[sign*6,13,-2.1])
  n=g.bone(side+'_leg','body',[sign*2.4,12,0]);box(n,[sign*2.4,6,0],[4,12,4],'leg')
  box(n,[sign*2.4,9.6,-2.25],[4.1,2.8,.5],'thigh')
 g.bone('crown','head',[0,32,0]);box('crown',[0,32.3,0],[8.4,.6,8.4],'crown')
 for sign in [-1,1]:box('head',[sign*2.1,29.6,-4.2],[3.7,.55,.6],'brow',[0,0,-sign*10])
 if id==IDS[0]:
  # Small swept crown horns and a shallow forked beard preserve a human head.
  for sign in [-1,1]:
   box('crown',[sign*3.8,33.6,1.1],[1.1,3,1.5],'horn',[12,0,-sign*18]);box('crown',[sign*4.3,35.0,1.65],[.8,1.3,1.1],'horn')
  g.bone('beard','head',[0,25,-4.15]);box('beard',[0,24.8,-4.4],[3.0,2.0,.6],'beard');box('beard',[-.65,23.4,-4.4],[.9,1.5,.6],'beard');box('beard',[.65,23.6,-4.4],[.9,1.1,.6],'beard')
  box('head',[0,31,-4.18],[1.4,1.5,.5],'pearl')
 else:
  box('crown',[0,33.1,0],[8.8,.8,7.0],'crown');box('crown',[0,34,1.3],[5.5,1,2.4],'crown')
  for sign in [-1,1]:
   box('head',[sign*3.35,27.3,-4.2],[1.0,3.5,.55],'mask_edge',[0,0,sign*6])
   box('crown',[sign*3.3,30.8,-3.9],[.45,3,.45],'pendant');box('crown',[sign*3.3,29.3,-3.9],[.75,.7,.7],'jade')
  g.bone('seal','left_grip',[6,13,-2.1]);box('seal',[6,12.4,-3],[2.8,2,2.8],'jade');box('seal',[6,13.7,-3],[1.4,.8,1.5],'crown')
 # Only two thin back cloth panels; no cabinet, rigid wheel or large shoulder mass.
 g.bone('mantle','chest',[0,23,2.3]);box('mantle',[-2,18,2.35],[3.8,10,.45],'mantle');box('mantle',[2,18,2.35],[3.8,10,.45],'mantle')
 g.bone('weapon','right_grip',[-6,13,-2.1])
 def wb(c,s,role,rot=None):box('weapon',c,s,role,rot)
 if id==IDS[0]:
  wb([-6,19,-2.1],[1.25,34,1.25],'shaft');wb([-6,13,-2.1],[1.7,5,1.7],'grip')
  wb([-6,34.2,-2.1],[3,3.2,2],'socket');wb([-6,38.0,-2.1],[2.2,6,1.3],'blade');wb([-6,43,-2.1],[1.3,4,1.3],'edge')
  wb([-6,34.2,-2.1],[13,1.5,1.5],'crossbar')
  for sign in [-1,1]:
   wb([-6+sign*6.3,37,-2.1],[2.2,6.5,1.4],'blade',[0,0,-sign*12]);wb([-6+sign*7.0,41.2,-2.1],[1.2,3,1.2],'edge')
  wb([-6,34.8,-3.2],[1.4,1.4,.55],'pearl')
 else:
  wb([-6,14,-2.1],[1.4,10,1.4],'grip');wb([-6,19.2,-2.1],[9,1.6,2.2],'crossbar')
  wb([-6,30,-2.1],[5.0,20,1.3],'sword');wb([-6,41,-2.1],[3.2,2,1.3],'edge');wb([-6,43,-2.1],[1.4,2,1.2],'edge')
  wb([-6,8.5,-2.1],[2.1,1.4,2.1],'jade');wb([-6,21,-3],[1.8,2,.5],'pearl')
 for b in g.bones:
  for c in b['cubes']:c.pop('_segment',None)
 return g

def paint(role,face,w,h,ctx=None):
 king=CURRENT==IDS[0];P=PAL if king else EM
 im=Image.new('RGB',(w,h),P['deep']);dr=ImageDraw.Draw(im)
 # Hand-arranged clusters in normalized face coordinates, quantized to actual UV pixels.
 def pt(x,y):return (round(x*(w-1)/15),round(y*(h-1)/23))
 def rect(x0,y0,x1,y1,c):dr.rectangle((*pt(x0,y0),*pt(x1,y1)),fill=P[c])
 def line(points,c,width=1):dr.line([pt(*p) for p in points],fill=P[c],width=width)
 def poly(points,c):dr.polygon([pt(*p) for p in points],fill=P[c])
 def fill(c):dr.rectangle((0,0,w-1,h-1),fill=P[c])
 front=face=='north';back=face=='south';side=face in ('east','west');cap=face in ('up','down')
 if role=='head':
  fill('deep')
  if front:
   rect(2,2,13,6,'metal');poly([(3,7),(12,7),(13,16),(10,22),(5,22),(2,16)],'skin' if king else 'metal')
   poly([(2,8),(5,8),(7,10),(6,12),(3,11)],'ink');poly([(13,8),(10,8),(8,10),(9,12),(12,11)],'ink')
   line([(4,10),(5,10)],'eye');line([(10,10),(11,10)],'eye')
   if king:
    line([(7,12),(7,16),(9,16)],'skinshade');line([(5,18),(10,18)],'deep');line([(3,15),(4,19),(6,21)],'white');line([(12,15),(11,19),(9,21)],'white')
    line([(3,6),(5,6)],'metalhi');line([(10,6),(12,6)],'metalhi')
   else:
    poly([(7,12),(8,12),(9,18),(7,21),(6,18)],'golddark');line([(7,12),(7,17)],'goldhi')
    line([(3,13),(4,17),(6,20)],'gold');line([(12,13),(11,17),(9,20)],'gold');line([(6,22),(9,22)],'ink')
  elif back:rect(2,2,13,17,'cloth');line([(4,3),(4,16)],'fold');line([(10,4),(10,18)],'light')
  elif side:
   rect(1,2,11,9,'cloth');poly([(2,10),(11,8),(13,18),(10,22),(3,20)],'metal' if not king else 'skinshade');line([(3,12),(5,17),(10,19)],'light')
  else:rect(3,3,12,19,'cloth')
 elif role in ('torso','arm','leg','mantle'):
  fill('fold');rect(1,1,14,22,'cloth')
  if cap:fill('deep' if face=='down' else 'metal');return im
  if role=='torso':
   if front:
    line([(1,0),(7,4),(14,0)],'gold',2);line([(2,3),(5,6),(5,16)],'light')
    if king:
     # Sea-jade breast clasp above layered, downward-growing scales.
     poly([(7,5),(11,8),(8,12),(4,9)],'jadedark');poly([(7,6),(9,8),(7,10),(5,8)],'jade');line([(7,6),(8,7)],'white')
     for y in [13,16]:
      for x in [2,7,12]:line([(x-1,y),(x,y+1),(x+1,y)],'metal')
     line([(1,19),(6,18),(10,19),(14,18)],'gold')
    else:
     poly([(2,5),(13,5),(12,15),(8,18),(3,15)],'golddark');poly([(3,6),(11,6),(11,14),(8,16),(4,14)],'metal')
     # One continuous coiling imperial device; not a new faction logo.
     poly([(7,7),(10,7),(10,9),(8,10),(6,9)],'gold');line([(7,7),(6,6)],'goldhi');line([(9,7),(10,6)],'goldhi');line([(8,10),(5,11),(5,14),(9,14),(10,12)],'gold');line([(7,12),(8,12)],'golddark');line([(9,8),(10,8)],'ink')
    rect(0,20,15,21,'leather');rect(6,19,9,22,'gold');rect(7,20,8,21,'jade');rect(0,22,5,23,'deep')
   elif back:line([(3,2),(4,10),(4,19)],'light');line([(10,3),(9,12),(11,21)],'deep');line([(3,20),(12,20)],'golddark')
   else:line([(3,1),(4,13),(3,20)],'light');line([(11,4),(10,16)],'deep')
  elif role=='arm':
   rect(0,0,15,5,'metal' if not king else 'deep');line([(2,1),(6,0),(12,2)],'metalhi');line([(1,5),(7,6),(14,5)],'gold')
   line([(3,7),(4,11),(3,16)],'light');line([(11,7),(10,14)],'deep')
   if king:
    line([(2,15),(5,13),(8,15),(12,13)],'metal');line([(1,16),(5,14),(8,16),(13,14)],'jadedark')
   else:poly([(2,12),(12,12),(13,16),(9,18),(3,17)],'golddark');line([(3,13),(10,13),(11,15)],'gold')
   rect(0,18,15,19,'gold');rect(0,20,15,23,'skinshade' if king else 'leather');rect(2,20,12,22,'skin' if king else 'metal')
  elif role=='leg':
   line([(3,1),(3,9),(5,13)],'light');line([(11,1),(9,12),(10,17)],'deep')
   if king:line([(1,12),(4,10),(8,12),(13,10)],'metal');line([(1,15),(4,13),(8,15),(13,13)],'jadedark')
   else:poly([(2,11),(12,11),(13,16),(10,19),(3,19)],'golddark');line([(3,12),(10,12),(11,15)],'metal');line([(5,14),(5,17)],'gold')
   rect(0,20,15,23,'leather');line([(2,20),(13,20)],'golddark')
  else:
   line([(2,1),(4,9),(3,22)],'light');line([(10,0),(9,12),(12,21)],'deep')
   if back:line([(2,18),(5,16),(8,18),(12,16)],'gold');line([(3,20),(7,19),(11,20)],'golddark')
 elif role in ('blade','edge','sword'):
  fill('metal');rect(2,1,6,22,'metalhi');rect(9,1,14,22,'deep');line([(0,0),(0,23)],'white')
  if role=='sword' and (front or back):
   rect(6,1,9,22,'golddark');line([(7,2),(7,8),(9,10),(7,12),(7,20)],'gold');line([(5,15),(3,17)],'metalhi')
  elif role=='blade' and (front or back):line([(8,2),(8,8),(10,9),(8,11),(8,20)],'jade')
  if cap:fill('metalhi' if face=='up' else 'deep')
 elif role in ('jade','pearl'):
  fill('jadedark');poly([(2,2),(11,1),(14,10),(11,20),(4,21),(1,10)],'jade');line([(3,4),(5,2),(9,2)],'white');line([(10,12),(9,18),(5,19)],'metal')
 elif role=='beard':
  fill('skinshade');rect(2,0,12,20,'white');line([(4,2),(4,18)],'metalhi');line([(10,4),(10,21)],'skinshade')
 elif role=='horn':
  fill('metal');rect(2,0,8,23,'white');line([(10,0),(10,22)],'skinshade')
 elif role=='grip':
  fill('leather')
  for y in range(2,23,5):line([(0,y+1),(15,y)],'golddark')
 elif role=='shaft':
  fill('deep');rect(1,0,5,23,'metal');line([(1,3),(14,3)],'gold');line([(1,19),(14,19)],'gold')
 else:
  fill('golddark' if role in ('crown','crossbar','brow','pendant') else 'deep')
  if face!='down':rect(1,1,14,14,'gold' if role not in ('thigh','mask_edge') else 'metal');line([(1,1),(8,1)],'goldhi' if role!='thigh' else 'metalhi')
  if role=='socket' and front:rect(5,5,10,17,'jade')
 return im

def motion(g,id):
 prior=json.loads((D/'before'/f'{id}.animation.json').read_text())['animations'];out={};king=id==IDS[0]
 for clip,old in prior.items():
  L=old['animation_length'];ch={};out[clip]={'animation_length':L,'loop':old.get('loop',False),'bones':ch}
  def r(n,v):ch.setdefault(n,{})['rotation']=v
  def keys(n,ts,vs):r(n,{format(t,'.8g'):v for t,v in zip(ts,vs)})
  idle=[-7,0,4] if king else [-12,0,3];wr=[0,0,-18] if king else [0,0,-12]
  r('right_arm',idle);r('left_arm',[-5,0,-4] if king else [-24,0,-6]);r('weapon',wr);r('head',[2,3 if king else -3,0]);r('mantle',[4,0,0])
  if clip=='idle':
   keys('head',[0,L/2,L],[[2,3 if king else -3,0],[3,1,0],[2,3 if king else -3,0]])
   keys('mantle',[0,L/2,L],[[4,0,-1],[6,0,1],[4,0,-1]])
  elif clip=='walk':
   ts=[0,L/4,L/2,L*3/4,L]
   for side,sign in [('right',-1),('left',1)]:keys(side+'_leg',ts,[[sign*v,0,0] for v in [16,0,-16,0,16]])
   keys('right_arm',ts,[[v,0,4] for v in [-9,-7,-5,-7,-9]])
   keys('mantle',ts,[[v,0,0] for v in [4,8,4,8,4]])
  elif clip=='attack':
   ts=[0,.09,.15,L]
   keys('right_arm',ts,[idle,[24,-8,10],[-86,4,6],idle]);keys('chest',ts,[[0,0,0],[0,-6,0],[2,7,0],[0,0,0]])
   keys('weapon',ts,[wr,[8,0,-26] if king else [-12,0,-18],[180,0,-6] if king else [165,0,8],wr])
   keys('left_arm',ts,[[-5,0,-4] if king else [-24,0,-6],[-22,0,-5],[-32,0,-4],[-5,0,-4] if king else [-24,0,-6]])
  elif clip=='cast':keys('left_arm',[0,.35,.85,L],[[-5,0,-4],[-78,0,-7],[-74,0,-7],[-5,0,-4]])
  elif clip=='hurt':keys('chest',[0,L/2,L],[[0,0,0],[-5,0,3],[0,0,0]])
  elif clip=='death':
   keys('body',[0,L*.3,L*.7,L],[[0,0,0],[0,0,-10],[0,0,-74],[0,0,-90]])
   keys('right_arm',[0,L*.5,L],[idle,[5,0,-12],[0,0,-30]])
   keys('weapon',[0,L*.5,L],[wr,[0,75,20],[0,90,20]])
  support=[b for b in g.bones if b['name'] not in ('weapon','seal')]
  ch['root']={'position':{format(t,'.8g'):[0,round(.02-min(v[1] for v in base.vertices(support,ch,float(t))),6),0] for t in np.linspace(0,L,121)}}
 return {'format_version':'1.8.0','animations':out}

def targets():return [A/f/(id+e) for id in IDS for f,e in [('geo/boss_cuboid','.geo.json'),('animations/boss_cuboid','.animation.json'),('textures/entity/boss_cuboid','.png')]]
def hashes():return {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in targets()}
def export():
 global CURRENT
 owner=D/'export-owner.json';expected=json.loads(owner.read_text()) if owner.exists() else {str(p.relative_to(R)):hashlib.sha256((D/'before'/p.name).read_bytes()).hexdigest() for p in targets()}
 assert hashes()==expected,'Concurrent/manual edits: refused'
 records={}
 for id in IDS:
  CURRENT=id;g=build(id);base.paint=paint;tex,islands=base.atlas(g);an=motion(g,id)
  for b in g.bones:
   b['pivot']=[round(v*S,6) for v in b['pivot']]
   for c in b['cubes']:
    for k in ('origin','size','pivot'):
     if k in c:c[k]=[round(v*S,6) for v in c[k]]
    c.pop('_role',None)
  for a in an['animations'].values():
   for ch in a['bones'].values():
    if 'position' in ch:ch['position']={t:[round(v*S,6) for v in vs] for t,vs in ch['position'].items()}
  desc={'identifier':'geometry.'+id,'texture_width':tex.width,'texture_height':tex.height,'visible_bounds_width':9,'visible_bounds_height':6,'visible_bounds_offset':[0,2,0]}
  (A/'geo/boss_cuboid'/f'{id}.geo.json').write_text(json.dumps({'format_version':'1.12.0','minecraft:geometry':[{'description':desc,'bones':g.bones}]},indent=2)+'\n')
  (A/'animations/boss_cuboid'/f'{id}.animation.json').write_text(json.dumps(an,indent=2)+'\n');tex.save(A/'textures/entity/boss_cuboid'/f'{id}.png')
  out=D/id;out.mkdir(exist_ok=True);tex.save(out/'texture.png');tex.resize((tex.width*4,tex.height*4),Image.Resampling.NEAREST).save(out/'texture-4x.png');(out/'islands.json').write_text(json.dumps(islands,indent=2)+'\n')
  records[id]={'bones':len(g.bones),'cubes':sum(len(b['cubes']) for b in g.bones),'atlas':tex.size,'steveScale':S,'bodyHeight':2*S,'clips':{k:v['animation_length'] for k,v in an['animations'].items()}}
 owner.write_text(json.dumps(hashes(),indent=2)+'\n');(D/'asset-report.json').write_text(json.dumps(records,indent=2)+'\n');print(records)
if __name__=='__main__':export()
