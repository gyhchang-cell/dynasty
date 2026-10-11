"""Original block-built heavy tomb guard: segmented body and stepped solid bronze hammers."""
import json
from pathlib import Path
from PIL import Image,ImageDraw

ID='juchui_jinjia_lishi';BASE=Path('src/main/resources/assets/dynasty')
colours=['#FFFFFF','#383B36','#C49A49','#B49B78'];slots=[(10,10),(2,2),(10,2),(2,10)]
atlas=Image.new('RGB',(16,16),colours[0]);draw=ImageDraw.Draw(atlas)
for i,box in [(1,(1,1,6,6)),(2,(9,1,14,6)),(3,(1,9,6,14))]:draw.rectangle(box,fill=colours[i])
def cube(o,s,m=1):
 u,v=slots[m];return {'origin':o,'size':s,'uv':{f:{'uv':[u,v],'uv_size':[4,4]} for f in ['north','south','east','west','up','down']}}
bones=[]
def bone(n,p,pivot,c=(),r=None):
 b={'name':n,'pivot':pivot,'cubes':list(c)}
 if p:b['parent']=p
 if r:b['rotation']=r
 bones.append(b)
def hammer(x,y,z):
 # Three intersecting broad cuboids make an eight-stepped silhouette, no smooth primitives.
 return [cube([x-.9,y-9,z-.9],[1.8,24,1.8]),cube([x-5.6,y-6,z-3.6],[11.2,9,7.2],2),cube([x-3.6,y-6,z-5.6],[7.2,9,11.2],2),cube([x-4.6,y-7,z-4.6],[9.2,11,9.2],2),cube([x-2,y-7.6,z-2],[4,.6,4])]
bone('root',None,[0,0,0]);bone('pelvis','root',[0,18,0],[cube([-6,15,-4],[12,6,8]),cube([-6.7,15,-4.5],[13.4,3,9],2)])
bone('waist','pelvis',[0,21,0],[cube([-4.5,21,-3.6],[9,4,7.2]),cube([-4.8,21,-4],[9.6,2,1],2)])
bone('chest','waist',[0,25,0],[cube([-8,25,-5],[16,11,10],3),cube([-8.5,26,-5.6],[17,9,1.2],2),cube([-7.5,25,4.8],[15,10,1.3],2),cube([-3.5,29,-6.3],[7,6,.7]),cube([-2.5,30,-6.8],[5,4,.5],2)])
bone('neck','chest',[0,36,0],[cube([-2.8,36,-2.8],[5.6,3,5.6],3)])
bone('head','neck',[0,39,0],[cube([-4.2,37.5,-3.8],[8.4,7.3,7.6],3),cube([-4.5,41,-4.1],[9,2.5,8.2],2),cube([-2.2,38.4,-4.4],[4.4,1.5,.8]),cube([-1,43.5,-4.2],[2,1.3,.6],2)])
for side,sgn in [('left',1),('right',-1)]:
 x=sgn*5
 bone(side+'_thigh','pelvis',[x,18,0],[cube([x-2.7,10,-3],[5.4,8,6],3),cube([x-3.1,11,-3.8],[6.2,6,1.1],2)])
 bone(side+'_knee',side+'_thigh',[x,10,0],[cube([x-3,8.8,-4],[6,3,2],2)])
 bone(side+'_shin',side+'_knee',[x,9.5,0],[cube([x-2.5,2.5,-2.7],[5,7,5.4]),cube([x-2.8,3,-3.4],[5.6,5,1.3],2)])
 bone(side+'_ankle',side+'_shin',[x,2.5,0]);bone(side+'_foot',side+'_ankle',[x,2.5,0],[cube([x-3,.1,-4.8],[6,2.6,8],2)])
 x=sgn*10.5
 bone(side+'_shoulder','chest',[x,34,0],[cube([x-3.5,30,-4.3],[7,6,8.6],3),cube([x-4.5,34,-5],[9,3,10],2),cube([x-3.5,37,-4],[7,1.8,8],2)])
 bone(side+'_upper_arm',side+'_shoulder',[x,32,0],[cube([x-2.8,24,-3.4],[5.6,8,6.8],3)])
 bone(side+'_elbow',side+'_upper_arm',[x,24,0],[cube([x-3,22.5,-3.8],[6,3,7.6],2)])
 bone(side+'_forearm',side+'_elbow',[x,23,0],[cube([x-2.7,17,-3.1],[5.4,6,6.2],3),cube([x-3,18,-3.8],[6,4,1],2)])
 bone(side+'_wrist',side+'_forearm',[x,17,0]);bone(side+'_hand',side+'_wrist',[x,17,0],[cube([x-3,14.5,-3.4],[6,3,6.8],3)])
 bone(side+'_hammer',side+'_hand',[x,17,-3.7],hammer(x,12,-3.7))
 bone('dropped_'+side+'_hammer','root',[sgn*14,0,-4],hammer(sgn*14,7.7,-4),[0,0,sgn*8])
for side,sgn in [('left',1),('right',-1)]:
 for i in range(3):bone(side+'_tasset_'+str(i),'pelvis',[sgn*(2+i*2.8),16,-4.5],[cube([sgn*(2+i*2.8)-1.3,9,-4.7],[2.6,7,1.2],2)])
def rig(parts,name,bounds=6):return {'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.'+name,'texture_width':16,'texture_height':16,'visible_bounds_width':bounds,'visible_bounds_height':6,'visible_bounds_offset':[0,2,0]},'bones':parts}]}
animations={}
def track(kind,seq):return {kind:{str(t):v for t,v in seq}}
def rot(seq):return track('rotation',seq)
def clip(name,length,ch,loop=False):animations['animation.'+ID+'.'+name]={'loop':loop,'animation_length':length,'bones':ch}
clip('idle',2,{'chest':rot([(0,[0,0,-1]),(1,[0,0,1]),(2,[0,0,-1])])},True)
walk={'chest':rot([(0,[5,0,-2]),(.6,[5,0,2]),(1.2,[5,0,-2])])}
for side,sign in [('left',1),('right',-1)]:
 walk[side+'_thigh']=rot([(0,[sign*18,0,0]),(.6,[-sign*18,0,0]),(1.2,[sign*18,0,0])]);walk[side+'_shoulder']=rot([(0,[-sign*8,0,0]),(.6,[sign*8,0,0]),(1.2,[-sign*8,0,0])])
clip('walk',1.2,walk,True)
slam={'chest':rot([(0,[0,0,0]),(1.2,[-16,0,0]),(1.4,[22,0,0]),(3,[18,0,0]),(4.85,[0,0,0])])}
for side,sgn in [('left',1),('right',-1)]:
 slam[side+'_shoulder']=rot([(0,[0,0,0]),(1.2,[-150,0,sgn*8]),(1.4,[-15,0,sgn*8]),(3,[-15,0,sgn*8]),(4.85,[0,0,0])])
 slam[side+'_elbow']=rot([(0,[0,0,0]),(1.2,[-20,0,0]),(1.4,[10,0,0]),(4.85,[0,0,0])])
clip('slam',4.85,slam)
wheel={'chest':rot([(0,[0,0,0]),(.9,[12,0,0]),(3.35,[12,0,0]),(5.35,[0,0,0])])}
for side,sgn in [('left',1),('right',-1)]:
 seq=[(0,[0,0,0]),(.75,[sgn*35,0,0])]
 for i,t in enumerate([.9,1.3,1.7,2.1,2.5,2.9]):seq.append((t,[(-25 if (i%2==0)==(sgn==1) else -95),0,sgn*10]))
 seq.extend([(3.35,[-20,0,sgn*10]),(5.35,[0,0,0])]);wheel[side+'_shoulder']=rot(seq)
clip('wheel',5.35,wheel)
clip('throw',5.7,{'chest':rot([(0,[0,0,0]),(1.65,[0,-28,0]),(1.8,[12,25,0]),(4.2,[12,25,0]),(5.7,[0,0,0])]),'right_shoulder':rot([(0,[0,0,0]),(1.65,[70,-30,-10]),(1.8,[-90,0,-10]),(3,[-90,0,-10]),(4.2,[-35,0,-10]),(5.7,[0,0,0])]),'right_elbow':rot([(0,[0,0,0]),(1.65,[-35,0,0]),(1.8,[0,0,0]),(5.7,[0,0,0])])})
clip('hurt',1.5,{'chest':rot([(0,[0,0,0]),(.15,[-20,0,5]),(.45,[6,0,-4]),(1.5,[0,0,0])])})
death={'root':track('position',[(0,[0,0,0]),(.6,[0,-3,0]),(1.4,[0,-11,0]),(3.5,[0,-11,0])]),'chest':rot([(0,[0,0,0]),(.7,[20,0,0]),(1.4,[40,0,0]),(3.5,[45,0,0])])}
for side,sgn in [('left',1),('right',-1)]:
 death[side+'_thigh']=rot([(0,[0,0,0]),(1.4,[-45,0,0]),(3.5,[-45,0,0])]);death[side+'_knee']=rot([(0,[0,0,0]),(1.4,[95,0,0]),(3.5,[95,0,0])]);death[side+'_shoulder']=rot([(0,[0,0,0]),(.6,[10,0,sgn*8]),(3.5,[10,0,sgn*8])]);death['dropped_'+side+'_hammer']=track('position',[(0,[0,0,0]),(.6,[0,3,0]),(1.4,[0,11,0]),(3.5,[0,11,0])])
clip('death',3.5,death)
for folder in ['geo/blueprint/elite','animations/blueprint/elite','textures/entity/blueprint/elite']:(BASE/folder).mkdir(parents=True,exist_ok=True)
(BASE/'geo/blueprint/elite'/f'{ID}.geo.json').write_text(json.dumps(rig(bones,ID),indent=2)+'\n')
(BASE/'animations/blueprint/elite'/f'{ID}.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':animations},indent=2)+'\n');atlas.save(BASE/'textures/entity/blueprint/elite'/f'{ID}.png')
parts=[{'name':'hammer','pivot':[0,0,0],'cubes':hammer(0,0,0)}]
(BASE/'geo/blueprint/elite/hammer_chain.geo.json').write_text(json.dumps(rig(parts,'hammer_chain',3),indent=2)+'\n')
(BASE/'animations/blueprint/elite/hammer_chain.animation.json').write_text(json.dumps({'format_version':'1.8.0','animations':{'animation.hammer_chain.spin':{'loop':True,'animation_length':.4,'bones':{'hammer':rot([(0,[0,0,0]),(.4,[360,0,0])])}}}},indent=2)+'\n')
print(f'{ID}: {len(bones)} bones / {sum(len(b["cubes"]) for b in bones)} cuboids / {len(animations)} clips / 16x16 four colours')
