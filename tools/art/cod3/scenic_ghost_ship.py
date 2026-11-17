#!/usr/bin/env python3
"""Original ghost ship geometry authoring. Never writes production PNGs or Java."""
from pathlib import Path
import json,math,uuid,base64,hashlib,sys,itertools
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
A=ROOT/'src/main/resources/assets/dynasty';D=ROOT/'docs/art/cod3-ghost-ship-v2'
SIDE=512
MATS={'wet_hull':(53,66,64),'deck':(119,98,70),'timber':(82,71,56),'iron':(44,51,56),'bamboo':(126,117,83),'sail':(151,170,158),'canopy':(67,97,93),'seal':(143,136,96)}
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def build():
 bones=[];by={};parts=[]
 def bone(n,parent,p=(0,0,0)):
  b={'name':n,'pivot':list(p),'cubes':[]}
  if parent:b['parent']=parent
  bones.append(b);by[n]=b
 def box(n,o,s,mat,label,lod=2):
  c={'origin':list(o),'size':list(s)};by[n]['cubes'].append(c);parts.append({'cube':c,'bone':n,'material':mat,'label':label,'lod':lod})
 bone('root',None);bone('hull','root')
 # 24m hull, stepped stern/bow transitions, real hollow space above deck.
 stations=[(-176,-136,70,0),(-136,-80,88,0),(-80,0,96,0),(0,80,96,0),(80,128,80,2),(128,160,56,6),(160,192,28,12)]
 for j,(z0,z1,w,rise) in enumerate(stations):
  length=z1-z0
  box('hull',(-w/2+12,-18+rise,z0),(w-24,8,length),'wet_hull',f'keel_course_{j}')
  box('hull',(-w/2+6,-10+rise,z0),(w-12,8,length),'wet_hull',f'belly_{j}')
  box('hull',(-w/2,-2+rise,z0),(w,8,length),'deck',f'deck_{j}')
  for side in (-1,1):
   x=-w/2 if side<0 else w/2-5
   box('hull',(x,6+rise,z0),(5,12,length),'timber',f'gunwale_{j}_{side}')
   box('hull',(x-1,17+rise,z0),(7,3,length),'timber',f'cap_{j}_{side}',1)
   # Vertical joints overlap side and lower hull: not unrelated floating patches.
   if j<6:
    box('hull',(x-.25,-2+rise,z0+length*.45),(5.5,20,3),'iron',f'frame_band_{j}_{side}',0)
 # Closure between width steps, all hull parts remain connected even in far LOD.
 box('hull',(-35,6,-176),(70,16,5),'timber','stern_transom')
 box('hull',(-14,18,187),(28,12,5),'timber','bow_transom')
 box('hull',(-6,21,181),(12,17,10),'timber','raised_stem')
 box('hull',(-9,35,177),(18,4,15),'iron','stem_binding',1)
 # Slightly raised aft deck and open canopy on four real posts.
 bone('stern_canopy','hull',(0,6,-140))
 box('stern_canopy',(-30,6,-172),(60,5,48),'deck','aft_platform')
 for x in (-27,23):
  for z in (-167,-129):box('stern_canopy',(x,10,z),(4,30,4),'timber',f'canopy_post_{x}_{z}')
 box('stern_canopy',(-31,38,-171),(62,4,50),'timber','canopy_frame')
 box('stern_canopy',(-35,41,-175),(70,3,58),'canopy','low_eaves')
 box('stern_canopy',(-26,44,-175),(52,3,58),'canopy','roof_step')
 box('stern_canopy',(-10,47,-175),(20,3,58),'canopy','roof_crown')
 for x in (-36,31):box('stern_canopy',(x,43,-175),(5,3,58),'canopy',f'eave_tip_{x}',1)
 # Rudder axle joins transom at pivot; held in restrained static travel pose.
 bone('rudder','hull',(0,7,-175))
 box('rudder',(-3,-20,-181),(6,34,8),'timber','rudder_axle')
 box('rudder',(-3,-21,-188),(6,22,10),'wet_hull','rudder_blade')
 box('rudder',(-3,10,-179),(6,3,23),'timber','tiller',1)
 for name,z,top,width,bottom in [('main',-38,158,96,54),('fore',88,126,72,50)]:
  bone(name+'_mast','hull',(0,6,z))
  box(name+'_mast',(-5,5,z-5),(10,top-5,10),'timber',name+'_mast_column')
  box(name+'_mast',(-12,5,z-12),(24,7,24),'iron',name+'_mast_socket',1)
  # Sail is attached at its centerline, pivots about mast, not at a detached corner.
  bone(name+'_sail',name+'_mast',(0,bottom,z))
  by[name+'_sail']['rotation']=[0,-18 if name=='main' else -12,0]
  h=(top-8-bottom)/5
  widths=[width*.76,width*.92,width,width*.93,width*.76]
  for k,w in enumerate(widths):
   y=bottom+k*h;left=-width*.24+k*2
   box(name+'_sail',(left,y,z-1.5),(w,h,3),'sail',name+f'_cloth_{k}')
   box(name+'_sail',(left-2,y,z-3),(w+4,2.5,6),'bamboo',name+f'_batten_{k}',1 if k%2==0 else 0)
  w=widths[-1];left=-width*.24+8
  box(name+'_sail',(left-2,top-8,z-3),(w+4,3,6),'bamboo',name+'_top_yard')
  # Two joined trailing tabs break the lower outline, not all-over shredded noise.
  for k in (0,1):
   box(name+'_sail',(width*.35-k*10,bottom-8-k*2,z-1.5),(6,8+k*2,3),'sail',name+f'_cloth_tab_{k}',0)
  for y in (20,top-12):box(name+'_mast',(-5.5,y,z-5.5),(11,3,11),'iron',name+f'_binding_{y}',0)
 # Restrained deck furnishings: only at perimeter, no blocked walkway.
 for z in (-100,110):
  for x in (-30,24):
   box('hull',(x,6,z),(6,9,6),'timber',f'mooring_{x}_{z}',0)
   box('hull',(x-2,14,z-1),(10,3,8),'iron',f'mooring_cap_{x}_{z}',0)
 for z in (-92,34):
  box('hull',(-12,6,z),(24,3,18),'timber',f'hatch_frame_{z}',1)
  box('hull',(-10,9,z+2),(20,1,14),'iron',f'hatch_lid_{z}',0)
 # UV layout is immutable while the texture author paints the handed-off atlas.
 lock=json.loads((D/'UV_LOCK.json').read_text());islands=lock['islands']
 expected={(r['part'],r['face']) for r in islands}
 actual={(p['label'],f) for p in parts for f in ('north','south','west','east','up','down')}
 mismatches=[]
 if lock['atlas_size']!=[SIDE,SIDE] or actual!=expected:mismatches.append('atlas size or face membership changed')
 lookup={p['label']:p for p in parts}
 for r in islands:
  p=lookup.get(r['part'])
  if p is None or p['material']!=r['material']:mismatches.append(r['part']+' material/membership changed')
 if mismatches:
  dump(D/'UV_CHANGE_REQUIRED.json',{'status':'PAUSED_AWAITING_TEXTURE_COORDINATION','issues':sorted(set(mismatches))})
  raise RuntimeError('Frozen UV change requires coordination; no model resources exported.')
 for p in parts:p['cube']['uv']={}
 for r in islands:
  x,y,w,h=r['rect'];lookup[r['part']]['cube']['uv'][r['face']]={'uv':[x,y],'uv_size':[w,h]}
 # No PNG generation and no TEXTURE_HANDOFF rewrite after freeze.
 description={'identifier':'geometry.dynasty.ghost_ship','texture_width':SIDE,'texture_height':SIDE,'visible_bounds_width':28,'visible_bounds_height':15,'visible_bounds_offset':[0,4,0]}
 counts={}
 for suffix,level in [('',0),('_medium',1),('_far',2)]:
  out=[]
  for b in bones:
   out.append(dict(b,cubes=[p['cube'] for p in parts if p['bone']==b['name'] and p['lod']>=level]))
  counts[suffix or 'full']=sum(len(b['cubes']) for b in out)
  dump(A/f'geo/scenic/ghost_ship{suffix}.geo.json',{'format_version':'1.12.0','minecraft:geometry':[{'description':description,'bones':out}]})
 def keys(values):return {str(i*2):v for i,v in enumerate(values)}
 tracks={'root':{'position':keys([[0,0,0],[0,1.3,0],[0,0,0],[0,-1.3,0],[0,0,0]]),'rotation':keys([[0,0,0],[-.2,0,.45],[0,0,0],[.2,0,-.45],[0,0,0]])},'main_sail':{'rotation':keys([[0,-1.4,0],[0,0,0],[0,1.4,0],[0,0,0],[0,-1.4,0]])},'fore_sail':{'rotation':keys([[0,0,0],[0,1.8,0],[0,0,0],[0,-1.8,0],[0,0,0]])}}
 anim={'format_version':'1.8.0','animations':{'animation.scenic.idle':{'loop':True,'animation_length':8,'bones':tracks}}}
 dump(A/'animations/scenic/ghost_ship.animation.json',anim);dump(D/'blockbench/ghost_ship.animation.json',anim)

 def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty/ghost-ship-v2/'+s))
 groups={};elements=[]
 for b in bones:
  g={'name':b['name'],'uuid':uid(b['name']),'origin':[-b['pivot'][0],*b['pivot'][1:]],'rotation':[-b.get('rotation',[0,0,0])[0],-b.get('rotation',[0,0,0])[1],b.get('rotation',[0,0,0])[2]],'children':[]};groups[b['name']]=g
  for c in b['cubes']:
   p=next(p for p in parts if p['cube'] is c);ident=uid(p['label']);xx,yy,zz=c['origin'];w,h,dep=c['size'];faces={}
   for f,t in c['uv'].items():
    u,v=t['uv'];du,dv=t['uv_size'];faces[f]={'texture':0,'uv':[u+du,v+dv,u,v] if f in ('up','down') else [u,v,u+du,v+dv]}
   elements.append({'name':p['label'],'uuid':ident,'type':'cube','from':[-xx-w,yy,zz],'to':[-xx,yy+h,zz+dep],'origin':g['origin'],'box_uv':False,'faces':faces});g['children'].append(ident)
 out=[]
 for b in bones:
  if b.get('parent'):groups[b['parent']]['children'].append(groups[b['name']])
  else:out.append(groups[b['name']])
 existing_textures=json.loads((D/'blockbench/ghost_ship.bbmodel').read_text())['textures']
 dump(D/'blockbench/ghost_ship.bbmodel',{'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},'name':'ghost_ship','model_identifier':'ghost_ship','geckolib_modid':'dynasty','resolution':{'width':SIDE,'height':SIDE},'elements':elements,'outliner':out,'textures':existing_textures})
 print('Export with frozen UV',counts,'bones',len(bones))
 return counts



def review(final=False):
 sys.path.insert(0,str(ROOT/'tools/art/boss-forms'))
 import texture_review as v
 v.r.CATEGORY='scenic'
 texture_path=A/'textures/entity/scenic/ghost_ship.png' if final else D/'temporary-material-atlas.png'
 if final:
  ready=json.loads((D/'texture/TEXTURE_READY.json').read_text())
  assert hashlib.sha256(texture_path.read_bytes()).hexdigest()==ready['sha256']=='b597834571b2acb2fee0a4880868bd733ef4a8ba00344cd5168ecee4466dd10c'
 tex=np.array(Image.open(texture_path).convert('RGB'))
 def pose(t=0,lod=''):
  return v.r.geometry('ghost_ship',clip='animation.scenic.idle',tick=t,geo_path=A/f'geo/scenic/ghost_ship{lod}.geo.json')
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
  g=json.loads((A/f'geo/scenic/ghost_ship{lod}.geo.json').read_text())['minecraft:geometry'][0];bs=g['bones'];names={b['name'] for b in bs};assert len(names)==len(bs)
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
   contacts=set()
   for i in range(len(boxes)):
    for j in range(i+1,len(boxes)):
     if q[i*6][2]!=q[j*6][2] and touches(boxes[i],boxes[j]):contacts.add((i,j))
   if initial_contacts is None:initial_contacts=contacts
   else:new_contacts.update(contacts-initial_contacts)
   pts=np.concatenate([qq[0] for qq in q]);bounds.append([pts.min(0),pts.max(0)])
  assert np.allclose(np.concatenate([q[0] for q in pose(0,lod)]),np.concatenate([q[0] for q in pose(160,lod)]))
  validations.append({'lod':lod or 'full','cubes':len(boxes),'poses_checked':161,'new_cross_bone_contacts_vs_start':sorted(new_contacts),'disconnected_cubes':0,'seam_positions_match':True})
 print('Connected',validations,flush=True)
 lo=np.min([b[0] for b in bounds],axis=0);hi=np.max([b[1] for b in bounds],axis=0);frame=np.array(list(itertools.product(*zip(lo,hi))))
 q=pose();foot='软件预览 · 真实生产PNG逐面采样 · 非实机截图 · 无粒子' if final else '软件灰模/临时分区色 · 非最终贴图 · 非实机截图 · 无粒子'
 def save(im,title,fn):v.labelled(im,title,foot).save(D/fn)
 for yaw,label in [(180,'front'),(135,'45'),(90,'right'),(-90,'left'),(0,'back')]:
  save(v.raster(q,tex,yaw=yaw,elevation=15,size=(1000,680),mode='lit',frame_points=frame),'幽冥古舰 / '+label,label+'.png')
 gray=np.repeat((tex@np.array([.2126,.7152,.0722]))[...,None],3,axis=-1).astype(np.uint8) if final else np.full_like(tex,153);black=np.zeros_like(tex)
 for t,n in [(gray,'gray'),(black,'silhouette')]:save(v.raster(q,t,yaw=135,elevation=15,size=(1000,680),mode='lit',frame_points=frame),'幽冥古舰 / '+n,n+'.png')
 for mast in ('main','fore'):
  cloth=[qq for qq in q if qq[2]==mast+'_sail']
  for yaw,face in [(180,'front'),(0,'back')]:save(v.raster(cloth,tex,yaw=yaw,elevation=0,size=(900,700),mode='unlit'),mast+' sail / '+face,mast+'-sail-'+face+'.png')
 for lod in ('_medium','_far'):save(v.raster(pose(0,lod),tex,yaw=135,elevation=15,size=(1000,680),mode='lit',frame_points=frame),'幽冥古舰 / '+lod,lod[1:]+'.png')
 refs=v.references(np.array([-125,0,140]));refs=[(p+np.array([-40,0,-48]) if i<12 else p,uv,bn) for i,(p,uv,bn) in enumerate(refs)];save(v.raster(q+refs,tex,yaw=135,elevation=15,size=(1200,760),mode='lit'),'24米古舰 / 1.8米玩家与1米方块 · 同比例','world-scale.png')
 frames=[]
 for tick in range(0,160,5):
  im=v.raster(pose(tick),tex,yaw=135,elevation=15,size=(720,480),mode='lit',frame_points=frame);frames.append(v.labelled(im,f'幽冥古舰 · {tick}/160 tick',foot))
 frames[0].save(D/'idle.webp',save_all=True,append_images=frames[1:],duration=250,loop=0,lossless=True)
 cycle=Image.new('RGB',(1440,1120))
 for i,k in enumerate([0,8,16,24]):cycle.paste(frames[k],(i%2*720,i//2*560))
 cycle.save(D/'cycle-check.png')
 # Asymmetric direction checker is docs-only and never copied to runtime.
 checker=Image.new('RGB',(SIDE,SIDE),'#20252a');dr=ImageDraw.Draw(checker)
 for n,r in enumerate(json.loads((D/'TEXTURE_HANDOFF.json').read_text())['islands']):
  x,y,w,h=r['rect'];dr.rectangle((x,y,x+w-1,y+h-1),fill=(155,83,73));dr.rectangle((x+w//2,y,x+w-1,y+h-1),fill=(77,138,105));dr.line((x,y+h-1,x+w-1,y+h-1),fill=(90,145,204))
  if w>12 and h>8:dr.text((x+1,y+1),str(n),fill='white')
 checker.save(D/'uv-direction-check.png');save(v.raster(q,np.array(checker),yaw=135,elevation=15,size=(1000,680),frame_points=frame),'UV方向：红左/绿右/蓝底，仅检查','uv-direction.png')
 hand=json.loads((D/'TEXTURE_HANDOFF.json').read_text());occ=np.zeros((SIDE,SIDE),dtype=bool)
 for island in hand['islands']:
  x,y,w,h=island['rect'];assert not occ[y:y+h,x:x+w].any();occ[y:y+h,x:x+w]=True
 dump(D/'validation.json',{'software_only':True,'lod_checks':validations,'uv_islands':len(hand['islands']),'uv_overlap':False,'nominal_waterline_y':0,'world_scale':1,'animated_bounds_metres':[list(lo/16),list(hi/16)],'animation_period_seconds':8,'production_png_written':False,'java_started':False,'final_texture_used':final,'texture_sha256':hashlib.sha256(texture_path.read_bytes()).hexdigest()})
 names=['front','45','right','back','gray','silhouette']
 out=Image.new('RGB',(1500,760))
 for i,n in enumerate(names):
  im=Image.open(D/(n+'.png'));im.thumbnail((500,380));out.paste(im,(i%3*500,i//3*380))
 out.save(D/'overview.png')
 html='<meta charset="utf-8"><title>幽冥古舰 · 模型交接</title><style>body{background:#20272b;color:#eee;font:18px sans-serif;max-width:1400px;margin:35px auto}img{max-width:100%}section{margin:30px 0}a{color:#a5d9d0}</style><h1>忘川漂流 · 幽冥古舰</h1><p>原创模型 / 24米 / 125、91、63 Cuboids / 双桅专用骨架。以下为生产PNG逐面采样的软件检查，不是游戏截图。</p><a href="references/index.html">100张已查看参考与来源</a>'
 for n in ['world-scale','front','45','right','left','back','gray','silhouette','medium','far','main-sail-front','main-sail-back','fore-sail-front','fore-sail-back','uv-direction']:html+=f'<section><h2>{n}</h2><img src="{n}.png"></section>'
 html+='<h2>完整8秒循环</h2><img src="idle.webp"><p>最终贴图已同步嵌图；原生游戏验收由主对话完成，不修改60秒奇观生命周期。</p>'
 (D/'index.html').write_text(html)
 print('Review complete',flush=True)

def sync_final_texture():
 path=A/'textures/entity/scenic/ghost_ship.png'
 ready=json.loads((D/'texture/TEXTURE_READY.json').read_text())
 assert hashlib.sha256(path.read_bytes()).hexdigest()==ready['sha256']=='b597834571b2acb2fee0a4880868bd733ef4a8ba00344cd5168ecee4466dd10c'
 target=D/'blockbench/ghost_ship.bbmodel';source=json.loads(target.read_text())
 assert Image.open(path).size==(512,512)
 source['textures'][0].update(name='ghost_ship.png',source='data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode())
 dump(target,source)

if __name__=='__main__':
 if '--final-review' in sys.argv:
  protected=[A/f'geo/scenic/ghost_ship{s}.geo.json' for s in ('','_medium','_far')]+[A/'animations/scenic/ghost_ship.animation.json',A/'textures/entity/scenic/ghost_ship.png',D/'TEXTURE_HANDOFF.json',D/'UV_LOCK.json']
  before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
  sync_final_texture();review(final=True)
  assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
 else:
  build()
  if '--review' in sys.argv:review()
