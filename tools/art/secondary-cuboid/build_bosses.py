"""Original species/profession-specific cuboid bosses. Actual final 16px assets."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw
from build_models import ASSET,keys

OUT=Path(__file__).resolve().parents[3]/'docs/art/cod6-cuboid-v1'
SPECS={
 'eunuch_mastermind':(['#302638','#6e4f78','#dbc79b'],['..CC..','.AAAA.','..CC..','CBBCBC','.BBBB.','.AAAA.']),
 'undead_first_emperor':(['#282e35','#5c7166','#c6b077'],['.CCCC.','CBAABC','.BAAB.','CBBCBC','.BBBB.','CAAAAC']),
 'dragon_king':(['#253743','#487c7b','#c4b17b'],['C....C','.BC CB.'.replace(' ',''),'BABBAB','.BCCB.','BBBBBB','.BCCB.']),
 'nine_heaven_general':(['#34455c','#718ba4','#d8c6a0'],['C....C','.CCCC.','.CAAC.','CBBCBC','.ABBA.','.AAAA.']),
 'dragon_emperor':(['#2b4039','#658573','#c6ae74'],['C....C','.BCCB.','BAAAAB','.CCCC.','.BBBB.','BCBBCB']),
}

class Rig:
 def __init__(self,id):
  self.id=id;self.bones=[];self.by={};palette,rows=SPECS[id]
  im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(im);self.islands={}
  for y,row in enumerate(rows,1):
   assert len(row)==6,(id,row)
   for x,c in enumerate(row,1):
    if c=='.':continue
    d.rectangle((x*2,y*2,x*2+1,y*2+1),fill=palette['ABC'.index(c)]);self.islands.setdefault(c,[x*2,y*2])
  p=ASSET/f'textures/entity/boss_cuboid/{id}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 def bone(self,name,pivot,parent='root',rotation=None):
  b={'name':name,'pivot':list(pivot)}
  if parent:b['parent']=parent
  if rotation:b['rotation']=rotation
  self.bones.append(b);self.by[name]=b;return name
 def cube(self,bone,origin,size,color='B'):
  self.by[bone].setdefault('cubes',[]).append({'origin':list(origin),'size':list(size),'uv':{f:{'uv':self.islands[color].copy(),'uv_size':[2,2]} for f in ['north','south','east','west','up','down']}})
 def save(self):
  g={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.boss_cuboid.'+self.id,'texture_width':16,'texture_height':16,'visible_bounds_width':14 if self.id=='dragon_emperor' else 4,'visible_bounds_height':8 if self.id=='dragon_emperor' else 4,'visible_bounds_offset':[0,2.5 if self.id=='dragon_emperor' else 1.5,0]},'bones':self.bones}]}
  p=ASSET/f'geo/boss_cuboid/{self.id}.geo.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(g,indent=2)+'\n');return self

def face(r,y,z,w=6):
 r.bone('head',(0,y,z),'neck');r.cube('head',(-w/2,y,z-3),(w,6,5),'C')
 r.cube('head',(-w/2,y+4,z-3.75),(w,1,1),'A')
 for x in [-w/2+.5,w/2-1.5]:r.cube('head',(x,y+3,z-4),(1,1,.5),'A')
 r.cube('head',(-1,y+1,z-4.75),(2,2,1.75),'C')
 r.bone('jaw',(0,y,z-2),'head');r.cube('jaw',(-2,y-.5,z-3.5),(4,1,3),'B')

def arms(r,y,x,depth=3,sleeve=False):
 for side,s in [('left',1),('right',-1)]:
  r.bone(side+'_arm',(s*x,y,0),'chest');r.cube(side+'_arm',(s*x-1.5,y-6,-depth/2),(3,6,depth))
  r.bone(side+'_elbow',(s*x,y-6,0),side+'_arm')
  r.bone(side+'_forearm',(s*x,y-6,0),side+'_elbow');r.cube(side+'_forearm',(s*x-1,y-11,-1),(2,5,2),'C')
  r.bone(side+'_hand',(s*x,y-11,-1),side+'_forearm');r.cube(side+'_hand',(s*x-1.5,y-13,-2),(3,2,3),'C');r.cube(side+'_hand',(s*x-s*1.5-.5,y-12.5,-2.25),(1,1,1.25),'B')
  r.bone(side+'_grip',(s*x,y-12,-1),side+'_hand')
  if sleeve:
   r.bone(side+'_sleeve',(s*x,y-6,0),side+'_elbow');r.cube(side+'_sleeve',(s*x-2,y-13,.75),(4,8,3))
   r.cube(side+'_sleeve',(s*x-2.25,y-13,-1.25),(4.5,2,5.25),'A')

def eunuch():
 r=Rig('eunuch_mastermind');r.bone('root',(0,0,0),None);r.bone('body',(0,15,0))
 r.bone('pelvis',(0,12,0),'body');r.cube('pelvis',(-3.5,10,-2),(7,4,4))
 r.bone('waist',(0,14,0),'pelvis');r.cube('waist',(-2.5,14,-1.5),(5,2,3),'A')
 r.bone('chest',(0,16,0),'waist');r.cube('chest',(-4,16,-2),(8,7,4))
 r.cube('chest',(-1,17,-2.5),(2,5,.5),'C')
 r.bone('neck',(0,23,0),'chest');r.cube('neck',(-1.5,23,-1.5),(3,1,3),'C');face(r,24,0)
 r.bone('hat',(0,30,0),'head');r.cube('hat',(-4,30,-3),(8,2,6),'A');r.cube('hat',(-2,32,-2),(4,2,4),'C')
 r.bone('mask',(0,26,-3),'head');r.cube('mask',(-3,24.5,-4.5),(6,1.5,.5),'A')
 arms(r,22,5.5,sleeve=True)
 for side,s in [('left',1),('right',-1)]:
  r.bone(side+'_leg',(s*2,11,0),'pelvis');r.cube(side+'_leg',(s*2-1,2,-1),(2,9,2),'A')
  r.bone(side+'_foot',(s*2,2,-1),side+'_leg');r.cube(side+'_foot',(s*2-1.5,0,-3),(3,2,4),'A')
  r.bone(side+'_robe',(s*2.5,12,0),'pelvis');r.cube(side+'_robe',(s*2.5-2,2,-2.75),(4,10,.75));r.cube(side+'_robe',(s*2.5-2,2,2),(4,10,.75))
 r.bone('ritual_case',(0,19,2),'chest');r.cube('ritual_case',(-2,16,2.5),(4,8,3),'A');r.cube('ritual_case',(-1,17,5.5),(2,6,.5),'C')
 for i,x in enumerate([-1.5,1.5]):r.bone('case_tassel_'+str(i),(x,16,4),'ritual_case');r.cube('case_tassel_'+str(i),(x-.5,10,3.5),(1,6,1),'C')
 return r.save()

def emperor():
 r=Rig('undead_first_emperor');r.bone('root',(0,0,0),None);r.bone('body',(0,16,0))
 r.bone('pelvis',(0,10,0),'body');r.cube('pelvis',(-4,7,-2.5),(8,5,5),'A')
 r.bone('waist',(0,12,0),'pelvis');r.cube('waist',(-3,12,-2),(6,3,4),'C')
 r.bone('chest',(0,15,0),'waist');r.cube('chest',(-5,15,-3),(10,9,6))
 r.bone('coffin_plate',(0,20,0),'chest');r.cube('coffin_plate',(-4,15,-4),(8,9,1),'A');r.cube('coffin_plate',(-1,16,-4.75),(2,7,.75),'C')
 for side,s in [('left',1),('right',-1)]:
  r.cube('coffin_plate',(s*4-.75,15,-4.25),(1.5,9,.5),'C')
  r.bone('shoulder_'+side,(s*5,23,0),'chest');r.cube('shoulder_'+side,(s*5-2,22,-3.25),(4,2.25,6.5),'A')
 r.bone('neck',(0,24,0),'chest');r.cube('neck',(-1.5,24,-1.5),(3,1,3),'A')
 # Hollow face mask has genuine recessed eyes, not a printed human portrait.
 face(r,25,0,7);r.cube('head',(-2,26,-4.25),(4,3,.25),'A')
 r.bone('hat',(0,31,0),'head');r.cube('hat',(-5,31,-4),(10,1,8),'C');r.cube('hat',(-3,32,-2),(6,2,4),'A')
 for i,x in enumerate([-4,-2,0,2,4]):
  r.bone('crown_bead_'+str(i),(x,32,-4),'hat');r.cube('crown_bead_'+str(i),(x-.5,28,-5),(1,4,1),'C')
 arms(r,22,6)
 for side,s in [('left',1),('right',-1)]:
  r.bone(side+'_leg',(s*2,9,0),'pelvis');r.cube(side+'_leg',(s*2-1.5,2,-1.5),(3,7,3),'A')
  r.bone(side+'_foot',(s*2,2,-1),side+'_leg');r.cube(side+'_foot',(s*2-1.5,0,-3),(3,2,4))
  r.bone('coffin_skirt_'+side,(s*3,10,0),'pelvis');r.cube('coffin_skirt_'+side,(s*3-2,2,-3.5),(4,9,1));r.cube('coffin_skirt_'+side,(s*3-2,2,2.5),(4,9,1))
  r.bone('binding_'+side,(s*4,24,3),'chest');r.cube('binding_'+side,(s*4-.75,5,3.25),(1.5,19,.5),'C')
 return r.save()

def king():
 r=Rig('dragon_king');r.bone('root',(0,0,0),None);r.bone('body',(0,17,0));r.cube('body',(-6,11,-4),(12,12,8))
 r.bone('lower_coil',(0,10,1),'body');r.cube('lower_coil',(-7,4,-3),(14,7,10),'A');r.cube('lower_coil',(-5,2,0),(10,2,8))
 r.bone('chest',(0,23,0),'body');r.cube('chest',(-6,23,-4),(12,7,8));r.cube('chest',(-3,13,-4.75),(6,15,.75),'C')
 r.bone('neck',(0,29,-2),'chest');r.cube('neck',(-4,29,-5),(8,5,7))
 r.bone('head',(0,34,-3),'neck');r.cube('head',(-5,33,-8),(10,7,8));r.cube('head',(-3,33,-13),(6,3,5),'C')
 for x in [-5,2]:r.cube('head',(x,37,-9),(3,2,2),'A');r.cube('head',(x,36,-9.5),(2,1,.5),'C')
 r.bone('jaw',(0,33,-7),'head');r.cube('jaw',(-3,31.5,-12),(6,1.5,8),'A')
 for side,s in [('left',1),('right',-1)]:
  r.bone('coral_'+side,(s*4,39,-3),'head');r.cube('coral_'+side,(s*4-1,39,-3),(2,5,2),'C');r.cube('coral_'+side,(s*4-1+(s*2),42,-3),(2,2,2),'C')
  r.bone('whisker_'+side,(s*3,33,-10),'jaw');r.cube('whisker_'+side,(s*3-.5,28,-11),(1,5,1),'C')
  r.bone('fin_'+side,(s*6,24,1),'chest');r.cube('fin_'+side,(s*7-1,22,0),(2,6,3),'C');r.cube('fin_'+side,(s*8-1,24,1),(2,3,2))
  r.bone(side+'_arm',(s*6,26,0),'chest');r.cube(side+'_arm',(s*6-1.5,20,-2),(3,6,4))
  r.bone(side+'_forearm',(s*6,20,-1),side+'_arm');r.cube(side+'_forearm',(s*6-1.5,15,-3),(3,5,3),'A')
  r.bone(side+'_hand',(s*6,15,-2),side+'_forearm');r.cube(side+'_hand',(s*6-2,13,-5),(4,2,4))
  for toe in [-1,1]:r.cube(side+'_hand',(s*6+toe-1,13,-6),(1,1,2),'C')
  r.bone(side+'_grip',(s*6,14,-3),side+'_hand')
 parent='lower_coil'
 for i,(y,z,w) in enumerate([(5,6,10),(3,12,7),(2,18,4)]):
  name='tail_'+str(i);r.bone(name,(0,y,z),parent);r.cube(name,(-w/2,y-2,z),(w,4,6));r.cube(name,(-1,y+2,z+1),(2,2,3),'C');parent=name
 return r.save()

def heavenly():
 r=Rig('nine_heaven_general');r.bone('root',(0,0,0),None);r.bone('body',(0,16,0))
 r.bone('pelvis',(0,11,0),'body');r.cube('pelvis',(-4,8,-2.5),(8,5,5),'A')
 r.bone('waist',(0,13,0),'pelvis');r.cube('waist',(-3,13,-2),(6,3,4),'C')
 r.bone('chest',(0,16,0),'waist');r.cube('chest',(-5,16,-3),(10,8,6))
 r.cube('chest',(-4,16,-4),(8,8,1),'A');r.cube('chest',(-1,17,-4.75),(2,6,.75),'C')
 r.bone('neck',(0,24,0),'chest');r.cube('neck',(-1.5,24,-1.5),(3,1,3),'A');face(r,25,0,7)
 r.bone('helmet',(0,31,0),'head');r.cube('helmet',(-4,30.5,-3.25),(8,2,6.5),'A');r.cube('helmet',(-1,31,-4),(2,3,7),'C')
 for side,s in [('left',1),('right',-1)]:
  r.bone('crown_wing_'+side,(s*3,31,0),'helmet');r.cube('crown_wing_'+side,(s*4-1,31,0),(2,4,3),'C');r.cube('crown_wing_'+side,(s*6-1,33,0),(2,3,2),'C')
  r.bone('shoulder_'+side,(s*5,23,0),'chest');r.cube('shoulder_'+side,(s*6-2.5,21,-3.75),(5,3.5,7.5),'A')
  r.cube('shoulder_'+side,(s*6-2,24.5,-3.25),(4,1,6.5),'C')
 arms(r,22,6)
 # Shoulder plates follow the arm rather than tearing off the chest during swings.
 for side in ['left','right']:r.by['shoulder_'+side]['parent']=side+'_arm'
 for side,s in [('left',1),('right',-1)]:
  r.bone(side+'_leg',(s*2.5,9,0),'pelvis');r.cube(side+'_leg',(s*2.5-1.5,5,-1.5),(3,4,3),'A')
  r.bone(side+'_knee',(s*2.5,5,0),side+'_leg');r.cube(side+'_knee',(s*2.5-1.5,1,-2),(3,4,4))
  r.bone(side+'_foot',(s*2.5,1,-1),side+'_knee');r.cube(side+'_foot',(s*2.5-2,0,-3),(4,1.5,5),'A')
  r.bone('skirt_'+side,(s*3,10,0),'pelvis');r.cube('skirt_'+side,(s*3-2,4,-3.25),(4,7,.75));r.cube('skirt_'+side,(s*3-2,4,2.5),(4,7,.75))
  r.bone('thunder_drum_'+side,(s*9,26,5),'chest');r.cube('thunder_drum_'+side,(s*9-3.5,22,4),(7,7,3),'A')
  r.cube('thunder_drum_'+side,(s*9-2.5,23,3.25),(5,5,.75),'C');r.cube('thunder_drum_'+side,(s*9-1,24,2.5),(2,3,.75))
  r.bone('storm_wedge_'+side,(s*9,26,5),'thunder_drum_'+side);r.cube('storm_wedge_'+side,(s*12-1,27,5.25),(2,6,2),'C');r.cube('storm_wedge_'+side,(s*13-1,31,5.25),(2,2,2),'C')
 # Preserve both segmented storm rings and all six thunder blades as real
 # coarse Cuboids behind the body, replacing the old beveled procedural mesh.
 for ring,count,radius,z,color in [('outer',16,18,11,'C'),('inner',12,13,14,'B')]:
  parent='storm_ring_'+ring;r.bone(parent,(0,23,z),'chest')
  for i in range(count):
   a=i*math.tau/count;x=round(math.cos(a)*radius/2)*2;y=23+round(math.sin(a)*radius/2)*2
   r.cube(parent,(x-2,y-2,z),(4,4,2),color)
 for side,s in [('left',1),('right',-1)]:
  for i in range(3):
   name='thunder_blade_'+side+'_'+str(i);x=s*(15+i*4);y=27-i*5;z=9+i
   r.bone(name,(x,y,z),'chest');r.cube(name,(x-1.5,y-3,z),(3,7-i,2))
   r.cube(name,(x-1,y+4-i,z),(2,2,2),'C');r.cube(name,(x-2,y-4,z-.25),(4,2,2.5),'C')
 # Reorder to put every parent before its child in the exported hierarchy.
 ordered=[];waiting=r.bones.copy();seen=set()
 while waiting:
  ready=[b for b in waiting if not b.get('parent') or b['parent'] in seen];assert ready
  for b in ready:ordered.append(b);seen.add(b['name']);waiting.remove(b)
 r.bones=ordered;return r.save()

def imperial_dragon():
 # Read the actual 65-part/64-Cuboid legacy rest mesh exported by native QA.
 # Preserve every volume, then rig its neck and ground the four claw groups.
 source=json.loads((OUT/'source/dragon-emperor-rest-parts.json').read_text())['parts']
 r=Rig('dragon_emperor');r.bone('root',(0,0,0),None);absolute={};mapping={}
 for part in source:
  old=part['name'];leaf=old.split('__')[-1]
  if old=='root':name='body'
  elif old=='root__chest':name='chest'
  elif old=='root__chest__head':name='head'
  elif leaf=='jaw':name='jaw'
  elif leaf.startswith('neck'):name='neck_'+leaf[4:]
  elif leaf.startswith('tail'):name='tail_'+leaf[4:]
  else:
   name=old.removeprefix('root__').replace('__','_').replace('-1','right')
   for side,label in [('leg1','left'),('legright','right')]:
    name=name.replace(side+'_0','front_'+label+'_leg').replace(side+'_1','hind_'+label+'_leg')
  mapping[old]=name
  parent=part.get('parent');base=absolute.get(parent,[0,0,0]);p=[base[i]+part['translation'][i] for i in range(3)];absolute[old]=p
  r.bone(name,[p[0],24-p[1],p[2]],mapping[parent] if parent else 'root',[round(v*180/math.pi,5) for v in part['rotation']])
  if leaf.startswith('neck'):r.by[name].pop('rotation',None)
  # Straight rest shins allow toes to rest on the same plane; knees animate separately.
  if leaf=='shin':r.by[name].pop('rotation',None)
  for box in part['cubes']:
   low,high=box['min'],box['max'];origin=[p[0]+low[0],24-p[1]-high[1],p[2]+low[2]];size=[high[i]-low[i] for i in range(3)]
   color='C' if any(k in name for k in ['horn','fork','claw','backplate','pauldron','spine']) else 'A' if any(k in name for k in ['eye','brow','jaw']) else 'B'
   if leaf=='shin':
    extra=7 if name.startswith('front_') else 1;origin[1]-=extra;size[1]+=extra
   r.cube(name,[round(v,5) for v in origin],[round(v,5) for v in size],color)
  if 'claw' in name:
   extra=7 if name.startswith('front_') else 1;r.by[name]['pivot'][1]-=extra
   for c in r.by[name].get('cubes',[]):c['origin'][1]-=extra
  if 'brow' in name or 'eye' in name:
   # Legacy brows and eyes ended exactly on the skull's front plane.
   r.by[name]['pivot'][2]-=.5
   for c in r.by[name].get('cubes',[]):c['origin'][2]-=.5
 # Four overlapping stepped neck blocks now form a coherent dedicated neck chain.
 for i in range(4):r.by['neck_'+str(i)]['parent']='chest' if i==0 else 'neck_'+str(i-1)
 r.by['head']['parent']='neck_3'
 r.bone('mouth',(0,43.7,-52),'head')
 ordered=[];waiting=r.bones.copy();seen=set()
 while waiting:
  ready=[b for b in waiting if not b.get('parent') or b['parent'] in seen];assert ready
  for b in ready:ordered.append(b);seen.add(b['name']);waiting.remove(b)
 r.bones=ordered
 assert sum(len(b.get('cubes',[])) for b in r.bones)==64
 return r.save()

def dragon_animations(r):
 clips={}
 for name,length in [('idle',2),('walk',1.2),('attack',.3),('cast',1.2),('hurt',.4),('death',1)]:
  ch={}
  def rot(b,a,values):
   vectors=[]
   for v in values:p=[0,0,0];p[a]=v;vectors.append(p)
   ch[b]={'rotation':keys(length,vectors)}
  if name in ['idle','walk']:
   rot('jaw',0,[3,5,3]);rot('neck_0',0,[0,1,0])
   for i in range(9):rot('tail_'+str(i),1,[2+i*.25,-2-i*.25,2+i*.25])
  if name=='walk':
   for side,s in [('left',1),('right',-1)]:
    for end,e in [('front',1),('hind',-1)]:
     rot(end+'_'+side+'_leg',0,[-s*e*12,s*e*12,-s*e*12]);rot(end+'_'+side+'_leg_shin',0,[0,8,0])
  if name in ['attack','cast']:
   rot('neck_0',0,[0,-8,8,0]);rot('neck_3',0,[0,-12,10,0]);rot('jaw',0,[3,3,28,3])
   if name=='attack':rot('front_right_leg',0,[0,-20,30,0]);rot('front_right_leg_shin',0,[0,15,-10,0])
  if name=='hurt':rot('chest',2,[0,5,0])
  if name=='death':ch['body']={'rotation':{'0':[0,0,0],'1':[0,0,55]}};ch['jaw']={'rotation':{'0':[3,0,0],'1':[20,0,0]}}
  clips[name]={'loop':name in ['idle','walk'],'animation_length':length,'bones':ch}
 p=ASSET/f'animations/boss_cuboid/{r.id}.animation.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def animations(r):
 clips={};king=r.id=='dragon_king'
 for name,length in [('idle',2),('walk',1.2),('attack',.3),('cast',1.2),('hurt',.4),('death',1)]:
  ch={}
  def rot(b,a,v):
   frames=[]
   for n in v:
    p=[0,0,0];p[a]=n;frames.append(p)
   ch[b]={'rotation':keys(length,frames)}
  if name in ['idle','walk']:
   ch['chest']={'position':keys(length,[[0,0,0],[0,.2,0],[0,0,0]])}
   if name=='walk':
    for side,s in [('left',1),('right',-1)]:
     rot(side+'_arm',0,[-s*12,s*12,-s*12])
     if not king:rot(side+'_leg',0,[s*16,-s*16,s*16])
   if king:
    for i in range(3):rot('tail_'+str(i),1,[2,-2,2])
  if name in ['attack','cast']:
   rot('chest',1,[0,-10,14,0]);rot('right_arm',0,[0,-25,65,0]);rot('left_arm',0,[0,-15,40,0])
   rot('jaw',0,[0,-5,20 if king else 5,0])
   if king:rot('head',0,[0,-10,8,0])
  if name=='hurt':rot('chest',2,[0,8,0])
  if name=='death':
   ch['chest']={'rotation':{'0':[0,0,0],'1':[20,0,0]}}
   if king:
    ch['jaw']={'rotation':{'0':[0,0,0],'1':[20,0,0]}}
  if r.id=='eunuch_mastermind':
   for side,s in [('left',1),('right',-1)]:
    if name in ['idle','walk','cast']:rot(side+'_sleeve',2,[s*2,-s*2,s*2])
  if r.id=='undead_first_emperor' and name in ['idle','walk']:
   for side,s in [('left',1),('right',-1)]:rot('binding_'+side,0,[2,-2,2])
  if r.id=='nine_heaven_general':
   if name in ['idle','walk','cast']:
    rot('storm_ring_outer',2,[0,8,0]);rot('storm_ring_inner',2,[0,-8,0])
   for side,s in [('left',1),('right',-1)]:
    if name in ['idle','walk','cast']:rot('thunder_drum_'+side,2,[s*2,-s*2,s*2])
    if name in ['idle','cast']:
     for i in range(3):rot('thunder_blade_'+side+'_'+str(i),2,[s*2,-s*2,s*2])
    if name=='walk':rot(side+'_knee',0,[0,8,0])
    if name=='cast':rot('storm_wedge_'+side,0,[0,-10,15,0]);rot(side+'_arm',0,[0,-40,-100,0])
  clips[name]={'loop':name in ['idle','walk'],'animation_length':length,'bones':ch}
 p=ASSET/f'animations/boss_cuboid/{r.id}.animation.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def main():
 OUT.mkdir(parents=True,exist_ok=True);manifest={}
 for r in [eunuch(),emperor(),king(),heavenly(),imperial_dragon()]:
  (dragon_animations if r.id=='dragon_emperor' else animations)(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),'atlas':[16,16],'palette':SPECS[r.id][0]+['#ffffff'],'animationNames':['idle','walk','attack','cast','hurt','death'],'specialSkillClock':'pending; not adding server/AI sync in art task'}
 (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Generated original boss resources:',', '.join(manifest))

if __name__=='__main__':main()
