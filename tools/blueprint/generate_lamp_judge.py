#!/usr/bin/env python3
"""Original animated judicial iron ledger and inkstone: no humanoid under its robe.

Inspected Twilight1.20.x DeathTomeModel create/prepareMobModel: actual cover/page hinges.
Borrow only the working parts of an object as its skeleton. All geometry/UV/art/keys original.
"""
from pathlib import Path
import ast,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'src/main/resources/assets/dynasty'
ID='qingdeng_panguan_guichai'
COLORS={'ink':'#202728','cover':'#49354E','jade':'#7AA79B','white':'#FFFFFF'}
UV={'ink':[3,3],'cover':[9,3],'jade':[3,9],'white':[9,9]};bones=[]
helper=(ROOT/'tools/blueprint/generate_tide_yasha.py').read_text()
for n in ast.parse(helper).body:
 if isinstance(n,ast.FunctionDef) and n.name in ('bone','cube','geo','write','keys'):exec(ast.get_source_segment(helper,n),globals())
def keys(rows):return {str(float(round(t,4))):v for t,v in rows}
bone('root')
basin=bone('inkstone','root');cube(basin,(-13,0,-9),(26,4,20),'ink')
cube(basin,(-12,3.8,-8),(24,2.2,3),'jade');cube(basin,(-12,3.8,8),(24,2.2,3),'jade')
cube(basin,(-13,3.8,-5),(3,2.2,13),'jade');cube(basin,(10,3.8,-5),(3,2.2,13),'jade')
cube(basin,(-9.8,3,-4.8),(19.6,2,12.6),'cover')
spine=bone('iron_spine','root',(0,15,3));cube(spine,(-2.8,4,0),(5.6,25,6),'ink')
cube(spine,(-4,27,-1),(8,8.2,8),'jade')
cube(spine,(-5.7,11.5,-2),(11.4,5,10),'jade')
for side,sign in (('left',1),('right',-1)):
 cover=bone(side+'_ledger','iron_spine',(sign*3,20,2))
 x=3 if sign>0 else -16
 cube(cover,(x,10,1),(13,23,4),'cover');cube(cover,(x,9,0),(13,3,6),'ink')
 cube(cover,(x,31,0),(13,3,6),'ink');cube(cover,(sign*15-2,11,-1.5),(4,21,8),'jade')
 pages=bone(side+'_pages',cover['name'],(sign*4,21,1))
 cube(pages,(4 if sign>0 else -14,13,-1),(10,17,3),'white')
 for y in (17,23,27):cube(pages,(5 if sign>0 else -13,y,-2),(8,2,2),'ink')
 ribbon=bone(side+'_seal_ribbon',cover['name'],(sign*12,12,4))
 cube(ribbon,(sign*12-2,6.3,3.4),(4,8,2.2),'cover');cube(ribbon,(sign*12-2.2,6.3,5.3),(4.4,3,2.3),'jade')
eye=bone('judicial_eye','iron_spine',(0,24,-5))
cube(eye,(-5.5,19,-7),(11,11,5),'ink');cube(eye,(-4,21,-10),(8,7,5),'white')
cube(eye,(-2,23,-11),(4,3,2),'ink')
lamp=bone('green_lamp','iron_spine',(-10,32,3));cube(lamp,(-13,30.6,0),(6,3.2,6),'ink')
cube(lamp,(-12,33.6,1),(4,1.6,4),'jade')
bridge=bone('brush_yoke','iron_spine',(4,18,4));cube(bridge,(2,15.6,1.7),(18,4.8,6.6),'ink')
cube(bridge,(15,14.5,0),(8,7,10),'jade')
joint=bone('brush_swivel','brush_yoke',(20,18,4));cube(joint,(15.5,17,2),(9,2,4),'ink')
brush=bone('judgment_brush','brush_swivel',(20,18,4))
cube(brush,(18,16,-10),(4,4,19),'ink')
tip=bone('broken_brush_tip','judgment_brush',(20,18,-10))
cube(tip,(18,16,-23),(4,4,13),'ink');cube(tip,(17,15,-24),(6,6,8),'jade')
cube(tip,(18,16,-29),(4,4,6),'white');cube(tip,(19,17,-33),(2,2,5),'ink')
# Six original page-butterflies are real folding pieces, visible only during death.
for i in range(6):
 p=bone('page_butterfly'+str(i),'root',((i-2.5)*4,23,1))
 for side,sign in (('left',1),('right',-1)):
  wing=bone(p['name']+'_'+side,p['name'],((i-2.5)*4,23,1))
  cube(wing,((i-2.5)*4+(0 if sign>0 else -5),22,0),(5,2,5),'ink')
  cube(wing,((i-2.5)*4+(1 if sign>0 else -4),23,-1),(3,2,3),'jade')
anims={}
def anim(name,length,loop=False):
 d={'animation_length':length,'bones':{}}
 if loop:d['loop']=True
 anims['animation.'+ID+'.'+name]=d;return d['bones']
def open_book(a,rows):
 for side,sign in (('left',1),('right',-1)):a[side+'_ledger']={'rotation':keys([(t,[0,sign*v,0]) for t,v in rows])}
a=anim('idle',2.4,True);open_book(a,[(0,8),(1.2,13),(2.4,8)])
a['judicial_eye']={'rotation':keys([(0,[0,-8,0]),(1.2,[0,8,0]),(2.4,[0,-8,0])])}
a=anim('walk',1.6,True);open_book(a,[(0,12),(.8,20),(1.6,12)])
a['iron_spine']={'position':keys([(0,[0,0,0]),(.4,[0,.7,0]),(.8,[0,0,0]),(1.2,[0,.7,0]),(1.6,[0,0,0])])}
a=anim('name',4.6);open_book(a,[(0,8),(.3,45),(1.8,45),(2,8),(4.6,8)])
a['brush_swivel']={'rotation':keys([(0,[0,0,0]),(.3,[0,-35,0]),(.6,[0,35,0]),(.9,[0,-25,0]),(1.2,[0,30,0]),(1.6,[0,0,0]),(4.6,[0,0,0])])}
a['judicial_eye']={'scale':keys([(0,[1,1,1]),(.6,[1.12,1.12,1.12]),(.65,[1,1,1]),(1.2,[1.12,1.12,1.12]),(1.25,[1,1,1]),(1.8,[1.12,1.12,1.12]),(2,[1,1,1]),(4.6,[1,1,1])])}
a=anim('strokes',4.2);open_book(a,[(0,8),(.5,25),(2.5,25),(3.2,8),(4.2,8)])
rows=[(0,[0,0,0]),(.3,[0,-30,0])]
for i,t in enumerate((.5,.9,1.3,1.7,2.1)):rows.extend([(t,[0,(i-2)*10,0]),(t+.15,[0,-30,0])])
rows.extend([(2.6,[0,0,0]),(4.2,[0,0,0])]);a['brush_swivel']={'rotation':keys(rows)}
a=anim('cage',10.6);open_book(a,[(0,8),(.6,90),(.8,90),(8.8,90),(9.5,8),(10.6,8)])
a['green_lamp']={'scale':keys([(0,[1,1,1]),(.8,[1.2,1,1.2]),(8.8,[1.2,1,1.2]),(10.6,[1,1,1])])}
a=anim('hurt',.4);a['judicial_eye']={'scale':keys([(0,[1,1,1]),(.1,[1,.5,1]),(.4,[1,1,1])])}
a=anim('death',4.2);open_book(a,[(0,8),(.4,110),(1.2,150),(4.2,150)])
a['iron_spine']={'scale':keys([(0,[1,1,1]),(.4,[1,1,1]),(1.1,[0,0,0]),(4.2,[0,0,0])]),'position':keys([(0,[0,0,0]),(.4,[0,0,0]),(1.1,[0,-15,0]),(4.2,[0,-15,0])])}
a['broken_brush_tip']={'rotation':keys([(0,[0,0,0]),(.3,[0,0,0]),(.8,[-35,0,30]),(1.1,[-35,0,30]),(4.2,[-35,0,30])])}
a['inkstone']={'scale':keys([(0,[1,1,1]),(1.2,[1.3,1,1.3]),(3,[1.3,1,1.3]),(4.2,[0,0,0])])}
for name,d in anims.items():
 for i in range(6):
  key='page_butterfly'+str(i)
  if name.endswith('.death'):
   d['bones'][key]={'scale':keys([(0,[0,0,0]),(.3,[0,0,0]),(.5,[1,1,1]),(2.8,[1,1,1]),(4.2,[0,0,0])]),
     'position':keys([(0,[0,0,0]),(.3,[0,0,0]),(2.8,[(i-2.5)*8,20-i*2,(-1 if i%2 else 1)*18]),(4.2,[(i-2.5)*8,24-i*2,(-1 if i%2 else 1)*22])])}
   for side,sign in (('left',1),('right',-1)):
    d['bones'][key+'_'+side]={'rotation':keys([(t,[0,0,sign*(55 if k%2 else -55)]) for k,t in enumerate((0,.3,.5,.7,.9,1.1,1.3,1.5,1.7,1.9,2.1,2.3,2.5,2.8,3.2,3.6,4.2))])}
  else:d['bones'][key]={'scale':[0,0,0]}
geo(ID,bones,6.6,4.4,[0,1.8,0]);write(A/'animations/blueprint/elite'/f'{ID}.animation.json',{'format_version':'1.8.0','animations':anims})
im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im)
for color,(x,y) in UV.items():d.rectangle((x,y,x+3,y+3),fill=COLORS[color])
p=A/'textures/entity/blueprint/elite'/f'{ID}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
write(A/'models/item'/f'{ID}_spawn_egg.json',{'parent':'minecraft:item/template_spawn_egg'})
for item in ('judge_iron_page','sealed_judge_ink'):
 icon=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(icon)
 if item=='judge_iron_page':
  d.rectangle((3,3,12,12),fill=COLORS['ink']);d.rectangle((5,3,10,10),fill=COLORS['cover']);d.rectangle((5,5,8,8),fill=COLORS['jade'])
 else:
  d.rectangle((6,3,9,6),fill=COLORS['ink']);d.rectangle((4,6,11,13),fill=COLORS['cover']);d.rectangle((6,8,9,11),fill=COLORS['jade'])
 icon.save(A/'textures/item'/f'{item}.png');write(A/'models/item'/f'{item}.json',{'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+item}})
main_count=(len(bones),sum(len(b.get('cubes',[])) for b in bones))
bones=[];b=bone('root');cube(b,(-4,8,-4),(8,72,8),'ink');cube(b,(-6,12,-6),(12,12,12),'jade');cube(b,(-3,2,-3),(6,8,6),'white');cube(b,(-1,0,-1),(2,3,2),'ink')
geo('judge_falling_pen',bones,1.2,5.2,[0,2.5,0]);write(A/'animations/blueprint/elite/judge_falling_pen.animation.json',{'format_version':'1.8.0','animations':{'animation.judge_falling_pen.idle':{'loop':True,'animation_length':1,'bones':{}}}})
bones=[];b=bone('root');cube(b,(-4,0,-88),(8,3,88),'ink');cube(b,(-3,3,-86),(6,2,84),'cover')
geo('judge_ink_stroke',bones,11.4,1,[0,.4,-2.75]);write(A/'animations/blueprint/elite/judge_ink_stroke.animation.json',{'format_version':'1.8.0','animations':{'animation.judge_ink_stroke.idle':{'loop':True,'animation_length':1,'bones':{}}}})
bones=[];bone('root')
for i,(x,z) in enumerate(((48,0),(0,48),(-48,0),(0,-48))):
 p=bone('cage_pillar'+str(i),'root',(x,0,z));cube(p,(x-7,0,z-7),(14,5,14),'ink');cube(p,(x-4,4,z-4),(8,39,8),'jade');cube(p,(x-6,42,z-6),(12,5,12),'cover');cube(p,(x-3,37,z-6),(6,4,3),'ink');cube(p,(x-1,38,z-7),(2,2,2),'white')
for i in range(32):
 angle=i*math.tau/32;x,z=48*math.cos(angle),48*math.sin(angle);p=bone('chain'+str(i),'root',(x,18,z))
 # Tangential links form a connected quarter arc between the four actual pillars.
 cube(p,(x-5.5,16,z-2),(11,4,4),'ink',rotation=(0,-math.degrees(angle)+90,0))
# The pillars and fixed arcs do not animate individually. Keep their cuboid pivots but
# collapse their unused bone transforms into one root; the cage has no server sub-AIs.
merged={'name':'root','pivot':[0,0,0],'cubes':[]}
for p in bones:
 for c in p.get('cubes',[]):
  if c.get('rotation'):c.setdefault('pivot',p['pivot'])
  merged['cubes'].append(c)
geo('judge_chain_cage',[merged],7.4,3.2,[0,1.4,0]);write(A/'animations/blueprint/elite/judge_chain_cage.animation.json',{'format_version':'1.8.0','animations':{'animation.judge_chain_cage.idle':{'loop':True,'animation_length':1,'bones':{}}}})
print('Exported original judicial ledger:',main_count,'seven clips and three independent spell resources; native pending.')

# Original component-directed cod1 creature atlas; preserve the approved rig.
import runpy as _creature_runpy
from pathlib import Path as _CreaturePath
_creature_runpy.run_path(str(_CreaturePath(__file__).resolve().parents[1]/"art/cod1-creatures-v32/paint.py"))["finish"]('qingdeng_panguan_guichai')
