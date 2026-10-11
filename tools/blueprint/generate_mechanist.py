"""Original cuboid rigs and hard pixel UV panels; no existing art is overwritten."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

BASE=Path('src/main/resources/assets/dynasty')
ID='qianji_bailian_yanshi'
palette={'iron':'#445457','copper':'#AA783D','gold':'#D5B263','cloth':'#344342',
         'skin':'#AE9675','thread':'#8DDDE1','dark':'#242C2D','leather':'#72533A'}
atlas=Image.new('RGBA',(64,64),'#242C2D');draw=ImageDraw.Draw(atlas)
slots={name:(i*8,0) for i,name in enumerate(palette)}
for name,(x,y) in slots.items():
    draw.rectangle((x,y,x+7,y+7),fill=palette[name])
    if name not in ('thread','skin','dark'):
        draw.rectangle((x,y,x+7,y+1),fill=palette['dark'])
        draw.rectangle((x+2,y+4,x+5,y+5),fill=palette['gold'] if name=='copper' else palette[name])
texture=BASE/'textures/entity/blueprint'/f'{ID}.png';texture.parent.mkdir(parents=True,exist_ok=True);atlas.save(texture)

def cube(origin,size,material='iron'):
    x,y=slots[material]
    return {'origin':origin,'size':size,'uv':{f:{'uv':[x+1,y+2],'uv_size':[6,6]} for f in ('north','south','east','west','up','down')}}
def make_rig(id,bounds):
    return {'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+id,'texture_width':64,'texture_height':64,'visible_bounds_width':bounds[0],'visible_bounds_height':bounds[1],'visible_bounds_offset':[0,bounds[2],0]},'bones':[]}]}
rig=make_rig(ID,(5,4,1.4));bones=rig['minecraft:geometry'][0]['bones']
def bone(name,parent,pivot,cubes=(),rotation=None):
    b={'name':name,'pivot':pivot,'cubes':list(cubes)}
    if parent:b['parent']=parent
    if rotation:b['rotation']=rotation
    bones.append(b)
bone('root',None,[0,0,0]);bone('pelvis','root',[0,12.5,0],[cube([-3.5,12,-2.2],[7,3,4.4],'leather')])
bone('waist','pelvis',[0,15,0],[cube([-2.6,15,-1.9],[5.2,3,3.8],'iron')])
bone('chest','waist',[0,18,0],[cube([-4.2,18,-2.8],[8.4,7.4,5.6],'cloth')])
bone('apron','pelvis',[0,15,-2.3],[cube([-3.8,8,-2.8],[7.6,7,.7],'leather')])
bone('chest_mirror','chest',[0,21.4,-3],[cube([-2,20,-3.3],[4,4,.6],'copper'),cube([-1,21,-3.6],[2,2,.3],'thread')])
bone('head','chest',[0,25.4,0],[cube([-2.8,25.4,-2.4],[5.6,5,4.8],'skin'),cube([0,26,-2.7],[3,4.4,.5],'iron')])
bone('left_monocle','head',[1.5,28,-2.9],[cube([.3,27,-3],[2.7,2.7,.6],'copper'),cube([1,27.7,-3.4],[1.4,1.3,.4],'thread')])
bone('nose','head',[0,27.7,-2.4],[cube([-.6,26.8,-3.4],[1.2,1.6,1],'skin')])
bone('right_eye','head',[-1.6,28,-2.4],[cube([-2,27.8,-2.7],[1,.5,.4],'dark')])
bone('hair','head',[0,30,0],[cube([-3,29.6,-2.4],[6,1,4.8],'dark'),cube([-2,27,2.1],[4,3.5,1.1],'dark')])
bone('backpack','chest',[0,19,3],[cube([-6,12,2.8],[12,15,6.2],'copper'),cube([-6.2,15,4],[.7,9,3],'gold'),cube([5.5,15,4],[.7,9,3],'gold')])
bone('box_lid','backpack',[0,26.6,8.6],[cube([-6.3,26.3,2.5],[12.6,1.2,7],'iron')])
bone('box_valve','backpack',[0,20,9],[cube([-2,18,9],[4,4,.7],'gold'),cube([-.6,19.4,9.6],[1.2,1.2,.5],'dark')])
for side,sign in [('left',1),('right',-1)]:
    x=sign*2
    bone(side+'_thigh','pelvis',[x,12.5,0],[cube([x-1.5,6,-1.7],[3,6.5,3.4],'cloth')])
    bone(side+'_knee',side+'_thigh',[x,6,0],[cube([x-1.4,1.4,-1.5],[2.8,4.6,3],'iron' if sign==1 else 'cloth')])
    bone(side+'_boot',side+'_knee',[x,1.5,0],[cube([x-1.6,0,-2.5],[3.2,1.7,4.4],'leather')])
    x=sign*5.4
    bone(side+'_shoulder','chest',[x,24,0],[cube([x-1.3,19,-1.6],[2.6,5,3.2],'iron' if sign==1 else 'cloth')])
    bone(side+'_elbow',side+'_shoulder',[x,19,0],[cube([x-1.2,15,-1.3],[2.4,4,2.6],'copper' if sign==1 else 'skin')])
    bone(side+'_hand',side+'_elbow',[x,15,0],[cube([x-1.3,13.5,-1.2],[2.6,1.8,2.4],'skin')])
    for i in range(5):
        fx=x-1+i*.5
        finger=side+'_finger_'+str(i);thread=side+'_thread_'+str(i)
        bone(finger,side+'_hand',[fx,13.7,-.8],[cube([fx-.16,12.5,-1],[.32,1.5,.45],'copper' if sign==1 else 'skin')])
        bone(thread,finger,[fx,12.5,-1],[cube([fx-.06,4,-1.06],[.12,8.5,.12],'thread')])
for n in range(4):
    sign=1 if n%2==0 else -1;y=18.5 if n<2 else 12.5;x=sign*4
    name='aux_'+str(n)
    bone(name,'waist',[x,y,5.5],[cube([x if sign>0 else x-5.5,y-.6,4.9],[5.5,1.2,1.2],'copper'),cube([x-1,y-1,4.6],[2,2,1.8],'gold')],[0,0,sign*(15 if n<2 else -15)])
    elbow=name+'_elbow';bone(elbow,name,[sign*9.5,y,5.5],[cube([sign*9.5-.7,y-4.2,4.8],[1.4,4.2,1.4],'iron'),cube([sign*9.5-1.2,y-.8,4.7],[2.4,1.6,1.6],'gold')])
    bone(name+'_claw',elbow,[sign*9.5,y-4,5.5],[cube([sign*9.5-1,y-5,4.9],[.6,1.8,1.2],'gold'),cube([sign*9.5+.4,y-5,4.9],[.6,1.8,1.2],'gold')])

def save_rig(id,data):
    p=BASE/'geo/blueprint/elite'/f'{id}.geo.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
save_rig(ID,rig)
animations={}
def rot(points):return {'rotation':{str(t):v for t,v in points}}
def anim(name,length,transforms,loop=False):animations['animation.'+ID+'.'+name]={'loop':loop,'animation_length':length,'bones':transforms}
anim('idle',2,{'chest':rot([(0,[0,0,-1]),(1,[0,0,1]),(2,[0,0,-1])]),'box_valve':rot([(0,[0,0,0]),(2,[0,0,360])])},True)
anim('walk',1,{**{s+'_thigh':rot([(0,[v*25,0,0]),(.5,[-v*25,0,0]),(1,[v*25,0,0])]) for s,v in [('left',1),('right',-1)]},'chest':rot([(0,[7,0,-3]),(.5,[7,0,3]),(1,[7,0,-3])])},True)
anim('hurt',.4,{'chest':rot([(0,[0,0,0]),(.12,[-15,0,7]),(.4,[0,0,0])])})
net={s+'_shoulder':rot([(0,[0,0,0]),(.35,[60,0,-sign*25]),(.7,[70,0,-sign*30]),(.85,[105,0,sign*15]),(2.1,[0,0,0])]) for s,sign in [('left',1),('right',-1)]}
for s in ['left','right']:
    net[s+'_elbow']=rot([(0,[0,0,0]),(.4,[70,0,0]),(.7,[90,0,0]),(.85,[15,0,0]),(2.1,[0,0,0])])
    for i in range(5):net[s+'_thread_'+str(i)]={'rotation':{'0':[0,0,0],'.7':[25,0,0],'.85':[85,0,0],'1.2':[85,0,0],'2.1':[0,0,0]},'scale':{'0':[1,1,1],'.7':[1,.7,1],'.85':[1,3,1],'1.2':[1,2,1],'2.1':[1,1,1]}}
anim('net',2.1,net)
wheels={'box_lid':rot([(0,[0,0,0]),(.4,[-65,0,0]),(.5,[-75,0,0]),(1.2,[-45,0,0]),(3.75,[0,0,0])])}
for n in range(4):wheels['aux_'+str(n)]=rot([(0,[0,0,0]),(.5,[0,35*(-1 if n%2 else 1),65*(-1 if n%2 else 1)]),(.7,[0,-55*(-1 if n%2 else 1),-35*(-1 if n%2 else 1)]),(3.75,[0,0,0])])
anim('wheels',3.75,wheels)
anim('spiders',2.8,{'root':{'position':{'0':[0,0,0],'.7':[0,-4,0],'1':[0,-4,0],'1.2':[0,0,0],'2.8':[0,0,0]}},'chest':rot([(0,[0,0,0]),(.7,[25,0,0]),(1,[-15,0,0]),(2.8,[0,0,0])]),'box_lid':rot([(0,[0,0,0]),(.7,[-90,0,0]),(1.2,[-90,0,0]),(2.8,[0,0,0])])})
death={'root':{'position':{'0':[0,0,0],'1.3':[0,2,0],'2':[0,3.3,0],'3':[0,3.3,0]},'rotation':{'0':[0,0,0],'1.4':[20,0,0],'2':[80,0,0],'3':[80,0,0]}},'chest_mirror':{'scale':{'0':[1,1,1],'.7':[1,1,1],'1.1':[0,0,0]}},'box_lid':rot([(0,[0,0,0]),(.7,[-100,0,0]),(1,[-150,0,0]),(3,[-150,0,0])]),'backpack':{'scale':{'0':[1,1,1],'.8':[1.15,1.15,1.15],'1.2':[.6,.5,.8],'3':[.6,.5,.8]}}}
for n in range(4):death['aux_'+str(n)]=rot([(0,[0,0,0]),(.3,[30,50,70]),(.6,[-40,-40,-60]),(.9,[60,60,90]),(1.4,[0,0,(-1 if n%2 else 1)*60]),(3,[0,0,(-1 if n%2 else 1)*60])])
anim('death',3,death)
def save_anims(id,anims):
    p=BASE/'animations/blueprint/elite'/f'{id}.animation.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'format_version':'1.8.0','animations':anims},indent=2)+'\n')
save_anims(ID,animations)

SID='yanshi_clockwork_spider';rig=make_rig(SID,(2,2,.3));bones=rig['minecraft:geometry'][0]['bones']
bone('root',None,[0,0,0]);bone('boiler','root',[0,3,0],[cube([-2.5,2,-2.5],[5,3,5],'copper'),cube([-1.4,4.5,-1.4],[2.8,1,2.8],'thread')])
for i in range(8):
    side=1 if i%2==0 else -1;z=-2.4+(i//2)*1.6
    bone('leg_'+str(i),'root',[side*2.2,3,z],[cube([side*2.2 if side>0 else -4.4,2.5,z-.3],[2.2,.6,.6],'iron')],[0,side*(i//2-1.5)*15,side*15])
    bone('leg_'+str(i)+'_tip','leg_'+str(i),[side*4.4,2.7,z],[cube([side*4.4-.3,0,z-.3],[.6,2.7,.6],'gold')])
save_rig(SID,rig)
walk={};fuse={'boiler':{'scale':{'0':[1,1,1],'.15':[1.16,1.2,1.16],'.3':[1,1,1]}}}
for i in range(8):walk['leg_'+str(i)]=rot([(0,[0,(1 if i%2 else -1)*20,0]),(.2,[0,(-1 if i%2 else 1)*20,0]),(.4,[0,(1 if i%2 else -1)*20,0])])
save_anims(SID,{'animation.'+SID+'.walk':{'loop':True,'animation_length':.4,'bones':walk},'animation.'+SID+'.fuse':{'loop':True,'animation_length':.3,'bones':fuse}})
print(f'{ID}: original 64px atlas, {len(animations)} clips; small spider 8 two-segment legs')
