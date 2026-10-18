#!/usr/bin/env python3
"""Original folded-silk ink ray: a compact ink case, paired fan folds and two sliding bamboo skids.
Studied Cataclysm Lionfish_Model's actual body-to-fin and fin pivot hierarchy, not its geometry.
All body, dagger carriage, bamboo, UV, texture and clips here are original and editable.
"""
from pathlib import Path
import ast,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'src/main/resources/assets/dynasty';DATA=ROOT/'src/main/resources/data/dynasty'
ID='mojia_jueying_cike';SPIKE='assassin_ink_bamboo_anchor'
COLORS={'ink':'#1F2428','fold':'#586461','bamboo':'#B8A47A','white':'#FFFFFF'}
UV={'ink':[3,3],'fold':[9,3],'bamboo':[3,9],'white':[9,9]};bones=[]
source=(ROOT/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(source).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','write','geo','keys'):exec(ast.get_source_segment(source,n),globals())
bone('root')
body=bone('ink_case','root',(0,5,0))
# A horizontal scroll case is the actual body; no humanoid head, arms, torso or pelvis.
cube(body,(-7,3,-10),(2,7,23),'ink');cube(body,(5,3,-10),(2,7,23),'ink')
cube(body,(-5,3,-10),(10,2,23),'fold');cube(body,(-5,5,10),(10,5,3),'ink')
cube(body,(-7,10,-10),(14,2,23),'white');cube(body,(-5,12,-7),(10,2,17),'ink')
core=bone('ink_heart','ink_case',(0,7,-5));cube(core,(-4,5,-8),(8,4,15),'ink')
slot=bone('front_ink_slot','ink_case',(0,7,-10));cube(slot,(-5,5,-12),(10,2,2),'bamboo');cube(slot,(-5,9,-12),(10,2,2),'fold')
for sign,side in [(1,'left'),(-1,'right')]:
 skid=bone(side+'_bamboo_skid','root',(sign*6,1,2))
 cube(skid,(4 if sign>0 else -8,0,-9),(4,2,23),'bamboo')
 cube(skid,(5 if sign>0 else -7,2,-5),(2,3,14),'ink')
 wing=bone(side+'_fold_wing','ink_case',(sign*6,8,-2))
 cube(wing,(6 if sign>0 else -14,7,-8),(8,2,18),'ink')
 panel=bone(side+'_outer_fold',wing['name'],(sign*14,8,-2))
 cube(panel,(14 if sign>0 else -20,7,-5),(6,2,10),'fold')
 for z in (-5,3):cube(wing,(6 if sign>0 else -20,9,z),(14,2,2),'bamboo')
 cube(panel,(16 if sign>0 else -20,9,-1),(4,2,2),'white')
 cube(body,(6 if sign>0 else -11,6,-9),(5,2,2),'bamboo')
 carriage=bone(side+'_dagger_carriage','ink_case',(sign*10,6,-11))
 cube(carriage,(8 if sign>0 else -12,4,-13),(4,4,4),'fold')
 cube(carriage,(9 if sign>0 else -11,5,-15),(2,2,5),'bamboo')
 dagger=bone(side+'_reverse_dagger',carriage['name'],(sign*10,5,-11))
 cube(dagger,(8 if sign>0 else -12,4,-10),(4,2,10),'ink')
 cube(dagger,(9 if sign>0 else -11,4,0),(2,2,3),'ink')
 cube(dagger,(7 if sign>0 else -13,3.5,-14),(6,2,2),'ink')
 # Short cloth vanes attach to the rear case as a two-joint ribbon, not a human cloak.
 tail=bone(side+'_silk_tail0','ink_case',(sign*4,6,12))
 cube(tail,(2 if sign>0 else -6,6,12),(4,2,6),'fold')
 tail2=bone(side+'_silk_tail1',tail['name'],(sign*4,6,18))
 cube(tail2,(2 if sign>0 else -6,6,18),(4,2,7),'ink')
wash=bone('death_wash','root');cube(wash,(-16,.02,-13),(32,.5,38),'white');cube(wash,(-20,.52,-6),(40,.5,23),'ink')
anims={}
def anim(n,length,loop=False):
 d={'animation_length':length,'bones':{}}
 if loop:d['loop']=True
 anims['animation.'+ID+'.'+n]=d;return d['bones']
def living(a):a['death_wash']={'scale':[0,0,0]}
def blades(a,curve):
 for side,sign in [('left',1),('right',-1)]:
  a[side+'_reverse_dagger']={'rotation':keys([(t,[0,sign*y,0]) for t,y in curve])}
  a[side+'_dagger_carriage']={'position':keys([(t,[-sign*5*min(1,y/150),0,0]) for t,y in curve])}
def folds(a,curve):
 for side,sign in [('left',1),('right',-1)]:
  a[side+'_fold_wing']={'rotation':keys([(t,[0,0,-sign*y]) for t,y in curve])}
a=anim('idle',2,True);living(a)
a['ink_case']={'position':keys([(0,[0,0,0]),(1,[0,.6,0]),(2,[0,0,0])])}
folds(a,[(0,0),(1,4),(2,0)])
for side,sign in [('left',1),('right',-1)]:
 a[side+'_silk_tail0']={'rotation':keys([(0,[0,0,0]),(1,[0,sign*5,0]),(2,[0,0,0])])}
 a[side+'_silk_tail1']={'rotation':keys([(0,[0,sign*-4,0]),(1,[0,sign*4,0]),(2,[0,sign*-4,0])])}
a=anim('walk',1,True);living(a);folds(a,[(0,2),(.5,8),(1,2)])
# Two longitudinal runners slide along the ground, rather than posing as animal legs.
for side,sign in [('left',1),('right',-1)]:a[side+'_bamboo_skid']={'position':keys([(0,[0,0,sign*1.5]),(.5,[0,0,sign*-1.5]),(1,[0,0,sign*1.5])])}
a['ink_case']={'rotation':keys([(0,[0,-3,0]),(.5,[0,3,0]),(1,[0,-3,0])])}
a=anim('stealth',5.55);living(a);a['root']={'scale':keys([(0,[1,1,1]),(.2,[1,.25,1]),(3.9,[1,.25,1]),(4,[1,1,1]),(5.55,[1,1,1])])};folds(a,[(0,0),(.2,20),(3.9,20),(4,0),(5.55,0)]);blades(a,[(0,0),(3.9,0),(4,180),(4.3,180),(4.7,0),(5.55,0)])
a=anim('field',4.6);living(a);folds(a,[(0,0),(.5,15),(2.8,15),(3.2,0),(4.6,0)])
blades(a,[(0,0),(.5,180),(2.8,180),(3.2,0),(4.6,0)])
for side,sign in [('left',1),('right',-1)]:a[side+'_dagger_carriage']['rotation']=keys([(0,[0,0,0]),(.5,[0,sign*8,0]),(.75,[0,sign*-8,0]),(1.35,[0,sign*8,0]),(1.95,[0,sign*-8,0]),(2.55,[0,sign*8,0]),(3.2,[0,0,0]),(4.6,[0,0,0])])
a=anim('mist',2.95);living(a);folds(a,[(0,0),(.15,35),(.3,20),(.4,0),(2.95,0)])
a['ink_heart']={'scale':keys([(0,[1,1,1]),(.3,[1.15,1.15,1.15]),(.4,[1,1,1]),(2.95,[1,1,1])])}
a=anim('hurt',.35);living(a);a['ink_case']={'rotation':keys([(0,[0,0,0]),(.1,[0,0,7]),(.35,[0,0,0])])}
a=anim('death',3);a['root']={'scale':keys([(0,[1,1,1]),(.6,[1,.18,1]),(2,[1.2,.18,1.2]),(2.9,[0,0,0]),(3,[0,0,0])])};a['death_wash']={'scale':keys([(0,[0,0,0]),(.7,[0,0,0]),(1,[1,1,1]),(2.3,[1.3,1,1.3]),(3,[0,0,0])])};folds(a,[(0,0),(.6,0),(3,0)])
geo(ID,bones,4.8,2.2,[0,.6,0]);write(A/'animations/blueprint/elite'/f'{ID}.animation.json',{'format_version':'1.8.0','animations':anims})
tex=Image.new('RGB',(16,16),COLORS['white']);d=ImageDraw.Draw(tex)
for key in ('ink','fold','bamboo'):
 x,y=UV[key];d.rectangle((x-1,y-1,x+4,y+4),fill=COLORS[key])
tex.save(A/'textures/entity/blueprint/elite'/f'{ID}.png')
print(ID,len(bones),'bones',sum(len(b.get('cubes',[])) for b in bones),'cuboids',len(anims),'clips')
bones=[];spike=bone('root');cube(spike,(-1.5,0,-1.5),(3,24,3),'ink');cube(spike,(-2,4,-2),(4,2,4),'bamboo');cube(spike,(-2,14,-2),(4,2,4),'bamboo');cube(spike,(-1,24,-1),(2,2,2),'white')
geo(SPIKE,bones,.4,1.7,[0,.8,0]);write(A/'animations/blueprint/elite'/f'{SPIKE}.animation.json',{'format_version':'1.8.0','animations':{'animation.'+SPIKE+'.idle':{'loop':True,'animation_length':1,'bones':{'root':{'scale':keys([(0,[1,1,1]),(.5,[1,1.02,1]),(1,[1,1,1])])}}}}})
PELLET='assassin_finite_ink_cloud';bones=[];pellet=bone('root')
cube(pellet,(-3,1,-2),(6,4,4),'ink');cube(pellet,(-2,0,-1),(4,1,2),'fold');cube(pellet,(-2,5,-1),(4,1,2),'ink')
geo(PELLET,bones,.6,.5,[0,.2,0]);write(A/'animations/blueprint/elite'/f'{PELLET}.animation.json',{'format_version':'1.8.0','animations':{'animation.'+PELLET+'.idle':{'loop':True,'animation_length':1,'bones':{'root':{'rotation':keys([(0,[0,0,0]),(1,[0,360,0])])}}}}})
items=('ink_crystal_shard','waterproof_ink_silk','hollow_ink_bamboo')
for name in items:
 im=Image.new('RGB',(16,16),COLORS['white']);d=ImageDraw.Draw(im)
 if name.endswith('shard'):
  d.rectangle((6,2,9,3),fill=COLORS['ink']);d.rectangle((4,4,11,11),fill=COLORS['ink']);d.rectangle((6,12,9,13),fill=COLORS['ink']);d.rectangle((4,6,5,9),fill=COLORS['fold']);d.rectangle((8,10,9,11),fill=COLORS['bamboo'])
 elif name.endswith('silk'):
  d.rectangle((4,2,11,13),fill=COLORS['fold']);d.rectangle((2,4,3,11),fill=COLORS['bamboo']);d.rectangle((12,4,13,11),fill=COLORS['bamboo']);d.rectangle((6,4,9,9),fill=COLORS['ink'])
 else:
  d.rectangle((6,2,9,13),fill=COLORS['bamboo']);d.rectangle((4,4,11,5),fill=COLORS['ink']);d.rectangle((4,10,11,11),fill=COLORS['ink']);d.rectangle((6,6,7,9),fill=COLORS['fold'])
 im.save(A/'textures/item'/f'{name}.png');write(A/'models/item'/f'{name}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+name}})
write(A/'models/item'/f'{ID}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
write(DATA/'loot_tables/entities'/f'{ID}.json',{'type':'minecraft:entity','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'dynasty:'+n}]} for n in items]})
write(DATA/'loot_tables/entities'/f'{SPIKE}.json',{'type':'minecraft:entity','pools':[]})
write(DATA/'advancements/blueprint'/f'kill_{ID}.json',{'criteria':{'kill':{'trigger':'minecraft:player_killed_entity','conditions':{'entity':{'type':'dynasty:'+ID}}}}})
write(DATA/'recipes/blueprint/ink_crystal_dye.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':'dynasty:ink_crystal_shard'}],'result':{'item':'minecraft:black_dye','count':2}})
write(DATA/'recipes/blueprint/ink_silk_string.json',{'type':'minecraft:crafting_shapeless','ingredients':[{'item':'dynasty:waterproof_ink_silk'}],'result':{'item':'minecraft:string','count':4}})

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('mojia_jueying_cike')

# Original MC creature shape correction, after the material export.
import runpy as _creature33_runpy
_creature33_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v33/refine.py"))["finish"]('mojia_jueying_cike')

# Connected anatomy correction; final authoritative export (V34).
import runpy as _creature34_runpy
_creature34_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v34/refine.py"))["finish"]('mojia_jueying_cike')

# Continuous anatomical masses and coherent pigmentation (V35).
_creature34_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/creature-mc-v35/refine.py"))["finish"]('mojia_jueying_cike')
