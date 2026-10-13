"""Original structural candidates, NOT a production replacement before grey approval.
One unit is 1/16 metre. No humanoid anatomy/enrichment template is imported.
The grey atlas is a review aid, not a finished texture.
"""
from pathlib import Path
import json, math, copy, hashlib
from PIL import Image
R=Path(__file__).resolve().parents[3]
D=R/'docs/art/boss-structure-v13'
IDS=['nine_heaven_general','dragon_king','dragon_emperor']
NAMES=['九霄天将','东海龙王','龙帝']
class Rig:
 def __init__(self,id):
  self.id=id;self.bones=[];self.by={};self.bone('root',None,[0,0,0])
 def bone(self,n,p,pivot,rotation=None):
  assert n not in self.by
  b={'name':n,'pivot':list(pivot),'cubes':[]}
  if p:b['parent']=p
  if rotation:b['rotation']=rotation
  self.by[n]=b;self.bones.append(b);return n
 def box(self,n,c,s,rotation=None):
  q={'origin':[c[i]-s[i]/2 for i in range(3)],'size':list(s),'uv':{f:{'uv':[2,2],'uv_size':[4,4]} for f in ['north','south','east','west','up','down']}}
  if rotation:q.update(rotation=rotation,pivot=list(c))
  self.by[n]['cubes'].append(q)
  return q
 def beam(self,n,a,b,w,d=None):
  v=[b[i]-a[i] for i in range(3)];L=math.sqrt(sum(x*x for x in v));c=[(a[i]+b[i])/2 for i in range(3)]
  q=self.box(n,c,[w,L,d or w],[-math.degrees(math.asin(v[2]/L)),0,math.degrees(math.atan2(v[0],v[1]))])
  q['_segment']=[list(a),list(b)]

def general():
 g=Rig(IDS[0]);g.bone('bearing','root',[0,16,1])
 # Grounded, staggered load-bearing legs. They do not carry a long NPC pelvis/waist.
 for s,side,z in [(1,'left',-4),(-1,'right',4)]:
  g.bone(side+'_leg','bearing',[s*9,20,z]);g.beam(side+'_leg',[s*9,21,z+2],[s*11,11,z],11,13)
  g.bone(side+'_shin',side+'_leg',[s*11,11,z]);g.box(side+'_shin',[s*11,7,z-1],[9,10,11],[8,0,0])
  g.bone(side+'_foot',side+'_shin',[s*11,3,z-1]);g.box(side+'_foot',[s*11,2,z-2],[9,4,13])
 g.box('bearing',[0,21,2],[24,12,20])
 g.bone('chest','bearing',[0,24,2],[10,-8,0])
 g.box('chest',[0,37,3],[27,20,21])
 # Paired pitched breast masses form one downward cuirass, not a flat box lid.
 for s in [-1,1]:g.box('chest',[s*7,37,-9],[16,18,9],[6,0,-s*12])
 g.box('chest',[0,29,-7],[17,10,14],[10,0,0])
 # The head is recessed INTO the upper mass, rather than stacked above a neck.
 g.bone('head','chest',[0,46,-8]);g.box('head',[0,49,-9],[10,13,12])
 g.box('head',[0,52,-15],[12,3,4],[12,0,0]);g.box('head',[0,44,-15],[4,10,5],[10,0,0])
 for s in [-1,1]:g.box('head',[s*4.8,46,-14],[4,10,5],[0,0,-s*14])
 g.bone('crown','head',[0,55,-6]);g.beam('crown',[0,55,-6],[0,63,3],4,7)
 for s,side in [(1,'left'),(-1,'right')]:
  n=g.bone(side+'_arm','chest',[s*17,42,1]);g.box(n,[s*19,44,2],[16,12,20],[0,0,-s*22])
  g.beam(n,[s*22,39,1],[s*26,29,-4],11,13)
  f=g.bone(side+'_forearm',n,[s*26,29,-4]);end=[s*27,17,-13] if s==1 else [s*27,22,-14]
  g.beam(f,[s*26,31,-4],end,14 if s==1 else 11,16 if s==1 else 13)
  # One continuous forearm blade on the defensive limb, rather than an oversized glove.
  if s==1:g.beam(f,[s*29,32,-12],[s*30,16,-18],7,5)
  h=g.bone(side+'_hand',f,end);g.box(h,[s*27,end[1]-2,end[2]-2],[12 if s==1 else 10,7,12])
  g.bone(side+'_grip',h,[s*27,21,-18] if s==-1 else [s*27,17,-16])
 # Back is the structural continuation of the cuirass: a folded command mantle.
 g.bone('command_mantle','chest',[0,43,14])
 for s in [-1,1]:
  g.box('command_mantle',[s*9,32,15],[17,30,4],[-8,0,s*9])
  g.beam('command_mantle',[s*14,43,12],[s*20,55,16],5,7)
 # Lance is seated through the grip, not hung at an arbitrary side position.
 g.bone('weapon','right_grip',[-27,21,-18]);g.beam('weapon',[-20.22,8,-14.82],[-40,51,-26],3,3)
 g.beam('weapon',[-40,51,-26],[-45,63,-29],7,4)
 g.beam('weapon',[-45,63,-29],[-47,68,-30],3,3)
 g.box('weapon',[-40,51,-26],[12,3,5],[0,0,-20])
 return g

def king():
 g=Rig(IDS[1]);g.bone('haunch','root',[0,16,5]);g.box('haunch',[0,21,6],[27,16,23])
 # Bent haunches and rear hocks replace long trouser legs. The feet stay compact.
 for s,side,z in [(1,'left',-3),(-1,'right',3)]:
  n=g.bone(side+'_leg','haunch',[s*10,20,5+z]);g.beam(n,[s*10,20,5+z],[s*14,11,10+z],12,13)
  sh=g.bone(side+'_hock',n,[s*14,11,10+z]);g.beam(sh,[s*14,11,10+z],[s*14,4,-2+z],8,10)
  ft=g.bone(side+'_foot',sh,[s*14,3,-2+z]);g.box(ft,[s*14,2,-4+z],[9,4,12])
 g.bone('chest','haunch',[0,25,4],[16,5,0]);g.box('chest',[0,34,4],[28,23,25])
 for s in [-1,1]:g.box('chest',[s*7,35,-8],[15,20,9],[12,0,-s*15])
 g.bone('neck','chest',[0,42,-6]);g.beam('neck',[0,42,-6],[0,48,-17],14,16)
 # Draconic royal head, projecting jaw and crown: not a human face with horns attached.
 g.bone('head','neck',[0,48,-17]);g.box('head',[0,50,-19],[14,12,18],[9,0,0])
 g.box('head',[0,46,-31],[10,7,16],[9,0,0]);g.box('head',[0,53,-24],[17,4,10],[7,0,0])
 g.bone('jaw','head',[0,42,-18]);g.box('jaw',[0,41.5,-28],[11,3,23],[5,0,0])
 for s in [-1,1]:
  g.box('head',[s*6.8,48,-23],[4,10,9],[0,0,-s*16])
  g.beam('head',[s*5,55,-13],[s*11,64,-4],4,5)
  g.beam('head',[s*11,64,-4],[s*17,67,4],3,4)
  g.box('jaw',[s*4.5,44,-34],[2,5,3])
 g.bone('crown','head',[0,56,-12]);g.box('crown',[0,56,-11],[12,3,10])
 for s,side in [(1,'left'),(-1,'right')]:
  n=g.bone(side+'_arm','chest',[s*16,40,4]);g.box(n,[s*19,38,3],[14,14,20],[0,0,-s*25])
  g.beam(n,[s*19,37,3],[s*24,27,-4],10,13)
  f=g.bone(side+'_forearm',n,[s*24,27,-4]);g.beam(f,[s*24,29,-4],[s*25,22,-16],11,14)
  h=g.bone(side+'_hand',f,[s*25,22,-16]);g.box(h,[s*25,21,-18],[10,7,11])
  if s==1:
   for dx in [-3,0,3]:g.beam(h,[s*25+dx,20,-22],[s*25+dx,15,-25],2,3)
  g.bone(side+'_grip',h,[s*25,23,-19])
 # Tail balances forward head and arms. It has real contiguous sections and pivots.
 points=[[0,20,16],[0,15,28],[15,11,36],[28,10,27],[30,15,15]]
 for i,(a,b) in enumerate(zip(points,points[1:])):
  n=g.bone('tail_'+str(i),'haunch' if i==0 else 'tail_'+str(i-1),a);g.beam(n,a,b,11-i*1.8,12-i*2)
 g.bone('royal_fins','chest',[0,41,15]);g.box('royal_fins',[0,43,18],[5,25,7],[-18,0,0])
 for s in [-1,1]:
  g.box('royal_fins',[s*10,37,18],[7,27,4],[-15,0,-s*24])
  g.box('haunch',[s*14,20,4],[6,19,21],[0,0,-s*8])
 g.bone('weapon','right_grip',[-25,23,-19]);g.beam('weapon',[-19.31,8,-17.1],[-40,58,-24],3,3)
 g.beam('weapon',[-46,55,-24],[-33,60,-24],4,4)
 for a,b in [([-46,55,-24],[-50,66,-25]),([-40,58,-24],[-45,73,-26]),([-33,60,-24],[-36,71,-25])]:g.beam('weapon',a,b,3,4)
 return g

def emperor():
 g=Rig(IDS[2]);g.bone('plinth','root',[0,16,3])
 # A living imperial effigy: short internal supports under a deep bell-shaped shell.
 for s,side,z in [(1,'left',-3),(-1,'right',3)]:
  n=g.bone(side+'_leg','plinth',[s*10,19,3+z]);g.beam(n,[s*10,19,3+z],[s*12,8,z],12,14)
  sh=g.bone(side+'_ankle',n,[s*12,8,z]);g.box(sh,[s*12,6,z],[10,8,11])
  ft=g.bone(side+'_foot',sh,[s*12,3,z]);g.box(ft,[s*12,2,z-1],[10,4,12])
 g.box('plinth',[0,20,4],[29,17,24])
 g.bone('chest','plinth',[0,24,3],[8,-6,-2]);g.box('chest',[0,36,4],[32,25,26])
 for s in [-1,1]:g.box('chest',[s*8,37,-10],[19,24,8],[8,0,-s*8])
 g.box('chest',[0,25,-10],[22,12,8],[9,0,0])
 # Two broad descending mantle planes, not many separate clothing boxes.
 for s in [-1,1]:
  g.box('chest',[s*15,26,3],[9,27,23],[0,0,-s*13])
  g.box('chest',[s*16,47,2],[21,9,21],[0,0,-s*26])
 # Mask is recessed beneath the imperial cowl; no visible human neck/skin.
 g.bone('head','chest',[0,47,-11]);g.box('head',[0,51,-10],[10,12,10])
 for s in [-1,1]:g.box('head',[s*5.5,49,-13],[4,12,7],[0,0,-s*18])
 g.box('head',[0,54,-16],[13,3,5]);g.box('head',[0,45,-14],[4,8,5],[8,0,0])
 g.bone('crown','head',[0,57,-7]);g.box('crown',[0,59,-7],[19,3,14],[-8,0,0])
 for s in [-1,1]:g.beam('crown',[s*6,60,-3],[s*10,65,3],3,5)
 for s,side in [(1,'left'),(-1,'right')]:
  n=g.bone(side+'_arm','chest',[s*19,42,1]);g.beam(n,[s*19,42,1],[s*25,33,-3],14,18)
  f=g.bone(side+'_forearm',n,[s*25,33,-3]);end=[s*23,30,-18] if s==1 else [s*29,24,-7]
  g.beam(f,[s*25,33,-3],end,15,18)
  h=g.bone(side+'_hand',f,end);g.box(h,[end[0],end[1]-2,end[2]-4],[13,8,14])
  g.bone(side+'_grip',h,[end[0],end[1],end[2]-5])
 g.bone('seal','left_hand',[23,30,-24]);g.box('seal',[23,33,-27],[8,8,6]);g.box('seal',[23,38,-27],[10,3,8])
 # Continuous dragon-law arch grows out of the mantle, not three flat signboards.
 g.bone('imperial_arch','chest',[0,30,17])
 for s in [-1,1]:
  points=[[s*10,19,17],[s*23,36,21],[s*22,51,17],[s*14,61,12],[s*8,63,10]]
  for i,(a,b) in enumerate(zip(points,points[1:])):g.beam('imperial_arch',a,b,6 if i<2 else 4,7 if i<2 else 5)
 g.box('imperial_arch',[0,31,20],[22,28,4],[-5,0,0])
 return g

def animations(g):
 # Small structural motion samples ONLY. Not a claim of finished battle animation.
 a={'idle':{'loop':True,'animation_length':2,'bones':{'chest':{'rotation':{'0':[0,0,0],'1':[1,0,0],'2':[0,0,0]}},'head':{'rotation':{'0':[0,-3,0],'1':[0,2,0],'2':[0,-3,0]}}}}}
 if g.id==IDS[1]:
  a['idle']['bones']['tail_1']={'rotation':{'0':[0,-3,0],'1':[0,3,0],'2':[0,-3,0]}}
 a['guard']={'loop':False,'animation_length':1,'bones':{'chest':{'rotation':{'0':[0,0,0],'.5':[3,-3,0],'1':[0,0,0]}},'head':{'rotation':{'0':[0,0,0],'.5':[3,0,0],'1':[0,0,0]}}}}
 return {'format_version':'1.8.0','animations':a}

def run():
 D.mkdir(parents=True,exist_ok=True);records=[]
 for id,fn in zip(IDS,[general,king,emperor]):
  g=fn()
  # Compact width and lengthen the actual bearing stage (not a camera-scale change).
  # Affine treatment of each bone/cube is recorded in the editable JSON itself.
  scale=[.70,.82,.82]
  def pos(v):return [v[0]*scale[0],(v[1]+(7 if v[1]>=20 else max(0,v[1]-4)*7/16))*scale[1],v[2]*scale[2]]
  for b in g.bones:
   b['pivot']=pos(b['pivot'])
   for c in b['cubes']:
    # Keep cubes rectangular: scale each authored extent, then move its centre.
    centre=[c['origin'][i]+c['size'][i]/2 for i in range(3)];newcentre=pos(centre)
    c['size']=[c['size'][i]*scale[i] for i in range(3)]
    if '_segment' in c:
     a,b=map(pos,c.pop('_segment'));v=[b[i]-a[i] for i in range(3)];L=math.sqrt(sum(x*x for x in v))
     newcentre=[(a[i]+b[i])/2 for i in range(3)];c['size'][1]=L
     c['rotation']=[-math.degrees(math.asin(v[2]/L)),0,math.degrees(math.atan2(v[0],v[1]))]
     c['pivot']=newcentre
    elif centre[1]<20 and centre[1]>4:c['size'][1]*=1+7/16
    c['origin']=[newcentre[i]-c['size'][i]/2 for i in range(3)]
    if 'pivot' in c and c['pivot']!=newcentre:c['pivot']=pos(c['pivot'])
  out=D/'candidates'/id;out.mkdir(parents=True,exist_ok=True)
  desc={'identifier':'geometry.'+id,'texture_width':16,'texture_height':16,'visible_bounds_width':10,'visible_bounds_height':8,'visible_bounds_offset':[0,2,0]}
  geo={'format_version':'1.12.0','minecraft:geometry':[{'description':desc,'bones':g.bones}]}
  (out/(id+'.geo.json')).write_text(json.dumps(geo,indent=2)+'\n')
  (out/(id+'.animation.json')).write_text(json.dumps(animations(g),indent=2)+'\n')
  Image.new('RGB',(16,16),(155,158,160)).save(out/'gray.png')
  records.append({'id':'dynasty:'+id,'bones':len(g.bones),'cuboids':sum(len(b['cubes']) for b in g.bones),'stage':'structural candidate; grey approval required; not production animation/texture'})
 (D/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':run()
