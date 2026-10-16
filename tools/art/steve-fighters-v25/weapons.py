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
 title,kind,L,*_=DESIGNS[id]
 parts[:]=[p for p in parts if p['name'] not in ('blade','sword_guard')]
 # 0.5-unit grid matches the runtime baker. Broad bevel planes surround a thicker
 # central web: side views show steel volume without turning the edge into a club.
 def q(n,x,y,w,h,mat='weapon_steel',depth=1):
  box(n,'weapon_shaft',[0,0,0],[x,y,-depth/2],[w,h,depth],mat,[0,90,0])
 reach={'straight':20,'saber':24,'broken':20,'stiletto':15,'cleaver':20,'ring':21,'shield':23,'hook':16,'dagger':15}[kind]
 width={'straight':3,'saber':3,'broken':3.5,'stiletto':2,'cleaver':4,'ring':3,'shield':4,'hook':2.5,'dagger':2.5}[kind]
 top=-2-reach
 single=kind in ('saber','broken','cleaver','ring','hook')
 # One uninterrupted main blade, with only the terminal 3-5 units tapering.
 tip=4 if reach>=20 else 3
 q('blade',-width/2,top+tip,width,reach-tip)
 if kind=='saber':
  q('blade_tip',-width/2+.5,top+2,width-.5,2)
  q('blade_point',.5,top,1,2,depth=.5)
 elif kind in ('broken','cleaver'):
  q('blade_tip',-width/2+.5,top+1,width-.5,tip-1)
  q('blade_point',width/2-1,top,1,1,depth=.5)
 elif kind in ('ring','hook'):
  q('blade_tip',-width/2+.5,top+1,width-.5,tip-1)
  q('blade_point',width/2-1,top,1,1,depth=.5)
 else:
  q('blade_tip',-(width-1)/2,top+1,width-1,tip-1)
  q('blade_point',-.25,top,.5,1,depth=.5)
 # The web is lighter steel, not a black rod laid over a silver blade.
 ridge_x=width/2-1 if single else -.5
 q('blade_ridge',ridge_x,top+tip,1,reach-tip,'weapon_ridge',1.5)
 guard=5.5 if kind in ('straight','shield')else 4.5 if kind in ('saber','ring','broken','cleaver')else 3.5
 metal='weapon_gold' if kind in ('straight','saber','ring','shield')else 'weapon_spine'
 q('sword_guard',-guard/2,-2.5,guard,1,metal,2)
 if kind in ('straight','shield'):
  for x in (-guard/2,guard/2-.5):q('guard_tip_'+str(x),x,-3.5,.5,1,metal,1.5)
 elif kind=='saber':
  q('cloud_guard',-guard/2,-3.5,1,1,metal,1.5)
 elif kind=='hook':q('hook_shoulder',width/2,top+reach/2,1,1.5,'weapon_spine',1)
 q('blade_collar',-1,-3.5,2,1,'weapon_gold' if kind in ('saber','ring','shield')else 'weapon_spine',1.5)
 if kind=='ring':
  q('ring_left',-1,3,.5,1.5,metal,1)
  q('ring_right',.5,3,.5,1.5,metal,1)
  q('ring_bottom',-1,4.5,2,.5,metal,1)
 else:q('pommel',-.75,3,1.5,1,metal,1.5)


def paint(mat,face,w,h,P,id):
 if id not in DESIGNS or mat not in ('weapon_steel','weapon_ridge','weapon_spine','weapon_gold','grip'):return None
 _,kind,L,steel,spine,gold=DESIGNS[id];steel,spine,gold=map(rgb,(steel,spine,gold));base=steel if mat in ('weapon_steel','weapon_ridge')else spine if mat=='weapon_spine'else gold if mat=='weapon_gold'else P['white']if kind=='dagger'else P['cloth']if kind in ('saber','stiletto')else P['leather']
 im=Image.new('RGBA',(w,h),(*base,255));d=ImageDraw.Draw(im)
 if mat in ('weapon_steel','weapon_ridge'):
  if face in ('north','south'):
   single=kind in ('saber','broken','cleaver','ring','hook')
   # Opposite faces reverse their cutting edge so the highlight follows the geometry.
   edge=0 if face=='north'else w-1
   if mat=='weapon_steel':
    d.line([(edge,0),(edge,h-1)],fill=shade(steel,1.23))
    other=w-1-edge
    d.line([(other,0),(other,h-1)],fill=shade(steel,.72 if single else 1.12))
   else:
    d.rectangle((0,0,w-1,h-1),fill=shade(steel,.82))
    d.line([(edge,0),(edge,h-1)],fill=shade(steel,1.08))
  elif face in ('east','west','down'):
   d.rectangle((0,0,w-1,h-1),fill=shade(steel,.67))
 elif mat=='weapon_spine':
  if face in ('north','south')and w>=2:d.line([(0,0),(0,h-1)],fill=shade(base,1.3))
 elif mat=='weapon_gold':
  if face in ('north','up'):d.line([(0,0),(w-1,0)],fill=shade(gold,1.25))
  if face in ('down','east'):d.rectangle((0,0,w,h),fill=shade(gold,.65))
 else:
  for y in range(1,h,3):d.line([(0,y),(w-1,min(h-1,y+1))],fill=shade(base,.65))
 return im
