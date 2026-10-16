"""Original creature-form corrections. No imported reference meshes/pixels.
Keep existing animated hierarchy, pivots, IDs, skill clips and held weapons.
Large connected anatomical masses replace box stacks. Called after V32 exporter.
"""
from pathlib import Path
import importlib.util,json,copy,math,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/creature-mc-v33';A=R/'src/main/resources/assets/dynasty'
s=importlib.util.spec_from_file_location('old_atlas',R/'tools/art/cod1-creatures-v32/paint.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
SPECS=old.SPECS

def C(at,size,mat,role='body',rotation=None,pivot=None):
 c={'origin':list(at),'size':list(size),'uv':{},'_m':mat,'_r':role}
 if rotation:c.update(rotation=list(rotation),pivot=list(pivot))
 return c

def segment(start,end,width,depth,mat,role):
 dx,dy,dz=[end[i]-start[i]for i in range(3)];length=math.sqrt(dx*dx+dy*dy+dz*dz)
 return C((start[0]-width/2,start[1]-length,start[2]-depth/2),(width,length,depth),mat,role,(math.degrees(math.asin(dz/length)),0,math.degrees(math.atan2(-dx,-dy))),start)

def forms(id,g):
 bones=g['minecraft:geometry'][0]['bones'];B={b['name']:b for b in bones}
 def put(n,*c):B[n]['cubes']=list(c)
 def add(n,parent,pivot,*c):
  if n in B:put(n,*c);return
  b={'name':n,'parent':parent,'pivot':list(pivot),'cubes':list(c)};bones.append(b);B[n]=b
 if id=='fubo_xunhai_yecha':
  # A horseshoe crab has a broad rear shield, a lower cephalon, a thin rim; not three boxes on a plinth.
  put('carapace',C((-12,10,-10),(24,9,23),'chitin','shell'),C((-10,17,-7),(20,4,17),'chitin','shell'),C((-9,12,-15),(18,6,8),'chitin','head'),C((-15,10,-8),(3,5,17),'chitin','rim'),C((12,10,-8),(3,5,17),'chitin','rim'))
  put('belly',C((-10,8,-9),(20,3,19),'linen','belly'))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_shell_rim',C((12 if sign>0 else -16,10,-8),(4,4,17),'chitin','rim'),C((14 if sign>0 else -18,11,-5),(4,2,10),'chitin','rim'))
   put(side+'_rear_fin',C((10 if sign>0 else -14,11,8),(4,2,11),'chitin','rim'))
   put(side+'_eye',C((sign*7-1.5,17,-16),(3,4,3),'chitin','eyestalk'),C((sign*7-2,19,-17),(4,2,2),'eye','eye'))
   put(side+'_tide_vent',C((sign*12-1.5,12,-14),(3,2,2),'jade','gill'))
   for i,z in enumerate((-8,0,8)):
    n=f'{side}_leg{i}';put(n,segment((sign*12,10,z),(sign*19,7,z),3,3,'chitin','leg'))
    put(n+'_knee',segment((sign*19,7,z),(sign*22,1,z),2.5,2.5,'chitin','leg'))
    put(n+'_foot',C((18 if sign>0 else -23,0,z-1.5),(5,2,3),'chitin','foot'),C((20 if sign>0 else -25,0,z-1),(5,1,2),'chitin','foot'))
  put('mandible',C((-6,9,-17),(12,3,3),'ink','mouth'),C((-6,7,-18),(3,4,3),'chitin','jaw'),C((3,7,-18),(3,4,3),'chitin','jaw'),C((-4,8,-19),(2,2,2),'linen','tooth'),C((2,8,-19),(2,2,2),'linen','tooth'))
  for n in ['fork_hinge','fork_foresegment','fork_clamp']:
   for c in B[n].get('cubes',[]):c.update(_m='chitin',_r='leg')
  put('telson_base',C((-3,11,10),(6,3,12),'chitin','tail'));put('telson_middle',C((-2,12,20),(4,2,10),'chitin','tail'));put('telson_tip',C((-1,12,28),(2,1,10),'chitin','tail'))
  put('reef_shell',*[copy.deepcopy(c)|{'_m':'stone'}for c in B['carapace']['cubes']])
 elif id=='mojia_jueying_cike':
  # Retain the ink-ray identity: broad continuous membranes, leading cephalon and trailing vanes.
  put('ink_case',C((-6,5,-8),(12,6,19),'ink','raybody'),C((-5,8,-5),(10,4,12),'ink','raybody'),C((-8,5,-13),(16,4,7),'ink','head'))
  put('ink_heart',C((-3,6,-7),(6,3,13),'jade','vein'))
  put('front_ink_slot',C((-6,7,-13.5),(4,2,1),'paper','rayeye'),C((2,7,-13.5),(4,2,1),'paper','rayeye'),C((-2,5,-14),(4,1,2),'ink','mouth'))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_fold_wing',C((5 if sign>0 else -15,6,-9),(10,2,19),'ink','membrane'),C((6 if sign>0 else -16,6,-11),(10,1,4),'ink','membrane'))
   put(side+'_outer_fold',C((14 if sign>0 else -22,6,-5),(8,1,10),'ink','membrane'),C((15 if sign>0 else -21,6,5),(6,1,5),'ink','membrane'))
   put(side+'_bamboo_skid',C((4 if sign>0 else -6,2,-7),(2,4,15),'ink','fin'),C((5 if sign>0 else -7,1,0),(2,2,10),'ink','fin'))
   put(side+'_silk_tail0',C((2 if sign>0 else -5,6,10),(3,1,9),'ink','tail'));put(side+'_silk_tail1',C((2 if sign>0 else -4,6,18),(2,1,9),'ink','tail'))
   # Existing blade carriers remain connected to their unchanged pivots and weapons.
   # Carriage UV and geometry belong to the weapon author and stay unchanged.
 elif id=='gudu_tianzhunv':
  # A compact ritual mask/upper half grows from one thorax; no straight pale block-person body.
  put('thorax',C((-8,8,-12),(16,8,17),'spider','thorax'),C((-6,12,-13),(12,5,12),'spider','thorax'))
  put('abdomen',C((-8,7,3),(16,10,10),'spider','abdomen'),C((-11,7,10),(22,12,15),'spider','abdomen'),C((-8,9,24),(16,8,8),'spider','abdomen'),C((-8,17,12),(16,4,11),'spider','abdomen'))
  put('pelvis',C((-4,13,-11),(8,5,7),'spider','thorax'));put('waist',C((-3,15,-10),(6,5,5),'spider','thorax'))
  put('chest',C((-4,19,-11),(8,5,6),'spider','thorax'),C((-2,20,-11.2),(4,3,1),'porcelain','seal'))
  put('neck',C((-1.5,24,-9.5),(3,2,3),'ink','neck'))
  put('face',C((-3,25,-11),(6,6,5),'porcelain','mask'),C((-2.5,27,-11.5),(2,1,1),'blood','eye'),C((.5,27,-11.5),(2,1,1),'blood','eye'),C((-1,25,-11.5),(2,1,1),'ink','mouth'))
  put('hair',C((-3.5,30,-11.5),(7,2,7),'ink','hair'),C((-3.5,24,-6),(7,7,3),'ink','hair'),C((-2,19,-5),(4,6,3),'ink','hair'))
  for side,sign in [('left',1),('right',-1)]:
   for suffix in ['upper_arm','forearm','hand']:
    for c in B[side+'_'+suffix]['cubes']:c.update(_m='spider',_r='limb')
   for i in range(4):
    n=f'{side}_leg{i}_tip';z=B[n]['pivot'][2]
    put(n,segment((sign*24,9,z),(sign*26,.5,z),2,2,'spider','leg'))
 elif id=='yinyang_liandan_fangshi':
  # Retain actual open furnace; lower chamfered kettle shoulders and a readable possessive mask.
  put('furnace',C((-10,12,-6),(3,10,12),'copper','body'),C((7,12,-6),(3,10,12),'copper','body'),C((-7,12,5),(14,10,3),'copper','body'),C((-7,11,-6),(14,3,3),'copper','body'),C((-7,21,-6),(14,3,3),'copper','body'),C((-7,14,-7),(3,7,3),'copper','body'),C((4,14,-7),(3,7,3),'copper','body'),C((-7,11,-3),(14,2,8),'iron','interior'))
  put('mask',C((-4,17,-9),(8,7,2),'porcelain','mask'),C((-3,20,-10),(2,1,1),'ink','eye'),C((1,20,-10),(2,1,1),'ink','eye'),C((-2,17.5,-10),(4,1,1),'ink','mouth'))
  put('cradle',C((-6,8,-5),(12,4,10),'copper','body'),C((-8,10,-6),(16,2,12),'copper','body'))
  put('lid',C((-9,24,-6),(18,2,12),'iron','rim'),C((-6,26,-4),(12,3,8),'copper','body'))
 elif id=='banshan_jiazhou_shikuang':
  # The coffin sits ON a powerful grave creature, instead of enclosing a cabinet display.
  put('coffin_shell',C((-13,24,-6),(3,12,18),'wood','coffin'),C((10,24,-6),(3,12,18),'wood','coffin'),C((-10,24,8),(20,12,4),'wood','coffin'),C((-13,36,-6),(26,4,18),'wood','coffin'),C((-9,40,-3),(18,2,12),'iron','band'))
  put('stitched_viscera',C((-11,16,-15),(22,17,18),'skin','muscle'),C((-8,28,-18),(16,8,8),'skin','head'),C((-7,22,-21),(14,8,7),'skin','muzzle'),C((-5,22,-22),(10,2,2),'ink','mouth'))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_grave_eye',C((sign*6-2,31,-19.5),(4,2,2),'ink','socket'),C((sign*6-1,31,-20),(2,1,1),'jade','eye'))
   put(side+'_blood_gate',C((-9 if sign<0 else 0,19,-16.5),(9,9,2),'blood','scar'))
   n=side+'_front_fist';put(n,C((18 if sign>0 else -29,0,-18),(11,7,12),'skin','hand'),C((18 if sign>0 else -29,1,-20),(11,3,3),'skin','knuckle'))
   n=side+'_front_support';put(n,C((12 if sign>0 else -28,16,-15),(16,9,11),'skin','muscle'))
  for n in ['linen_band-10','linen_band3','linen_band18']:
   for j,c in enumerate(B[n]['cubes']):
    c['size'][0]=min(c['size'][0],22);c['size'][1]=min(c['size'][1],12)
    if j in (2,3):c['origin'][1]=30
    elif j==4:c['origin'][1]=37
 elif id=='hanshan_tongjia_juyuan':
  # Keep forelimb locomotion and disproportionate arms, expose actual fur masses between limited cast armour.
  put('ribcage',C((-13,16,-12),(26,16,20),'fur','coat'),C((-11,13,-9),(22,10,17),'fur','coat'),C((-14,24,-8),(28,8,16),'fur','coat'))
  put('ape_skull',C((-7,25,-22),(14,10,12),'fur','facefur'),C((-8,30,-23),(16,4,8),'fur','brow'),C((-6,24,-28),(12,7,8),'skin','muzzle'),C((-3,28,-29),(6,2,2),'ink','nose'),C((-6,29,-28.5),(3,1,1),'eye','eye'),C((3,29,-28.5),(3,1,1),'eye','eye'),C((-9,26,-17),(3,4,4),'fur','ear'),C((6,26,-17),(3,4,4),'fur','ear'))
  put('ape_jaw',C((-6,22,-27),(12,3,7),'skin','muzzle'),C((-4,24,-28.6),(2,2,1),'linen','tooth'),C((2,24,-28.6),(2,2,1),'linen','tooth'))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_upperarm',C((12 if sign>0 else -26,15,-13),(14,15,13),'fur','coat'),C((11.5 if sign>0 else -27,25,-12.5),(15.5,5,13),'copper','plate'))
   put(side+'_forearm',C((16 if sign>0 else -28,6,-19),(12,13,13),'fur','coat'),C((15.5 if sign>0 else -28.5,5,-20),(13,5,14),'copper','cuff'))
   put(side+'_knuckles',C((16 if sign>0 else -28,0,-26),(12,8,13),'fur','hand'),C((17 if sign>0 else -27,1,-28),(10,3,3),'skin','knuckle'),C((15.5 if sign>0 else -28.5,7,-24),(13,3,9),'copper','plate'))
   put(side+'_hindfoot',C((4 if sign>0 else -14,0,14),(10,4,12),'fur','foot'),C((5 if sign>0 else -13,.25,24),(8,2,3),'skin','toe'))
 elif id=='qingdeng_panguan_guichai':
  # Living ledger / one watchful eye; thin pages and bowed cover, not twin iron wardrobes.
  put('iron_spine',C((-2,7,1),(4,24,4),'ink','spine'),C((-3,26,0),(6,7,6),'purple','book'))
  put('judicial_eye',C((-5,20,-5),(10,10,3),'purple','socket'),C((-4,22,-7),(8,6,3),'paper','sclera'),C((-1.5,23,-8),(3,4,1),'jade','pupil'))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_ledger',C((3 if sign>0 else -16,10,1),(13,23,2),'purple','book'),C((3 if sign>0 else -16,9,0),(13,2,4),'purple','book'))
   put(side+'_pages',C((4 if sign>0 else -14,13,-1),(10,17,2),'paper','pages'),C((5 if sign>0 else -13,17,-2),(8,1,1),'ink','writing'),C((5 if sign>0 else -13,23,-2),(8,1,1),'ink','writing'))
   put(side+'_seal_ribbon',C((10 if sign>0 else -13,5,3),(3,10,1),'purple','ribbon'))
  put('inkstone',C((-10,0,-6),(20,3,15),'stone','basin'),C((-8,2,-4),(16,2,11),'ink','pool'))
  put('brush_yoke',C((2,16,2),(18,3,4),'purple','limb'),C((16,15,1),(6,6,6),'iron','hinge'))
 elif id=='liefeng_jindiao_yushi':
  # Three bodily masses, a small predatory head, less boxy thick wing slabs; bow/grip untouched.
  put('raptor_body',C((-9,11,-8),(18,13,22),'feather','body'),C((-7,10,-10),(14,10,17),'pale_feather','breast'),C((-7,22,-4),(14,4,16),'feather','back'))
  put('raptor_neck',C((-5,21,-14),(10,7,10),'pale_feather','neck'))
  put('raptor_skull',C((-6,24,-23),(12,7,11),'pale_feather','head'),C((-5,29,-24),(10,2,8),'feather','brow'),C((-6.5,27,-23),(2,2,3),'eye','eye'),C((4.5,27,-23),(2,2,3),'eye','eye'))
  put('hooked_beak',C((-3,25,-29),(6,4,7),'copper','beak'),C((-2,22,-31),(4,5,3),'copper','beak'))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_wing',C((9 if sign>0 else -27,21,-8),(18,4,15),'feather','wing'),C((10 if sign>0 else -26,24,-6),(16,2,10),'feather','coverts'))
   # Consolidate redundant overlapping strips; one feather per stepped primary.
   cs=B[side+'_outer_wing']['cubes'];B[side+'_outer_wing']['cubes']=[cs[i]for i in [0,1,3,5,7]] if len(cs)>5 else cs
   for c in B[side+'_outer_wing']['cubes']:c.update(_m='feather',_r='flight');c['size'][1]=min(c['size'][1],2)
 elif id=='zhenmu_suanni_tonghou':
  # Hollow cast lion stays hollow. Simplify squared gear frame into stepped mane lobes.
  put('lion_head',C((-8,24,-23),(16,10,13),'copper','lionface'),C((-6,24,-30),(12,5,8),'copper','muzzle'),C((-3,28,-31),(6,2,2),'ink','nose'),C((-8.5,29,-25),(2,2,4),'ink','socket'),C((-8.8,29,-25),(1,1,2),'fire','eye'),C((-7,33,-18),(3,3,4),'copper','ear'),C((-5,22,-29),(2,3,2),'linen','tooth'),C((6.5,29,-25),(2,2,4),'ink','socket'),C((7.8,29,-25),(1,1,2),'fire','eye'),C((4,33,-18),(3,3,4),'copper','ear'),C((3,22,-29),(2,3,2),'linen','tooth'))
  put('hinged_lower_jaw',C((-6,20,-30),(12,3,12),'copper','jaw'),C((-4,23,-29),(8,1,1),'linen','tooth'))
  for i in range(2):
   z=-16-i*-6
   put('mane_gear'+str(i),C((-8,33,z),(16,3,3),'copper','mane'),C((-8,15,z),(16,3,3),'copper','mane'),C((-11,19,z),(4,13,3),'copper','mane'),C((7,19,z),(4,13,3),'copper','mane'),C((-10,30,z),(5,4,3),'copper','mane'),C((5,30,z),(5,4,3),'copper','mane'))
 return g

# Texture materials use anatomy and model-space direction; reference assets are never loaded.
def tile(id,n,j,c,f,w,h,mat,role):
 p=old.PAL[mat];im=Image.new('RGBA',(w,h),p[2]);pix=im.load()
 for y in range(h):
  for x in range(w):
   X,Y,Z=old.worldpixel(c,f,x,y,w,h);v=2
   if f=='down' or role in ('socket','interior','mouth','spine'):v=0 if role=='mouth' else 1
   if mat=='fur':
    v=1 if Y<13 else 2
    flow=int(Z if n in ('ribcage','haunch')else -Y);across=int(X if f in ('north','south','up','down')else Z)
    if flow%7 in (0,1) and across%6 in (0,1):v=max(0,v-1)
    if role in ('brow','ear'):v=1
   elif mat in ('chitin','spider'):
    if role in ('shell','abdomen','thorax'):
     v=1 if f in ('east','west') and Y<13 else 2
     if f=='up' and abs(X)<4:v=3
     if role=='abdomen'and abs(abs(X)-abs(Z-19)*.65)<2:v=1
     if mat=='chitin'and f=='up'and int(Z)%9==0 and abs(X)<8:v=1
    elif role in ('foot','leg'):v=1 if Y<4 else 2
   elif mat=='ink':
    if role in ('raybody','head'):v=2 if Y>7 else 1
    if role in ('membrane','fin','tail'):
     # Symmetric organic vein bands within an uninterrupted dark membrane.
     v=2 if abs(X)<13 else 1
     if f in ('up','down') and int(Z+abs(X)*.5)%11 in (0,1):v=3
    if role=='hair':v=1 if int(X)%4==0 else 2
   elif mat=='feather' or mat=='pale_feather':
    flow=int(abs(X) if role in ('flight','wing','coverts')else Z if 'tail'in n else -Y)
    across=int(Z if role in ('flight','wing','coverts')else X)
    v=1 if flow%8==0 and across%6<4 else 2
    if role=='flight'and across%8==1:v=3
    if role=='brow':v=1
   elif mat=='skin':
    if role in ('muzzle','hand','toe','knuckle'):v=2 if Y>24 or Y<5 else 1
    if role=='muscle' and f in ('north','south') and abs(X)>8:v=1
    if role=='muzzle' and f=='north' and abs(X)<2:v=1
   elif mat=='wood':
    if int(Z)%7==0 and int(Y)%16<10:v=1
    if f=='up':v=3
   elif mat=='purple':
    if role=='book':
     if f=='north' and (int(Y)in (13,29) or int(abs(X))==14):v=1
    elif role=='ribbon':v=1 if x==0 else 2
   elif mat=='copper':
    if f=='up':v=3
    if f in ('north','south') and Y<c['origin'][1]+2:v=1
    if role in ('muzzle','lionface') and f in ('east','west')and int(Y)==27:v=1
    if role in ('plate','body') and f in ('east','west') and int(Z)%13==0 and int(Y)%17<3:v=1
   elif mat=='paper':
    if role=='pages':v=1 if int(Y)%3==0 else 2
   elif mat=='stone':
    if f=='up':v=2
    if int(Y)%9==0 and int(X)%11<3:v=1
   elif mat=='porcelain':
    if f in ('east','west','down'):v=1
    if role=='mask' and f=='north':
     # Lower cheeks and bridge establish a simple face without painting a human skin.
     if Y<c['origin'][1]+2 or abs(X)>c['size'][0]*.35:v=1
   elif mat=='blood':
    if role=='scar':v=1
   # Pixel clusters are aligned to anatomy, not independent panel borders.
   # Large quiet midtones remain; two-pixel locks carry the material direction.
   ix,iy,iz=math.floor(X),math.floor(Y),math.floor(Z)
   if mat=='fur' and role not in ('eye','mouth'):
    along=-iy;across=ix if f in ('north','south','up','down')else iz
    lock=(across+2*(along//6))%7
    if along%6 in (0,1,2)and lock in (0,1):v=max(0,v-1)
    if along%6==3 and lock in (1,2)and Y>16:v=3
    if n=='ribcage'and f=='north'and abs(X)<7 and 17<Y<26:v=1
   elif mat=='skin':
    if role=='muzzle':
     if f=='north' and Y<c['origin'][1]+2:v=1
     if f=='north' and abs(X)>4:v=1
     if f=='north' and abs(X)<2 and Y>c['origin'][1]+c['size'][1]-3:v=0
    elif role=='muscle':
     if (abs(ix)+iy//5)%11 in (0,1)and iy%8<3:v=max(0,v-1)
     if f=='up'and abs(X)<c['size'][0]*.3:v=3
    elif role in ('hand','knuckle','toe')and f=='north'and ix%4==0:v=1
   elif mat in ('chitin','spider'):
    if role in ('shell','head','abdomen','thorax'):
     if mat=='chitin':
      if f=='up'and abs(X)<3:v=1 if iz%8<2 else 3
      if f in ('east','west')and iy%7 in (0,1)and iz%10<6:v=1
      if f=='north'and Y<14:v=1
      if f=='up'and 6<abs(X)<9 and iz%12 in (3,4):v=3
     else:
      # Twin chevrons follow the abdomen, not gray camouflage squares.
      if 'abdomen'==role and f=='up':
       band=int(abs(X)*.65+Z)%12
       if band in (0,1,2):v=1
       elif band==3:v=3
      if f in ('east','west')and iy<12:v=1
    if role=='leg'and iy%9 in (0,1):v=max(0,v-1)
   elif mat in ('feather','pale_feather'):
    along=abs(ix)if role in ('flight','wing','coverts')else -iy
    across=iz if role in ('flight','wing','coverts')else ix
    if (across+(along//6)*2)%5 in (0,1)and along%6 in (0,1,2):v=1
    if along%6==3 and across%5 in (2,3):v=3
    if role=='breast'and Y<17:v=1
   elif mat=='wood':
    if f in ('north','south'):v=2 if ix%8>1 else 1
    if f in ('east','west')and iz%8 in (0,1):v=1
    if f!='up'and iy%13 in (0,1)and iz%15 in (4,5,6):v=3
   elif mat=='copper':
    if role in ('body','plate','cast')and f in ('north','east','west','south'):
     if iy<c['origin'][1]+2:v=1
     # Short cast relief and sparse rubbed facets, not a frame on every cube.
     if iy%14 in (5,6)and (ix if f in ('north','south')else iz)%18 in (5,6,7,8):v=3
    if role=='lionface'and f=='north'and abs(X)<3:v=1
   elif mat=='iron':
    if f=='down'or role in ('hinge','interior'):v=1
    elif f=='up':v=3
    elif iy%12 in (2,3)and ix%14<4:v=1
   elif mat=='purple'and role=='cloth':
    if ix%7 in (0,1):v=1
    if ix%7==4 and iy%13<7:v=3
   elif mat=='linen':
    if iy%10 in (0,1):v=1
    if f=='up':v=3
   if role in ('eye','rayeye','pupil'):
    v=0 if x==w//2 else 2
    if w>=3 and x==w//2-1 and y==0:v=3
   if role in ('core','vein','gill','sac'):v=3 if (x>=w//3 and x<w*2//3)else 1
   if role in ('nose','writing','mouth'):v=0
   pix[x,y]=(*p[v],255)
 return im

def finish(id):
 gp=old.path(id,'geo');tp=old.path(id,'texture');g=json.loads(gp.read_text());d=D/id;d.mkdir(parents=True,exist_ok=True)
 # Preserve the actual immediately previous runtime resources once, not HEAD's older flat swatches.
 if not(d/'before.geo.json').exists():
  (d/'before.geo.json').write_bytes(gp.read_bytes());(d/'before.png').write_bytes(tp.read_bytes());(d/'before.animation.json').write_bytes(old.path(id,'anim').read_bytes())
 legacy=Image.open(tp).convert('RGBA').crop((0,0,16,16));g=forms(id,g);records=[]
 for b in g['minecraft:geometry'][0]['bones']:
  for j,c in enumerate(b.get('cubes',[])):
   if '_m'in c:mat,role=c['_m'],c['_r']
   else:mat,role=old.category(id,b['name'],j,c)
   if mat is None:continue
   for f,dims in {'north':(0,1),'south':(0,1),'west':(2,1),'east':(2,1),'up':(0,2),'down':(0,2)}.items():
    w,h=[max(1,math.ceil(c['size'][i]))for i in dims];records.append({'bone':b['name'],'index':j,'cube':c,'face':f,'w':w,'h':h,'material':mat,'role':role})
 for size in (128,256,512,1024):
  x=0;y=18;row=0;ok=True
  for v in sorted(records,key=lambda v:(-v['h'],-v['w'])):
   w,h=v['w'],v['h']
   if x+w+2>size:x=0;y+=row+2;row=0
   if x+w+2>size or y+h+2>size:ok=False;break
   v['xy']=(x+1,y+1);x+=w+2;row=max(row,h)
  if ok:break
 atlas=Image.new('RGBA',(size,size));atlas.paste(legacy,(0,0));islands=[]
 for v in records:
  x,y=v['xy'];w,h=v['w'],v['h'];f=v['face'];c=v['cube'];im=tile(id,v['bone'],v['index'],c,f,w,h,v['material'],v['role']);atlas.paste(im,(x,y));c.setdefault('uv',{})[f]={'uv':[x,y],'uv_size':[w,h]};islands.append({k:value for k,value in v.items()if k not in ('cube','xy')}|{'rect':[x,y,w,h]})
  atlas.paste(im.crop((0,0,w,1)),(x,y-1));atlas.paste(im.crop((0,h-1,w,h)),(x,y+h));atlas.paste(im.crop((0,0,1,h)),(x-1,y));atlas.paste(im.crop((w-1,0,w,h)),(x+w,y))
 for b in g['minecraft:geometry'][0]['bones']:
  for c in b.get('cubes',[]):c.pop('_m',None);c.pop('_r',None)
 g['minecraft:geometry'][0]['description'].update(texture_width=size,texture_height=size);gp.write_text(json.dumps(g,indent=2)+'\n');atlas.save(tp);atlas.save(d/'texture.png');atlas.resize((size*2,size*2),Image.Resampling.NEAREST).save(d/'texture-2x.png');(d/'islands.json').write_text(json.dumps(islands,indent=2))
 for aux in SPECS[id][2]:
  f=old.path(aux,'geo')
  if f.exists():v=json.loads(f.read_text());v['minecraft:geometry'][0]['description'].update(texture_width=size,texture_height=size);f.write_text(json.dumps(v,indent=2)+'\n')
 dead=tp.with_name(id+'_dead.png')
 if dead.exists():
  im=atlas.copy()
  for v in islands:
   if v['role']in ('eye','core','pupil','gill'):
    x,y,w,h=v['rect'];patch=im.crop((x,y,x+w,y+h));rgb=patch.convert('RGB').point(lambda z:int(z*.55));rgb.putalpha(255);im.paste(rgb,(x,y))
  im.save(dead)
 print('Refined',id,size,len(records),flush=True)
if __name__=='__main__':
 import sys
 for id in sys.argv[1:]or SPECS:finish(id)
