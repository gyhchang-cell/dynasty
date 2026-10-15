"""Original shallow helmet relief over the user's locked six-block Steve body.

Only head/crest surfaces and six attached shallow helmet cubes change. The
immutable V16 snapshot preserves every other UV, pixel, vertex and animation.
No external artwork is read. Older export entrypoints delegate here.
"""
from pathlib import Path
import json,hashlib,copy,math,sys,importlib.util
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/tianjiang-helmet-v17'
A=R/'src/main/resources/assets/dynasty';ID='nine_heaven_general';S=1.35
TARGETS=[A/f/(ID+e) for f,e in [('geo/boss_cuboid','.geo.json'),('animations/boss_cuboid','.animation.json'),('textures/entity/boss_cuboid','.png')]]
spec=importlib.util.spec_from_file_location('v16paint',R/'tools/art/tianjiang-texture-v16/paint.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);P=old.PAL
FACES=['north','south','east','west','up','down']
def hashes():return {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in TARGETS}
def tile(role,face,w,h):
 im=Image.new('RGB',(w,h),P['iron_dark']);d=ImageDraw.Draw(im)
 def r(box,c):d.rectangle(box,fill=P[c])
 def l(points,c):d.line(points,fill=P[c])
 def p(points,c):d.polygon(points,fill=P[c])
 if role=='head':
  if face=='north':
   # Recessed closed war mask: narrow directed eyes, no caricature nose/lips.
   r((1,0,14,4),'iron_mid');r((4,0,11,2),'iron')
   p([(3,5),(12,5),(13,9),(11,14),(4,14),(2,9)],'navy')
   p([(4,6),(11,6),(11,11),(9,14),(6,14),(4,11)],'iron_dark')
   p([(4,9),(6,10),(7,12),(7,14),(5,12),(4,11)],'iron')
   p([(11,9),(9,10),(8,12),(8,14),(10,12),(11,11)],'iron_mid')
   p([(2,5),(5,5),(7,7),(7,8),(4,8),(2,7)],'ink')
   p([(13,5),(10,5),(8,7),(8,8),(11,8),(13,7)],'ink')
   l([(4,7),(5,7)],'edge');l([(10,7),(11,7)],'edge')
   # Quiet cheek planes surround, rather than outline, the attention centre.
   p([(0,4),(2,5),(2,9),(4,12),(4,15),(0,15)],'iron_mid')
   p([(15,4),(13,5),(13,9),(11,12),(11,15),(15,15)],'iron_mid')
   l([(1,8),(2,11),(3,12)],'iron');l([(14,8),(13,11),(12,12)],'iron')
   r((6,15,9,15),'navy')
  elif face=='south':
   r((2,0,13,10),'iron_mid');r((4,1,11,7),'iron')
   l([(7,2),(7,10)],'iron_dark');r((1,12,14,15),'cloth_fold')
   l([(2,11),(6,11)],'gold_dark');l([(9,11),(13,11)],'gold_dark')
  elif face in ['east','west']:
   p([(1,0),(14,0),(14,5),(11,10),(3,10),(1,6)],'iron_mid')
   p([(3,1),(12,1),(11,5),(8,7),(3,7)],'iron')
   l([(3,1),(7,1)],'iron_hi');l([(3,11),(10,11)],'gold_dark')
   r((2,13,13,15),'cloth_fold')
  elif face=='up':
   r((2,2,w-3,h-3),'iron_mid');r((6,1,9,h-2),'iron')
 else:
  # Narrow physical trim receives a few longitudinal material changes;
  # no all-edge white frame and no rivet/noise template.
  r((0,0,w-1,h-1),'iron_mid' if face!='down' else 'iron_dark')
  if role in ['brow','forehead']:
   r((0,0,w-1,h-1),'gold_dark' if face in ['south','down'] else 'gold_mid')
   if face=='north':
    r((0,0,w-1,max(0,h//3)),'gold');l([(0,0),(max(0,w//2-1),0)],'gold_hi')
    if role=='forehead' and h>=4:
     r((w//2,1,w//2,2),'jade');r((w//2,1,w//2,1),'jade_hi')
  elif role=='cheek':
   if face=='north':
    r((0,0,max(0,w//2-1),h-2),'iron');l([(0,0),(max(0,w//2-1),0)],'iron_hi')
    l([(0,h-2),(w-1,h-2)],'gold_dark')
  elif role=='bridge':
   r((0,0,w-1,h-1),'gold_mid');l([(0,0),(0,h-2)],'gold')
  elif role=='crown':
   if face in ['north','south']:r((0,0,w-1,h-1),'iron_dark');l([(2,0),(w-3,0)],'gold_mid')
   elif face=='up':r((3,2,w-4,h-3),'iron_mid')
  elif role=='crest':
   r((0,0,w-1,h-1),'iron_dark');r((0,0,w-1,0),'gold_mid')
   if face in ['east','west']:r((1,1,w-2,h-2),'iron_mid')
 return im

def assemble():
 geo=json.loads((D/'before'/TARGETS[0].name).read_text());bones=geo['minecraft:geometry'][0]['bones'];by={b['name']:b for b in bones}
 tex=Image.open(D/'before'/TARGETS[2].name).convert('RGB');used=np.zeros((128,128),bool);islands=[];allowed=np.zeros((128,128),bool)
 for b in bones:
  for j,c in enumerate(b.get('cubes',[])):
   for f,u in c['uv'].items():
    x,y=u['uv'];w,h=u['uv_size'];used[y:y+h,x:x+w]=True
    role='head' if b['name']=='head' else ('crown' if j==0 else 'crest') if b['name']=='crest' else 'locked'
    islands.append(dict(bone=b['name'],cube=j,face=f,role=role,rect=[x,y,w,h],w=w,h=h))
    if role!='locked':tex.paste(tile(role,f,w,h),(x,y));allowed[y:y+h,x:x+w]=True
 def alloc(w,h):
  for y in range(1,128-h):
   for x in range(1,128-w):
    if not used[y-1:y+h+1,x-1:x+w+1].any():
     used[y:y+h,x:x+w]=True;return x,y
  raise ValueError('No padded UV space; never repack locked body UV')
 def cube(center,size,role,rot=None):
  c={'origin':[round((v-s/2)*S,6) for v,s in zip(center,size)],'size':[round(v*S,6) for v in size],'uv':{}}
  if rot:c.update(pivot=[round(v*S,6) for v in center],rotation=rot)
  dims=[max(1,round(v*2)) for v in size];x,y,z=dims;j=len(by['head']['cubes'])
  for f,(w,h) in zip(FACES,[(x,y),(x,y),(z,y),(z,y),(x,z),(x,z)]):
   u,v=alloc(w,h);c['uv'][f]={'uv':[u,v],'uv_size':[w,h]};tex.paste(tile(role,f,w,h),(u,v));allowed[v:v+h,u:u+w]=True
   islands.append(dict(bone='head',cube=j,face=f,role=role,rect=[u,v,w,h],w=w,h=h))
  by['head']['cubes'].append(c)
 # Six shallow connected pieces. Outer rise <= .8 model unit (~0.0675 block).
 # Brow slopes down towards the centre; cheek edges slope inward at the jaw.
 for s in [-1,1]:
  cube([s*2.05,29.55,-4.25],[3.8,.65,.7],'brow',[0,0,-s*9])
  cube([s*3.45,26.6,-4.18],[1.25,3.5,.65],'cheek',[0,0,s*8])
 cube([0,30.8,-4.18],[1.3,2.3,.65],'forehead')
 cube([0,28.6,-4.17],[.65,1.1,.6],'bridge')
 # Reshape only the pre-existing small helmet crest into a low longitudinal ridge.
 crest=by['crest']['cubes'][1]
 crest['origin']=[-.75*S,32.4*S,-1.7*S];crest['size']=[1.5*S,1.8*S,4.5*S]
 # Never alter animation, skeleton, body/weapon vertices, or existing UVs.
 before=json.loads((D/'before'/TARGETS[0].name).read_text())['minecraft:geometry'][0]
 for b,oldb in zip(bones,before['bones']):
  if b['name']=='crest':
   assert b['cubes'][0]==oldb['cubes'][0]
   assert b['cubes'][1]['uv']==oldb['cubes'][1]['uv']
   assert {k:v for k,v in b.items() if k!='cubes'}=={k:v for k,v in oldb.items() if k!='cubes'}
  elif b['name']!='head':assert b==oldb
  else:assert {k:v for k,v in b.items() if k!='cubes'}=={k:v for k,v in oldb.items() if k!='cubes'};assert b['cubes'][0]==oldb['cubes'][0]
 assert not (np.any(np.array(tex)!=np.array(Image.open(D/'before'/TARGETS[2].name)),axis=2)&~allowed).any()
 return geo,tex,islands,allowed

def export():
 owner=D/'export-owner.json';assert hashes()==json.loads((owner if owner.exists() else D/'before-hashes.json').read_text()),'Concurrent/manual edits: export refused'
 geo,tex,islands,allowed=assemble()
 assert TARGETS[1].read_bytes()==(D/'before'/TARGETS[1].name).read_bytes()
 TARGETS[0].write_text(json.dumps(geo,indent=2)+'\n');tex.save(TARGETS[2])
 for name,im in [('before',Image.open(D/'before'/TARGETS[2].name)),('after',tex),('texture',tex)]:
  im.save(D/(name+'.png'));im.resize((512,512),Image.Resampling.NEAREST).save(D/(name+'-4x.png'))
 (D/'islands.json').write_text(json.dumps(islands,indent=2)+'\n');owner.write_text(json.dumps(hashes(),indent=2)+'\n')
 print('V17: six shallow helmet parts; original head dimensions, all body/weapon/animation/old UV locked; atlas 128 unchanged.')
if __name__=='__main__':export()
