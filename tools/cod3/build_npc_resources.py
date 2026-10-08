"""Deterministic articulated Minecraft NPC rigs; each role has its own anatomy/prop silhouette."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw
base=Path('src/main/resources/assets/dynasty')
roles=json.loads((base.parent.parent/'data/dynasty/cod3/catalog.json').read_text())['npcs']
for index,row in enumerate(roles):
 role=row['id'];bones=[]
 stature=.76 if role=='xiaoyuanzi' else .91 if role=='hei_po' else 1.02 if role in ['ba_tu','han_chong'] else 1
 breadth=1.23 if role in ['lao_chen','ba_tu','baibao_jin'] else .86 if role in ['a_ji','chu_nongyu','hong_ling'] else 1
 def bone(name,parent,pivot,cubes=[],rotation=None):
  b=dict(name=name,pivot=pivot,cubes=cubes)
  if parent:b['parent']=parent
  if rotation:b['rotation']=rotation
  bones.append(b)
 def cube(o,s,uv=[0,0],rotation=None,pivot=None):
  c=dict(origin=o,size=s,uv=uv)
  if rotation:c.update(rotation=rotation,pivot=pivot or o)
  return c
 bone('root',None,[0,0,0]);bone('pelvis','root',[0,11,0],[cube([-3.2,10,-2],[6.4,3,4],[0,32]),cube([-3.6,12,-2.3],[7.2,1,4.6],[32,32])])
 bone('waist','pelvis',[0,13,0],[cube([-2.7,13,-1.8],[5.4,3,3.6],[0,40])])
 bone('chest','waist',[0,15,0],[cube([-3.5*breadth,16,-2.3],[7*breadth,4,4.6],[0,48]),cube([-3.8*breadth,20,-2],[7.6*breadth,2,4],[0,58]),cube([-3,16,1.6],[6,5,1],[40,48])],[-12 if role=='hei_po' else 0,0,0])
 bone('neck','chest',[0,22,0],[cube([-1.2,22,-1],[2.4,1.7,2],[64,0])])
 bone('head','neck',[0,23,0],[cube([-2.5,24,-2.1],[5,4.8,4.2],[64,8]),cube([-2.1,23,-2.2],[4.2,1.5,3.8],[64,20]),cube([-.55,25,-2.6],[1.1,1.6,.8],[86,8]),cube([-2.3,28.8,-2],[4.6,.8,4],[64,28])])
 hair=[cube([-2.7,28.3,-2.25],[5.4,1.3,4.5],[96,8]),cube([-2.65,25.5,1.8],[5.3,3.5,1],[96,18])]
 if role in ['lao_chen','han_chong','ba_tu']:hair.extend([cube([-2.3,23,-2.5],[4.6,1.8,.7],[96,24]),cube([-1.6,21.8,-2.2],[3.2,1.5,.8],[96,24])])
 bone('hair','head',[0,28,0],hair)
 if role=='lao_chen':bone('eyepatch','head',[-1,26,-2.3],[cube([-2.25,26,-2.35],[1.8,.8,.2],[96,30])])
 if role=='chu_nongyu':bone('blindfold','head',[0,26,-2.3],[cube([-2.55,26,-2.3],[5.1,1,.3],[100,38])])
 hat=role in ['han_chong','baibao_jin','cao_chengfu','sai_banxian','ba_tu','yan_chifeng','huang_laohan']
 if hat:bone('hat','head',[0,29,0],[cube([-3.5,29,-3],[7,.6,6],[0,72]),cube([-2.5,29.6,-2],[5,1.8,4],[20,72]),cube([-1.4,31.4,-1],[2.8,.6,2],[40,72])])
 else:bone('hairpin','head',[0,29,0],[cube([-3,29.5,0],[6,.35,.35],[96,40]),cube([-1,29.2,.5],[2,2,1.6],[96,18])])
 for side,sgn in [('left',1),('right',-1)]:
  x=sgn*(4*breadth)
  bone(side+'_shoulder','chest',[x,21,0],[cube([x-1.5,19.8,-1.9],[3,2.5,3.8],[0,82])])
  bone(side+'_upper_arm',side+'_shoulder',[x,20.4,0],[cube([x-1.1,15.4,-1.3],[2.2,5,2.6],[20,82])])
  bone(side+'_elbow',side+'_upper_arm',[x,15.4,0],[cube([x-1.05,14.7,-1.25],[2.1,1.4,2.5],[36,82])])
  bone(side+'_forearm',side+'_elbow',[x,14.8,0],[cube([x-1.05,10.8,-1.2],[2.1,4,2.4],[48,82])])
  bone(side+'_wrist',side+'_forearm',[x,10.8,0],[cube([x-.8,10.2,-.9],[1.6,.6,1.8],[64,38])])
  bone(side+'_hand',side+'_wrist',[x,10.2,0],[cube([x-.9,8.8,-1],[1.8,1.4,2],[64,42]),cube([x-.95,9.2,-1.4],[.5,.9,.7],[84,42])])
  legx=sgn*1.8
  bone(side+'_thigh','pelvis',[legx,11,0],[cube([legx-1.45,6.2,-1.5],[2.9,4.8,3],[0,96])])
  bone(side+'_knee',side+'_thigh',[legx,6.2,0],[cube([legx-1.3,5.2,-1.55],[2.6,1.2,3.1],[20,96])])
  bone(side+'_shin',side+'_knee',[legx,5.4,0],[cube([legx-1.15,1,-1.25],[2.3,4.4,2.5],[36,96])])
  bone(side+'_ankle',side+'_shin',[legx,1,0],[cube([legx-1.15,.7,-1.3],[2.3,.5,2.6],[48,96])])
  bone(side+'_foot',side+'_ankle',[legx,.8,0],[cube([legx-1.25,0,-2.6],[2.5,1,4],[64,96])])
 # Independent visual props and clothing, rather than recolouring the same silhouette.
 prop=[]
 if role=='lao_chen':prop=[cube([-1.5,10,-3.1],[3,8,.6],[0,110]),cube([4,8,-1],[.6,6,.6],[0,72]),cube([3.2,13,-2],[2.4,1.6,2],[40,48])]
 elif role=='han_chong':prop=[cube([-4,17,-2.8],[8,4,.4],[0,58]),cube([4.5,7,-1],[.5,8,.5],[40,48])]
 elif role=='qingxuanzi':prop=[cube([-4,8,-2.5],[8,7,1],[0,110]),cube([-5.5,12,-1],[1.5,2,1.5],[0,48]),cube([-5.2,14,-.8],[.9,1,.9],[0,48])]
 elif role=='baibao_jin':prop=[cube([-4,11,2.5],[8,10,3],[0,110]),cube([-5,10,2],[2,4,3],[0,72]),cube([3,10,-3],[3,.6,2],[0,72])]
 elif role=='a_ji':prop=[cube([-4,17,-2.8],[3,3,.4],[40,48]),cube([2,18,-2.8],[2,2,.4],[40,48])]
 elif role=='hei_po':prop=[cube([-2,9,-3],[4,2,3],[64,20]),cube([-4,19,-3],[1,3,1],[40,48])]
 elif role=='cao_chengfu':prop=[cube([4,9,-1],[.5,8,.5],[0,72]),cube([3.4,6,-1.6],[1.7,4,1.7],[64,28]),cube([-4,9,-2.6],[8,7,1],[0,110])]
 elif role=='hong_ling':prop=[cube([-5,7,-3],[3,3,3],[0,72]),cube([-5,10,-3],[.4,2,3],[0,72]),cube([-5,12,-3],[3,.4,3],[0,72])]
 elif role=='chu_nongyu':prop=[cube([-6,10,-3],[12,1.5,2.8],[0,72]),cube([-5.5,11.5,-3],[11,.2,2.6],[64,28]),cube([-4,8,-2.6],[8,8,1],[0,110])]
 elif role=='xiaoyuanzi':prop=[cube([-3,12,2.2],[6,8,3],[0,72]),cube([4,8,-1],[.5,6,.5],[0,72]),cube([3.5,13,-1.2],[1.5,1.5,.5],[40,48])]
 elif role=='mo_jizi':prop=[cube([3.4,11,-1.8],[3.2,9,3.6],[40,48]),cube([2.9,15,-2.2],[4.2,1.2,4.4],[40,48]),cube([-2.7,25.8,-2.8],[2.5,1.4,.6],[40,48])]
 elif role=='sai_banxian':prop=[cube([-2.3,26.1,-2.5],[1.7,.8,.4],[96,30]),cube([.6,26.1,-2.5],[1.7,.8,.4],[96,30]),cube([4,6,0],[.5,20,.5],[0,72]),cube([4.3,17,0],[5,8,.3],[64,28])]
 elif role=='ba_tu':prop=[cube([-5,20,-2.8],[10,2,6],[96,24]),cube([-5,10,3],[10,2,1],[0,72]),cube([4,8,-2],[.4,12,.4],[0,72])]
 elif role=='yan_chifeng':prop=[cube([-4,10,2],[8,10,.5],[0,110]),cube([-2,9,2.6],[.6,12,.6],[40,48]),cube([2,9,2.6],[.6,12,.6],[40,48])]
 else:prop=[cube([4,0,0],[.45,30,.45],[0,72]),cube([-3,7,-2.5],[6,3,1],[0,110])]
 bone('equipment','chest',[0,20,0],prop)
 # Anatomy remains articulated at knees/elbows; stature modifies the full skeleton.
 for b in bones:
  b['pivot']=[x*stature for x in b['pivot']]
  for c in b.get('cubes',[]):
   c['origin']=[x*stature for x in c['origin']];c['size']=[x*stature for x in c['size']]
 geo={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.npc_'+role,'texture_width':128,'texture_height':128,'visible_bounds_width':3,'visible_bounds_height':4,'visible_bounds_offset':[0,1.5,0]},'bones':bones}]}
 animations={}
 for state in ['idle','walk','turn','talk','work','react','rain','night','danger','player_near','player_holds_special']:
  movements={'chest':{'rotation':{'0.0':[0,0,-1],'1.0':[0,0,1],'2.0':[0,0,-1]}}}
  if state=='walk':
   for part in ['left_thigh','right_upper_arm']:movements[part]={'rotation':{'0.0':[24,0,0],'0.5':[-24,0,0],'1.0':[24,0,0]}}
   for part in ['right_thigh','left_upper_arm']:movements[part]={'rotation':{'0.0':[-24,0,0],'0.5':[24,0,0],'1.0':[-24,0,0]}}
   movements['left_knee']={'rotation':[12 if role=='han_chong' else 4,0,0]}
  if state in ['talk','player_near','turn']:movements['head']={'rotation':{'0.0':[0,-8,0],'1.0':[4,8,0],'2.0':[0,-8,0]}}
  if state=='work':movements['right_forearm']={'rotation':{'0.0':[-25,0,-8],'0.5':[-65,0,-8],'1.0':[-25,0,-8]}};movements['left_forearm']={'rotation':[-40,0,10]}
  if state in ['react','rain','danger']:movements['left_upper_arm']={'rotation':[-95,0,-25]};movements['head']={'rotation':[12,0,0]}
  if state=='player_holds_special':movements['chest']={'rotation':[18,0,0]};movements['right_forearm']={'rotation':[-45,0,0]}
  if state=='night':movements['right_forearm']={'rotation':[-30,0,0]}
  animations['animation.npc.'+state]={'loop':True,'animation_length':1 if state in ['walk','work'] else 2,'bones':movements}
 for rel,obj in [('geo/npc/'+role+'.geo.json',geo),('animations/npc/'+role+'.animation.json',{'format_version':'1.8.0','animations':animations})]:
  p=base/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
 im=Image.new('RGB',(128,128));draw=ImageDraw.Draw(im)
 cloth=[(82,82,68),(86,93,101),(46,106,82),(122,98,65),(74,68,53),(56,70,107),(86,47,101),(149,83,91),(40,45,53),(121,125,110),(80,98,98),(70,74,78),(92,73,54),(136,47,42),(76,94,82)][index]
 for y in range(128):
  for x in range(128):
   c=cloth if x<64 else (187,145,109) if x<96 else (45,40,35)
   shade=((x*11+y*7+index*13)%7)-3
   im.putpixel((x,y),tuple(max(0,min(255,v+shade)) for v in c))
 draw.rectangle((64,0,95,48),fill=(185,145,110));draw.rectangle((96,8,127,31),fill=(38,32,30))
 draw.rectangle((0,72,63,81),fill=(94,69,42));draw.rectangle((40,48,63,71),fill=(110,119,120));draw.rectangle((64,28,95,31),fill=(205,202,181))
 for y in [35,60,111,118]:draw.line((0,y,63,y),fill=(173,143,79),width=1)
 # Front head UV: brow/eyes/mouth, with an eye patch or blindfold by identity.
 draw.line((68,13,69,13),fill=(69,47,35));draw.line((71,13,73,13),fill=(69,47,35))
 draw.point((69,14),fill=(28,26,23));draw.point((72,14),fill=(28,26,23));draw.line((70,16,71,16),fill=(119,75,57))
 if role=='lao_chen':draw.rectangle((68,13,69,15),fill=(26,26,25))
 if role=='chu_nongyu':draw.rectangle((68,13,73,14),fill=(36,30,38))
 for y in range(49,58,3):
  for x in range(1,31,5):draw.line((x,y,x+1,y+1),fill=tuple(min(255,v+18) for v in cloth))
 if role in ['han_chong','mo_jizi']:
  for x in range(42,62,4):draw.line((x,49,x,69),fill=(150,157,151))
 p=base/('textures/entity/npc/'+role+'.png');p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 print(role,len(bones),sum(len(b.get('cubes',[])) for b in bones))
