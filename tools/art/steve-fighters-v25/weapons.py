"""Nine original, low-poly service blades; palm attachment and combat clocks stay unchanged."""
from PIL import Image,ImageDraw
DESIGNS={
'imperial_soldier':('制式脊剑','straight',8,'a6bdc5','2e4452','b9a069'),
'royal_guard':('云首佩刀','saber',11,'c5d5d9','374453','c5a264'),
'rebel_soldier':('缺锋战刀','broken',8,'8eaaa9','384744','967455'),
'assassin':('乌脊双刃','stiletto',6,'819aa9','232f40','68758a'),
'bandit_thug':('阔背斩刀','cleaver',8,'a0ada6','48514a','92704e'),
'zuwu_daoshou':('环首步刀','ring',8,'acb9be','36444a','b9a078'),
'ludun_jiashi':('镇列阔剑','shield',11,'afc3c3','334b4b','b19864'),
 'tiesuo_chihou':('钩背短锋','hook',6,'92adb2','30424b','978b70'),
'kuijun_sishi':('折锋军匕','dagger',6,'b8c4bc','414c48','a49779')}
def rgb(h):return tuple(bytes.fromhex(h))
def shade(c,m):return tuple(min(255,max(0,round(x*m)))for x in c)
def refine(id,parts,box,P):
 if id not in DESIGNS:return
 title,kind,L,*_=DESIGNS[id];parts[:]=[p for p in parts if p['name']not in ('blade','sword_guard')]
 def q(n,x,y,w,h,mat='weapon_steel',z=-.25,depth=.5,rot=None):box(n,'weapon_shaft',[0,0,0],[x,y,z],[w,h,depth],mat,rot or [0,90,0])
 # The primary blade owns most of the silhouette; a few stepped transitions form the point.
 if kind=='straight':
  q('blade',-1,-2-L+2,2,L-2);q('blade_point',-.5,-2-L,1,2);q('blade_ridge',-.25,-2-L+2,.5,L-2,'weapon_spine',-.5,1)
  q('sword_guard',-2.25,-2.5,4.5,.5,'weapon_gold',-.75,1.5);q('guard_ends',-2.25,-3,.5,.5,'weapon_gold');q('pommel',-.75,3,1.5,1,'weapon_gold',-.5,1)
 elif kind=='saber':
  q('blade',-.75,-8,1.5,6);q('blade_curve',-.25,-11,1.5,3);q('blade_point',.25,-13,1,2);q('blade_spine',.5,-8,.5,5,'weapon_spine',-.5,1)
  q('sword_guard',-2,-2.5,4,.5,'weapon_gold',-.75,1.5);q('cloud_guard',-2.5,-3.5,1,1,'weapon_gold');q('cloud_guard_hook',1.5,-2,1,1,'weapon_gold');q('pommel',-.75,3,1.5,1,'weapon_gold',-.5,1)
 elif kind=='broken':
  q('blade',-1,-8,2.5,6);q('broken_point',-1,-10,1.5,2);q('blade_back',1,-7,.5,5,'weapon_spine',-.5,1)
  q('sword_guard',-1.75,-2.5,3.5,.5,'weapon_spine',-.75,1.5);q('guard_brace',-1.75,-3,.5,1,'weapon_gold');q('pommel',-.5,3,1,1,'weapon_spine',-.5,1)
 elif kind=='stiletto':
  q('blade',-.5,-7,1,5);q('blade_point',-.25,-8,.5,1);q('blade_ridge',-.25,-6,.5,4,'weapon_spine',-.5,1)
  q('sword_guard',-1.25,-2.5,2.5,.5,'weapon_spine',-.5,1);q('pommel',-.5,3,1,.5,'weapon_spine',-.5,1)
 elif kind=='cleaver':
  q('blade',-1,-7,2.5,5);q('blade_belly',-1.5,-9,3,2);q('blade_tip',-.5,-10,2,1);q('heavy_spine',1,-8,.5,6,'weapon_spine',-.5,1)
  q('sword_guard',-1.5,-2.5,3,.5,'weapon_spine',-.75,1.5);q('pommel',-.75,3,1.5,1,'weapon_gold',-.5,1)
 elif kind=='ring':
  q('blade',-.75,-8,1.5,6);q('blade_tip',-.25,-10,1,2);q('blade_spine',.5,-8,.5,6,'weapon_spine',-.5,1)
  q('sword_guard',-1.5,-2.5,3,.5,'weapon_gold',-.75,1.5)
  q('ring_left',-1,3,.5,1.5,'weapon_gold');q('ring_right',.5,3,.5,1.5,'weapon_gold');q('ring_bottom',-1,4.5,2,.5,'weapon_gold')
 elif kind=='shield':
  q('blade',-1.25,-10,2.5,8);q('blade_tip',-.75,-12,1.5,2);q('blade_point',-.25,-13,.5,1);q('blade_ridge',-.25,-10,.5,8,'weapon_spine',-.5,1)
  q('sword_guard',-2,-2.5,4,1,'weapon_gold',-.75,1.5);q('guard_lug',-2,-3,.5,1,'weapon_gold');q('pommel',-.75,3,1.5,1,'weapon_gold',-.5,1)
 elif kind=='hook':
  q('blade',-.75,-6,1.5,4);q('blade_tip',-.25,-8,1,2);q('hook_shoulder',.75,-5,1,1,'weapon_spine');q('hook_return',1.25,-4,.5,1,'weapon_spine')
  q('sword_guard',-1.5,-2.5,3,.5,'weapon_gold',-.5,1);q('pommel',-.5,3,1,.5,'weapon_gold',-.5,1)
 else:
  q('blade',-.75,-5,1.5,3);q('blade_tip',-.5,-7,1,2);q('blade_point',-.25,-8,.5,1);q('blade_ridge',-.25,-5,.5,3,'weapon_spine',-.5,1)
  q('sword_guard',-1.5,-2.5,3,.5,'weapon_spine',-.5,1);q('pommel',-.5,3,1,1,'weapon_spine',-.5,1)
 # One small collar unifies tang and guard without changing the palm's grip transform.
 q('blade_collar',-.75,-3,1.5,1,'weapon_gold',-.5,1)
 # Body is 32 model units high. Service blades now read as swords, not palm-sized knives.
 reach={'straight':18,'saber':24,'broken':19,'stiletto':12,'cleaver':18,'ring':19,'shield':22,'hook':13,'dagger':12}[kind]
 factor=reach/L
 for part in parts:
  if part.get('parent')!='weapon_shaft':continue
  n=part['name']
  if n=='blade_collar' or not (n.startswith(('blade','broken_point','heavy_spine','hook_'))):continue
  part['origin'][1]=round((-2+(part['origin'][1]+2)*factor)*2)/2
  part['size'][1]=round(part['size'][1]*factor*2)/2


def paint(mat,face,w,h,P,id):
 if id not in DESIGNS or mat not in ('weapon_steel','weapon_spine','weapon_gold','grip'):return None
 _,kind,L,steel,spine,gold=DESIGNS[id];steel,spine,gold=map(rgb,(steel,spine,gold));base=steel if mat=='weapon_steel'else spine if mat=='weapon_spine'else gold if mat=='weapon_gold'else P['white']if kind=='dagger'else P['cloth']if kind in ('saber','stiletto')else P['leather']
 im=Image.new('RGBA',(w,h),(*base,255));d=ImageDraw.Draw(im)
 if mat=='weapon_steel':
  if face in ('north','south'):
   # Edge and spine are directional and deliberately unequal, not four-sided outlines.
   d.rectangle((0,0,max(0,w//4-1),h-1),fill=shade(steel,1.25));d.rectangle((min(w-1,max(1,w*3//4)),0,w-1,h-1),fill=spine)
   if h>8 and w>3:
    y=h//3 if kind in ('broken','cleaver')else h*2//3;d.line([(1,y),(min(w-1,2),y+1)],fill=shade(steel,1.35))
  elif face in ('east','down'):d.rectangle((0,0,w,h),fill=spine)
 elif mat=='weapon_spine':
  if face in ('north','south')and w>=2:d.line([(0,0),(0,h-1)],fill=shade(base,1.3))
 elif mat=='weapon_gold':
  if face in ('north','up'):d.line([(0,0),(w-1,0)],fill=shade(gold,1.25))
  if face in ('down','east'):d.rectangle((0,0,w,h),fill=shade(gold,.65))
 else:
  for y in range(1,h,3):d.line([(0,y),(w-1,min(h-1,y+1))],fill=shade(base,.65))
 return im
