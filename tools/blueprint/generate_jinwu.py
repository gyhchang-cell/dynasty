"""Original segmented block armour, stepped halberd and sixteen-pixel/four-colour islands."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw
ID='pilin_zhijinwu';BASE=Path('src/main/resources/assets/dynasty')
colours=['#FFFFFF','#30353B','#CCA34E','#8D2C32'];slots=[(10,10),(2,2),(10,2),(2,10)]
atlas=Image.new('RGB',(16,16),colours[0]);draw=ImageDraw.Draw(atlas)
for index,box in [(1,(1,1,6,6)),(2,(9,1,14,6)),(3,(1,9,6,14))]:draw.rectangle(box,fill=colours[index])
def cube(o,s,m=1):
 u,v=slots[m];return {'origin':o,'size':s,'uv':{f:{'uv':[u,v],'uv_size':[4,4]} for f in ['north','south','east','west','up','down']}}
bones=[]
def bone(n,p,pivot,c=(),r=None):
 b={'name':n,'pivot':pivot,'cubes':list(c)}
 if p:b['parent']=p
 if r:b['rotation']=r
 bones.append(b)
bone('root',None,[0,0,0]);bone('pelvis','root',[0,14,0],[cube([-5,13,-3],[10,5,6])]);bone('waist','pelvis',[0,18,0],[cube([-4,18,-2.5],[8,3,5],2)])
bone('chest','waist',[0,21,0],[cube([-6,21,-4],[12,8,8]),cube([-4.5,22,-4.6],[9,6,.75],2),cube([-3.5,23,-5],[7,4,.5])])
for row,y in enumerate([22,24,26]):
 for x in [-4,-1,2]:bone('scale_'+str(row)+'_'+str(x),'chest',[x+1.5,y,-5],[cube([x,y,-5.15],[3,1.5,.4],2)])
bone('neck','chest',[0,29,0],[cube([-2,29,-2],[4,2,4],2)])
bone('head','neck',[0,31,0],[cube([-4,30,-3.5],[8,5.5,7]),cube([-3,31,-4],[6,3.5,.75],2),cube([-2.5,32,-4.75],[5,1.25,.75]),cube([-1,30.5,-5],[2,2.5,1],2)])
bone('helmet_crest','head',[0,35,0],[cube([-1,35,-3],[2,1.8,6],2),cube([-1,36,-2],[2,.8,4],3)])
for side,sgn in [('left',1),('right',-1)]:
 x=sgn*4
 bone(side+'_thigh','pelvis',[x,14,0],[cube([x-2,8,-2.7],[4,6,5.4]),cube([x-2.4,9,-3.2],[4.8,4,.7],2)])
 bone(side+'_knee',side+'_thigh',[x,8,0],[cube([x-2,6.4,-3.3],[4,2.5,1.4],2)])
 bone(side+'_shin',side+'_knee',[x,7,0],[cube([x-1.7,2,-2.2],[3.4,5,4.4])])
 bone(side+'_ankle',side+'_shin',[x,2,0]);bone(side+'_foot',side+'_ankle',[x,2,0],[cube([x-2.1,.1,-3.6],[4.2,2,6],2),cube([x-1.7,1.9,-2.2],[3.4,1,4.4])])
 x=sgn*8
 bone(side+'_shoulder','chest',[x,27.5,0],[cube([x-2,24,-3],[4,4,6]),cube([x-3,26,-3.7],[6,2.5,7.4],2),cube([x-2,28,-3],[4,1.5,6]),cube([x-1,29,-2],[2,1.5,4],2)])
 bone(side+'_upper_arm',side+'_shoulder',[x,26,0],[cube([x-1.7,20,-2],[3.4,6,4])])
 bone(side+'_elbow',side+'_upper_arm',[x,20,0],[cube([x-1.8,18.5,-2.3],[3.6,2.5,4.6],2)])
 bone(side+'_forearm',side+'_elbow',[x,19,0],[cube([x-1.6,14,-1.9],[3.2,5,3.8])])
 bone(side+'_wrist',side+'_forearm',[x,14,0]);bone(side+'_hand',side+'_wrist',[x,14,0],[cube([x-1.8,12.5,-2],[3.6,2.5,4],2)])
bone('cape_0','chest',[0,28,4.1],[cube([-7,20,4.3],[14,8,1],3)])
bone('cape_1','cape_0',[0,20,4.7],[cube([-7,12,4.7],[14,8,1],3)])
bone('cape_2','cape_1',[0,12,5.2],[cube([-6,5,5.1],[12,7,1],3),cube([-5,3,5.1],[3,2,1],3),cube([2,3,5.1],[3,2,1],3)])
bone('halberd','right_hand',[8,14,-2.5],[cube([7.4,.2,-3.1],[1.2,48,1.2]),cube([7,11,-3.5],[2,7,2],2),cube([7.2,48,-3.3],[1.6,7,1.6],2),cube([7.6,55,-2.9],[.8,2.6,.8])])
for side,s in [('blade_left',1),('blade_right',-1)]:
 bone(side,'halberd',[8,48,-2.5],[cube([8 if s>0 else 2,45,-3],[6,2,1],2),cube([11 if s>0 else 2,47,-3.2],[3,5,1.4]),cube([10 if s>0 else 3,52,-3.2],[3,3,1.4],2),cube([9 if s>0 else 4,54,-3.1],[3,2,1.2],2)])
bone('halberd_tassel','halberd',[8,45,-2.5],[cube([6.5,39,-3.5],[3,6,2],3)])
# Weapon coordinates share the right hand's -8-X pivot, including all children.
for part in bones:
 if part['name'] in ['halberd','blade_left','blade_right','halberd_tassel']:
  part['pivot'][0]-=16;part['pivot'][2]+=2.5
  for block in part['cubes']:block['origin'][0]-=16;block['origin'][2]+=2.5;block['origin'][1]-=2.2
rig={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+ID,'texture_width':16,'texture_height':16,'visible_bounds_width':7,'visible_bounds_height':6,'visible_bounds_offset':[0,2,0]},'bones':bones}]}
animations={}
def track(kind,seq):return {kind:{str(t):v for t,v in seq}}
def rot(seq):return track('rotation',seq)
def clip(name,length,ch,loop=False):animations['animation.'+ID+'.'+name]={'loop':loop,'animation_length':length,'bones':ch}
def cape(length):return {'cape_'+str(i):rot([(0,[4+i*2,0,0]),(length/2,[-4-i*2,0,0]),(length,[4+i*2,0,0])]) for i in range(3)}
idle={'chest':rot([(0,[0,0,-1]),(1,[0,0,1]),(2,[0,0,-1])]),**cape(2)};clip('idle',2,idle,True)
walk={**cape(1),'chest':rot([(0,[4,0,-2]),(.5,[4,0,2]),(1,[4,0,-2])])}
for side,s in [('left',1),('right',-1)]:
 walk[side+'_thigh']=rot([(0,[s*18,0,0]),(.5,[-s*18,0,0]),(1,[s*18,0,0])]);walk[side+'_knee']=rot([(0,[max(0,-s*16),0,0]),(.5,[max(0,s*16),0,0]),(1,[max(0,-s*16),0,0])])
clip('walk',1,walk,True);clip('hurt',.4,{'chest':rot([(0,[0,0,0]),(.1,[-12,0,8]),(.4,[0,0,0])]),**cape(.4)})
hands={'right_shoulder':rot([(0,[0,0,0]),(.4,[-70,0,-15]),(1,[-80,0,-10]),(2.65,[0,0,0])]),'left_shoulder':rot([(0,[0,0,0]),(.4,[-65,0,30]),(1,[-80,0,30]),(2.65,[0,0,0])])}
clip('sweep',2.65,{'waist':rot([(0,[0,0,0]),(.85,[0,-90,0]),(1,[0,-100,0]),(1.1,[0,170,0]),(2.65,[0,0,0])]),'halberd':rot([(0,[0,0,0]),(.8,[-10,0,0]),(1.1,[-10,0,0]),(2.65,[0,0,0])]),**hands,**cape(2.65)})
charge={'chest':rot([(0,[0,0,0]),(.8,[15,0,0]),(1.6,[15,0,0]),(3.1,[0,0,0])]),'halberd':rot([(0,[0,0,0]),(.5,[-40,0,0]),(1.6,[-40,0,0]),(3.1,[0,0,0])]),**cape(3.1)}
for side,s in [('right',-1),('left',1)]:charge[side+'_shoulder']=rot([(0,[0,0,0]),(.5,[-65,0,s*25]),(1.6,[-65,0,s*25]),(3.1,[0,0,0])])
charge['right_thigh']=rot([(0,[0,0,0]),(.2,[20,0,0]),(.3,[0,0,0]),(.4,[20,0,0]),(.5,[0,0,0]),(.6,[20,0,0]),(.8,[0,0,0]),(3.1,[0,0,0])]);clip('charge',3.1,charge)
clip('order',3,{'right_shoulder':rot([(0,[0,0,0]),(.7,[-35,0,0]),(1.1,[10,0,0]),(1.2,[0,0,0]),(3,[0,0,0])]),'halberd':track('position',[(0,[0,0,0]),(.7,[0,6,0]),(1.2,[0,0,0]),(3,[0,0,0])]),**cape(3)})
death={'pelvis':track('position',[(0,[0,0,0]),(1.5,[0,-7.5,0]),(3.5,[0,-7.5,0])]),'waist':rot([(0,[0,0,0]),(1.5,[20,0,0]),(3.5,[20,0,0])]),'right_thigh':rot([(0,[0,0,0]),(1.5,[-35,0,0]),(3.5,[-35,0,0])]),'right_knee':rot([(0,[0,0,0]),(1.5,[115,0,0]),(3.5,[115,0,0])]),'right_ankle':rot([(0,[0,0,0]),(1.5,[-80,0,0]),(3.5,[-80,0,0])]),'halberd':{**track('position',[(0,[0,0,0]),(1.5,[0,4,0]),(3.5,[0,4,0])]),**rot([(0,[0,0,0]),(1.5,[-20,0,0]),(3.5,[-20,0,0])])},'cape_0':rot([(0,[0,0,0]),(1.5,[20,0,0]),(3.5,[20,0,0])]),'cape_2':track('scale',[(0,[1,1,1]),(2,[.8,.6,1]),(3.5,[.8,.6,1])])}
death['left_thigh']=rot([(0,[0,0,0]),(1.5,[-65,0,0]),(3.5,[-65,0,0])])
death['left_knee']=rot([(0,[0,0,0]),(1.5,[135,0,0]),(3.5,[135,0,0])])
death['left_ankle']=rot([(0,[0,0,0]),(1.5,[-70,0,0]),(3.5,[-70,0,0])])
clip('death',3.5,death)
# Solve the two seven/five-pixel arm links in Gecko's baked coordinates.
# JSON X/Y rotations are negated by Gecko; its model X coordinates are mirrored.
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def mv(a,v):return [sum(a[i][k]*v[k] for k in range(3)) for i in range(3)]
def tr(a):return list(map(list,zip(*a)))
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mat(v):
 x,y,z=map(math.radians,v);cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
 return mm(mm([[cz,-sz,0],[sz,cz,0],[0,0,1]],[[cy,0,sy],[0,1,0],[-sy,0,cy]]),[[1,0,0],[0,cx,-sx],[0,sx,cx]])
def jsonrot(a):
 y=math.asin(max(-1,min(1,-a[2][0])))
 if abs(math.cos(y))>.00001:x,z=math.atan2(a[2][1],a[2][2]),math.atan2(a[1][0],a[0][0])
 else:x,z=math.atan2(-a[1][2],a[1][1]),0
 return [-math.degrees(x),-math.degrees(y),math.degrees(z)]
def sample(ch,n,k,t,default):
 frames=ch.get(n,{}).get(k)
 if frames is None:return default
 keys=sorted((float(x),v) for x,v in frames.items())
 if t<=keys[0][0]:return keys[0][1]
 for (a,v),(b,w) in zip(keys,keys[1:]):
  if t<=b:return [u+(v2-u)*(t-a)/(b-a) for u,v2 in zip(v,w)]
 return keys[-1][1]
rigmap={b['name']:b for b in bones}
def baked(v):return [-v[0],v[1],v[2]]
def pose(ch,n,t):
 b=rigmap[n];p=baked(b['pivot']);offset=baked(sample(ch,n,'position',t,[0,0,0]));r=sample(ch,n,'rotation',t,[0,0,0]);r=mat([-r[0],-r[1],r[2]])
 if not b.get('parent'):return r,add(p,offset)
 parent=rigmap[b['parent']];pr,pp=pose(ch,b['parent'],t)
 return mm(pr,r),add(pp,mv(pr,add(sub(p,baked(parent['pivot'])),offset)))
def arm(ch,side,t,target):
 ch[side+'_shoulder']={'rotation':{'0':[0,0,0]}}
 upper=side+'_upper_arm';fore=side+'_forearm';parent=rigmap[upper]['parent'];pr,pp=pose(ch,parent,t)
 start=add(pp,mv(pr,sub(baked(rigmap[upper]['pivot']),baked(rigmap[parent]['pivot']))));d=mv(tr(pr),sub(target,start))
 radius=math.sqrt(sum(x*x for x in d));assert 2<radius<12.001,(side,t,radius,target,start)
 angle=math.atan2(math.hypot(d[0],d[2]),-d[1]);yaw=math.atan2(-d[0],-d[2]);alpha=math.acos(max(-1,min(1,(49+radius*radius-25)/(14*radius))));bend=math.pi-math.acos(max(-1,min(1,(49+25-radius*radius)/70)))
 ch.setdefault(upper,{}).setdefault('rotation',{})[str(t)]=[-math.degrees(angle-alpha),-math.degrees(yaw),0]
 ch.setdefault(fore,{}).setdefault('rotation',{})[str(t)]=[-math.degrees(bend),0,0]
for key,a in animations.items():
 name=key.rsplit('.',1)[1];ch=a['bones'];length=a['animation_length']
 # A half-tick sampling interval keeps both grips on the shaft throughout the turn.
 times=sorted(set([0,length]+[round(i*.05,4) for i in range(int(length/.05)+1)]))
 for n in ['right_shoulder','left_shoulder','right_upper_arm','left_upper_arm','right_forearm','left_forearm','halberd']:ch.pop(n,None)
 for t in times:
  body,centre=pose(ch,'chest',t)
  active=min(1,t/.5) if name in ['sweep','charge'] else 0
  if name in ['sweep','charge']:
   right=[2*(1-active),16+4*active,-2-4*active];left=[2*(1-active),20,-2-active]
   right=add(centre,mv(body,sub(right,[0,21,0])));left=add(centre,mv(body,sub(left,[0,21,0])))
   desired=mat([-90*active,0,0]) if name=='charge' else mm(body,mat([-90*active,0,0]))
  elif name=='death':
   u=min(1,t/1.5);right=[2,16-2*u,-2];left=[2,20-3*u,-2];desired=mat([0,0,0])
  else:
   lift=sample(ch,'halberd','position',t,[0,0,0])[1] if name=='order' else 0
   if name=='order':lift=3*math.sin(math.pi*min(1,t/1.2)) if t<1.2 else 0
   right=add(centre,mv(body,[-0+2,-5+lift,-2]));left=add(centre,mv(body,[2,-1+lift,-2]));desired=body
  arm(ch,'right',t,right);arm(ch,'left',t,left)
  hand,_=pose(ch,'right_hand',t);ch.setdefault('halberd',{}).setdefault('rotation',{})[str(t)]=jsonrot(mm(tr(hand),desired))
 # The shaft itself supplies the vertical lift; it remains joined to the right hand.
 ch['halberd'].pop('position',None)

for folder,ext,data in [('geo','.geo.json',rig),('animations','.animation.json',{'format_version':'1.8.0','animations':animations})]:
 p=BASE/folder/'blueprint/elite'/(ID+ext);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
p=BASE/'textures/entity/blueprint/elite'/(ID+'.png');p.parent.mkdir(parents=True,exist_ok=True);atlas.save(p)
p=BASE/'models/item'/(ID+'_spawn_egg.json');p.write_text(json.dumps({'parent':'minecraft:item/template_spawn_egg'},indent=2)+'\n')
root=Path('src/main/resources/data/dynasty')
p=root/'tags/worldgen/structure/blueprint/jinwu_sites.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'replace':False,'values':['dynasty:imperial_tomb','dynasty:great_wall_gate']},indent=2)+'\n')
p=root/'loot_tables/entities'/(ID+'.json');p.write_text(json.dumps({'type':'minecraft:entity','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'dynasty:'+item}]} for item in ['refined_wrought_iron','broken_heart_mirror','broken_iron_blade']]},indent=2)+'\n')
p=root/'advancements/blueprint'/('kill_'+ID+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'criteria':{'kill':{'trigger':'minecraft:player_killed_entity','conditions':{'entity':{'type':'dynasty:'+ID}}}}},indent=2)+'\n')
assert len(atlas.getcolors(256))==4 and atlas.size==(16,16)
assert set(b['name'] for b in bones).issuperset(n for a in animations.values() for n in a['bones'])
print(ID,len(bones),'bones',sum(len(b.get('cubes',[])) for b in bones),'cuboids',len(animations),'clips;16px/four colours')
