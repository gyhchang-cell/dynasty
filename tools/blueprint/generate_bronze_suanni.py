#!/usr/bin/env python3
"""Original hollow bronze lion furnace, segmented ball-supported limbs and two real gear collars.
Actual AlexMobs Tiger constructor/stance/paw keyframes and Twilight Hydra jaw were inspected.
No borrowed mesh, texture, animation or human skeleton. Native acceptance is pending.
"""
from pathlib import Path
import ast,json,math,importlib.util
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'src/main/resources/assets/dynasty';ID='zhenmu_suanni_tonghou'
COLORS={'patina':'#354840','bronze':'#A7844A','fire':'#DB6228','white':'#FFFFFF'};UV={'patina':[3,3],'bronze':[9,3],'fire':[3,9],'white':[9,9]};bones=[]
helper=(ROOT/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(helper).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','geo','write'):exec(ast.get_source_segment(helper,n),globals())
def keys(rows):
 data=[(str(float(round(t,4))),[round(float(x),6) for x in v]) for t,v in rows]
 return {t:v for i,(t,v) in enumerate(data) if i==0 or i==len(data)-1 or v!=data[i-1][1] or v!=data[i+1][1]}
bone('root');body=bone('hollow_furnace','root',(0,23,5))
# Roof, floor and four real corner braces. Both sides have open vent cavities.
cube(body,(-11,12,-6),(22,3,31),'patina');cube(body,(-11,28,-5),(22,4,29),'bronze')
for sign in (-1,1):
 x=9 if sign>0 else -12
 cube(body,(x,15,-6),(3,13,6),'bronze');cube(body,(x,15,21),(3,13,5),'bronze')
 cube(body,(x-.2,14.7,-5),(3.4,2.2,30.8),'bronze');cube(body,(x-.2,25.5,-4.8),(3.4,2.2,30.4),'bronze')
 # Flat broad grille uprights leave actual open space, rather than painted black recesses.
 for z in (4,14):cube(body,(x+.3,17.2,z),(2.4,8,2),'patina')
front=bone('front_casting','hollow_furnace',(0,25,-7));cube(front,(-10,15,-13),(20,12,8),'bronze');cube(front,(-7,25.2,-10),(14,7,8),'patina')
fire=bone('stone_fire_core','hollow_furnace',(0,22,10));cube(fire,(-5,17.5,3),(10,9,14),'fire');cube(fire,(-2,20,2.8),(4,5,2),'white')
for sign in (-1,1):
 bellows=bone(('left' if sign>0 else 'right')+'_bellows','hollow_furnace',(sign*8.8,21,10));cube(bellows,(7.4 if sign>0 else -9.8,18,5),(2.4,6,12),'patina');cube(bellows,(8.6 if sign>0 else -10.8,19.2,7),(2.2,3.6,8),'fire')
# Two octagonal coarse gear collars, with a visible centre hole around the neck.
for layer,z in enumerate((-15,-9)):
 gear=bone('mane_gear'+str(layer),'hollow_furnace',(0,25,z))
 for at,size in [((-9,34,z-1.5),(18,3,3)),((-9,13,z-1.5),(18,3,3)),((-12,16,z-1.5),(3,18,3)),((9,16,z-1.5),(3,18,3))]:cube(gear,at,size,'bronze')
 for sign in (-1,1):
  for y in (16,31):cube(gear,(sign*9-2,y,z-2),(4,4,4),'patina')
head=bone('lion_head','hollow_furnace',(0,27,-12));cube(head,(-9,23,-24),(18,10,14),'bronze');cube(head,(-7,24,-32),(14,5,10),'bronze');cube(head,(-4,27.2,-33),(8,3,2),'patina')
for sign in (-1,1):
 cube(head,(sign*9.1-1.1,28.2,-25),(2.2,3.8,5),'patina');cube(head,(sign*9.3-1.2,29,-25.1),(2.4,2,2.2),'white')
 cube(head,(sign*7-2,32.8,-18),(4,3,4),'bronze')
 # Two cast incisors, rooted in the upper muzzle, outside the open flame outlet.
 cube(head,(sign*5-1,21,-31),(2,4,2),'white')
jaw=bone('hinged_lower_jaw','lion_head',(0,22,-20));cube(jaw,(-6.5,19.5,-32.8),(13,2.5,14),'patina');cube(jaw,(-5,22,-32),(10,2,2),'bronze')
# Segmented curled exhaust tail is a rear counterweight, not a straight pole.
tail=bone('exhaust_tail','hollow_furnace',(0,25,24));cube(tail,(-2.5,23,23),(5,5,11),'patina')
tip=bone('curled_tail_tip','exhaust_tail',(0,26,33));cube(tip,(-2,25,32),(4,4,10),'bronze');cube(tip,(-3,27.2,39),(6,6,5),'patina')
HIP={};REST={};L=10.5
for i,(name,x,z,y) in enumerate([('front_left',11,-10,25),('front_right',-11,-10,25),('rear_left',10,20,23),('rear_right',-10,20,23)]):
 HIP[name]=(x,y,z);REST[name]=(12 if x>0 and z<0 else -12 if z<0 else x,9,-13 if z<0 else 21)
 upper=bone(name+'_upper','hollow_furnace',HIP[name]);cube(upper,(x-3,y-L,z-3),(6,L,6),'bronze')
 lower=bone(name+'_shin',upper['name'],(x,y-L,z));cube(lower,(x-2.3,y-2*L,z-2.3),(4.6,L,4.6),'patina')
 paw=bone(name+'_paw','root',REST[name]);xx,yy,zz=REST[name];cube(paw,(xx-4.5,yy-1.2,zz-5),(9,3,9),'bronze')
 for toe in (-2,2):cube(paw,(xx+toe-1,yy-.8,zz-6),(2,2.4,3),'patina')
 ball=bone(name+'_bronze_ball',paw['name'],(xx,4,zz));cube(ball,(xx-3,0,zz-3),(6,2,6),'patina');cube(ball,(xx-4,2,zz-4),(8,4,8),'bronze');cube(ball,(xx-5,2.1,zz-3),(10,3.8,6),'bronze');cube(ball,(xx-3,2.2,zz-5),(6,3.6,10),'bronze');cube(ball,(xx-3,6,zz-3),(6,2,6),'fire')
anims={}
def anim(name,length,loop=False):
 d={'animation_length':length,'bones':{}}
 if loop:d['loop']=True
 anims['animation.'+ID+'.'+name]=d;return d['bones']
def legs(a,rows):
 # Sample the same four endpoints before solving; intermediate stances keep their real joints.
 original=rows;rows=[]
 for (ta,pa),(tb,pb) in zip(original,original[1:]):
  steps=max(1,round((tb-ta)*100))
  for k in range(steps):
   u=k/steps;points={name:tuple(pa.get(name,REST[name])[j]+(pb.get(name,REST[name])[j]-pa.get(name,REST[name])[j])*u for j in range(3)) for name in HIP};rows.append((ta+(tb-ta)*u,points))
 rows.append(original[-1])
 # Every row stores the actual desired four paw endpoints. Solve hip and shin from them.
 for name in HIP:
  rots=[];knees=[];positions=[]
  for t,points in rows:
   endpoint=points.get(name,REST[name]);dx,dy,dz=[endpoint[j]-HIP[name][j] for j in range(3)];radius=math.sqrt(dx*dx+dy*dy+dz*dz);assert radius<2*L,(name,endpoint)
   alpha=math.acos(radius/(2*L));theta=math.atan2(math.hypot(dx,dz),-dy)-alpha;phi=math.atan2(dx,dz)
   rots.append((t,[math.degrees(theta),math.degrees(phi),0]));knees.append((t,[math.degrees(alpha*2),0,0]));positions.append((t,[endpoint[j]-REST[name][j] for j in range(3)]))
  a[name+'_upper']={'rotation':keys(rots)};a[name+'_shin']={'rotation':keys(knees)};a[name+'_paw']={'position':keys(positions)}
a=anim('idle',2.4,True);legs(a,[(0,{}),(2.4,{})]);a['curled_tail_tip']={'rotation':keys([(0,[0,-8,0]),(1.2,[0,8,0]),(2.4,[0,-8,0])])}
a=anim('walk',2.4,True);rows=[]
for t in np.linspace(0,2.4,241):
 points={}
 for i,name in enumerate(HIP):
  u=(float(t)/2.4-i/4)%1
  dz=-3+24*u if u<.25 else 3-8*(u-.25);lift=math.sin(math.pi*4*u)*3 if u<.25 else 0
  points[name]=(REST[name][0],REST[name][1]+lift,REST[name][2]+dz)
 rows.append((float(t),points))
legs(a,rows)
for name in HIP:a[name+'_bronze_ball']={'rotation':keys([(float(t),[float(t)/2.4*360,0,0]) for t in np.linspace(0,2.4,241)])}
a=anim('fire',6.4);legs(a,[(0,{}),(6.4,{})]);a['lion_head']={'rotation':keys([(0,[0,0,0]),(1.2,[0,-45,0]),(4.15,[0,45,0]),(4.2,[0,45,0]),(5,[0,0,0]),(6.4,[0,0,0])])}
a['hinged_lower_jaw']={'rotation':keys([(0,[0,0,0]),(1.2,[25,0,0]),(4.2,[25,0,0]),(5,[0,0,0]),(6.4,[0,0,0])])}
for i in range(2):a['mane_gear'+str(i)]={'rotation':keys([(0,[0,0,0]),(1.2,[0,0,-720 if i==0 else 720]),(4.2,[0,0,-2520 if i==0 else 2520]),(6.4,[0,0,-2520 if i==0 else 2520])])}
for side,sign in [('left',1),('right',-1)]:a[side+'_bellows']={'position':keys([(0,[0,0,0]),(1.2,[-sign*2,0,0]),(1.3,[0,0,0]),(4.2,[0,0,0]),(6.4,[0,0,0])])}
a=anim('stomp',3.1);legs(a,[(0,{}),(.45,{'front_left':(12,15,-13)}),(.5,{}),(3.1,{})]);a['front_left_bronze_ball']={'rotation':keys([(0,[0,0,0]),(.45,[0,720,0]),(.5,[0,720,0]),(3.1,[0,720,0])])}
a=anim('roar',3.0);legs(a,[(0,{}),(3,{})]);a['lion_head']={'rotation':keys([(0,[0,0,0]),(.7,[-25,0,0]),(1.2,[-25,0,0]),(2,[0,0,0]),(3,[0,0,0])])};a['hinged_lower_jaw']={'rotation':keys([(0,[0,0,0]),(.7,[30,0,0]),(1.2,[30,0,0]),(2,[0,0,0]),(3,[0,0,0])])}
for i in range(2):a['mane_gear'+str(i)]={'rotation':keys([(0,[0,0,0]),(.7,[0,0,22 if i==0 else -22]),(1.2,[0,0,22 if i==0 else -22]),(3,[0,0,0])])}
a=anim('hurt',.5);legs(a,[(0,{}),(.5,{})]);a['lion_head']={'rotation':keys([(0,[0,0,0]),(.15,[0,12,0]),(.5,[0,0,0])])}
a=anim('death',4.5);legs(a,[(0,{}),(4.5,{})]);a['hollow_furnace']={'position':keys([(0,[0,0,0]),(.4,[0,0,0]),(1.2,[0,-18,0]),(4.5,[0,-18,0])]),'scale':keys([(0,[1,1,1]),(.4,[1,1,1]),(1.2,[1,.45,1]),(4.5,[1,.45,1])])}
a['lion_head']={'rotation':keys([(0,[0,0,0]),(.4,[0,0,0]),(1.2,[35,0,0]),(4.5,[35,0,0])])};a['hinged_lower_jaw']={'rotation':keys([(0,[0,0,0]),(.5,[35,0,0]),(4.5,[35,0,0])])};a['stone_fire_core']={'scale':keys([(0,[1,1,1]),(.4,[1.2,1.2,1.2]),(.8,[0,0,0]),(4.5,[0,0,0])])}
geo(ID,bones,6,5,[0,2,0]);ap=A/'animations/blueprint/elite'/f'{ID}.animation.json';write(ap,{'format_version':'1.8.0','animations':anims})
# Use actual exported corner transforms for the ground-contact offset of the coarse balls.
spec=importlib.util.spec_from_file_location('suanni_geometry',ROOT/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);r.CATEGORY='blueprint/elite'
for name in HIP:
 poses=[]
 for t in np.linspace(0,2.4,241):
  q=[v for v,u,b in r.geometry(ID,clip='animation.'+ID+'.walk',tick=float(t*20)) if b==name+'_bronze_ball'];minimum=float(np.concatenate(q)[:,1].min())
  # Preserve the intentional lifted paw; correct only the ball's own rotated extents.
  ch=anims['animation.'+ID+'.walk']['bones'][name+'_paw']['position'];lift=float(r.sample(ch,float(t))[1]);poses.append((float(t),[0,lift-minimum,0]))
 anims['animation.'+ID+'.walk']['bones'][name+'_bronze_ball']['position']=keys(poses)
# Grounded broken cast limbs in death: core compression breaks joints on purpose.
for name in HIP:
 poses=[]
 for t in np.linspace(0,4.5,451):
  q=[v for v,u,b in r.geometry(ID,clip='animation.'+ID+'.death',tick=float(t*20)) if b in (name+'_upper',name+'_shin')];minimum=float(np.concatenate(q)[:,1].min());sc=float(r.sample(anims['animation.'+ID+'.death']['bones']['hollow_furnace']['scale'],float(t))[1]);poses.append((float(t),[0,max(0,-minimum)/sc,0]))
 anims['animation.'+ID+'.death']['bones'][name+'_upper']['position']=keys(poses)
# The cast head actually reaches its local floor after the limbs have collapsed.
poses=[]
for t in np.linspace(0,4.5,451):
 q=[v for v,u,b in r.geometry(ID,clip='animation.'+ID+'.death',tick=float(t*20)) if b in ('lion_head','hinged_lower_jaw')];minimum=float(np.concatenate(q)[:,1].min());sc=float(r.sample(anims['animation.'+ID+'.death']['bones']['hollow_furnace']['scale'],float(t))[1]);blend=min(1,max(0,(float(t)-.4)/.8));poses.append((float(t),[0,(-minimum/sc if minimum<0 else -minimum/sc*blend)+(.006/sc if minimum<0 else 0),0]))
anims['animation.'+ID+'.death']['bones']['lion_head']['position']=keys(poses);write(ap,{'format_version':'1.8.0','animations':anims})
im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
for color,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=COLORS[color])
im.save(A/'textures/entity/blueprint/elite'/f'{ID}.png');dead=im.copy();dead.putdata([((53,72,64) if c==(219,98,40) else c) for c in im.get_flattened_data()]);dead.save(A/'textures/entity/blueprint/elite'/f'{ID}_dead.png');write(A/'models/item'/f'{ID}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
print('Original hollow bronze lion exported',len(bones),'bones',sum(len(b.get('cubes',[])) for b in bones),'cuboids; seven clips, native pending.',flush=True)

# Actual finite auxiliary models, using the same original material islands.
bones=[];b=bone('root')
for i in range(6):
 z=-(i+1)*128/6;cube(b,(-2-i*.8,-1.5-i*.2,z),(4+i*1.6,3+i*.4,128/6+.5),'fire');cube(b,(-1,0,z+3),(2,2,10),'white')
geo('suanni_fixed_flame_jet',bones,17,3,[0,0,-4]);write(A/'animations/blueprint/elite/suanni_fixed_flame_jet.animation.json',{'format_version':'1.8.0','animations':{'animation.suanni_fixed_flame_jet.idle':{'animation_length':.5,'loop':True,'bones':{'root':{'scale':keys([(0,[1,1,1]),(.25,[1,.85,1]),(.5,[1,1,1])])}}}}})
bones=[];b=bone('root');cube(b,(-5,0,-5),(10,1.5,10),'patina');cube(b,(-3,1,-3),(6,6,6),'fire');cube(b,(-1,6,-1),(2,5,2),'white');geo('suanni_ground_fire_crack',bones,1.4,1.6,[0,.6,0]);write(A/'animations/blueprint/elite/suanni_ground_fire_crack.animation.json',{'format_version':'1.8.0','animations':{'animation.suanni_ground_fire_crack.idle':{'animation_length':1,'loop':True,'bones':{'root':{'scale':keys([(0,[1,1,1]),(.5,[1,.8,1]),(1,[1,1,1])])}}}}})
for name in ('suanni_copper_gear','stone_fire_cinder'):
 icon=Image.new('RGB',(16,16),'white');draw=ImageDraw.Draw(icon)
 if name=='suanni_copper_gear':
  for box in [(4,4,11,11),(6,2,9,13),(2,6,13,9)]:draw.rectangle(box,fill=COLORS['bronze'])
  draw.rectangle((6,6,9,9),fill=COLORS['white']);draw.rectangle((4,4,5,7),fill=COLORS['patina']);draw.rectangle((10,8,11,11),fill=COLORS['fire'])
 else:
  draw.rectangle((4,4,11,11),fill=COLORS['patina']);draw.rectangle((4,4,11,9),fill=COLORS['fire']);draw.rectangle((6,4,9,7),fill=COLORS['white']);draw.rectangle((8,10,11,11),fill=COLORS['bronze'])
 icon.save(A/'textures/item'/f'{name}.png');write(A/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+name}})

# Approved inventory transparency: preserve entity atlases.
import runpy as _inventory_runpy
from pathlib import Path as _InventoryPath
_inventory_runpy.run_path(str(_InventoryPath(__file__).resolve().parents[1]/"art/inventory-refresh/transparent.py"))["cleanup_white"]()

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('zhenmu_suanni_tonghou')

# Original MC creature shape correction, after the material export.
import runpy as _creature33_runpy
_creature33_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v33/refine.py"))["finish"]('zhenmu_suanni_tonghou')

# Connected anatomy correction; final authoritative export (V34).
import runpy as _creature34_runpy
_creature34_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v34/refine.py"))["finish"]('zhenmu_suanni_tonghou')

# Continuous anatomical masses and coherent pigmentation (V35).
_creature34_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v35/refine.py"))["finish"]('zhenmu_suanni_tonghou')
