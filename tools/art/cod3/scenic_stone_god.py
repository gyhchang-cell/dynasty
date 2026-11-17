#!/usr/bin/env python3
"""Original scenic #6 mountain giant. Own geometry only; never production PNG/Java."""
from pathlib import Path
import json,math,uuid,base64,hashlib,sys,itertools
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];A=ROOT/'src/main/resources/assets/dynasty';D=ROOT/'docs/art/cod3-stone-god-v2'
SIDE=1024
MATS={'rock':(121,130,125),'joint_rock':(70,81,79),'strata':(103,116,109),'stone_face':(151,157,142),'crown':(115,129,118),'axe_edge':(177,183,167),'haft':(91,72,50),'binding':(90,80,56),'bronze':(114,99,65),'jade':(101,157,142)}
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def design():
 bones=[];by={};parts=[]
 def bone(n,parent,p):
  b={'name':n,'pivot':list(p),'cubes':[]}
  if parent:b['parent']=parent
  bones.append(b);by[n]=b
 def box(b,o,s,mat,label,lod=2,rot=None,pivot=None):
  c={'origin':list(o),'size':list(s)}
  if rot:c.update(rotation=rot,pivot=list(pivot))
  by[b]['cubes'].append(c);parts.append({'cube':c,'bone':b,'material':mat,'label':label,'lod':lod})
 def segment(b,start,end,w,dep,mat,label,lod=2,overlap=12):
  start=np.array(start,dtype=float);dv=np.array(end)-start;length=np.linalg.norm(dv)
  rot=[-math.degrees(math.asin(dv[2]/length)),0,math.degrees(math.atan2(dv[0],dv[1]))]
  box(b,[start[0]-w/2,start[1]-overlap/2,start[2]-dep/2],[w,length+overlap,dep],mat,label,lod,rot,start)
 bone('root',None,(0,0,0));bone('pelvis','root',(0,220,0))
 box('pelvis',(-66,196,-44),(132,68,88),'rock','pelvic_mass')
 box('pelvis',(-75,232,-48),(150,22,96),'strata','iliac_ridge',1)
 box('pelvis',(-26,194,42),(52,45,12),'bronze','central_girdle',0)
 bone('waist','pelvis',(0,253,0));box('waist',(-51,250,-43),(102,68,86),'joint_rock','lumbar_core')
 box('waist',(-54,267,37),(108,38,12),'rock','abdominal_plane',1)
 bone('chest','waist',(0,308,0))
 box('chest',(-90,304,-54),(180,91,108),'rock','ribcage')
 box('chest',(-79,320,48),(75,66,15),'strata','pectoral_left',1)
 box('chest',(4,320,48),(75,66,15),'strata','pectoral_right',1)
 box('chest',(-16,315,55),(32,73,14),'rock','sternum_keystone',1)
 box('chest',(-70,324,-66),(140,56,19),'strata','scapular_shelf',1)
 box('chest',(-25,312,-72),(50,68,12),'rock','spinal_ridge',0)
 # Heavy layered shoulders, not detached mini cubes or armor boxes.
 for side in (-1,1):
  x=side*95
  box('chest',(x-34,359,-44),(68,49,87),'rock',f'deltoid_{side}')
  box('chest',(x-38,394,-39),(76,16,77),'strata',f'shoulder_cap_{side}',1)
  box('chest',(x-22,407,-28),(44,9,54),'crown',f'shoulder_crest_{side}',0)
 bone('neck','chest',(0,390,1));box('neck',(-29,386,-28),(58,38,60),'joint_rock','neck_column')
 bone('head','neck',(0,420,5))
 box('head',(-38,410,-29),(76,67,65),'rock','skull')
 box('head',(-32,415,30),(64,53,17),'stone_face','stone_mask')
 box('head',(-35,455,42),(70,10,13),'crown','brow_ridge',1)
 box('head',(-7,433,43),(14,26,14),'stone_face','nose_bridge',1)
 box('head',(-24,410,36),(48,15,17),'stone_face','jaw_plane',1)
 for side in (-1,1):
  x=side*20
  box('head',(x-8,448,46.8),(16,4,1.2),'jade',f'eye_inlay_{side}',0)
  box('head',(side*37-6,422,4),(12,28,23),'strata',f'temple_{side}',1)
 box('head',(-43,473,-33),(86,13,72),'bronze','crown_band',2)
 box('head',(-34,482,-26),(68,16,58),'crown','mountain_crown_base')
 box('head',(-14,496,-21),(28,25,43),'crown','central_peak')
 box('head',(-34,494,-18),(16,16,37),'crown','left_peak',1)
 box('head',(19,494,-18),(15,12,37),'crown','right_peak',1)
 for side,name in [(-1,'right'),(1,'left')]:
  hip=(side*48,220,-4);knee=(side*76,132,14);ankle=(side*82,32,5)
  bone(name+'_thigh','pelvis',hip);segment(name+'_thigh',hip,knee,68,74,'rock',name+'_femur')
  box(name+'_thigh',(side*76-34,119,-12),(68,38,64),'strata',name+'_kneecap',1)
  bone(name+'_shin',name+'_thigh',knee);segment(name+'_shin',knee,ankle,54,60,'joint_rock',name+'_tibia')
  segment(name+'_shin',(side*78,113,40),(side*82,43,32),46,17,'strata',name+'_shin_plane',1)
  bone(name+'_foot',name+'_shin',ankle)
  box(name+'_foot',(side*82-37,0,-36),(74,33,102),'rock',name+'_heel_and_sole')
  box(name+'_foot',(side*82-31,28,-23),(62,14,62),'strata',name+'_instep',1)
  box(name+'_foot',(side*82-34,0,62),(68,22,10),'strata',name+'_toe_group',0)
  shoulder=(side*112,368,0);elbow=(side*153,290,25);wrist=(side*148,274,90)
  bone(name+'_upper_arm','chest',shoulder);segment(name+'_upper_arm',shoulder,elbow,58,66,'rock',name+'_humerus',overlap=22)
  box(name+'_upper_arm',(side*153-32,268,-2),(64,44,58),'strata',name+'_elbow',1)
  bone(name+'_forearm',name+'_upper_arm',elbow);segment(name+'_forearm',elbow,wrist,58,58,'rock',name+'_radius',overlap=22)
  segment(name+'_forearm',(side*153,300,38),(side*148,286,82),60,16,'strata',name+'_forearm_ridge',1)
  grip=(side*148,274,112);bone(name+'_hand',name+'_forearm',grip)
  x,y,z=grip
  if name=='right':
   # Actual 14x14 shaft aperture, all four gripping groups touch its surface.
   for label,o,size in [('palm',(x-23,y-23,z-23),(46,46,16)),('fingers',(x-23,y-23,z+7),(46,46,16)),('thumb',(x-23,y-23,z-7),(16,46,14)),('knuckles',(x+7,y-23,z-7),(16,46,14))]:box(name+'_hand',o,size,'rock',name+'_'+label)
   bone('axe',name+'_hand',grip)
   box('axe',(x-7,134,z-7),(14,316,14),'haft','axe_haft')
   box('axe',(x-10,244,z-10),(20,7,20),'binding','lower_grip_binding',0)
   box('axe',(x-10,297,z-10),(20,8,20),'binding','upper_grip_binding',0)
   box('axe',(x-20,416,z-20),(44,44,40),'binding','axe_socket')
   box('axe',(x-66,398,z-18),(50,76,36),'rock','axe_root')
   box('axe',(x-112,390,z-12),(48,92,24),'strata','axe_cheek')
   box('axe',(x-132,402,z-5),(22,68,10),'axe_edge','axe_cutting_edge')
   box('axe',(x-122,394,z-7),(13,84,14),'axe_edge','axe_bevel',1)
   box('axe',(x+18,424,z-14),(21,27,28),'rock','axe_poll',1)
  else:
   box(name+'_hand',(x-25,y-25,z-25),(50,50,48),'rock','left_counterweight_fist')
   box(name+'_hand',(x-28,y-20,z+20),(56,36,10),'strata','left_finger_group',1)
   box(name+'_hand',(x-30,y+3,z-10),(13,23,28),'rock','left_thumb',0)
 # Lower body stays planted; upper anatomy carries a slow gathering-and-settling motion.
 times=[0,2.5,4,4.8,6,8]
 def keys(values):return {str(t):v for t,v in zip(times,values)}
 tracks={'waist':{'rotation':keys([[0,0,0],[-1,-3,0],[-2,-4,0],[1,2,0],[0,1,0],[0,0,0]])},'chest':{'rotation':keys([[0,0,0],[-1,-2,0],[-2,-3,0],[1,2,0],[0,1,0],[0,0,0]])},'head':{'rotation':keys([[0,0,0],[0,2,0],[1,3,0],[0,-1,0],[0,0,0],[0,0,0]])},'right_upper_arm':{'rotation':keys([[0,0,0],[-4,0,-2],[-8,0,-3],[3,0,1],[1,0,0],[0,0,0]])},'right_forearm':{'rotation':keys([[0,0,0],[-5,0,0],[-10,0,0],[4,0,0],[1,0,0],[0,0,0]])},'left_upper_arm':{'rotation':keys([[0,0,0],[2,0,1],[4,0,2],[-2,0,0],[-1,0,0],[0,0,0]])}}
 return bones,parts,{'format_version':'1.8.0','animations':{'animation.scenic.idle':{'loop':True,'animation_length':8,'bones':tracks}}}

def build():
 bones,parts,anim=design();islands=[]
 for p in parts:
  w,h,d=p['cube']['size']
  for face,a,b in [('north',w,h),('south',w,h),('west',d,h),('east',d,h),('up',w,d),('down',w,d)]:
   islands.append({'part':p['label'],'bone':p['bone'],'material':p['material'],'face':face,'rect':[0,0,max(2,round(a*.5)),max(2,round(b*.5))],'cube_origin':p['cube']['origin'],'cube_size':p['cube']['size'],'cube_rotation':p['cube'].get('rotation',[0,0,0]),'cube_pivot':p['cube'].get('pivot'), 'direction':'Cube-local UV; side V follows local Y, cap axes X/Z; rotations included above.'})
 lock=D/'UV_LOCK.json'
 if lock.exists():
  old=json.loads(lock.read_text())['islands'];assert [[r[k] for k in ('part','face','material','cube_origin','cube_size','cube_rotation','cube_pivot')] for r in old]==[[r[k] for k in ('part','face','material','cube_origin','cube_size','cube_rotation','cube_pivot')] for r in islands],'Frozen geometry/UV changed'
  islands=old
 else:
  x=y=2;row=0
  for r in sorted(islands,key=lambda r:-r['rect'][3]):
   _,_,w,h=r['rect']
   if x+w+2>SIDE:x=2;y+=row+2;row=0
   assert y+h+2<SIDE,'Atlas too small'
   r['rect']=[x,y,w,h];x+=w+2;row=max(row,h)
 lookup={p['label']:p for p in parts}
 for p in parts:p['cube']['uv']={}
 temp=Image.new('RGB',(SIDE,SIDE),(32,37,39));draw=ImageDraw.Draw(temp)
 for r in islands:
  x,y,w,h=r['rect'];lookup[r['part']]['cube']['uv'][r['face']]={'uv':[x,y],'uv_size':[w,h]};draw.rectangle((x,y,x+w-1,y+h-1),fill=MATS[r['material']])
 temp.save(D/'temporary-material-atlas.png')
 dump(D/'draft-uv.json',{'atlas_size':[SIDE,SIDE],'islands':islands,'pixels_per_metre':8,'production_png_owner':'texture author; this generator never writes production PNG'})
 desc={'identifier':'geometry.dynasty.stone_god','texture_width':SIDE,'texture_height':SIDE,'visible_bounds_width':70,'visible_bounds_height':45,'visible_bounds_offset':[0,20,0]}
 counts={}
 for suffix,level in [('',0),('_medium',1),('_far',2)]:
  out=[dict(b,cubes=[p['cube'] for p in parts if p['bone']==b['name'] and p['lod']>=level]) for b in bones]
  counts[suffix or 'full']=sum(len(b['cubes']) for b in out)
  dump(A/f'geo/scenic/stone_god{suffix}.geo.json',{'format_version':'1.12.0','minecraft:geometry':[{'description':desc,'bones':out}]})
 dump(A/'animations/scenic/stone_god.animation.json',anim);dump(D/'blockbench/stone_god.animation.json',anim)
 def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty/stone-god-v2/'+s))
 groups={b['name']:{'name':b['name'],'uuid':uid(b['name']),'origin':[-b['pivot'][0],*b['pivot'][1:]],'children':[]} for b in bones};elements=[]
 for p in parts:
  c=p['cube'];x,y,z=c['origin'];w,h,d=c['size'];cp=c.get('pivot',next(b['pivot'] for b in bones if b['name']==p['bone']));rot=c.get('rotation',[0,0,0]);faces={}
  for f,t in c['uv'].items():
   u,v=t['uv'];du,dv=t['uv_size'];faces[f]={'texture':0,'uv':[u+du,v+dv,u,v] if f in ('up','down') else [u,v,u+du,v+dv]}
  ident=uid(p['label']);elements.append({'name':p['label'],'uuid':ident,'type':'cube','from':[-x-w,y,z],'to':[-x,y+h,z+d],'origin':[-cp[0],cp[1],cp[2]],'rotation':[-rot[0],-rot[1],rot[2]],'box_uv':False,'faces':faces});groups[p['bone']]['children'].append(ident)
 out=[]
 for b in bones:
  if b.get('parent'):groups[b['parent']]['children'].append(groups[b['name']])
  else:out.append(groups[b['name']])
 target=D/'blockbench/stone_god.bbmodel'
 textures=json.loads(target.read_text())['textures'] if target.exists() else [{'name':'temporary-material-atlas.png','uuid':uid('texture'),'source':'data:image/png;base64,'+base64.b64encode((D/'temporary-material-atlas.png').read_bytes()).decode()}]
 dump(target,{'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},'name':'stone_god','model_identifier':'stone_god','geckolib_modid':'dynasty','resolution':{'width':SIDE,'height':SIDE},'elements':elements,'outliner':out,'textures':textures})
 print('Export',counts,'bones',len(bones),flush=True)
 return counts

def review(final=False):
 sys.path.insert(0,str(ROOT/'tools/art/boss-forms'));import texture_review as v
 v.r.CATEGORY='scenic';tex=np.array(Image.open(A/'textures/entity/scenic/stone_god.png' if final else D/'temporary-material-atlas.png').convert('RGB'))
 def pose(t=0,lod=''):return v.r.geometry('stone_god',clip='animation.scenic.idle',tick=t,geo_path=A/f'geo/scenic/stone_god{lod}.geo.json')
 q=pose();pts=np.concatenate([x[0] for x in q]);frame=np.array(list(itertools.product(*zip(pts.min(0)-25,pts.max(0)+25))))
 foot='真实生产PNG逐面采样 · 软件预览 · 非实机截图 · 1格=16单位' if final else '软件灰模/临时材质分区 · 非最终贴图 · 非实机截图 · 1格=16单位'
 def save(q,t,yaw,name,size=(900,900)):
  v.labelled(v.raster(q,t,yaw=yaw,elevation=6,size=size,mode='lit',frame_points=frame),'开山石神 / '+name,foot).save(D/(name+'.png'))
 for yaw,n in [(180,'front'),(135,'45'),(90,'right'),(-90,'left'),(0,'back')]:save(q,tex,yaw,n)
 save(q,np.full_like(tex,153),135,'gray');save(q,np.zeros_like(tex),180,'silhouette')
 refs=v.references(np.array([-230,0,80]));v.labelled(v.raster(q+refs,tex,yaw=180,elevation=3,size=(1100,1000),mode='lit'),'32.56米石神 / 1.8米玩家 / 1米方块',foot).save(D/'world-scale.png')
 for lod in ('','_medium','_far'):
  save(pose(0,lod),tex,135,'lod'+(lod or '_full'))
  frames=[v.labelled(v.raster(pose(t,lod),tex,yaw=135,elevation=6,size=(640,640),mode='lit',frame_points=frame),f'{lod or "full"} / {t} tick',foot) for t in range(0,160,5)]
  frames[0].save(D/f'idle{lod}.webp',save_all=True,append_images=frames[1:],duration=250,loop=0,lossless=True)
 for bones,n in [({'head','neck'},'head-close'),({'right_hand','axe','right_forearm'},'grip-close')]:
  subset=[qq for qq in q if qq[2] in bones];v.labelled(v.raster(subset,tex,yaw=135,elevation=10,size=(900,700),mode='lit'),n,foot).save(D/f'{n}.png')
 cycle=Image.new('RGB',(1800,1360))
 for i,tick in enumerate((0,50,80,96,120,159)):
  im=v.labelled(v.raster(pose(tick),tex,yaw=135,elevation=6,size=(600,600),mode='lit',frame_points=frame),f'{tick} tick',foot);cycle.paste(im,(i%3*600,i//3*680))
 cycle.save(D/'cycle-check.png')
 if final:
  gray=np.repeat((tex@np.array([.2126,.7152,.0722]))[...,None],3,axis=-1).astype(np.uint8);save(q,gray,135,'texture-gray')
  v.labelled(v.raster(q,tex,yaw=135,elevation=6,size=(900,900),mode='unlit',frame_points=frame),'原色贴图',foot).save(D/'unlit.png')
 contact=Image.new('RGB',(1800,1800))
 for i,n in enumerate(['front','45','right','back']):contact.paste(Image.open(D/(n+'.png')).resize((900,900)),(i%2*900,i//2*900))
 contact.save(D/'overview.png')
 print('Previews written',flush=True)

def validate():
 sys.path.insert(0,str(ROOT/'tools/art/boss-forms'));import texture_review as v
 v.r.CATEGORY='scenic'
 def pose(t=0,lod=''):return v.r.geometry('stone_god',clip='animation.scenic.idle',tick=t,geo_path=A/f'geo/scenic/stone_god{lod}.geo.json')
 def obb(quads):
  pts=np.concatenate([x[0] for x in quads]);q=quads[0][0];a=q[1]-q[0];b=q[3]-q[0]
  return pts,np.array([a/np.linalg.norm(a),b/np.linalg.norm(b),np.cross(a,b)/np.linalg.norm(np.cross(a,b))])
 def touches(a,b):
  ap,aa=a;bp,ba=b
  if np.any(ap.max(0)<bp.min(0)-1e-6) or np.any(bp.max(0)<ap.min(0)-1e-6):return False
  for axis in list(aa)+list(ba)+[np.cross(x,y) for x in aa for y in ba]:
   if np.linalg.norm(axis)<1e-8:continue
   p=ap@axis;q=bp@axis
   if max(p)<min(q)-1e-6 or max(q)<min(p)-1e-6:return False
  return True
 validations=[];bounds=[]
 for lod in ('','_medium','_far'):
  g=json.loads((A/f'geo/scenic/stone_god{lod}.geo.json').read_text())['minecraft:geometry'][0];bs=g['bones'];names={b['name'] for b in bs};assert len(names)==len(bs)
  assert all(not b.get('parent') or b['parent'] in names for b in bs)
  for b in bs:
   for c in b['cubes']:
    assert min(c['size'])>0 and len(c['uv'])==6
    for t in c['uv'].values():
     u,vv=t['uv'];w,h=t['uv_size'];assert min(u,vv,w,h)>0 and u+w<SIDE and vv+h<SIDE
  initial_contacts=None;new_contacts=set()
  for tick in range(0,161):
   q=pose(tick,lod);boxes=[obb(q[i:i+6]) for i in range(0,len(q),6)];seen={0};todo=[0]
   while todo:
    i=todo.pop()
    for j in range(len(boxes)):
     if j not in seen and touches(boxes[i],boxes[j]):seen.add(j);todo.append(j)
   assert len(seen)==len(boxes),(lod,tick,[(i,q[i*6][2]) for i in range(len(boxes)) if i not in seen])
   assert abs(min(np.concatenate([qq[0] for qq in q])[:,1]))<1e-6,'feet lifted'
   if not lod:
    labels=[p['label'] for b in design()[0] for p in design()[1] if p['bone']==b['name']]
    shaft=boxes[labels.index('axe_haft')]
    for grip in ('right_palm','right_fingers','right_thumb','right_knuckles'):assert touches(boxes[labels.index(grip)],shaft),(tick,grip)
   contacts=set()
   for i in range(len(boxes)):
    for j in range(i+1,len(boxes)):
     if q[i*6][2]!=q[j*6][2] and touches(boxes[i],boxes[j]):contacts.add((i,j))
   if initial_contacts is None:initial_contacts=contacts
   else:new_contacts.update(contacts-initial_contacts)
   pts=np.concatenate([qq[0] for qq in q]);bounds.append([pts.min(0),pts.max(0)])
  assert np.allclose(np.concatenate([q[0] for q in pose(0,lod)]),np.concatenate([q[0] for q in pose(160,lod)]))
  validations.append({'lod':lod or 'full','cubes':len(boxes),'poses_checked':161,'new_cross_bone_contacts_vs_start':sorted(new_contacts),'disconnected_cubes':0,'seam_positions_match':True})

 lo=np.min([b[0] for b in bounds],axis=0);hi=np.max([b[1] for b in bounds],axis=0)
 hand=json.loads((D/'draft-uv.json').read_text());occ=np.zeros((SIDE,SIDE),bool)
 for r in hand['islands']:
  x,y,w,h=r['rect'];assert not occ[y:y+h,x:x+w].any();occ[y:y+h,x:x+w]=True
 dump(D/'validation.json',{'software_only':True,'lod_checks':validations,'uv_overlap':False,'islands':len(hand['islands']),'feet_y':0,'scale':1,'animated_bounds_units':[lo.tolist(),hi.tolist()],'animated_bounds_metres':[(lo/16).tolist(),(hi/16).tolist()],'grip_checked_all_161_poses':True,'native_validation':'pending; no Java launched'})
 print('VALIDATED',validations,flush=True)

def final_review():
 ready=json.loads((D/'texture/TEXTURE_READY.json').read_text());png=A/'textures/entity/scenic/stone_god.png'
 assert hashlib.sha256(png.read_bytes()).hexdigest()==ready['sha256']
 protected=[A/f'geo/scenic/stone_god{s}.geo.json' for s in ('','_medium','_far')]+[A/'animations/scenic/stone_god.animation.json',D/'UV_LOCK.json',D/'TEXTURE_HANDOFF.json',png]
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
 source=D/'blockbench/stone_god.bbmodel';doc=json.loads(source.read_text());doc['textures'][0].update(name='stone_god.png',source='data:image/png;base64,'+base64.b64encode(png.read_bytes()).decode());dump(source,doc)
 review(final=True)
 assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items())
 assert base64.b64decode(json.loads(source.read_text())['textures'][0]['source'].split(',',1)[1])==png.read_bytes()
 dump(D/'final-texture-check.json',{'production_sha256':ready['sha256'],'embedded_bytes_identical':True,'protected_files':before,'protected_bytes_unchanged':True,'software_only':True,'java_started':False})

if __name__=='__main__':
 if '--final-review' in sys.argv:final_review()
 else:
  build()
  if '--validate' in sys.argv:validate()
  if '--review' in sys.argv:review()
