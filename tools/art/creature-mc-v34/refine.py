"""Original creature-form corrections. No imported reference meshes/pixels.
Keep existing animated hierarchy, pivots, IDs, skill clips and held weapons.
Large connected anatomical masses replace box stacks. Called after V32 exporter.
"""
from pathlib import Path
import importlib.util,json,copy,math,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/creature-mc-v34';A=R/'src/main/resources/assets/dynasty'
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
 B={b['name']:b for b in g['minecraft:geometry'][0]['bones']}
 def put(n,*cs):B[n]['cubes']=list(cs)
 def box(n,at,size,m,r,rot=None,piv=None):put(n,C(at,size,m,r,rot,piv))
 # One thorax/one abdomen, with legs entering the thorax. No stacked shell lids.
 if id=='gudu_tianzhunv':
  box('thorax',(-7,8,-12),(14,8,18),'spider','thorax',(10,0,0),(0,12,-3))
  put('abdomen',C((-8,7,3),(16,14,24),'spider','abdomen',(-12,0,0),(0,12,5)),C((-10,9,7),(20,10,16),'spider','abdomen',(-12,0,0),(0,12,5)))
  box('pelvis',(-4,12,-10),(8,6,7),'spider','thorax')
  box('waist',(-3,16,-10),(6,5,5),'spider','thorax',(12,0,0),(0,17,-8))
  put('chest',C((-4.5,19,-11),(9,5,7),'spider','thorax',(10,0,0),(0,20,-8)),C((-2,20,-11.8),(4,3,.5),'porcelain','seal'))
  # Face stays recognizable; shoulder and elbow masses taper instead of vertical rods.
  for side,sign in [('left',1),('right',-1)]:
   for i in range(4):
    z=B[f'{side}_leg{i}_hip']['pivot'][2]
    put(f'{side}_leg{i}_hip',segment((sign*6,12,z),(sign*16,13,z),2.8,2.8,'spider','leg'))
    put(f'{side}_leg{i}_knee',segment((sign*16,13,z),(sign*24,9,z),2.2,2.2,'spider','leg'))
    put(f'{side}_leg{i}_tip',segment((sign*24,9,z),(sign*26,.5,z),1.5,1.5,'spider','leg'))
 elif id=='fubo_xunhai_yecha':
  box('carapace',(-12,10,-11),(24,8,26),'chitin','shell',(-7,0,0),(0,12,1))
  box('belly',(-9,8,-9),(18,3,20),'linen','belly')
  put('reef_shell',*[copy.deepcopy(c)|{'_m':'stone'}for c in B['carapace']['cubes']])
  for side,sign in [('left',1),('right',-1)]:
   box(side+'_shell_rim',(10 if sign>0 else -14,10,-8),(4,3,21),'chitin','rim',(0,0,sign*18),(sign*10,12,1))
   box(side+'_rear_fin',(8 if sign>0 else -12,10,12),(4,1,10),'chitin','rim',(0,sign*18,0),(sign*9,11,12))
   for i,z in enumerate((-8,0,8)):
    put(f'{side}_leg{i}',segment((sign*10,11,z),(sign*19,7,z),2.5,3,'chitin','leg'))
    put(f'{side}_leg{i}_knee',segment((sign*19,7,z),(sign*22,1,z),1.8,2,'chitin','leg'))
    box(f'{side}_leg{i}_foot',(sign*22-1,0,z-1.5),(2,1.5,4),'chitin','foot')
 elif id=='mojia_jueying_cike':
  put('ink_case',C((-5,5,-10),(10,5,23),'ink','raybody',(-6,0,0),(0,7,0)),C((-7,5,-14),(14,3,6),'ink','head'))
  for side,sign in [('left',1),('right',-1)]:
   box(side+'_fold_wing',(4 if sign>0 else -16,6,-9),(12,1.5,22),'ink','membrane',(0,sign*12,-sign*8),(sign*5,7,-7))
   box(side+'_outer_fold',(14 if sign>0 else -23,6,-3),(9,1,14),'ink','membrane',(0,sign*22,-sign*12),(sign*15,7,-2))
   box(side+'_bamboo_skid',(4 if sign>0 else -5,3,-5),(1,3,15),'ink','fin',(0,0,sign*15),(sign*5,6,0))
 elif id=='banshan_jiazhou_shikuang':
  # Keep coffin contents/weapon sockets, but a single sloped shoulder carries them.
  put('stitched_viscera',C((-10,16,-15),(20,17,22),'skin','muscle',(-12,0,0),(0,22,-3)),C((-7,26,-20),(14,10,10),'skin','head'),C((-5,23,-23),(10,6,5),'skin','muzzle'),C((-4,23,-23.6),(8,1,1),'ink','mouth'))
  box('rear_grave_mass',(-9,12,7),(18,14,20),'skin','muscle',(10,0,0),(0,18,14))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_grave_eye',C((sign*5-2,31,-21),(4,2,1),'ink','socket'),C((sign*5-1,31,-21.5),(2,1,1),'jade','eye'))
   put(side+'_front_support',segment((sign*10,25,-9),(sign*23,14,-12),10,11,'skin','muscle'))
   put(side+'_foreknuckle',segment((sign*23,15,-12),(sign*24,5,-14),7,8,'skin','muscle'))
   put(side+'_front_fist',C((sign*24-4.5,0,-19),(9,6,10),'skin','hand'),C((sign*24-3.5,1,-20),(7,2,2),'skin','knuckle'))
   put(side+'_hind_support',segment((sign*9,18,18),(sign*20,10,21),8,9,'skin','muscle'))
   put(side+'_hind_ankle',segment((sign*20,10,21),(sign*20,3,21),4,5,'skin','leg'))
   box(side+'_hind_foot',(sign*20-3.5,0,16),(7,3,10),'skin','foot')
 elif id=='hanshan_tongjia_juyuan':
  box('ribcage',(-12,15,-13),(24,18,25),'fur','coat',(-12,0,0),(0,24,0))
  box('haunch',(-9,9,5),(18,14,18),'fur','coat',(8,0,0),(0,15,13))
  # Short neck: skull grows forward out of raised shoulders, not a box on top.
  put('ape_skull',C((-7,25,-23),(14,10,13),'fur','facefur'),C((-7.5,30,-24),(15,3,8),'fur','brow'),C((-5,24,-28),(10,6,7),'skin','muzzle'),C((-2.5,28,-29),(5,1.5,2),'ink','nose'),C((-6,29,-28.5),(2,1,1),'eye','eye'),C((4,29,-28.5),(2,1,1),'eye','eye'),C((-8,26,-17),(2,4,4),'fur','ear'),C((6,26,-17),(2,4,4),'fur','ear'))
  for side,sign in [('left',1),('right',-1)]:
   put(side+'_upperarm',segment((sign*11,28,-5),(sign*22,16,-10),11,12,'fur','coat'),C((sign*15-6,25,-11),(12,3,10),'copper','plate',(0,0,-sign*22),(sign*13,27,-5)))
   put(side+'_forearm',segment((sign*22,17,-10),(sign*22,7,-19),9,10,'fur','coat'),C((sign*22-5,6,-21),(10,3,10),'copper','cuff'))
   put(side+'_knuckles',C((sign*22-5,0,-25),(10,7,10),'fur','hand'),C((sign*22-4,1,-27),(8,2.5,3),'skin','knuckle'))
   put(side+'_hindleg',segment((sign*8,16,12),(sign*9,5,18),7,9,'fur','coat'))
   put(side+'_hindfoot',C((sign*9-4,0,15),(8,3.5,10),'fur','foot'),C((sign*9-3,0,24),(6,2,2),'skin','toe'))
   # The broken breast guards expose one continuous pelt rather than two cabinets.
   box(side+'_chest_plate',(1 if sign>0 else -10,22,-15.5),(9,7,1.5),'copper','plate',(0,0,-sign*8),(sign*4,27,-14))
 elif id=='yinyang_liandan_fangshi':
  # A tapered three-foot vessel; shoulders slope inward, no double box/plinth.
  put('furnace',C((-9,12,-5),(3,10,12),'copper','body',(0,0,-12),(-7,17,1)),C((6,12,-5),(3,10,12),'copper','body',(0,0,12),(7,17,1)),C((-7,12,5),(14,10,3),'copper','body'),C((-7,11,-5),(14,3,11),'iron','interior'),C((-7,20,-6),(14,3,3),'copper','body'),C((-7,14,-6),(3,7,2),'copper','body'),C((4,14,-6),(3,7,2),'copper','body'))
  box('cradle',(-6,9,-4),(12,4,10),'copper','body')
  put('lid',C((-8,23,-5),(16,2,12),'iron','rim'),C((-5,25,-3),(10,3,8),'copper','body'))
  for i in range(3):
   x,y,z=B[f'furnace_leg{i}']['pivot'];sx=-1 if x<0 else 1 if x>0 else 0
   put(f'furnace_leg{i}',segment((x,11,z),(x+sx*1.5,5,z+.5),3,3,'copper','leg'))
   put(f'furnace_knee{i}',segment((x+sx*1.5,5,z+.5),(x,1,z-1),2,2,'iron','hinge'))
   box(f'furnace_foot{i}',(x-2,0,z-3),(4,1.5,5),'iron','foot')
 elif id=='qingdeng_panguan_guichai':
  # Death Tome's useful lesson is a thin articulated book, not a rectangular cabinet.
  box('iron_spine',(-1.5,9,1),(3,23,3),'ink','spine')
  for side,sign in [('left',1),('right',-1)]:
   piv=(sign*3,20,2);rot=(0,-sign*24,sign*5)
   box(side+'_ledger',(3 if sign>0 else -16,10,1),(13,23,1),'purple','book',rot,piv)
   put(side+'_pages',C((4 if sign>0 else -15,12,-1),(11,19,2),'paper','pages',rot,piv))
   # Same hinge transform for cover and page block prevents disconnected paper slabs.
   box(side+'_seal_ribbon',(10 if sign>0 else -12,5,3),(2,10,.5),'purple','ribbon',rot,piv)
  put('judicial_eye',C((-5,20,-4),(10,9,2),'purple','socket'),C((-4,22,-6),(8,5,2),'paper','sclera'),C((-1,22,-6.5),(2,4,1),'jade','pupil'))
  box('inkstone',(-9,0,-5),(18,2,13),'stone','basin')
  put('brush_yoke',segment((3,18,3),(19,18,3),2.5,3,'purple','limb'))
 elif id=='liefeng_jindiao_yushi':
  box('raptor_body',(-7,11,-8),(14,14,23),'feather','body',(-18,0,0),(0,18,2))
  box('raptor_neck',(-4,21,-14),(8,7,10),'pale_feather','neck',(15,0,0),(0,23,-8))
  put('raptor_skull',C((-4.5,25,-23),(9,7,11),'pale_feather','head'),C((-4.5,30,-24),(9,1,7),'feather','brow'),C((-5,28,-22.5),(1,1,3),'eye','eye'),C((4,28,-22.5),(1,1,3),'eye','eye'))
  put('hooked_beak',C((-2,26,-27),(4,3,5),'copper','beak'),C((-1.5,23,-28),(3,4,2),'copper','beak'))
  for side,sign in [('left',1),('right',-1)]:
   box(side+'_wing',(6 if sign>0 else -27,22,-7),(21,2,16),'feather','wing',(0,sign*7,-sign*5),(sign*9,23,1))
   # One thin outer vane with stepped primary tips, instead of overlapping thick boards.
   put(side+'_outer_wing',C((25 if sign>0 else -45,22,-4),(20,1,16),'feather','flight'),*[C((sign*(31+i*4)-2.5,22,10+i*.7),(5,1,8-i),'feather','flight')for i in range(4)])
   put(side+'_tail_fan',C((-1 if sign>0 else -7,11,13),(8,1,19),'feather','flight',(8,sign*8,0),(sign*3,14,14)))
 elif id=='zhenmu_suanni_tonghou':
  # Hollow cast ribs follow an arched back; side openings remain genuine geometry.
  put('hollow_furnace',C((-9,12,-4),(18,3,28),'copper','body'),C((-9,27,-4),(18,4,28),'copper','body',(-8,0,0),(0,28,8)),*[C((x,15,z),(3,13,5),'copper','cast',(0,0,a),(x+1.5,23,z+2))for x,a in [(-11,-12),(8,12)]for z in [-4,18]])
  put('front_casting',C((-9,17,-13),(18,14,10),'copper','body',(12,0,0),(0,24,-7)))
  for k in range(2):
   z=-16+k*6
   put('mane_gear'+str(k),C((-9,28,z),(4,8,3),'copper','mane',(0,0,-25),(-7,30,z)),C((5,28,z),(4,8,3),'copper','mane',(0,0,25),(7,30,z)),C((-7,33,z),(14,2,3),'copper','mane'))
  for side,sign in [('left',1),('right',-1)]:
   for pre,x,z,y in [('front',11,-10,25),('rear',10,20,23)]:
    put(f'{pre}_{side}_upper',segment((sign*x,y,z),(sign*x,14.5 if pre=='front'else 12.5,z),7,8,'copper','muscle'))
    # Splayed feline wrist, still rests on the approved bronze ball and original paw.
    put(f'{pre}_{side}_shin',segment((sign*x,14.5 if pre=='front'else 12.5,z),(sign*(12 if pre=='front'else 10),9,-13 if pre=='front'else 21),4,5,'iron','leg'))
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
    v=1 if f=='down' or (f=='north' and abs(X)<7 and 17<Y<26) else 2
    if role in ('brow','ear'):v=1
    if f in ('east','west') and Y<12:v=1
    # Sparse two-pixel tufts only at the coat boundary, never tiled checker noise.
    if role=='coat' and Y<c['origin'][1]+2 and abs(ix)%7<2:v=1
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
