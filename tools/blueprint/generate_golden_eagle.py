#!/usr/bin/env python3
"""Original raptor with actual two-joint talons and a drawn rib bow; no human torso.
Inspected actual AlexMobs BaldEagle and Twilight Raven constructors/flight wing and hock motion.
Only anatomy/joint principles are borrowed, never assets or numeric layouts.
"""
from pathlib import Path
import ast,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'src/main/resources/assets/dynasty';ID='liefeng_jindiao_yushi'
COLORS={'dark':'#38352E','gold':'#BA8436','straw':'#E9CB71','white':'#FFFFFF'};UV={'dark':[3,3],'gold':[9,3],'straw':[3,9],'white':[9,9]};bones=[]
helper=(ROOT/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(helper).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','geo','write'):exec(ast.get_source_segment(helper,n),globals())
def keys(rows):
 data=[(str(float(round(t,4))),[round(float(x),6) for x in v]) for t,v in rows]
 # Retain hold boundaries; erase only identical interior poses, never an actual bend.
 return {t:v for i,(t,v) in enumerate(data) if i==0 or i==len(data)-1 or v!=data[i-1][1] or v!=data[i+1][1]}

bone('root');body=bone('raptor_body','root',(0,18,2));cube(body,(-10,10,-9),(20,14,24),'gold');cube(body,(-8,9,-11),(16,9,18),'straw');cube(body,(-8,21,-6),(16,5,19),'dark')
neck=bone('raptor_neck','raptor_body',(0,23,-8));cube(neck,(-6,21.1,-15),(12,6.8,12),'straw')
head=bone('raptor_skull','raptor_neck',(0,27,-17));cube(head,(-7,23,-23),(14,8.2,12),'gold');cube(head,(-5,29,-24),(10,2,10),'straw')
beak=bone('hooked_beak','raptor_skull',(0,25,-23));cube(beak,(-3,24,-31),(6,5,9),'straw');cube(beak,(-2,20,-33),(4,7,4),'dark')
for sign in (-1,1):
 cube(head,(sign*7-1,26,-22),(2,3,6),'dark');cube(head,(sign*7-1.1,26.8,-21),(2.2,2,3),'white')
for side,sign in (('left',1),('right',-1)):
 upper=bone(side+'_wing','raptor_body',(sign*9,23,1));cube(upper,(9 if sign>0 else -27,21,-8.9),(18,5,15.9),'gold')
 cube(upper,(10 if sign>0 else -26,25.5,-7),(16,2,10),'straw')
 outer=bone(side+'_outer_wing',upper['name'],(sign*27,23,3));cube(outer,(25.9 if sign>0 else -45.1,21.1,-6),(19.2,3.8,15),'gold')
 for i in range(4):
  end=46-i*3;start=26-i
  cube(outer,(start if sign>0 else -end,20-i*.6,6+i*4),(end-start,3,7),'straw' if i%2==0 else 'gold')
  cube(outer,((start+3.2) if sign>0 else -end+.2,19.65-i*.61,11+i*4),(end-start-3.4,2,3),'dark')
 tail=bone(side+'_tail_fan','raptor_body',(sign*3,14,14))
 for i in range(2):cube(tail,(sign*(3+i*5)-3,10.1-i*.95,14+i*.2),(5.6,3.8,22-i*3),'gold' if i==0 else 'straw')
# Legs have real serial hips and hocks. The independent gripping pads are positioned by
# the same analytic endpoint, so neither talon detaches while the bowstring is drawn.
HIP={'grip':(6,12,2),'draw':(-6,12,2)};REST={'grip':(13,10,-12),'draw':(13,10,-6)};L=12
for name in HIP:
 x,y,z=HIP[name];upper=bone(name+'_thigh','raptor_body',HIP[name]);cube(upper,(x-2,y-L,z-2),(4,L,4),'gold')
 lower=bone(name+'_hock',upper['name'],(x,y-L,z));cube(lower,(x-1.5,y-L*2,z-1.5),(3,L,3),'straw')
 foot=bone(name+'_talon','raptor_body',REST[name]);x,y,z=REST[name]
 cube(foot,(x-3,y+2.3,z-3),(6,2,6),'dark')
 for i in range(3):
  cube(foot,(x-3+i*2,y-1.8,z-4),(2,4.2,2),'straw')
  cube(foot,(x-2.9+i*2,y-2.8,z-3.9),(1.8,2,6.8),'straw')
 cube(foot,(x-2,y-.7,z+2.8),(4,3.1,2),'gold')
bow=bone('rib_bow','grip_talon',REST['grip']);cube(bow,(11,8,-14),(4,4,4),'dark')
for side,sign in (('upper',1),('lower',-1)):
 limb=bone(side+'_bow_limb','rib_bow',(13,10,-12))
 cube(limb,(12,10 if sign>0 else -3,-14.2),(2,13,4.1),'straw')
 cube(limb,(12,23 if sign>0 else -10,-11),(2,7,4),'gold')
 cube(limb,(11.9,28 if sign>0 else -10.2,-8),(2.2,2.2,4),'straw')
 string=bone(side+'_string','rib_bow',(13,30 if sign>0 else -10,-6))
 cube(string,(12.6,10 if sign>0 else -10,-6.4),(.8,20,.8),'white')
arrow=bone('drawn_arrow','rib_bow',(13,10,-6));cube(arrow,(12.5,9.5,-26),(1,1,20),'straw');cube(arrow,(12,9,-29),(2,2,4),'white');cube(arrow,(11.5,9,-9),(3,2,4),'gold')
anims={}
def anim(name,length,loop=False):
 d={'animation_length':length,'bones':{}}
 if loop:d['loop']=True
 anims['animation.'+ID+'.'+name]=d;return d['bones']
def legs(a,rows):
 # Densify the shared tilt/draw curve before solving both real serial legs.
 # A linearly interpolated final claw alone would detach from its hock mid-draw.
 original=rows;rows=[]
 for i,(ta,pa,ra) in enumerate(original[:-1]):
  tb,pb,rb=original[i+1];steps=max(1,round((tb-ta)*100))
  for k in range(steps):
   u=k/steps;rows.append((ta+(tb-ta)*u,pa+(pb-pa)*u,ra+(rb-ra)*u))
 rows.append(original[-1])
 for name in HIP:
  rots=[];knees=[];positions=[];footrots=[]
  for t,pull,tilt in rows:
   endpoint=REST[name]
   if name=='draw':
    rx=math.radians(-tilt);v=6+pull;endpoint=(13,10-math.sin(rx)*v,-12+math.cos(rx)*v)
   dx,dy,dz=[endpoint[i]-HIP[name][i] for i in range(3)];radius=math.sqrt(dx*dx+dy*dy+dz*dz);assert radius<L*2,(name,endpoint,radius)
   alpha=math.acos(radius/(2*L));theta=math.atan2(math.hypot(dx,dz),-dy)-alpha;phi=math.atan2(dx,dz)
   rots.append((t,[math.degrees(theta),math.degrees(phi),0]));knees.append((t,[math.degrees(alpha*2),0,0]))
   positions.append((t,[endpoint[i]-REST[name][i] for i in range(3)]));footrots.append((t,[tilt if name=='draw' else 0,0,0]))
  a[name+'_thigh']={'rotation':keys(rots)};a[name+'_hock']={'rotation':keys(knees)};a[name+'_talon']={'position':keys(positions),'rotation':keys(footrots)}
 for side,sign in (('upper',1),('lower',-1)):
  a[side+'_string']={'rotation':keys([(t,[sign*math.degrees(math.atan2(pull,20)),0,0]) for t,pull,tilt in rows]),'scale':keys([(t,[1,math.hypot(20,pull)/20,1]) for t,pull,tilt in rows])}
 a['drawn_arrow']={'position':keys([(t,[0,0,pull]) for t,pull,tilt in rows])}
 a['rib_bow']={'rotation':keys([(t,[tilt,0,0]) for t,pull,tilt in rows])}
def wings(a,rows,fold=0):
 for side,sign in (('left',1),('right',-1)):
  a[side+'_wing']={'rotation':keys([(t,[0,0,-sign*v]) for t,v in rows])}
  a[side+'_outer_wing']={'rotation':keys([(t,[0,sign*fold,0]) for t,v in rows])}
a=anim('idle',1.6,True);wings(a,[(0,8),(.4,-12),(.8,8),(1.2,15),(1.6,8)]);legs(a,[(0,0,0),(1.6,0,0)])
a=anim('fly',.8,True);wings(a,[(0,-16),(.2,18),(.4,-16),(.6,-25),(.8,-16)]);legs(a,[(0,0,0),(.8,0,0)])
a=anim('rain',5.8);wings(a,[(0,8),(.6,0),(1.5,0),(1.8,14),(3.5,8),(5.8,8)])
legs(a,[(0,0,0),(.3,0,-45),(1.5,10,-45),(1.55,0,-45),(1.9,0,0),(5.8,0,0)])
a=anim('fan',3.6);legs(a,[(0,0,0),(3.6,0,0)])
# Genuine front-fold: upper wings pivot forward, wrists close around the beak/breast,
# then both joints unfold before the authoritative12tick feather release.
for side,sign in (('left',1),('right',-1)):
 a[side+'_wing']={'rotation':keys([(0,[0,0,-sign*8]),(.5,[0,sign*85,-sign*8]),(.6,[0,0,sign*10]),(1,[0,0,-sign*8]),(3.6,[0,0,-sign*8])])}
 a[side+'_outer_wing']={'rotation':keys([(0,[0,0,0]),(.5,[0,sign*45,0]),(.6,[0,0,0]),(3.6,[0,0,0])])}

a=anim('dive',6.6);wings(a,[(0,8),(.8,65),(1.6,65),(2,8),(6.6,8)],55);legs(a,[(0,0,0),(6.6,0,0)])
a['raptor_body']={'rotation':keys([(0,[0,0,0]),(.8,[0,720,0]),(1.6,[0,1440,0]),(2,[0,1440,0]),(6.6,[0,1440,0])])}
a=anim('hurt',.5);wings(a,[(0,8),(.15,35),(.5,8)]);legs(a,[(0,0,0),(.5,0,0)])
a=anim('death',4.5);wings(a,[(0,8),(.7,65),(4.5,65)],65);legs(a,[(0,0,0),(4.5,0,0)])
a['raptor_body']={'rotation':keys([(0,[0,0,0]),(.7,[65,0,0]),(1.4,[90,0,0]),(4.5,[90,0,0])])}
a['rib_bow']={'rotation':keys([(0,[0,0,0]),(.5,[0,0,45]),(4.5,[0,0,45])])}
for side in ('upper','lower'):a[side+'_string']={'scale':keys([(0,[1,1,1]),(.3,[1,1,1]),(.4,[0,0,0]),(4.5,[0,0,0])])}
a['raptor_body']['scale']=keys([(0,[1,1,1]),(2.8,[1,1,1]),(4.2,[0,0,0]),(4.5,[0,0,0])])
geo(ID,bones,8,7,[0,1.7,0]);write(A/'animations/blueprint/elite'/f'{ID}.animation.json',{'format_version':'1.8.0','animations':anims})
im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
for color,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=COLORS[color])
im.save(A/'textures/entity/blueprint/elite'/f'{ID}.png');write(A/'models/item'/f'{ID}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
print('Original raptor exported:',len(bones),'bones',sum(len(b.get('cubes',[])) for b in bones),'cuboids, seven clips; native pending.')

# Use actual exported transforms to keep the fallen death pose above its local floor.
# This is mesh clearance, not the server's independent gravity/fall displacement.
import importlib.util,numpy as np
spec=importlib.util.spec_from_file_location('eagle_geometry',ROOT/'tools/art/secondary-cuboid/review_models.py');review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review);review.CATEGORY='blueprint/elite'
for clip,length in [('death',4.5),('dive',6.6)]:
 positions=[]
 for t in np.linspace(0,length,round(length*100)+1):
  q=review.geometry(ID,clip='animation.'+ID+'.'+clip,tick=float(t*20));minimum=float(np.concatenate([row[0] for row in q])[:,1].min())
  positions.append((float(t),[0,max(0,-minimum)+(.01 if minimum<0 else 0),0]))
 anims['animation.'+ID+'.'+clip]['bones'].setdefault('raptor_body',{})['position']=keys(positions)
write(A/'animations/blueprint/elite'/f'{ID}.animation.json',{'format_version':'1.8.0','animations':anims})
# A separate dim texture keeps four colours while the native body falls and dissolves.
death=im.copy()
for yy in range(16):
 for xx in range(16):
  col=death.getpixel((xx,yy))
  if col==tuple(bytes.fromhex(COLORS['gold'][1:])):death.putpixel((xx,yy),(117,114,103))
  elif col==tuple(bytes.fromhex(COLORS['straw'][1:])):death.putpixel((xx,yy),(170,167,150))
death.save(A/'textures/entity/blueprint/elite'/f'{ID}_dead.png')

# Original native projectile: upward source axis, renderer orients it to native velocity.
bones=[];b=bone('root');cube(b,(-.5,-14,-.5),(1,12,1),'straw');cube(b,(-1,-3,-1),(2,3,2),'white');cube(b,(-2,-14,-1),(4,3,2),'gold');geo('eagle_finite_gold_arrow',bones,2,2,[0,0,0])
write(A/'animations/blueprint/elite/eagle_finite_gold_arrow.animation.json',{'format_version':'1.8.0','animations':{'animation.eagle_finite_gold_arrow.idle':{'loop':True,'animation_length':1,'bones':{}}}})
for name,kind in [('eagle_hard_feather','feather'),('eagle_rib_bow_fragment','bow')]:
 icon=Image.new('RGB',(16,16),'white');draw=ImageDraw.Draw(icon)
 if kind=='feather':
  draw.rectangle((5,2,10,11),fill=COLORS['gold']);draw.rectangle((7,2,8,13),fill=COLORS['straw']);draw.rectangle((5,8,6,11),fill=COLORS['dark'])
 else:
  draw.rectangle((4,2,7,5),fill=COLORS['straw']);draw.rectangle((6,4,9,11),fill=COLORS['gold']);draw.rectangle((8,10,11,13),fill=COLORS['straw']);draw.rectangle((6,8,9,11),fill=COLORS['dark'])
 icon.save(A/'textures/item'/f'{name}.png');write(A/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+name}})

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('liefeng_jindiao_yushi')

# Original MC creature shape correction, after the material export.
import runpy as _creature33_runpy
_creature33_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v33/refine.py"))["finish"]('liefeng_jindiao_yushi')

# Connected anatomy correction; final authoritative export (V34).
import runpy as _creature34_runpy
_creature34_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v34/refine.py"))["finish"]('liefeng_jindiao_yushi')
