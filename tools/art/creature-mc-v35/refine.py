"""Original anatomy pass after source-geometry study. Keeps gameplay and animated sockets."""
from pathlib import Path
import importlib.util,json,copy,math,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('v34',R/'tools/art/creature-mc-v34/refine.py');base=importlib.util.module_from_spec(s);s.loader.exec_module(base)
old=base.old;SPECS=base.SPECS;D=R/'docs/art/creature-mc-v35';C=base.C;segment=base.segment
original_forms=base.forms;original_tile=base.tile
# Fur is charcoal, not the same green-grey as undead skin.
old.PAL['fur']=[(32,38,39),(52,61,61),(77,87,85),(119,128,120)]

def forms(id,g):
 g=original_forms(id,g);B={b['name']:b for b in g['minecraft:geometry'][0]['bones']}
 def put(n,*c): B[n]['cubes']=list(c)
 def box(n,o,z,m,r,rot=None,p=None):put(n,C(o,z,m,r,rot,p))
 if id=='gudu_tianzhunv':
  box('thorax',(-7,8,-12),(14,9,20),'spider','thorax')
  put('abdomen',C((-9,8,4),(18,13,23),'spider','abdomen',(-8,0,0),(0,12,5)),C((-7,9,24),(14,9,6),'spider','abdomen'))
  box('venom_sac',(-4,7,27),(8,5,6),'spider','sac')
  box('pelvis',(-4,13,-9),(8,6,6),'spider','thorax')
  box('waist',(-3.5,17,-9),(7,5,5),'spider','thorax')
  for side,sign in [('left',1),('right',-1)]:
   for i in range(4):
    z=B[f'{side}_leg{i}_hip']['pivot'][2]
    put(f'{side}_leg{i}_hip',segment((sign*6,12,z),(sign*16,13,z),2,2,'spider','leg'))
    put(f'{side}_leg{i}_knee',segment((sign*16,13,z),(sign*24,9,z),1.6,1.6,'spider','leg'))
    put(f'{side}_leg{i}_tip',segment((sign*24,9,z),(sign*26,.5,z),1.1,1.1,'spider','leg'))
 elif id=='fubo_xunhai_yecha':
  put('carapace',C((-12,10,-12),(24,7,22),'chitin','shell'),C((-9,16,-9),(18,3,16),'chitin','shell'),C((-9,10,9),(18,4,7),'chitin','shell'))
  put('reef_shell',*[copy.deepcopy(c)|{'_m':'stone'} for c in B['carapace']['cubes']])
  put('mandible',C((-5,10,-15),(10,4,4),'chitin','head'),C((-4,8,-17),(3,4,3),'linen','mouthpart'),C((1,8,-17),(3,4,3),'linen','mouthpart'))
  for side,sign in [('left',1),('right',-1)]:
   box(side+'_shell_rim',(10 if sign>0 else -13,10,-9),(3,4,18),'chitin','shell')
   box(side+'_rear_fin',(7 if sign>0 else -10,10,11),(3,1,7),'chitin','fin',(0,sign*15,0),(sign*9,11,12))
   put(side+'_eye',C((sign*6-1,15,-14),(2,5,2),'chitin','eyestalk'),C((sign*6-1.5,18,-15),(3,2,2),'eye','eye'))
 elif id=='mojia_jueying_cike':
  put('ink_case',C((-5,5,-11),(10,5,24),'ink','raybody'),C((-6,6,-14),(12,3,7),'ink','head'))
  put('front_ink_slot',C((-5,9,-11),(2,1,2),'jade','rayeye'),C((3,9,-11),(2,1,2),'jade','rayeye'),C((-2,5,-14),(4,.5,2),'ink','mouth'))
  for side,sign in [('left',1),('right',-1)]:
   # Broad tapered fins; no rectangular tray edge.
   put(side+'_fold_wing',C((4 if sign>0 else -13,6,-11),(9,2,24),'ink','membrane',(0,0,-sign*6),(sign*5,7,-7)),C((12 if sign>0 else -19,6,-6),(7,1.5,16),'ink','membrane',(0,sign*12,-sign*6),(sign*12,7,-5)))
   put(side+'_outer_fold',C((18 if sign>0 else -24,6,-1),(6,1,8),'ink','membrane',(0,sign*18,-sign*12),(sign*18,6,0)),C((23 if sign>0 else -27,6,1),(4,.5,4),'ink','membrane',(0,sign*18,-sign*12),(sign*18,6,0)))
   box(side+'_bamboo_skid',(4 if sign>0 else -5,4,-5),(1,2,14),'ink','fin')
 elif id=='hanshan_tongjia_juyuan':
  box('ribcage',(-12,15,-13),(24,18,25),'fur','coat',(-8,0,0),(0,24,0))
  box('haunch',(-8,10,8),(16,13,15),'fur','coat')
  for i in range(3):box('dorsal_plate'+str(i),(-9,31,-7+i*6),(18,1.2,5),'copper','plate')
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_upperarm',segment((sign*10,27,-7),(sign*22,16,-10),9,10,'fur','coat'),C((sign*13-4.5,25,-10),(9,1.5,8),'copper','plate'))
   put(side+'_forearm',segment((sign*22,17,-10),(sign*22,5,-20),7,8,'fur','coat'))
   put(side+'_knuckles',C((sign*22-4,0,-25),(8,6,9),'fur','hand'),C((sign*22-3,1,-26),(6,2,2),'skin','knuckle'))
   box(side+'_ankle',(sign*9-2.5,2,15),(5,6,7),'fur','coat')
   box(side+'_chest_plate',(1 if sign>0 else -9,22,-15),(8,6,1),'copper','plate')
 elif id=='banshan_jiazhou_shikuang':
  put('stitched_viscera',C((-11,16,-13),(22,17,22),'skin','muscle',(-8,0,0),(0,22,-3)),C((-7,25,-20),(14,11,10),'skin','head'),C((-5,23,-23),(10,6,5),'skin','muzzle'),C((-4,24,-23.5),(8,1,.5),'ink','mouth'))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_front_support',segment((sign*10,25,-9),(sign*23,14,-12),9,10,'skin','muscle'))
   put(side+'_foreknuckle',segment((sign*23,15,-12),(sign*24,4,-14),6,7,'skin','muscle'))
   box(side+'_front_fist',(sign*24-4,0,-19),(8,5,9),'skin','hand')
   box(side+'_blood_gate',(-8 if sign<0 else 1,19,-14),(7,7,.6),'blood','scar')
  # Binding stays a strap, not a second cage surrounding the flesh.
  for name in ('linen_band-10','linen_band3','linen_band18'):
   for c in B[name]['cubes']:
    if c['size'][0]==2:c['size'][0]=1
    c['size'][2]=2;c['_m']='linen';c['_r']='binding'
 elif id=='yinyang_liandan_fangshi':
  # One recognizable ritual vessel rather than a box sitting on another box.
  put('furnace',C((-8,12,-5),(3,11,12),'copper','body'),C((5,12,-5),(3,11,12),'copper','body'),C((-6,12,5),(12,11,3),'copper','body'),C((-6,11,-5),(12,3,11),'copper','body'),C((-6,21,-6),(12,2,3),'copper','body'),C((-6,14,-6),(2,7,2),'copper','body'),C((4,14,-6),(2,7,2),'copper','body'))
  box('cradle',(-5,10,-3),(10,3,8),'copper','body')
  put('lid',C((-8,23,-5),(16,1.5,12),'iron','rim'),C((-5,24.5,-3),(10,2,8),'copper','body'))
  put('mask',C((-4,17,-7),(8,7,1),'porcelain','mask'),C((-3,20,-8),(2,1,1),'ink','socket'),C((1,20,-8),(2,1,1),'ink','socket'),C((-2,18,-8),(4,.5,1),'ink','mouth'))
 elif id=='qingdeng_panguan_guichai':
  box('iron_spine',(-1.5,10,1),(3,22,3),'purple','spine')
  for side,sign in [('left',1),('right',-1)]:
   piv=(sign*3,20,2);rot=(0,-sign*24,sign*5)
   box(side+'_ledger',(1 if sign>0 else -14,10,1),(13,22,.8),'purple','book',rot,piv)
   box(side+'_pages',(2 if sign>0 else -13,11,-.6),(11,20,1.6),'paper','pages',rot,piv)
  put('judicial_eye',C((-4,21,-2),(8,7,1),'purple','socket'),C((-3,22,-3),(6,4,1),'paper','sclera'),C((-1,22,-4),(2,4,1),'jade','pupil'))
 elif id=='liefeng_jindiao_yushi':
  box('raptor_body',(-7,12,-9),(14,14,23),'feather','body',(-12,0,0),(0,18,2))
  box('raptor_neck',(-4.5,21,-16),(9,8,11),'pale_feather','neck')
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_wing',C((5 if sign>0 else -15,22,-7),(10,3,17),'feather','wing'),C((14 if sign>0 else -27,22,-4),(13,1.5,16),'feather','flight'))
   # Fine feather tips are geometry only at the silhouette; the vane is continuous.
   put(side+'_outer_wing',C((25 if sign>0 else -43,22,-1),(18,.8,14),'feather','flight'),*[C((sign*(29+i*4)-2,22,11+i),(4,.8,7-i),'feather','flight')for i in range(4)])
 elif id=='zhenmu_suanni_tonghou':
  # Continuous feline shoulder/haunch around a genuine narrow furnace aperture.
  put('hollow_furnace',C((-9,13,-3),(18,4,27),'copper','body'),C((-9,25,-3),(18,6,27),'copper','body'),C((-10,16,-3),(4,10,12),'copper','cast'),C((6,16,-3),(4,10,12),'copper','cast'),C((-9,16,13),(18,10,11),'copper','body'))
  box('front_casting',(-9,18,-13),(18,13,12),'copper','body')
  for side,sign in [('left',1),('right',-1)]:
   for pre,x,z,y in [('front',10,-10,25),('rear',9,20,23)]:
    put(f'{pre}_{side}_upper',segment((sign*x,y,z),(sign*(11 if pre=='front'else 10),14,z),8,9,'copper','muscle'))
   box(side+'_bellows',(7 if sign>0 else -9,18,5),(2,6,11),'iron','interior')
 return g

def tile(id,n,j,c,f,w,h,mat,role):
 # Continuous pigmentation crosses cuboid seams in model coordinates. No random noise.
 if mat in ('fur','skin','spider','chitin','feather','pale_feather','ink') and role not in ('eye','rayeye','pupil','nose','mouth','socket','interior','writing'):
  p=old.PAL[mat];im=base.Image.new('RGBA',(w,h));pix=im.load()
  for y in range(h):
   for x in range(w):
    X,Y,Z=old.worldpixel(c,f,x,y,w,h);v=2
    if f=='down':v=1
    if mat=='fur':
     if role in ('muzzle','hand','ear','brow'):v=1
     if n in ('ribcage','haunch')and f=='up':v=3 if abs(X)<6 else 2
     if f in ('north','south')and role=='coat'and Y<19:v=1
     if n in ('ribcage','haunch') and Z>0 and Y>21:
      # A connected silver saddle, not separate patches on every cube.
      edge=7-((int(Z)//5)%2)
      if abs(X)<edge:v=3 if Y>25 else 2
     if role=='coat' and f!='down':
      # Few long tufts at shoulder and forearm boundaries.
      bands=((int(abs(X))//3)+(int(Z)//6))%5
      if bands==0 and int(Y)%11 in (0,1,2):v=max(1,v-1)
     if role=='coat' and ('arm'in n or 'hindleg'in n):
      across=abs(X) if f in ('north','south')else Z
      # Designed grouped hairs on upper/fore limbs, staggered along the limb.
      if (int(across)//3)%3==0 and int(Y)%9 in (2,3,4):v=3
      if (int(across)//3)%3==2 and int(Y)%9 in (6,7):v=1
     if role=='facefur' and f=='north'and abs(X)>4:v=1
    elif mat=='skin':
     if role=='muzzle'and f=='north':v=1 if Y<26 else 2
     if role=='hand'and f=='north'and int(X)%4==0:v=1
     if role=='muscle'and f=='up':v=3
     if role=='muscle'and 21<Y<23 and 4<abs(X)<10:v=1
     if role=='muscle' and (int(Z)+int(abs(X)))%17 in (0,1,2) and 15<Y<19:v=1
    elif mat=='spider':
     if role=='abdomen'and f=='up':
      q=int(Z-abs(X)*.7)%14;v=1 if q<3 else 3 if q==3 else 2
     if role=='leg':v=2 # Remove alternating armor cuffs on biological legs.
    elif mat=='chitin':
     if role=='shell'and f=='up':v=3 if abs(X)<6 else 2
     if role=='shell'and f in ('east','west')and Y<12:v=1
     if role=='shell'and f=='up':
      # Two bilateral shell markings follow the carapace, not its individual slabs.
      ridge=Z+abs(X)*.6
      if -3<ridge<0 or 7<ridge<9:v=1
      elif 0<=ridge<2 or 9<=ridge<11:v=3
     if role=='shell'and f in ('east','west') and 12<Y<15 and int(Z)%10<4:v=3
    elif mat in ('feather','pale_feather'):
     if role in ('wing','flight'):
      v=1 if int(abs(X))%7 in (0,1) and Z>5 else 2
      if Z>13:v=1
     elif role=='body':
      if f=='north' or (f in ('east','west') and Z<-1):
       pale=old.PAL['pale_feather'];v=1 if Y<16 else 2
       if int(Y)%6<2 and int(X+Z)%7<3:v=1
       pix[x,y]=(*pale[v],255);continue
      v=1 if Y<17 else 2
     if role in ('flight','wing') and f in ('up','down'):
      # Long vanes follow span; short staggered tips, no tiled noise.
      along=int(abs(X));across=int(Z)
      if (across+along//8)%6 in (0,1) and along%8<6:v=max(1,v-1)
      if Z>12 or abs(X)>39:v=1
    elif mat=='ink':
     if role=='membrane':v=3 if 3<abs(X)<6 else 2 if abs(X)<18 else 1
     if role=='raybody'and f=='up'and abs(X)<2:v=3
    pix[x,y]=(*p[v],255)
  return im
 im=original_tile(id,n,j,c,f,w,h,mat,role)
 if mat=='paper'and role=='pages'and f in ('north','south'):
  pix=im.load()
  for y in range(h):
   for x in range(w):
    X,Y,Z=old.worldpixel(c,f,x,y,w,h)
    if 13<Y<28 and 3<abs(X)<12 and int(abs(X))%4 in (0,1) and int(Y)%5 in (0,1,2):pix[x,y]=(*old.PAL['paper'][0],255)
 if mat=='copper' and role in ('body','cast','muscle'):
  pix=im.load()
  for y in range(h):
   for x in range(w):
    X,Y,Z=old.worldpixel(c,f,x,y,w,h)
    # Oxidation gathers at lower casting joints; clean raised planes stay bronze.
    if f!='up' and Y<c['origin'][1]+2 and int(X+Z)%11<5:pix[x,y]=(65,91,80,255)
 return im

base.forms=forms;base.tile=tile;base.D=D
finish=base.finish
if __name__=='__main__':
 import sys
 for id in sys.argv[1:]or SPECS:finish(id)
