#!/usr/bin/env python3
"""Original bronze-cast knuckle-walking ape, not a humanoid armour template.

Inspected Alex's Mobs ModelGorilla constructor/stand/chest-beat and Twilight YetiModel
body/limb mass. Borrow only animal weight distribution and articulated support principles;
all geometry, UV, palette and keys are original. Helpers are our own cuboid exporter.
"""
from pathlib import Path
import ast, json, math
from PIL import Image, ImageDraw
import numpy as np
import itertools
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/'src/main/resources/assets/dynasty';DATA=ROOT/'src/main/resources/data/dynasty'
ID='hanshan_tongjia_juyuan'
COLORS={'fur':'#343A36','bronze':'#96744B','gold':'#D8AF50','white':'#FFFFFF'}
UV={'fur':[3,3],'bronze':[9,3],'gold':[3,9],'white':[9,9]};bones=[]
helper=(ROOT/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(helper).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','write','geo','keys'):exec(ast.get_source_segment(helper,n),globals())
def keys(rows):return {str(float(round(t,4))):v for t,v in rows}
bone('root')
pelvis=bone('haunch','root',(0,14,12));cube(pelvis,(-10,9,5),(20,15,16),'fur')
cube(pelvis,(-8,21,8),(16,4,12),'bronze')
torso=bone('ribcage','root',(0,20,10))
cube(torso,(-13,16,-13),(26,16,21),'fur')
cube(torso,(-11,13,-9),(22,9,17),'fur')
cube(torso,(-15,24,-9),(30,9,16),'bronze')
cube(torso,(-11,29,-6),(22,4,12),'bronze')
cube(torso,(-10,18,-14),(20,11,3),'fur')
for i,z in enumerate((-7,-1,5)):
 p=bone(f'dorsal_plate{i}','ribcage',(0,31,z))
 cube(p,(-12,30,z-2),(24,4,4),'bronze')
 cube(p,(-8,34,z-1),(16,1.2,2),'gold')
for side,sign in (('left',1),('right',-1)):
 p=bone(side+'_chest_plate','ribcage',(sign*2,24,-14))
 cube(p,(1 if sign>0 else -11,20,-16),(10,11,3),'bronze')
 cube(p,(sign*6-2,23,-18),(4,4,3),'gold')
head=bone('ape_skull','ribcage',(0,28,-16))
cube(head,(-7,25,-22),(14,9.2,13),'fur')
cube(head,(-9,31,-21),(18,4.2,13),'bronze')
cube(head,(-8,29,-26),(16,4,6),'bronze')
cube(head,(-6,24,-29),(12,6,8),'fur')
cube(head,(-3,28,-30),(6,3,3),'bronze')
for sign in (-1,1):
 cube(head,(sign*5-2,29.5,-27),(4,2,2),'gold')
 cube(head,(sign*8-2,25,-14),(4,5,5),'fur')
jaw=bone('ape_jaw','ape_skull',(0,25,-23));cube(jaw,(-6,22,-28),(12,3,8),'fur')
for x in (-4,2):cube(jaw,(x,23,-30),(2,3,2),'white')
for side,sign in (('left',1),('right',-1)):
 upper=bone(side+'_upperarm','ribcage',(sign*17,27,-7))
 cube(upper,(sign*19-7,15,-13),(14,15,13),'fur')
 cube(upper,(sign*19-8,24,-12),(16,7,13),'bronze')
 cube(upper,(sign*20-3,21,-15),(6,6,3),'bronze')
 fore=bone(side+'_forearm',upper['name'],(sign*22,16,-10))
 cube(fore,(sign*22-6,6,-19),(12,13,13),'fur')
 cube(fore,(sign*22-7,5,-20),(14,11,15),'bronze')
 fist=bone(side+'_knuckles',fore['name'],(sign*22,4,-20))
 cube(fist,(sign*22-7,0,-27),(14,9,15),'bronze')
 cube(fist,(sign*22-6,.25,-29),(12,3.75,3),'gold')
 for x in (-5,1):cube(fist,(sign*22+x,4,-29),(4,3,3),'bronze')
 cube(fist,(sign*22-8 if sign>0 else sign*22+4,6,-19),(4,5,6),'fur')
 thigh=bone(side+'_hindleg','haunch',(sign*9,15,12))
 cube(thigh,(sign*9-5,6,6),(10,12,14),'fur')
 shin=bone(side+'_ankle',thigh['name'],(sign*9,7,17))
 cube(shin,(sign*9-4,2,13),(8,8,10),'fur')
 foot=bone(side+'_hindfoot',shin['name'],(sign*9,2,19))
 cube(foot,(sign*9-7,0,13),(14,4,14),'fur')
 for x in (-4,2):cube(foot,(sign*9+x,.25,25),(4,1.75,3),'bronze')
pile=bone('broken_bronze_pile','right_knuckles',(-22,6,-18))
cube(pile,(-25.5,5,-20),(7.5,23,8),'bronze')
cube(pile,(-27,25,-21),(10,3,10),'bronze')
cube(pile,(-25,28,-19),(4,3,6),'gold')
cube(pile,(-22,28.5,-18.5),(2,1.5,5),'bronze')
rock=bone('held_rock','root',(0,13,-20));cube(rock,(-12,2,-32),(24,20,24),'fur')
cube(rock,(-10,22,-30),(20,4,20),'bronze')
anims={}
def anim(name,length,loop=False):
 d={'animation_length':length,'bones':{}}
 if loop:d['loop']=True
 anims['animation.'+ID+'.'+name]=d;return d['bones']
def living(a):a['held_rock']={'scale':[0,0,0]}
def stand(a,curve,length):
 a['ribcage']={'rotation':keys([(t,[-65*v,0,0]) for t,v in curve])}
 a['ape_skull']={'rotation':keys([(t,[65*v,0,0]) for t,v in curve])}
 for side in ('left','right'):a[side+'_upperarm']={'rotation':keys([(t,[65*v,0,0]) for t,v in curve])}
def fore(a,side,sign,curve):
 # Rotate on the true elbow; a small analytic floor clearance prevents corner penetration.
 rot=[];pos=[];end=curve[-1][0]
 for n in range(round(end*20)+1):
  t=n/20;v=curve[-1][1]
  for (ta,va),(tb,vb) in zip(curve,curve[1:]):
   if ta<=t<=tb:v=va+(vb-va)*(t-ta)/(tb-ta);break
  rad=math.radians(v);lift=max(0,19*math.sin(rad)+16*math.cos(rad)-16)+(.02 if v else 0)
  rot.append((t,[-v,0,0]));pos.append((t,[0,round(lift,4),0]))
 a[side+'_forearm']={'rotation':keys(rot),'position':keys(pos)}
a=anim('idle',2.4,True);living(a)
a['ape_jaw']={'rotation':keys([(0,[0,0,0]),(1.2,[4,0,0]),(2.4,[0,0,0])])}
a=anim('walk',1.6,True);living(a)
for i,n in enumerate(('left_upperarm','right_hindleg','right_upperarm','left_hindleg')):
 rows=[]
 for k in range(33):
  t=k/20;p=(t/1.6-i*.25)%1;lift=2*math.sin(p/.2*math.pi) if p<.2 else 0
  rows.append((t,[0,round(lift,4),round(1.5*math.sin(p*2*math.pi),4)]))
 a[n]={'position':keys(rows)}
a=anim('smash',6.5);living(a)
stand(a,[(0,0),(.5,1),(.9,1),(1.2,0),(6.5,0)],6.5)
for side,sign in (('left',1),('right',-1)):
 a[side+'_upperarm']['position']=keys([(0,[0,0,0]),(1.2,[-sign*8,0,0]),(4.4,[-sign*8,0,0]),(5.2,[0,0,0]),(6.5,[0,0,0])])
 a[side+'_forearm']={'rotation':keys([(0,[0,0,0]),(.5,[30,0,sign*70]),(.7,[30,0,sign*90]),(.9,[30,0,sign*70]),(1.2,[0,0,0]),(6.5,[0,0,0])])}
 curve=[(0,0),(1.2,0)]
 for hit in range(8):
  t=1.2+hit*.4
  if hit%2==(0 if side=='left' else 1):curve.extend([(t+.05,0),(t+.2,60),(t+.35,10),(t+.4,0)])
 curve.append((6.5,0))
 # Merge the raised swing after the chest beat without resetting the windup track.
 beat=a[side+'_forearm'];fore(a,side,sign,curve);swing=a[side+'_forearm']
 swing['rotation'].update({k:v for k,v in beat['rotation'].items() if float(k)<=1.2})
a=anim('throw',3.4);living(a)
for side,sign in (('left',1),('right',-1)):
 fore(a,side,sign,[(0,0),(.35,25),(.55,35),(.8,55),(.9,0),(3.4,0)])
 a[side+'_upperarm']={'position':keys([(0,[0,0,0]),(.25,[-sign*6,0,0]),(.8,[-sign*6,0,0]),(1.2,[0,0,0]),(3.4,[0,0,0])])}
a['held_rock']={'scale':keys([(0,[0,0,0]),(.2,[0,0,0]),(.25,[1,1,1]),(.89,[1,1,1]),(.9,[0,0,0]),(3.4,[0,0,0])]),'position':keys([(0,[0,0,0]),(.25,[0,0,0]),(.8,[0,12,4]),(.9,[0,12,4]),(3.4,[0,0,0])])}
a=anim('leap',3.9);living(a)
for n in ('left_upperarm','right_upperarm','left_hindleg','right_hindleg'):
 a[n]={'position':keys([(0,[0,0,0]),(.55,[0,0,0]),(.6,[0,2,0]),(1.2,[0,4,0]),(1.75,[0,2,0]),(1.8,[0,0,0]),(3.9,[0,0,0])])}
a['ape_jaw']={'rotation':keys([(0,[0,0,0]),(.6,[15,0,0]),(1.8,[0,0,0]),(3.9,[0,0,0])])}
a=anim('hurt',.45);living(a)
a['ape_jaw']={'rotation':keys([(0,[0,0,0]),(.1,[10,0,0]),(.45,[0,0,0])])}
a=anim('death',4.5);living(a)
stand(a,[(0,0),(.6,1),(1.1,1),(4.5,1)],4.5)
a['ape_jaw']={'rotation':keys([(0,[0,0,0]),(.6,[15,0,0]),(1.1,[15,0,0]),(1.8,[0,0,0]),(4.5,[0,0,0])])}
# Fall as an entire heavy ape, not a tiny humanoid fold. Clearance derived from real corners.
a['root']={'rotation':keys([(0,[0,0,0]),(1.1,[0,0,0]),(1.8,[90,0,0]),(4.5,[90,0,0])])}
for side,sign in (('left',1),('right',-1)):
 a[side+'_chest_plate']={'rotation':keys([(0,[0,0,0]),(.6,[0,sign*45,0]),(4.5,[0,sign*45,0])])}
 a[side+'_forearm']={'rotation':keys([(0,[0,0,0]),(1.1,[0,0,0]),(1.8,[45,0,sign*70]),(4.5,[45,0,sign*70])])}
 a[side+'_hindleg']={'rotation':keys([(0,[0,0,0]),(1.1,[0,0,0]),(1.8,[-60,0,0]),(4.5,[-60,0,0])])}
# Exact exported coordinate convention; derive the planted fall clearance from every corner.
source=(ROOT/'tools/art/secondary-cuboid/review_models.py').read_text()
for n in ast.parse(source).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('sample','transform'):exec(ast.get_source_segment(source,n),globals())
def min_y(channels,t):
 world={};pivots={b['name']:np.array(b['pivot'],dtype=float) for b in bones};minimum=math.inf
 for b in bones:
  if b['name']=='held_rock':continue
  p=pivots[b['name']];ch=channels.get(b['name'],{});pos=p-(pivots[b['parent']] if b.get('parent') else np.zeros(3))
  pos=pos+(sample(ch['position'],t) if 'position' in ch else 0)
  rot=np.array(b.get('rotation',[0,0,0]))+(sample(ch['rotation'],t) if 'rotation' in ch else 0)
  matrix=(world[b['parent']] if b.get('parent') else np.eye(4))@transform(pos,rot)
  world[b['name']]=matrix
  for c in b.get('cubes',[]):
   cp=np.array(c.get('pivot',b['pivot']));cm=matrix@transform(cp-p,c.get('rotation',[0,0,0]))
   corners=np.array(list(itertools.product((0,1),repeat=3)))*np.array(c['size'])+np.array(c['origin'])-cp
   pts=(cm@np.column_stack((corners*[-1,1,1],np.ones(8))).T).T[:,:3];minimum=min(minimum,float(pts[:,1].min()))
 return minimum
lift=[]
for k in range(181):
 t=k/100;low=min_y(a,t);lift.append((t,[0,round(max(0,-low)+(.02 if low<0 else 0),5),0]))
lift.append((4.5,lift[-1][1]));a['root']['position']=keys(lift)
geo(ID,bones,8,6,[0,2,0]);write(A/'animations/blueprint/elite'/f'{ID}.animation.json',{'format_version':'1.8.0','animations':anims})
im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
for color,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=COLORS[color])
p=A/'textures/entity/blueprint/elite'/f'{ID}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
for item in ('gorilla_cast_plate','gorilla_stone_chip'):
 im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
 d.rectangle((2,2,13,13),fill=COLORS['fur']);d.rectangle((4,4,11,11),fill=COLORS['bronze'])
 d.rectangle((6,6,9,9) if item=='gorilla_cast_plate' else (8,4,11,7),fill=COLORS['gold'])
 p=A/'textures/item'/f'{item}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
# Independent physical rock and fragment use stepped cuboids, never a smooth sphere.
for rid,size in (('gorilla_cast_boulder',24),('gorilla_stone_fragment',8)):
 bones=[];b=bone('root');half=size/2
 cube(b,(-half,0,-half),(size,size*.75,size),'fur');cube(b,(-half+2,size*.75,-half+2),(size-4,size*.25,size-4),'bronze')
 geo(rid,bones,2.4 if size==24 else .9,size/16+.2,[0,size/32,0]);write(A/'animations/blueprint/elite'/f'{rid}.animation.json',{'format_version':'1.8.0','animations':{'animation.'+rid+'.spin':{'loop':True,'animation_length':1,'bones':{'root':{'rotation':keys([(0,[0,0,0]),(1,[0,360,0])])}}}}})
write(A/'models/item'/f'{ID}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
print('Exported original heavy ape and two physical projectile models; native acceptance pending.')

# Approved inventory transparency: preserve entity atlases.
import runpy as _inventory_runpy
from pathlib import Path as _InventoryPath
_inventory_runpy.run_path(str(_InventoryPath(__file__).resolve().parents[1]/"art/inventory-refresh/transparent.py"))["cleanup_white"]()

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('hanshan_tongjia_juyuan')

# Original MC creature shape correction, after the material export.
import runpy as _creature33_runpy
_creature33_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v33/refine.py"))["finish"]('hanshan_tongjia_juyuan')

# Connected anatomy correction; final authoritative export (V34).
import runpy as _creature34_runpy
_creature34_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v34/refine.py"))["finish"]('hanshan_tongjia_juyuan')

# Continuous anatomical masses and coherent pigmentation (V35).
_creature34_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v35/refine.py"))["finish"]('hanshan_tongjia_juyuan')
