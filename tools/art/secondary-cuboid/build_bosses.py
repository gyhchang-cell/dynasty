"""Original species/profession-specific cuboid bosses. Actual final 16px assets."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from build_models import ASSET,keys

OUT=Path(__file__).resolve().parents[3]/'docs/art/cod6-cuboid-v1'
SPECS={
 'eunuch_mastermind':(['#302638','#6e4f78','#dbc79b'],['..CC..','.AAAA.','..CC..','CBBCBC','.BBBB.','.AAAA.']),
 'undead_first_emperor':(['#282e35','#5c7166','#c6b077'],['.CCCC.','CBAABC','.BAAB.','CBBCBC','.BBBB.','CAAAAC']),
 'dragon_king':(['#253743','#487c7b','#c4b17b'],['C....C','.BC CB.'.replace(' ',''),'BABBAB','.BCCB.','BBBBBB','.BCCB.']),
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
  g={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.boss_cuboid.'+self.id,'texture_width':16,'texture_height':16,'visible_bounds_width':4,'visible_bounds_height':4,'visible_bounds_offset':[0,1.5,0]},'bones':self.bones}]}
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
  clips[name]={'loop':name in ['idle','walk'],'animation_length':length,'bones':ch}
 p=ASSET/f'animations/boss_cuboid/{r.id}.animation.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'format_version':'1.8.0','animations':clips},indent=2)+'\n')

def main():
 OUT.mkdir(parents=True,exist_ok=True);manifest={}
 for r in [eunuch(),emperor(),king()]:
  animations(r);manifest[r.id]={'bones':len(r.bones),'cuboids':sum(len(b.get('cubes',[])) for b in r.bones),'atlas':[16,16],'palette':SPECS[r.id][0]+['#ffffff'],'animationNames':['idle','walk','attack','cast','hurt','death'],'specialSkillClock':'pending; not adding server/AI sync in art task'}
 (OUT/'model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Generated original boss resources:',', '.join(manifest))

if __name__=='__main__':main()
