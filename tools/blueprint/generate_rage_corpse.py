#!/usr/bin/env python3
"""Original four-knuckle coffin corpse. Main cavity, ground support and blood gate come first.

Studied Goety's actual GraveGolemModel for a grave container as the core body and clear limb
mass. This original articulated four-support chassis has its own geometry and seven clips;
no external geometry/UV/texture/animation is copied. Source helpers reuse our yasha exporter.
"""
from pathlib import Path
import ast
import json
import math
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
A=ROOT/'src/main/resources/assets/dynasty'
DATA=ROOT/'src/main/resources/data/dynasty'
ID='banshan_jiazhou_shikuang'
COLORS={'iron':'#35373D','rust':'#937051','blood':'#7A2632','white':'#FFFFFF'}
UV={'iron':[3,3],'rust':[9,3],'blood':[3,9],'white':[9,9]}
bones=[]
helper=(ROOT/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(helper).body:
    if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','write','geo','keys'):
        exec(ast.get_source_segment(helper,n),globals())

bone('root')
shell=bone('coffin_shell','root',(0,14,0))
# The large folded grave cavity is the body. No human head/neck/waist hidden inside it.
cube(shell,(-14,14,-16),(4,22,28),'iron')
cube(shell,(10,14,-16),(4,22,28),'iron')
cube(shell,(-10,14,-16),(20,4,28),'iron')
cube(shell,(-10,18,8),(20,18,4),'iron')
cube(shell,(-14,36,-16),(28,4,28),'rust')
cube(shell,(-12,40,-12),(24,2,20),'iron')
cube(shell,(-14,14,-19),(28,6,4),'rust')
cube(shell,(-14,20,-19),(4,16,4),'iron')
cube(shell,(10,20,-19),(4,16,4),'iron')
cube(shell,(-10,32,-19),(20,4,4),'rust')
core=bone('stitched_viscera','coffin_shell',(0,24,-10))
cube(core,(-9,18,-14),(18,14,6),'blood')
for x in (-8,-4,0,4):
    cube(core,(x,19,-16),(2,10,2),'white')
for sign in (-1,1):
    eye=bone(('left' if sign>0 else 'right')+'_grave_eye','coffin_shell',(sign*7,34,-19))
    cube(eye,(sign*7-3,32,-21),(6,4,3),'blood')
    cube(eye,(sign*7-1,33,-22),(2,2,2),'white')
    gate=bone(('left' if sign>0 else 'right')+'_blood_gate','coffin_shell',(sign*10,23,-19))
    cube(gate,(0 if sign>0 else -10,20,-20),(10,12,2),'iron')
    cube(gate,(6 if sign>0 else -8,22,-22),(2,8,2),'white')
rear=bone('rear_grave_mass','coffin_shell',(0,20,11))
cube(rear,(-11,12,10),(22,16,16),'iron')
cube(rear,(-9,28,12),(18,4,12),'rust')
cube(rear,(-7,12,26),(14,12,3),'blood')
# Broad linen bands belong to the container; they do not create a robe or human chest.
for z in (-10,3,18):
    band=bone(f'linen_band{z}','coffin_shell',(0,24,z))
    cube(band,(-15,17,z-2),(2,18 if z<10 else 10,4),'white')
    cube(band,(13,17,z-2),(2,18 if z<10 else 10,4),'white')
    if z<10:
        cube(band,(-15,35,z-2),(2,9,4),'white')
        cube(band,(13,35,z-2),(2,9,4),'white')
        cube(band,(-13,42,z-2),(26,2,4),'white')

for side,sign in [('left',1),('right',-1)]:
    upper=bone(side+'_front_support','root',(sign*13,22,-10))
    cube(upper,(12 if sign>0 else -28,16,-16),(16,9,12),'rust')
    cube(upper,(14 if sign>0 else -25,25,-14),(11,3,8),'iron')
    fore=bone(side+'_foreknuckle',upper['name'],(sign*23,14,-12))
    cube(fore,(18 if sign>0 else -28,5,-15),(10,12,6),'iron')
    fist=bone(side+'_front_fist',fore['name'],(sign*24,5,-12))
    cube(fist,(17 if sign>0 else -31,0,-19),(14,8,14),'rust')
    cube(fist,(19 if sign>0 else -29,8,-17),(10,2,10),'iron')
    cube(fist,(18 if sign>0 else -30,2,-21),(12,4,2),'white')
    # A real cuff and three connected hollow chain links fold in under the wrist at rest.
    cube(fist,(16 if sign>0 else -32,6,-18),(16,3,12),'iron')
    parent=fist['name']
    for i in range(3):
        x=sign*(24+i*6)
        link=bone(f'{side}_chain{i}',parent,(x,7,-12),(0,180,0) if i==0 else None)
        start=x if sign>0 else x-6
        cube(link,(start,5,-14),(6,2,4),'rust')
        cube(link,(start,9,-14),(6,2,4),'rust')
        cube(link,(start,7,-14),(2,2,4),'iron')
        cube(link,(start+4,7,-14),(2,2,4),'iron')
        parent=link['name']
    hind=bone(side+'_hind_support','root',(sign*10,16,21))
    cube(hind,(9 if sign>0 else -22,9,17),(13,9,8),'iron')
    ankle=bone(side+'_hind_ankle',hind['name'],(sign*20,10,21))
    cube(ankle,(17 if sign>0 else -23,5,18),(6,6,6),'rust')
    foot=bone(side+'_hind_foot',ankle['name'],(sign*20,3,21))
    cube(foot,(15 if sign>0 else -25,0,15),(10,3,12),'iron')
    cube(foot,(17 if sign>0 else -23,3,17),(6,2,8),'white')

# Three distinct broken weapons attach to actual sockets on the upper shell.
for i,(x,z,height) in enumerate([(-8,4,15),(0,7,12),(8,9,18)]):
    socket=bone(f'blade_socket{i}','coffin_shell',(x,38,z))
    cube(socket,(x-3,36,z-3),(6,4,6),'rust')
    blade=bone(f'broken_blade{i}',socket['name'],(x,39,z),(12+(i*6),0,(i-1)*12))
    cube(blade,(x-1,38,z-1),(2,height,2),'iron')
    cube(blade,(x-4,41,z-2),(8,2,4),'rust')
    cube(blade,(x-2,44,z-2),(4,height-6,2),'white')
    cube(blade,(x-2,44,z+1),(2,4,2),'blood')
mud=bone('death_mud','root')
cube(mud,(-18,.02,-22),(36,1,52),'iron')
cube(mud,(-25,.02,-16),(50,1,30),'iron')

anims={}
def anim(name,length,loop=False):
    d={'animation_length':length,'bones':{}}
    if loop:d['loop']=True
    anims['animation.'+ID+'.'+name]=d
    return d['bones']
def living(a):a['death_mud']={'scale':[0,0,0]}
def shakes(a,length,amplitude):
    for i in range(3):a[f'broken_blade{i}']={'rotation':keys([(0,[0,0,0]),(length*.3,[amplitude,0,(i-1)*amplitude]),(length*.6,[-amplitude,0,0]),(length,[0,0,0])])}
def front_pose(a,side,sign,points,length,strike_lift=0):
    # Fist corners sweep around the elbow. Lift the joint just enough to keep the
    # lowest real corner above the floor through the complete interpolated swing.
    rotations=[];positions=[]
    last_motion=max(points[i+1][0] for i in range(len(points)-1) if points[i][1]!=points[i+1][1])
    for step in range(round(last_motion*100)+1):
        t=round(step/100,2)
        angle=points[-1][1]
        for (ta,va),(tb,vb) in zip(points,points[1:]):
            if ta<=t<=tb:angle=va+(vb-va)*(t-ta)/(tb-ta);break
        rad=math.radians(angle)
        lift=max(0,8*abs(math.sin(rad))+14*math.cos(rad)-14)+(.03 if abs(angle)>.0001 else 0)+strike_lift*angle/90
        rotations.append((t,[0,0,sign*angle]));positions.append((t,[0,round(lift,5),0]))
    if last_motion<length:rotations.append((length,[0,0,0]));positions.append((length,[0,0,0]))
    a[side+'_foreknuckle']={'rotation':keys(rotations),'position':keys(positions)}

a=anim('idle',2.4,True);living(a)
a['coffin_shell']={'position':keys([(0,[0,0,0]),(1.2,[0,.5,0]),(2.4,[0,0,0])])}
a['stitched_viscera']={'scale':keys([(0,[1,1,1]),(1.2,[1.04,1,1.08]),(2.4,[1,1,1])])}
for side in ('left','right'):a[side+'_blood_gate']={'rotation':keys([(0,[0,0,0]),(1.2,[0,(-4 if side=='left' else 4),0]),(2.4,[0,0,0])])}
a=anim('walk',1.6,True);living(a)
# Successive single-support transfers: at least three contacts rather than a hopping box.
for n,name in enumerate(('left_front_support','right_hind_support','right_front_support','left_hind_support')):
    pos=[];yaw=[]
    for tick in range(33):
        t=tick/20;phase=(t/1.6-n*.25)%1
        lift=2.5*math.sin(phase/.2*math.pi) if phase<.2 else 0
        pos.append((t,[0,round(lift,4),round(math.sin(phase*2*math.pi)*2,4)]))
        yaw.append((t,[0,round(math.sin(phase*2*math.pi)*5,4),0]))
    a[name]={'position':keys(pos),'rotation':keys(yaw)}
a['coffin_shell']={'rotation':keys([(0,[0,0,1]),(.8,[0,0,-1]),(1.6,[0,0,1])])}
a=anim('spin',7.1);living(a)
a['root']={'rotation':keys([(0,[0,0,0]),(1.1,[0,0,0]),(5.1,[0,2160,0]),(7.1,[0,2160,0])])}
a['coffin_shell']={'rotation':keys([(0,[0,0,0]),(.3,[3,0,0]),(.6,[-3,0,0]),(.9,[3,0,0]),(1.1,[0,0,0]),(5.1,[0,0,0]),(5.6,[0,0,4]),(6.1,[0,0,-4]),(7.1,[0,0,0])])}
for side,sign in [('left',1),('right',-1)]:
    front_pose(a,side,sign,[(0,0),(.5,50),(.9,20),(1.1,0),(7.1,0)],7.1)
    a[side+'_chain0']={'rotation':keys([(0,[0,0,0]),(.9,[0,0,0]),(1.1,[0,-180,0]),(5.1,[0,-180,0]),(5.6,[0,0,0]),(7.1,[0,0,0])])}
shakes(a,1.1,4)
a=anim('leap',4.2);living(a)
a['coffin_shell']={'rotation':keys([(0,[0,0,0]),(.6,[-4,0,0]),(.7,[5,0,0]),(1.2,[0,0,0]),(1.65,[8,0,0]),(2.3,[0,0,0]),(4.2,[0,0,0])])}
for name in ('left_front_support','right_front_support','left_hind_support','right_hind_support'):
    a[name]={'position':keys([(0,[0,0,0]),(.6,[0,0,0]),(.7,[0,3,0]),(1.2,[0,5,0]),(1.65,[0,0,0]),(4.2,[0,0,0])])}
shakes(a,.7,6)
a=anim('blood',4.05);living(a)
for side,sign in [('left',1),('right',-1)]:
    front_pose(a,side,sign,[(0,0),(.35,70),(.6,90),(.8,0),(4.05,0)],4.05,11)
    a[side+'_blood_gate']={'rotation':keys([(0,[0,0,0]),(.7,[0,sign*-8,0]),(.8,[0,sign*-70,0]),(1.8,[0,sign*-70,0]),(2.5,[0,0,0]),(4.05,[0,0,0])])}
a['stitched_viscera']={'scale':keys([(0,[1,1,1]),(.7,[1.08,1.08,1.08]),(.8,[1,1,1]),(4.05,[1,1,1])])}
a=anim('hurt',.45);living(a)
a['coffin_shell']={'rotation':keys([(0,[0,0,0]),(.1,[0,0,-4]),(.45,[0,0,0])])}
a=anim('death',4)
a['root']={'scale':keys([(0,[1,1,1]),(.6,[1,.45,1]),(2.6,[1,.45,1]),(3.9,[0,0,0]),(4,[0,0,0])])}
a['coffin_shell']={'rotation':keys([(0,[0,0,0]),(.6,[20,0,0]),(4,[20,0,0])])}
a['death_mud']={'scale':keys([(0,[0,0,0]),(.8,[0,0,0]),(1.2,[1,1,1]),(3,[1,1,1]),(4,[0,0,0])])}
for side,sign in [('left',1),('right',-1)]:a[side+'_blood_gate']={'rotation':keys([(0,[0,0,0]),(.4,[0,sign*-90,0]),(4,[0,sign*-90,0])])}
for i in range(3):
    a[f'broken_blade{i}']={'position':keys([(0,[0,0,0]),(.4,[0,0,0]),(.8,[(i-1)*10,8,4]),(1.5,[(i-1)*14,0,10]),(4,[(i-1)*14,0,10])]),'rotation':keys([(0,[0,0,0]),(.8,[25,0,(i-1)*30]),(1.5,[50,0,(i-1)*60]),(4,[50,0,(i-1)*60])])}

geo(ID,bones,7.2,4.4,[0,1.8,0])
write(A/'animations/blueprint/elite'/f'{ID}.animation.json',{'format_version':'1.8.0','animations':anims})
tex=Image.new('RGB',(16,16),COLORS['white']);d=ImageDraw.Draw(tex)
for key in ('iron','rust','blood'):
    x,y=UV[key];d.rectangle((x-1,y-1,x+4,y+4),fill=COLORS[key])
tex.save(A/'textures/entity/blueprint/elite'/f'{ID}.png')
items=('corpse_iron_shackle','oil_soaked_shroud','broken_burial_blade')
for identifier in items+('corpse_armor_corrosion',):
    im=Image.new('RGB',(16,16),COLORS['white']);d=ImageDraw.Draw(im)
    if identifier.endswith('shackle'):
        d.rectangle((2,2,13,13),fill=COLORS['rust']);d.rectangle((4,4,11,11),fill=COLORS['white'])
        d.rectangle((4,2,11,3),fill=COLORS['iron']);d.rectangle((6,12,9,13),fill=COLORS['blood'])
    elif identifier.endswith('shroud'):
        d.rectangle((4,2,11,13),fill=COLORS['rust']);d.rectangle((2,6,3,11),fill=COLORS['rust']);d.rectangle((12,4,13,9),fill=COLORS['rust'])
        d.rectangle((6,6,9,11),fill=COLORS['iron']);d.rectangle((4,10,5,11),fill=COLORS['blood'])
    elif identifier.endswith('blade'):
        d.rectangle((6,2,9,11),fill=COLORS['iron']);d.rectangle((8,2,9,9),fill=COLORS['white'])
        d.rectangle((2,10,13,11),fill=COLORS['rust']);d.rectangle((6,12,9,13),fill=COLORS['rust']);d.rectangle((6,4,7,5),fill=COLORS['blood'])
    else:
        d.rectangle((2,2,13,13),fill=COLORS['iron']);d.rectangle((4,4,11,11),fill=COLORS['rust']);d.rectangle((6,4,7,11),fill=COLORS['blood']);d.rectangle((8,8,9,9),fill=COLORS['white'])
    folder='mob_effect' if identifier=='corpse_armor_corrosion' else 'item'
    p=A/'textures'/folder/f'{identifier}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
    if identifier in items:write(A/'models/item'/f'{identifier}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+identifier}})
write(A/'models/item'/f'{ID}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
write(DATA/'loot_tables/entities'/f'{ID}.json',{'type':'minecraft:entity','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'dynasty:'+n}]} for n in items]})
write(DATA/'advancements/blueprint'/f'kill_{ID}.json',{'criteria':{'kill':{'trigger':'minecraft:player_killed_entity','conditions':{'entity':{'type':'dynasty:'+ID}}}}})
write(DATA/'recipes/blueprint/corpse_shackle_salvage.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':'dynasty:corpse_iron_shackle'}],'result':{'item':'minecraft:iron_nugget','count':6}})
write(DATA/'recipes/blueprint/corpse_recovered_sword.json',{'type':'minecraft:crafting_shaped','pattern':['B','B','S'],'key':{'B':{'item':'dynasty:broken_burial_blade'},'S':{'item':'minecraft:stick'}},'result':{'item':'minecraft:iron_sword'}})
print('Exported four-knuckle coffin corpse:',len(bones),'bones',sum(len(b.get('cubes',[])) for b in bones),'cuboids',len(anims),'clips; native acceptance pending.')

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('banshan_jiazhou_shikuang')
