"""Original code-native eight-face bird rig; no bitmap or legacy atlas is modified."""
import copy
import json
from pathlib import Path

BASE=Path('src/main/resources/assets/dynasty')
ID='guiche_jiushouniao'
sample=json.loads((BASE/'geo/blueprint/youdeng_guimianfu.geo.json').read_text())['minecraft:geometry'][0]['bones']
dark=sample[1]['cubes'][0]['uv']; pale=sample[2]['cubes'][0]['uv']; black=sample[2]['cubes'][1]['uv']
bones=[]
def cube(at,size,uv):return dict(origin=at,size=size,uv=copy.deepcopy(uv))
def bone(name,parent,pivot,cubes=(),rotation=None):
    value=dict(name=name,pivot=pivot,cubes=list(cubes))
    if parent:value['parent']=parent
    if rotation:value['rotation']=rotation
    bones.append(value)
bone('root',None,[0,0,0])
bone('body','root',[0,14,0],[cube([-8,6,-6],[16,15,18],dark)])
bone('tail','body',[0,13,10],[cube([-4,10,10],[8,2,20],dark),cube([-6,9,26],[12,1,8],pale)],[15,0,0])
for name,sign in [('left',1),('right',-1)]:
    x0=8 if sign==1 else -23
    bone(name+'_wing','body',[sign*8,19,0],[cube([x0,17,-3],[15,3,12],dark)])
    x1=23 if sign==1 else -39
    bone(name+'_wing_tip',name+'_wing',[sign*23,19,0],[cube([x1,17.5,-2],[16,2,9],dark)])
    for n in range(5):
        x=sign*(17+n*4)-1.2
        bone(f'{name}_feather_{n}',name+'_wing_tip',[x,18,3],[cube([x,17,3],[2.4,1.1,15-n],dark)],[0,sign*(10+n*4),0])
    bone(name+'_leg','body',[sign*5,8,2],[cube([sign*5-1,1,1],[2,7,2],pale)])
    for n in range(3):bone(f'{name}_claw_{n}',name+'_leg',[sign*5+n-1,1,1],[cube([sign*5+n-1.4,0,-3],[.8,1,5],black)])
bone('central_stump','body',[0,20,-5],[cube([-1.7,20,-6.7],[3.4,6,3.4],pale),cube([-2,26,-7],[4,.7,4],dark)])
for n,fan in enumerate([-50,-35,-20,-7,7,20,35,50]):
    x=(n-3.5)*1.5
    bone(f'neck_{n}_base','body',[x,19,-5],[cube([x-1,19,-6],[2,6,2],pale)],[12,0,fan])
    bone(f'neck_{n}_middle',f'neck_{n}_base',[x,25,-5],[cube([x-1,25,-6],[2,6,2],pale)])
    bone(f'neck_{n}_tip',f'neck_{n}_middle',[x,31,-5],[cube([x-1,31,-6],[2,5,2],pale)])
    bone(f'face_{n}',f'neck_{n}_tip',[x,36,-5],[cube([x-2.2,35,-7.4],[4.4,5,4.8],pale),cube([x-1.4,37.4,-7.8],[.8,.7,.4],black),cube([x+.6,37.4,-7.8],[.8,.7,.4],black)])
    bone(f'beak_{n}',f'face_{n}',[x,35.5,-7.4],[cube([x-.8,35.3,-11.4],[1.6,1.2,4],dark)])
    bone(f'jaw_{n}',f'face_{n}',[x,35.2,-7.4],[cube([x-.6,34.7,-10.8],[1.2,.6,3.4],dark)])
geometry={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+ID,'texture_width':128,'texture_height':128,'visible_bounds_width':9,'visible_bounds_height':8,'visible_bounds_offset':[0,2,0]},'bones':bones}]}
target=BASE/f'geo/blueprint/elite/{ID}.geo.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(geometry,indent=2)+'\n')
animations={}
def rot(points):return {'rotation':{str(t):v for t,v in points}}
def anim(name,length,transforms,loop=False):animations['animation.'+ID+'.'+name]=dict(loop=loop,animation_length=length,bones=transforms)
fly={'body':{'position':{'0':[0,0,0],'.6':[0,1.4,0],'1.2':[0,0,0]}},'tail':rot([(0,[4,0,0]),(.6,[-4,0,0]),(1.2,[4,0,0])])}
for side,sign in [('left',1),('right',-1)]:fly[side+'_wing']=rot([(0,[0,0,sign*22]),(.6,[0,0,-sign*18]),(1.2,[0,0,sign*22])])
for n in range(8):fly[f'neck_{n}_middle']=rot([(0,[0,-3,0]),(.6,[0,3,0]),(1.2,[0,-3,0])])
anim('fly',1.2,fly,True)
peck={'body':{'position':{'0':[0,0,0],'.6':[0,0,0],'.8':[0,-6,0],'3.7':[0,-6,0],'4.85':[0,0,0]}}}
for side,sign in [('left',1),('right',-1)]:peck[side+'_wing']=rot([(0,[0,0,0]),(.6,[0,0,sign*65]),(3.7,[0,0,sign*65]),(4.85,[0,0,0])])
for n in range(8):
    points=[(0,[0,0,0]),(.6,[25,0,0])]
    for strike in [n,n+8]:
        t=.6+strike*.2;points.extend([(t,[25,0,0]),(t+.1,[140,0,0]),(t+.2,[25,0,0])])
    points.append((4.85,[0,0,0]));peck[f'neck_{n}_base']=rot(sorted(points))
anim('peck',4.85,peck)
bomb={f'neck_{n}_base':rot([(0,[0,0,0]),(.8,[-35,0,0]),(1,[25,0,0]),(2.55,[0,0,0])]) for n in range(8)}
for n in range(8):bomb[f'jaw_{n}']=rot([(0,[0,0,0]),(.7,[35,0,0]),(1.1,[35,0,0]),(2.55,[0,0,0])])
bomb['central_stump']={'scale':{'0':[1,1,1],'.8':[1.4,1.1,1.4],'1.1':[1,1,1]}}
anim('bomb',2.55,bomb)
dive={'body':rot([(0,[0,0,0]),(1.2,[40,0,0]),(2.7,[40,0,0]),(3.7,[0,0,0]),(5.7,[0,0,0])])}
for side,sign in [('left',1),('right',-1)]:dive[side+'_wing']=rot([(0,[0,0,0]),(1.2,[0,0,sign*78]),(2.7,[0,0,sign*78]),(3.7,[0,0,0]),(5.7,[0,0,0])]);dive[side+'_leg']=rot([(0,[0,0,0]),(1.2,[45,0,0]),(3.7,[-25,0,0]),(5.7,[0,0,0])])
anim('dive',5.7,dive)
anim('hurt',.35,{'body':rot([(0,[0,0,0]),(.1,[-15,0,10]),(.35,[0,0,0])])})
anim('stunned',2,{'body':rot([(0,[0,0,12]),(.5,[0,0,-12]),(1,[0,0,12]),(2,[0,0,-12])])},True)
death={'body':rot([(0,[0,0,0]),(1.4,[0,25,25]),(2.5,[70,40,60]),(5,[85,40,65])])}
for n in range(8):death[f'neck_{n}_base']=rot([(0,[0,0,0]),(.5,[30,n%2*30,0]),(1.5,[-30,-n%2*30,0]),(3,[90,0,0]),(5,[90,0,0])])
for side,sign in [('left',1),('right',-1)]:death[side+'_wing']=rot([(0,[0,0,0]),(1,[0,0,sign*60]),(2,[0,0,-sign*20]),(5,[0,0,-sign*20])])
anim('death',5,death)
target=BASE/f'animations/blueprint/elite/{ID}.animation.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(dict(format_version='1.8.0',animations=animations),indent=2)+'\n')
print(f'Generated {ID}: {len(bones)} bones and {len(animations)} animations')
