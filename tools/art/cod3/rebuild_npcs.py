"""Original Cuboid NPC art with natural, deterministic per-face pixel atlases.

Bedrock runtime coordinates, not Blockbench editor coordinates. This generator
only writes the fifteen NPC geo/animation/textures and its own authoring report.
No gameplay, entity IDs, AI, quests, renderer or controller changes.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / 'src/main/resources/assets/dynasty'
DOC = ROOT / 'docs/art/cod3-npc-v3'
STATES = 'idle walk turn talk work react rain night danger player_near player_holds_special'.split()
# Height is applied to every cube, pivot and locator together. Adult bodies stay
# close to 1.9m, with intentional silhouette differences and a 1.4m child.
ROLES = {
 'baibao_jin': (1, 10, 7, '#976132', 'wide belly / three stacked packs / abacus'),
 'hei_po': (.91, 7, 5, '#334f80', 'hunched upper back / silver braid / shoulder centipede'),
 'mo_jizi': (1, 7.5, 5, '#39736c', 'left mechanical chest and claw / three stepped lenses'),
 'lao_chen': (.98, 9, 6, '#845132', 'thick bare forearms / apron / one eye / forged hammer'),
 'han_chong': (1.01, 8.5, 5.5, '#586573', 'thick lamellar plates / ear helmet / ring pommel / limp'),
 'qingxuanzi': (1, 7, 4.5, '#396c4b', 'narrow long robe / bamboo hairpin / stepped gourd / scroll'),
 'a_ji': (.98, 5.5, 3.5, '#75654b', 'thin waist / tucked shoulders / asymmetric broken armour'),
 'cao_chengfu': (1, 7, 4.5, '#613b75', 'tall ceremonial cap / wide sleeves / purple robe / whisk'),
 'hong_ling': (.98, 6.5, 4.5, '#a14b52', 'flared dress / flower basket / hidden articulated snake tail'),
 'chu_nongyu': (1, 6.5, 4.5, '#303947', 'white blindfold / long black sleeves / seven-string zither'),
 'xiaoyuanzi': (.73, 7, 5, '#73796b', 'large child head / twin hair buns / medicine basket / shovel'),
 'sai_banxian': (.99, 7, 4.5, '#4c515d', 'stepped dark lenses / long robe / tall white divination banner'),
 'ba_tu': (1.02, 10, 7, '#72523c', 'broad fur shoulders / wolf pelt cap / heavy stepped bow'),
 'yan_chifeng': (1, 7, 4.5, '#a83d32', 'broken stepped straw hat / split red cape / twin swords'),
 'huang_laohan': (.96, 8, 5, '#3e6b62', 'bare calves / short water jacket / wide boat hat / bamboo pole'),
}
# Original frontal portraits double as a four-colour face-UV atlas. Each cell is
# a real 2x2 pixel region, with a two-pixel white margin on every edge.
PORTRAITS = {
 'baibao_jin':['........','..DDDD..','..DSSD..','..SSSS..','.CCCCCC.','.SLCCLS.','..D..D..','........'],
 'hei_po':['........','...DDD..','..DSSS..','..SSL...','.DCCCCD.','.SCLLCS.','..D..D..','........'],
 'mo_jizi':['........','..DDDD..','..DSSL..','..SSSL..','.DCCLLD.','.SCCLLL.','..D..D..','........'],
 'lao_chen':['........','..DDDD..','..DSDS..','..DDDD..','.SCCCCS.','.SCLLCS.','..D..D..','........'],
 'han_chong':['........','..DLLD..','..DSSD..','..SSSS..','.DCLLCD.','.SCLLCS.','..D..D..','........'],
 'qingxuanzi':['........','..DCCD..','..DSSD..','..SSSS..','.DCCCCD.','.SCLLCS.','..D..D..','........'],
 'a_ji':['........','..DDDD..','..DSSD..','...SS...','..LCCC..','..SCLS..','..D..D..','........'],
 'cao_chengfu':['........','.DDDDDD.','..DSSD..','..SSSS..','.CCCCCC.','.CCLLCC.','..D..D..','........'],
 'hong_ling':['........','..DDDD..','..DSSD..','..SSSS..','.DCCCCD.','.SCLLCS.','..CCCC..','........'],
 'chu_nongyu':['........','..DDDD..','..LLLL..','..SSSS..','.DCCCCD.','.SCLLCS.','..CCCC..','........'],
 'xiaoyuanzi':['........','..D..D..','..DSSD..','..SSSS..','..CCCC..','.SCLLCS.','..D..D..','........'],
 'sai_banxian':['........','..DDDD..','..DSDS..','..SSSS..','.DCCCCL.','.SCLLCL.','..D..D..','........'],
 'ba_tu':['........','..DLLD..','..DSSD..','..SSSS..','.DLLLLD.','.SCLLCS.','..D..D..','........'],
 'yan_chifeng':['........','.SSSSSS.','..DSSD..','..SSSS..','.DCCCCD.','.SCLLCS.','..D..D..','........'],
 'huang_laohan':['........','.SSSSSS.','..DSSD..','..SSSS..','.DCCCCD.','.SCLLCS.','..S..S..','........'],
}
MATERIALS={'S':'skin','C':'cloth','D':'dark','L':'light'}

class Rig:
 def __init__(self, role):
  self.role = role
  self.scale, self.width, self.depth, self.colour, self.design = ROLES[role]
  self.bones = []
  self.names = {}
  self.props = []
  self.materials = {}
  self.uv={}
  for y,row in enumerate(PORTRAITS[role]):
   for x,letter in enumerate(row):
    if letter in MATERIALS:self.uv.setdefault(MATERIALS[letter],[x*2,y*2])
  assert set(self.uv)=={'skin','cloth','dark','light'}
 def bone(self, name, parent, pivot, rotation=None):
  b = {'name': name, 'pivot': list(pivot)}
  if parent: b['parent'] = parent
  if rotation: b['rotation'] = rotation
  self.bones.append(b); self.names[name] = b
  return name
 def box(self, bone, origin, size, material='cloth', rotation=None, pivot=None):
  assert bone in self.names
  assert all(x > 0 for x in size)
  faces = {face: {'uv': self.uv[material][:], 'uv_size': [2, 2]} for face in ('north','south','east','west','up','down')}
  c = {'origin': list(origin), 'size': list(size), 'uv': faces}
  if rotation: c.update(rotation=rotation, pivot=list(pivot or origin))
  self.names[bone].setdefault('cubes', []).append(c)
  self.materials.setdefault(bone, []).append(material)
 def prop(self, name, parent, pivot):
  self.props.append(name)
  self.bone(name, parent, pivot)
  self.names[name]['locators'] = {'grip_'+name: list(pivot)}
  return name
 def anatomy(self):
  r=self.role; w=self.width; d=self.depth
  self.bone('root',None,[0,0,0]);self.bone('pelvis','root',[0,11,0])
  self.box('pelvis',[-w*.43,10,-d*.43],[w*.86,4,d*.86],'dark')
  self.box('pelvis',[-w*.48,13,-d*.48],[w*.96,1,d*.96],'cloth')
  self.bone('waist','pelvis',[0,14,0]);self.box('waist',[-w*.34,14,-d*.34],[w*.68,3,d*.68])
  self.bone('chest','waist',[0,17,0],[18,0,0] if r=='hei_po' else [7,0,0] if r=='a_ji' else None)
  self.box('chest',[-w/2,17,-d/2],[w,5.5,d])
  self.box('chest',[-w*.44,22.5,-d*.42],[w*.88,1,d*.84])
  self.bone('neck','chest',[0,23,0]);self.box('neck',[-1,23,-1],[2,1.5,2],'skin')
  self.bone('head','neck',[0,24,0]);hw=6 if r=='xiaoyuanzi' else 5 if r=='a_ji' else 5.5
  self.box('head',[-hw/2,24,-2.5],[hw,5.5,5],'skin')
  self.box('head',[-1,23.5,-2],[2,1,3.5],'skin')
  self.box('head',[-.5,25.5,-3],[1,1.5,.5],'skin')
  # Eyes and age cues are painted on the head UV, avoiding floating black eye cubes.
  self.bone('hair','head',[0,29,0]);self.box('hair',[-hw/2-.25,29,-2.6],[hw+.5,1,5.2],'dark')
  self.box('hair',[-hw/2-.25,25.5,2.25],[hw+.5,4,.75],'dark')
  self.bone('equipment','chest',[0,20,0])
  for side,sign in (('left',1),('right',-1)):
   x=sign*(w/2+1.25); arm=3 if r in ('lao_chen','ba_tu') else 1.75 if r=='a_ji' else 2.5
   self.bone(side+'_shoulder','chest',[x,22,0])
   self.box(side+'_shoulder',[x-arm/2,20.5,-1.75],[arm,2.5,3.5])
   self.bone(side+'_upper_arm',side+'_shoulder',[x,21,0]);self.box(side+'_upper_arm',[x-arm/2,16,-1.5],[arm,5,3],'skin' if r in ('lao_chen','huang_laohan') else 'cloth')
   self.bone(side+'_elbow',side+'_upper_arm',[x,16,0]);self.box(side+'_elbow',[x-arm/2,15.5,-1.4],[arm,1,2.8],'dark')
   self.bone(side+'_forearm',side+'_elbow',[x,15.5,0]);self.box(side+'_forearm',[x-arm/2,11.5,-1.5],[arm,4,3],'skin' if r in ('lao_chen','huang_laohan') else 'cloth')
   self.bone(side+'_wrist',side+'_forearm',[x,11.5,0]);self.box(side+'_wrist',[x-1,11,-1.3],[2,.75,2.6],'dark')
   self.bone(side+'_hand',side+'_wrist',[x,11,0]);self.box(side+'_hand',[x-1,9.5,-1.25],[2,1.5,2.5],'skin')
   self.names[side+'_hand']['locators']={side+'_grip':[x,10.25,0]}
   lx=sign*(w*.22);lw=2 if r=='a_ji' else 3
   self.bone(side+'_thigh','pelvis',[lx,11,0]);self.box(side+'_thigh',[lx-lw/2,6,-1.6],[lw,5,3.2],'skin' if r=='huang_laohan' else 'dark')
   self.bone(side+'_knee',side+'_thigh',[lx,6,0]);self.box(side+'_knee',[lx-lw/2,5.5,-1.6],[lw,1,3.2],'skin' if r=='huang_laohan' else 'cloth')
   self.bone(side+'_shin',side+'_knee',[lx,5.5,0]);self.box(side+'_shin',[lx-lw/2,1,-1.4],[lw,4.5,2.8],'skin' if r=='huang_laohan' else 'dark')
   self.bone(side+'_ankle',side+'_shin',[lx,1,0]);self.box(side+'_ankle',[lx-lw/2,.75,-1.4],[lw,.5,2.8],'skin')
   self.bone(side+'_foot',side+'_ankle',[lx,.8,0]);self.box(side+'_foot',[lx-lw/2-.25,0,-2.5],[lw+.5,1,4],'dark')
 def skirt(self, material='cloth', width=None):
  w=width or self.width+1
  for sign in (-1,1):
   b=self.bone(('left' if sign==1 else 'right')+'_robe','pelvis',[sign*w/4,13,0])
   self.box(b,[0 if sign==1 else -w/2,5,-3],[w/2-.25,8,6],material)
  self.box('pelvis',[-w/2,11.5,-3.15],[w,1, .5],'dark')
 def beard(self):
  self.box('hair',[-2.5,23,-3],[5,2,.75],'dark');self.box('hair',[-1.5,21.5,-2.8],[3,1.5,.75],'dark')
 def hat(self, kind):
  self.bone('hat','head',[0,29.5,0])
  if kind=='helmet':
   self.box('hat',[-3.5,29,-3],[7,2,6],'light');self.box('hat',[-2.5,31,-2],[5,.75,4],'dark')
   for x in (-3.75,2.75):self.box('hat',[x,25.5,-1],[1,4,3.5],'light')
   self.box('hat',[-.5,27,-3.1],[1,4,.75],'light')
  elif kind=='official':
   self.box('hat',[-3,29,-2.75],[6,2,5.5],'dark');self.box('hat',[-2,31,-2],[4,1,4],'cloth')
   for x in (-6,3):self.box('hat',[x,29.5,-.5],[3,.75,1],'dark')
  elif kind=='wolf':
   self.box('hat',[-3.5,28.5,-3],[7,2,6],'light');self.box('hat',[-2.5,28,-4],[5,1.5,2],'light')
   for x in (-3,2):self.box('hat',[x,30,-1],[1,2,2],'dark')
  elif kind=='straw':
   self.box('hat',[-5,29,-4.5],[10,.75,9],'skin');self.box('hat',[-3.5,29.75,-3],[7,.75,6],'skin');self.box('hat',[-2,30.5,-1.5],[4,1,3],'skin')
   if self.role=='yan_chifeng':self.box('hat',[-5.75,28.5,-1],[2,.75,3],'dark')
  else:
   self.box('hat',[-3.25,29,-2.75],[6.5,.75,5.5],'dark');self.box('hat',[-2.5,29.75,-2],[5,1.75,4],'cloth')
 def handx(self, side):return (1 if side=='left' else -1)*(self.width/2+1.25)
 def pole(self, name, side, height, material='skin'):
  x=self.handx(side);self.prop(name,side+'_hand',[x,10.25,0]);self.box(name,[x-.5,3,-.5],[1,height,1],material)
  return x
 def costume(self):
  r=self.role;w=self.width
  if r=='baibao_jin':
   self.box('waist',[-5,13.5,-3.5],[10,5,7]);self.box('chest',[-5.5,18,-3],[11,4.5,6]);self.hat('merchant')
   b=self.bone('pack','chest',[0,20,3]);
   for o,s in [([-4,12,3],[8,6,4]),([-3.5,18,3],[7,5,5]),([-3,23,3],[6,3,3])]:self.box(b,o,s,'skin')
   for x in (-4,3):self.box(b,[x,12,2.5],[1,14,1],'dark')
   for x in (-6,4):self.box('pelvis',[x,10,0],[2,4,3],'skin');self.box('pelvis',[x,9.5,-1],[2,1,1],'light')
   x=self.handx('left');self.prop('abacus','left_hand',[x,10.25,0]);self.box('abacus',[x-3,9,-3],[6,3.5,1],'dark')
   for dx in (-2.25,-.25,1.75):self.box('abacus',[x+dx,9.75,-3.2],[1.5,2,.5],'skin')
   self.box('left_hand',[x-1.25,10,-1.5],[.75,1,.75],'cloth')
  elif r=='hei_po':
   self.skirt(width=8.5);self.box('chest',[-3.5,19,2],[7,4.5,2],'cloth')
   self.bone('braid','head',[0,28,2.5]);
   for i in range(3):self.box('braid',[-.75,21+i*2,2.8+i*.25],[1.5,2,1.5],'light')
   self.box('neck',[-2,23,-1.5],[4,.75,3],'light')
   self.bone('centipede','left_shoulder',[4,22,0]);
   for i in range(3):self.box('centipede',[3,21+i*.5,-2+i*1.5],[2,1,2],'skin')
   for x in (-4.5,3):self.box('pelvis',[x,10,-2],[1.5,2.5,2],'light')
   x=self.handx('left');self.prop('medicine_bowl','left_hand',[x,10.25,0]);self.box('medicine_bowl',[x-2,9,-4],[4,2.5,3],'dark');self.box('medicine_bowl',[x-1.5,11.5,-3.5],[3,.5,2],'cloth')
   x=self.handx('right');self.prop('stirrer','right_hand',[x,10.25,0]);self.box('stirrer',[x-.25,8,-.25],[.5,5,.5],'skin')
  elif r=='mo_jizi':
   self.box('chest',[0,17,-3],[4.5,6,6],'light');self.box('chest',[.5,18,-3.75],[3,3,.75],'dark')
   x=self.handx('left');self.box('left_shoulder',[x-2,20,-2.5],[4,3,5],'light')
   self.box('left_upper_arm',[x-1.5,16.5,-2],[3,4,4],'light');self.box('left_elbow',[x-2,15,-2],[4,2,4],'dark')
   self.box('left_forearm',[x-1.75,11.5,-2],[3.5,4,4],'light')
   self.prop('claw','left_hand',[x,10.25,0]);self.box('claw',[x-1.5,9,-1.5],[3,1.5,3],'light')
   for side,dx in (('claw_outer',1.5),('claw_inner',-2.5)):
    self.bone(side,'claw',[x+dx,10,0]);self.box(side,[x+dx,7,-1],[1,3,2],'dark');self.box(side,[x+dx,6.5,-1],[1.5,1,2],'light')
   self.bone('goggles','head',[0,27,-3]);
   for i in range(3):self.box('goggles',[1-i,26.5-i*.5,-3.25-i*.75],[2,2,.75],'light')
   self.box('goggles',[-2.5,27.5,-2.8],[5,1,.5],'dark')
   self.bone('powerpack','chest',[0,21,2.5]);self.box('powerpack',[-2,18,2.5],[4,5,3],'dark');self.box('powerpack',[-1.5,23,3],[3,2,2],'light')
   self.pole('spanner','right',10,'light')
  elif r=='lao_chen':
   self.beard();self.bone('eyepatch','head',[1.5,27,-2.5]);self.box('eyepatch',[.5,26.5,-2.65],[2,1.5,.2],'dark')
   self.box('chest',[-3,17,-3.15],[6,6,.75],'dark');self.box('waist',[-3,11,-3],[6,6,.75],'cloth')
   for x in (-2.75,2):self.box('chest',[x,22,-3],[.75,1.5,.75],'dark')
   self.box('right_shoulder',[-7,21,-1.8],[2,.75,.2],'dark')
   x=self.pole('hammer','right',9,'skin');self.box('hammer',[x-2,11,-2],[4,3,4],'light')
  elif r=='han_chong':
   self.hat('helmet');self.beard()
   self.box('chest',[-4.5,17,-3.5],[9,5,1],'dark')
   for y in (17.5,20):
    for x in (-4,-1,2):self.box('chest',[x,y,-3.75],[2.5,2,.75],'light')
   for side in ('left','right'):
    x=self.handx(side);self.box(side+'_shoulder',[x-1.75,20,-2],[3.5,2.5,4],'light');self.box(side+'_thigh',[x*.35-1.75,7,-2.1],[3.5,4,.75],'light')
   x=self.pole('sabre','right',8,'dark');self.box('sabre',[x-.5,3,-1],[1,6,2],'light');self.box('sabre',[x-1.5,9,-1],[3,.75,2],'skin')
   for dx,dy,sx,sy in [(-1,11,2,.5),(-1,13,2,.5),(-1,11,.5,2),( .5,11,.5,2)]:self.box('sabre',[x+dx,dy,-.5],[sx,sy,1],'light')
  elif r=='qingxuanzi':
   self.skirt(width=8);self.bone('hairpin','head',[0,30,0]);self.box('hairpin',[-3.5,30,-.5],[7,.75,1],'cloth')
   self.bone('gourd','pelvis',[-4,13,0]);self.box('gourd',[-5,10,0],[2,3,2],'skin');self.box('gourd',[-4.75,13,.25],[1.5,2,1.5],'skin')
   x=self.handx('left');self.prop('scroll','left_hand',[x,10.25,0]);self.box('scroll',[x-2.5,9,-2],[5,3.5,1],'skin')
   for dx in (-2.5,1.5):self.box('scroll',[x+dx,8.75,-2.5],[1,4,2],'dark')
  elif r=='a_ji':
   self.box('chest',[-3,18,-2.2],[2.5,3,.75],'light');self.box('right_shoulder',[-5,20,-1.5],[2.5,2,3.5],'light')
   self.box('waist',[-2.5,14,-1.6],[5,.75,.5],'skin');self.box('chest',[-2.75,21,-2],[5.5,.75,.5],'skin')
   self.box('head',[-2.5,24,-2.65],[1.5,2,.15],'dark');self.box('pelvis',[1,10,-2],[2,2,.5],'cloth')
  elif r=='cao_chengfu':
   self.skirt(width=9);self.hat('official')
   for side in ('left','right'):
    x=self.handx(side);self.box(side+'_forearm',[x-2,10,-2.25],[4,5.5,4.5],'cloth')
   self.box('chest',[-.75,17,-2.5],[1.5,6,.5],'light')
   x=self.pole('whisk','right',9,'skin');self.box('whisk',[x-1.5,10,-1.5],[3,4,3],'light')
   self.bone('lantern','left_hand',[self.handx('left'),10,0]);self.box('lantern',[self.handx('left')-1.5,6,-1.5],[3,3,3],'light')
  elif r=='hong_ling':
   self.skirt(width=9);self.box('hair',[-2,22.5,2.5],[4,4,1],'dark')
   x=self.handx('left');self.prop('basket','left_hand',[x,10.25,0]);self.box('basket',[x-2,7,-3],[4,3,4],'skin')
   for dx in (-2,1.5):self.box('basket',[x+dx,10,-2.5],[.5,2,3],'dark')
   self.box('basket',[x-2,12,-2.5],[4,.5,3],'dark');self.box('basket',[x-1.5,10,-2.5],[3,1.5,3],'cloth')
   self.bone('snake_tail','pelvis',[0,11,1.5]);self.box('snake_tail',[-1.5,6,1.5],[3,5,3],'cloth')
   self.bone('tail_tip','snake_tail',[0,6,3]);self.box('tail_tip',[-1,3,3],[2,3,3],'dark')
  elif r=='chu_nongyu':
   self.skirt(width=9);self.bone('blindfold','head',[0,27,-2.5]);self.box('blindfold',[-2.85,26.5,-2.7],[5.7,1.5,.25],'light')
   self.box('hair',[-2.5,20,2.5],[5,6,1],'dark')
   for side in ('left','right'):
    x=self.handx(side);self.box(side+'_forearm',[x-2,9.5,-2.25],[4,6,4.5],'cloth')
   self.prop('zither','left_hand',[self.handx('left'),10.25,0]);x=self.handx('left')
   self.box('zither',[x-10,9,-4],[10,1.5,3],'skin')
   # Seven coarse flat strings are authored as planes, never smooth cylinders.
   for i in range(7):self.box('zither',[x-9.25,10.5,-3.8+i*.4],[8.5,.08,.15],'light')
   self.box('zither',[x-10,9.5,-4.5],[1,1,4],'dark');self.box('zither',[x-1,9.5,-4.5],[1,1,4],'dark')
  elif r=='xiaoyuanzi':
   for x in (-3.75,1.75):self.box('hair',[x,29,-1.5],[2,2.5,3],'dark')
   self.box('hair',[2.5,31,-1],[2,1,2],'light')
   self.bone('herb_basket','chest',[0,20,2.5]);self.box('herb_basket',[-3.5,12,2.5],[7,8,4],'skin')
   for x in (-3.75,2.75):self.box('herb_basket',[x,19.5,2],[1,1,5],'dark')
   for x in (-2,0,2):self.box('herb_basket',[x,20,3],[1,3,1],'cloth')
   x=self.pole('shovel','right',10,'skin');self.box('shovel',[x-1.5,3,-.75],[3,2,1.5],'light')
  elif r=='sai_banxian':
   self.skirt(width=8);self.hat('merchant');self.bone('glasses','head',[0,27,-2.5])
   for x in (-2.5,.5):self.box('glasses',[x,26.5,-2.75],[2,1.5,.5],'dark');self.box('glasses',[x+.5,26,-2.75],[1,2.5,.5],'dark')
   x=self.pole('banner','left',25,'skin');self.box('banner',[x+1,20,0],[5,8,.5],'light')
   for y in (21,24,26):self.box('banner',[x+2,y,-.2],[3,1,.25],'dark')
   x=self.handx('right');self.prop('coins','right_hand',[x,10.25,0]);self.box('coins',[x-1,9,-2],[2,2,.5],'skin')
  elif r=='ba_tu':
   self.hat('wolf');self.beard();self.box('chest',[-6,20,-4],[12,3,8],'light')
   self.box('chest',[-5,17,3],[10,5,1.5],'skin')
   x=self.handx('left');self.prop('bow','left_hand',[x,10.25,0]);
   for o,s in [([x-.5,7,-1],[1,7,2]),([x-.5,14,-2],[1,3,2]),([x-.5,17,-3],[1,3,2]),([x-.5,4,-2],[1,3,2]),([x-.5,1,-3],[1,3,2])]:self.box('bow',o,s,'skin')
   self.box('bow',[x-.25,2,-3.25],[.5,17,.5],'light')
   x=self.pole('machete','right',8,'dark');self.box('machete',[x-1,3,-1],[2,6,1],'light')
  elif r=='yan_chifeng':
   self.hat('straw');self.bone('cape','chest',[0,23,2.5]);
   for x,y in [(-4,10),(0,12)]:self.box('cape',[x,y,2.5],[3.75,23-y,1],'cloth')
   for side in ('left','right'):
    x=self.pole('sword_'+side,side,9,'skin');self.box('sword_'+side,[x-.5,2,-.75],[1,8,1.5],'light');self.box('sword_'+side,[x-1.5,10,-.75],[3,.75,1.5],'dark')
   self.box('head',[.5,25,-3],[3,.5,.5],'skin')
  elif r=='huang_laohan':
   self.hat('straw');self.box('chest',[-4,17,-2.8],[8,4,.75],'dark');self.box('pelvis',[-4,9,-2.8],[8,4,5.6],'cloth')
   x=self.pole('bamboo_pole','right',30,'skin')
   for y in (7,14,21,28):self.box('bamboo_pole',[x-.6,y,-.6],[1.2,.75,1.2],'dark')

 def animation(self, state):
  r=self.role
  length=1 if state=='walk' else .6 if state=='idle' and r=='a_ji' else 4 if state=='idle' and r=='han_chong' else 2
  b={'chest':{'rotation':keys([[0,0,-.5],[0,0,.5],[0,0,-.5]],length)}}
  def rot(n, values, seconds=2):b[n]={'rotation':keys(values,seconds) if isinstance(values[0],list) else values}
  # Role-specific rest poses remain active in all states, including held props.
  poses={
   'baibao_jin':{'left_upper_arm':[-15,0,-10],'left_forearm':[-65,0,0]},
   'hei_po':{'left_upper_arm':[-15,0,-10],'left_forearm':[-55,0,0]},
   'mo_jizi':{'left_upper_arm':[-8,0,-8]},
   'han_chong':{'right_upper_arm':[-10,0,8],'left_knee':[8,0,0]},
   'qingxuanzi':{'left_forearm':[-60,0,0]},
   'a_ji':{'left_upper_arm':[-25,0,-10],'right_upper_arm':[-25,0,10],'left_forearm':[-55,0,0],'right_forearm':[-55,0,0],'head':[12,0,0]},
   'cao_chengfu':{'left_upper_arm':[-20,0,-25],'right_upper_arm':[-20,0,25],'left_forearm':[-50,0,0],'right_forearm':[-50,0,0]},
   'hong_ling':{'left_forearm':[-25,0,0]},
   'chu_nongyu':{'left_upper_arm':[-30,0,-15],'left_forearm':[-50,0,0],'right_upper_arm':[-35,0,15],'right_forearm':[-60,0,0]},
   'sai_banxian':{'left_upper_arm':[-10,0,-15]},
   'ba_tu':{'left_upper_arm':[-15,0,-15]},
   'yan_chifeng':{'left_upper_arm':[-10,0,-12],'right_upper_arm':[-10,0,12]},
   'huang_laohan':{'right_upper_arm':[-18,0,12],'right_forearm':[-20,0,0]},
  }
  for n,v in poses.get(r,{}).items():rot(n,v)
  if r=='hei_po':rot('medicine_bowl',[52,0,0])
  if r=='chu_nongyu':rot('zither',[80,0,0])
  if r=='hong_ling':
   b['snake_tail']={'scale':[1,1,1] if state in ('react','danger') else [0,0,0]}
   if state in ('react','danger'):rot('snake_tail',[[0,-20,0],[0,20,0],[0,-20,0]]);rot('tail_tip',[[0,20,0],[0,-20,0],[0,20,0]])
  if r=='cao_chengfu':b['lantern']={'scale':[1,1,1] if state=='night' else [0,0,0]}
  if state=='idle':
   if r=='a_ji':rot('chest',[[0,0,-2],[0,0,2],[0,0,-2]],.6)
   elif r=='baibao_jin':rot('right_forearm',[[-40,0,10],[-55,0,10],[-40,0,10]])
   elif r=='mo_jizi':rot('claw_outer',[[0,0,-8],[0,0,8],[0,0,-8]]);rot('claw_inner',[[0,0,8],[0,0,-8],[0,0,8]])
   elif r=='xiaoyuanzi':b['pelvis']={'position':keys([[0,0,0],[0,1,0],[0,0,0]],2)}
   elif r=='yan_chifeng':rot('cape',[[0,0,-2],[0,0,2],[0,0,-2]])
   elif r=='han_chong':rot('head',[[0,-12,0],[0,12,0],[0,-12,0]],4)
   elif r=='sai_banxian':rot('right_wrist',[[0,0,-15],[0,0,15],[0,0,-15]])
  elif state=='walk':
   for side,sign in (('left',1),('right',-1)):
    amp=10 if r=='han_chong' and side=='left' else 20
    rot(side+'_thigh',[[amp*sign,0,0],[-amp*sign,0,0],[amp*sign,0,0]],1)
    rot(side+'_knee',[[6,0,0],[18 if sign==1 else 6,0,0],[6,0,0]],1)
    # Tools and held vessels travel with their hand, never a fixed chest prop.
    if not any(self.names[n].get('parent')==side+'_hand' for n in self.props):rot(side+'_upper_arm',[[-14*sign,0,0],[14*sign,0,0],[-14*sign,0,0]],1)
    if side+'_robe' in self.names:rot(side+'_robe',[[6*sign,0,0],[-6*sign,0,0],[6*sign,0,0]],1)
  elif state=='work':
   if r=='hei_po':
    rot('left_upper_arm',[-25,25,25]);rot('left_forearm',[-70,0,0]);rot('medicine_bowl',[77,0,0])
    rot('right_upper_arm',[-45,-25,-30]);rot('stirrer',[[87,15,10],[102,-15,10],[87,15,10]],2)
   if r=='chu_nongyu':
    rot('left_upper_arm',[-30,0,15]);rot('right_upper_arm',[-35,0,-15])
   work={
    'lao_chen':('right_upper_arm',[[-45,0,10],[-105,0,10],[-45,0,10]]),
    'han_chong':('head',[[8,-12,0],[8,12,0],[8,-12,0]]),
    'qingxuanzi':('right_forearm',[[-60,0,15],[-75,0,5],[-60,0,15]]),
    'baibao_jin':('right_forearm',[[-70,0,35],[-85,0,25],[-70,0,35]]),
    'a_ji':('head',[[15,-10,0],[20,10,0],[15,-10,0]]),
    'hei_po':('right_forearm',[[-60,-15,-10],[-75,15,-10],[-60,-15,-10]]),
    'cao_chengfu':('head',[[12,0,0],[3,0,0],[12,0,0]]),
    'hong_ling':('right_upper_arm',[[-20,0,15],[-55,0,25],[-20,0,15]]),
    'chu_nongyu':('right_wrist',[[0,0,-8],[0,0,8],[0,0,-8]]),
    'xiaoyuanzi':('right_upper_arm',[[-20,0,10],[-75,0,10],[-20,0,10]]),
    'mo_jizi':('right_forearm',[[-45,0,15],[-85,0,25],[-45,0,15]]),
    'sai_banxian':('right_wrist',[[0,0,-25],[0,0,25],[0,0,-25]]),
    'ba_tu':('chest',[[18,0,0],[30,0,0],[18,0,0]]),
    'yan_chifeng':('right_forearm',[[-50,0,25],[-80,0,35],[-50,0,25]]),
    'huang_laohan':('right_upper_arm',[[-25,0,10],[-65,0,10],[-25,0,10]]),
   }
   n,v=work[r];rot(n,v,2)
   if r=='mo_jizi':rot('claw_outer',[[0,0,-18],[0,0,8],[0,0,-18]],2);rot('claw_inner',[[0,0,18],[0,0,-8],[0,0,18]],2)
   if r=='huang_laohan':rot('chest',[[0,-8,0],[8,8,0],[0,-8,0]],2)
  elif state in ('talk','turn','player_near'):rot('head',[[0,-8,0],[3,8,0],[0,-8,0]],2)
  elif state in ('react','danger'):
   rot('head',[12 if r=='a_ji' else -8,0,0]);rot('right_upper_arm',[-70,0,25] if r=='a_ji' else [-25,0,15])
   if r=='a_ji':rot('left_upper_arm',[[-70,0,-25],[-95,0,-35],[-70,0,-25]],2)
   if r=='mo_jizi':rot('head',[[-8,-10,0],[-18,10,0],[-8,-10,0]],2)
  elif state=='rain':rot('head',[15,0,0]);rot('right_upper_arm',[-100,0,20]);rot('right_forearm',[-25,0,0])
  elif state=='night':rot('head',[6,0,0])
  elif state=='player_holds_special':rot('chest',[16,0,0]);rot('head',[10,0,0]);rot('right_forearm',[-60,0,10])
  return {'loop':True,'animation_length':length,'bones':b}
 def export(self):
  bones=copy.deepcopy(self.bones)
  for b in bones:
   for field in ('pivot',):b[field]=[round(v*self.scale,4) for v in b[field]]
   if 'locators' in b:b['locators']={n:[round(v*self.scale,4) for v in p] for n,p in b['locators'].items()}
   for c in b.get('cubes',[]):
    for field in ('origin','size','pivot'):
     if field in c:c[field]=[round(v*self.scale,4) for v in c[field]]
  from natural_pixels import atlas
  texture,paint_report=atlas(bones,self.materials,self.role,self.colour)
  geo={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.npc_'+self.role,'texture_width':texture.width,'texture_height':texture.height,'visible_bounds_width':4,'visible_bounds_height':5,'visible_bounds_offset':[0,1.4,0]},'bones':bones}]}
  anim={'format_version':'1.8.0','animations':{'animation.npc.'+s:self.animation(s) for s in STATES}}
  return geo,anim,texture,{'id':self.role,'design':self.design,'stature':self.scale,'chestWidth':self.width,'chestDepth':self.depth,'bones':len(bones),'cuboids':sum(len(b.get('cubes',[])) for b in bones),'pixels':paint_report,'handProps':self.props}

def keys(values, length):return {str(round(i*length/(len(values)-1),3)):v for i,v in enumerate(values)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--roles',nargs='+',choices=ROLES,default=list(ROLES));p.add_argument('--backup',type=Path);a=p.parse_args()
 DOC.mkdir(parents=True,exist_ok=True)
 report={r['id']:r for r in json.loads((DOC/'authoring.json').read_text())} if (DOC/'authoring.json').exists() else {}
 for role in a.roles:
  rig=Rig(role);rig.anatomy();rig.costume();geo,anim,texture,row=rig.export()
  outputs=[(f'geo/npc/{role}.geo.json',geo),(f'animations/npc/{role}.animation.json',anim),(f'textures/entity/npc/{role}.png',texture)]
  row['before']={}
  for rel,obj in outputs:
   target=ASSETS/rel;old=target.read_bytes()
   if a.backup:
    dest=a.backup/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():dest.write_bytes(old)
   row['before'][rel]=hashlib.sha256((a.backup/rel).read_bytes()).hexdigest() if a.backup else report.get(role,{}).get('before',{}).get(rel,hashlib.sha256(old).hexdigest())
   if isinstance(obj,Image.Image):obj.save(target)
   else:target.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
  report[role]=row;print(role,row['bones'],row['cuboids'])
 (DOC/'authoring.json').write_text(json.dumps(list(report.values()),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
