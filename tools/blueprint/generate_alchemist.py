#!/usr/bin/env python3
"""Original hollow robe and offset furnace; only emits the alchemist's own assets."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/'src/main/resources/assets/dynasty'
ID='yinyang_liandan_fangshi'
COLORS={'dark':'#28242B','copper':'#B66D35','cold':'#63BAC7','white':'#FFFFFF'}
UV={'dark':[2,2],'copper':[10,2],'cold':[2,10],'white':[10,10]}
bones=[]
def bone(name,parent=None,pivot=(0,0,0),rotation=None):
 b={'name':name,'pivot':list(pivot)}
 if parent:b['parent']=parent
 if rotation:b['rotation']=list(rotation)
 bones.append(b);return b
def cube(b,at,size,color='dark',rotation=None):
 c={'origin':list(at),'size':list(size),'uv':{f:{'uv':UV[color],'uv_size':[4,4]} for f in ('north','south','east','west','up','down')}}
 if rotation:c.update(pivot=b['pivot'],rotation=list(rotation))
 b.setdefault('cubes',[]).append(c)
def keys(data):return {str(t):v for t,v in data}
def geo(id,model,width,height):
 p=A/'geo/blueprint/elite'/f'{id}.geo.json';p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps({'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+id,'texture_width':16,'texture_height':16,'visible_bounds_width':width,'visible_bounds_height':height,'visible_bounds_offset':[0,1,0]},'bones':model}]},indent=2)+'\n')
def animation(id,data):
 p=A/'animations/blueprint/elite'/f'{id}.animation.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'format_version':'1.8.0','animations':data},indent=2)+'\n')
root=bone('root',pivot=(0,12,0))
waist=bone('waist','root',(0,14,0));cube(waist,(-3,12,-2),(6,5,4));cube(waist,(-4,14,-3),(8,2,6),'copper')
chest=bone('chest','waist',(0,17,0));cube(chest,(-4,16,-3),(8,7,6));cube(chest,(-2,17,-4),(4,4,2),'white')
collar=bone('collar','chest',(0,22,0));cube(collar,(-6,21,-4),(12,3,8),'copper');cube(collar,(-5,22,-3),(10,3,6));cube(collar,(-6,23,-5),(4,3,2),'white',rotation=(0,0,-18));cube(collar,(2,23,-5),(4,3,2),'white',rotation=(0,0,18))
neck=bone('neck','chest',(0,24,0));cube(neck,(-1.5,24,-1.5),(3,2,3),'copper')
mask=bone('mask','neck',(0,27,0));cube(mask,(-2.5,25,-3),(5,5,5),'white');cube(mask,(-2,27,-3.5),(4,2,1));cube(mask,(-1,25,-3.5),(2,2,1),'copper')
crown=bone('lotus_crown','mask',(0,30,0));cube(crown,(-4,29,-3),(8,2,6),'copper');cube(crown,(-3,31,-2),(2,2,4),'copper');cube(crown,(1,30,-2),(2,2,4),'copper');cube(crown,(-1,31,-1),(2,2,2),'cold')
back=bone('back_mantle','chest',(0,22,3));cube(back,(-7,11,3),(14,12,3));cube(back,(-6,21,5),(12,2,2),'white')
skirt=bone('back_skirt','waist',(0,14,3));cube(skirt,(-6,10,3),(12,4,3));cube(skirt,(-9,6,3),(18,4,3));cube(skirt,(-10,2,3),(20,4,3));cube(skirt,(-10,2,6),(20,2,2),'copper')
# Separated wide panels keep an open centre: there are no hidden trouser legs.
for side,s in (('left',1),('right',-1)):
 panel=bone(side+'_robe','waist',(s*4,14,0),(0,0,-s*10));cube(panel,(4 if s>0 else -10,4,-3),(6,11,6));cube(panel,(5 if s>0 else -9,3,-4),(4,3,8),'copper')
 tail=bone(side+'_hem',panel['name'],(s*7,5,0));cube(tail,(5 if s>0 else -10,1,-4),(5,5,8))
 upper=bone(side+'_upper_arm','chest',(s*5,21,0),(0,0,-s*28));cube(upper,(5 if s>0 else -9,16,-2),(4,6,4),'copper')
 sleeve=bone(side+'_sleeve',upper['name'],(s*7,17,0));cube(sleeve,(4 if s>0 else -11,12,-4),(7,7,8));cube(sleeve,(4 if s>0 else -11,12,-5),(7,2,10),'white')
 fore=bone(side+'_forearm',sleeve['name'],(s*7,14,0),(55,0,0));cube(fore,(5 if s>0 else -9,10,-2),(4,5,4),'copper')
 hand=bone(side+'_hand',fore['name'],(s*7,10,0));cube(hand,(5 if s>0 else -9,8,-2),(4,3,4),'white')
front=bone('front_tabard','waist',(0,14,-3));cube(front,(-4,9,-5),(8,6,2),'white');cube(front,(-3,5,-5),(6,4,2),'white');cube(front,(-3,3,-5),(6,3,2),'copper')
furnace=bone('furnace','root',(13,15,-3));cube(furnace,(8,10,-8),(10,2,10),'copper')
for at,size in [((8,12,-8),(2,5,10)),((16,12,-8),(2,5,10)),((10,12,-8),(6,5,2)),((10,12,0),(6,5,2))]:cube(furnace,at,size,'copper')
cube(furnace,(10,16,-6),(6,2,6));cube(furnace,(12,18,-4),(2,2,2),'copper')
for i,(x,z) in enumerate(((9,-7),(15,-7),(12,0))):
 leg=bone(f'furnace_leg{i}','furnace',(x+1,11,z+1));cube(leg,(x,6,z),(2,5,2),'copper')
warm=bone('warm_flame','furnace',(11,18,-3));cube(warm,(10,17,-4),(3,5,3),'copper');cube(warm,(11,22,-3),(2,2,2),'white')
cold=bone('cold_flame','furnace',(15,18,-3));cube(cold,(14,17,-4),(3,5,3),'cold');cube(cold,(14,22,-3),(2,2,2),'white')
whisk=bone('whisk','right_hand',(-7,9,0));cube(whisk,(-8,6,-1),(2,9,2),'copper');cube(whisk,(-9,4,-2),(4,3,4),'white')
for i,x in enumerate((-10,-8,-6)):
 strand=bone(f'whisk_tassel{i}','whisk',(x+1,4,0),(0,0,(i-1)*16));cube(strand,(x,-1-i,-1),(2,5+i,2),'white')
for i in range(3):
 pill=bone(f'gold{i}','root',(10+i*3,20,-8));cube(pill,(9+i*3,19,-9),(2,2,2),'copper')
anims={}
def anim(name,length,loop=False):
 d={'animation_length':length,'bones':{}}
 if loop:d['loop']=True
 anims['animation.'+ID+'.'+name]=d;return d['bones']
a=anim('idle',2,True);a['furnace']={'position':keys([(0,[0,0,0]),(1,[0,1,0]),(2,[0,0,0])]),'rotation':keys([(0,[0,-8,0]),(1,[0,8,0]),(2,[0,-8,0])])};a['back_mantle']={'rotation':keys([(0,[3,0,0]),(1,[-3,0,0]),(2,[3,0,0])])}
for name in ('warm_flame','cold_flame'):a[name]={'scale':keys([(0,[1,1,1]),(1,[1,1.25,1]),(2,[1,1,1])])}
a=anim('walk',1,True);a['waist']={'position':keys([(0,[0,0,0]),(.5,[0,1,0]),(1,[0,0,0])]),'rotation':keys([(0,[0,-5,0]),(.5,[0,5,0]),(1,[0,-5,0])])}
for side,s in (('left',1),('right',-1)):
 a[side+'_robe']={'rotation':keys([(0,[s*8,0,0]),(.5,[-s*8,0,0]),(1,[s*8,0,0])])};a[side+'_hem']={'rotation':keys([(0,[s*12,0,0]),(.5,[-s*12,0,0]),(1,[s*12,0,0])])}
a['furnace']={'rotation':keys([(0,[0,0,-4]),(.5,[0,0,4]),(1,[0,0,-4])])}
a=anim('helix',4);a['right_upper_arm']={'rotation':keys([(0,[0,0,0]),(.6,[-55,0,20]),(.8,[-75,0,-20]),(1.15,[-80,0,-30]),(3.3,[0,0,0]),(4,[0,0,0])])};a['whisk']={'rotation':keys([(0,[0,0,0]),(.6,[0,0,-40]),(.8,[0,0,35]),(1.2,[0,0,35]),(4,[0,0,0])])};a['furnace']={'rotation':keys([(0,[0,0,0]),(.75,[0,120,-15]),(.8,[0,160,-25]),(3,[0,180,0]),(4,[0,0,0])])}
a=anim('sea',3.05);a['furnace']={'rotation':keys([(0,[0,0,0]),(1.15,[0,20,-150]),(1.2,[0,20,-180]),(1.6,[0,20,-180]),(3.05,[0,0,0])])};a['right_forearm']={'rotation':keys([(0,[0,0,0]),(1.1,[-70,0,0]),(1.2,[-95,0,0]),(2,[0,0,0]),(3.05,[0,0,0])])};a['chest']={'rotation':keys([(0,[0,0,0]),(1.15,[-12,0,0]),(1.3,[20,0,0]),(3.05,[0,0,0])])}
a=anim('pells',2.75);a['left_upper_arm']={'rotation':keys([(0,[0,0,0]),(.7,[-25,0,-20]),(1.1,[-70,0,-30]),(1.3,[20,0,10]),(2.75,[0,0,0])])};a['mask']={'rotation':keys([(0,[0,0,0]),(.9,[-18,0,0]),(1.1,[-30,0,0]),(1.4,[0,0,0]),(2.75,[0,0,0])])}
for i in range(3):a[f'gold{i}']={'position':keys([(0,[0,0,0]),(.9,[-10 if i==0 else 0,6 if i==0 else 0,4 if i==0 else 0]),(1.1,[-10 if i==0 else 0,6 if i==0 else 0,4 if i==0 else 0])]),'scale':keys([(0,[1,1,1]),(1.05,[1,1,1]),(1.1,[0,0,0]),(2.75,[0,0,0])])}
a=anim('hurt',.4);a['chest']={'rotation':keys([(0,[0,0,0]),(.1,[-15,0,8]),(.4,[0,0,0])])};a['furnace']={'rotation':keys([(0,[0,0,0]),(.1,[0,0,20]),(.4,[0,0,0])])}
a=anim('death',4);a['mask']={'rotation':keys([(0,[0,0,0]),(.4,[-45,0,0]),(1,[20,0,0]),(4,[20,0,0])])};a['chest']={'rotation':keys([(0,[0,0,0]),(.5,[-20,0,0]),(1.5,[65,0,0]),(4,[65,0,0])])};a['furnace']={'position':keys([(0,[0,0,0]),(.3,[-2,1,0]),(.6,[-10,5,0]),(1.2,[-10,-8,0]),(4,[-10,-8,0])]),'scale':keys([(0,[1,1,1]),(.6,[1.4,1.2,1.4]),(.9,[.2,.2,.2]),(4,[.2,.2,.2])])};a['root']={'scale':keys([(0,[1,1,1]),(1.2,[1,1,1]),(3.8,[0,0,0]),(4,[0,0,0])])}
for i in range(3):a[f'furnace_leg{i}']={'position':keys([(0,[0,0,0]),(.6,[(i-1)*10,8,-8]),(1.5,[(i-1)*12,-5,-10]),(4,[(i-1)*12,-5,-10])]),'rotation':keys([(0,[0,0,0]),(1,[90,80*i,40]),(4,[90,80*i,40])])}
geo(ID,bones,4,4);animation(ID,anims)
texture=Image.new('RGB',(16,16),'white')
for color,(u,v) in UV.items():
 for x in range(u-1,u+5):
  for y in range(v-1,v+5):texture.putpixel((x,y),tuple(bytes.fromhex(COLORS[color][1:])))
p=A/'textures/entity/blueprint/elite'/f'{ID}.png';p.parent.mkdir(parents=True,exist_ok=True);texture.save(p)
count=(len(bones),sum(len(b.get('cubes',[])) for b in bones))
bones=[];bone('root',pivot=(0,3,0))
for name,color in [('warm','copper'),('cold','cold'),('pill','copper')]:
 b=bone(name,'root',(0,3,0));cube(b,(-2,1,-2),(4,4,4),color)
 if name!='pill':cube(b,(-1,5,-1),(2,2,2),'white')
geo('alchemist_cast_orb',bones,1,1)
animation('alchemist_cast_orb',{'animation.alchemist_cast_orb.spin':{'loop':True,'animation_length':1,'bones':{'root':{'rotation':keys([(0,[0,0,0]),(1,[0,360,0])])}}}})
print(f'Original alchemist: {count[0]} bones, {count[1]} cuboids, seven clips; orb uses the same actual 16x16 four-colour texture.')
