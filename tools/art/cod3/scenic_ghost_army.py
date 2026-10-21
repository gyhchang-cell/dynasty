#!/usr/bin/env python3
"""Original scenic #4 soldier art only. Never writes production PNG, Java or task list."""
from pathlib import Path
import json,math,uuid,hashlib,base64,sys,itertools
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/cod3-ghost-army-v2';NAME='ghost_army_soldier';SIDE=256
MATS={'clay_face':(171,158,136),'fired_clay':(128,119,101),'lamellar':(102,113,109),'undercloth':(63,72,74),'binding':(107,85,66),'old_bronze':(114,126,112),'haft':(97,87,70),'blade':(163,179,173),'recess':(54,63,62)}
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def design():
 bones=[];by={};parts=[]
 def bone(n,parent,p):
  b={'name':n,'pivot':list(p),'cubes':[]}
  if parent:b['parent']=parent
  bones.append(b);by[n]=b
 def box(b,o,s,m,label,lod=2,rotation=None,pivot=None):
  c={'origin':list(o),'size':list(s)}
  if rotation:c.update(rotation=rotation,pivot=list(pivot))
  by[b]['cubes'].append(c);parts.append({'bone':b,'cube':c,'material':m,'label':label,'lod':lod})
 def segment(b,start,end,w,dep,m,label,lod=2):
  start=np.array(start,float);dv=np.array(end)-start;length=np.linalg.norm(dv)
  # Local +Y segment; Bedrock cube rotations match the preview/native convention.
  rot=[-math.degrees(math.asin(dv[2]/length)),0,math.degrees(math.atan2(dv[0],dv[1]))]
  box(b,[start[0]-w/2,start[1]-.35,start[2]-dep/2],[w,length+.7,dep],m,label,lod,rot,start)
 bone('root',None,(0,0,0));bone('pelvis','root',(0,18,0))
 box('pelvis',(-4.7,16.8,-3),(9.4,4.2,6),'undercloth','hip_undercoat')
 box('pelvis',(-5.2,20,-3.5),(10.4,1.6,7),'binding','girdle',1)
 box('pelvis',(-1,20.1,3.4),(2,1.5,.65),'old_bronze','belt_fastening',0)
 bone('waist','pelvis',(0,21,0));box('waist',(-4.5,20.8,-2.8),(9,4.8,5.6),'undercloth','waist_core')
 bone('chest','waist',(0,25,0))
 box('chest',(-6,24.2,-3.5),(12,8.6,7),'lamellar','cuirass_body')
 box('chest',(-6.25,25.2,3.1),(12.5,6.8,1.4),'lamellar','front_lamellar_course',1)
 box('chest',(-5.8,25.5,-4.1),(11.6,6.4,1.1),'lamellar','back_lamellar_course',1)
 box('chest',(-2.5,32,-2.6),(5,1.4,5.2),'binding','collar_base',1)
 bone('neck','chest',(0,32.6,0));box('neck',(-2.1,32.4,-2),(4.2,3.9,4),'fired_clay','neck_column')
 bone('head','neck',(0,35,0))
 box('head',(-3.7,35,-3.2),(7.4,6.4,6.4),'fired_clay','head_mass')
 box('head',(-3.2,35.4,2.9),(6.4,4.9,.85),'clay_face','terracotta_face',1)
 box('head',(-2.8,35.1,2.7),(5.6,1.2,1.15),'clay_face','chin_plane',0)
 box('head',(-.5,36.9,3.7),(1,1.8,.65),'clay_face','nose_plane',0)
 box('head',(-3.8,39.7,2.6),(7.6,.9,1.4),'lamellar','helmet_brow',1)
 box('head',(-4.1,40,-3.6),(8.2,1.8,7.2),'lamellar','helmet_dome')
 box('head',(-1.2,41.4,-2.2),(2.4,1.1,4.4),'old_bronze','helmet_low_ridge',1)
 box('head',(-3.9,33.8,-3.85),(7.8,5.2,1.3),'lamellar','nape_guard',1)
 for s in (-1,1):
  box('head',(s*3.45-.65,35,-1.8),(1.3,5.1,4.8),'lamellar',f'cheek_guard_{s}',1)
  box('chest',(s*6.6-2,30.7,-3.5),(4,2.4,7.6),'lamellar',f'shoulder_shell_{s}',1)
 for s,n in [(-1,'right'),(1,'left')]:
  hip=(s*3.0,18,0);knee=(s*3,10,0);ankle=(s*3,2,0)
  bone(n+'_thigh','pelvis',hip)
  box(n+'_thigh',(s*3-1.9,9.7,-2.2),(3.8,8.6,4.4),'undercloth',n+'_upper_leg')
  box(n+'_thigh',(s*3-2.15,14.2,1.8),(4.3,5.8,1.1),'lamellar',n+'_thigh_apron',1)
  bone(n+'_shin',n+'_thigh',knee)
  box(n+'_shin',(s*3-1.65,1.75,-1.85),(3.3,8.5,3.7),'fired_clay',n+'_shin_core')
  box(n+'_shin',(s*3-1.85,3.2,1.4),(3.7,6.6,1.1),'lamellar',n+'_greave',1)
  box(n+'_shin',(s*3-1.9,8.9,-1.9),(3.8,1.1,4),'binding',n+'_knee_binding',0)
  bone(n+'_foot',n+'_shin',ankle)
  box(n+'_foot',(s*3-2.15,0,-2.4),(4.3,2.7,6.4),'fired_clay',n+'_foot')
  box(n+'_foot',(s*3-1.8,2,-1.6),(3.6,1.2,3.8),'binding',n+'_ankle_wrap',0)
  shoulder=(s*7.3,31.6,0)
  elbow=(s*9.7,25.9,1.3 if s<0 else .2)
  wrist=(s*10.5,22,5 if s<0 else 1.2)
  bone(n+'_upper_arm','chest',shoulder);segment(n+'_upper_arm',shoulder,elbow,3.8,4.4,'undercloth',n+'_upper_arm_core')
  box(n+'_upper_arm',(s*8.4-2.1,27.7,-1.5),(4.2,3.2,4.8),'lamellar',n+'_armour_sleeve',1)
  bone(n+'_forearm',n+'_upper_arm',elbow);segment(n+'_forearm',elbow,wrist,3.25,3.6,'fired_clay',n+'_forearm_core')
  segment(n+'_forearm',(elbow[0],elbow[1]-.2,elbow[2]+1.6),(wrist[0],wrist[1]+.8,wrist[2]+1.6),3.45,1.0,'lamellar',n+'_vambrace',1)
  bone(n+'_hand',n+'_forearm',wrist)
  x,y,z=wrist
  if s<0:
   # Four connected grip groups enclose a 1.1-unit square aperture.
   for lab,o,size in [('palm',(x-1.65,y-1.5,z-1.8),(3.3,3,1.25)),('fingers',(x-1.65,y-1.5,z+.55),(3.3,3,1.25)),('thumb',(x-1.65,y-1.5,z-.55),(1.1,3,1.1)),('knuckles',(x+.55,y-1.5,z-.55),(1.1,3,1.1))]:box(n+'_hand',o,size,'clay_face',n+'_'+lab)
   bone('spear',n+'_hand',wrist)
   box('spear',(x-.55,2,z-.55),(1.1,41,1.1),'haft','spear_shaft')
   box('spear',(x-.85,41.6,z-.85),(1.7,2.2,1.7),'old_bronze','spear_socket',1)
   box('spear',(x-1.6,43,z-.45),(3.2,3.8,.9),'blade','spear_blade_base')
   box('spear',(x-.85,46.6,z-.35),(1.7,2,.7),'blade','spear_blade_tip')
   box('spear',(x-.85,2,z-.85),(1.7,2,1.7),'old_bronze','spear_butt',0)
   for yy in (20.1,23.5):box('spear',(x-.7,yy,z-.7),(1.4,.55,1.4),'binding','grip_stop_'+str(yy),0)
  else:
   box(n+'_hand',(x-1.7,y-2.1,z-1.5),(3.4,3.6,3.4),'clay_face','left_hand_palm')
   box(n+'_hand',(x-2.05,y-.6,z+.6),(1,1.8,1.7),'clay_face','left_thumb',0)
 return bones,parts

def animation():
 tracks={};period=4.0
 def channel(b,ch,t,v):tracks.setdefault(b,{}).setdefault(ch,{})[f'{t:.4f}'.rstrip('0').rstrip('.') if t else '0']=[round(float(x),6) for x in v]
 for i in range(161):
  t=i*period/160;p=t/period
  bob=-.6-.12*abs(math.sin(2*math.pi*p));channel('pelvis','position',t,[0,bob,0])
  # Stable torso; the right shoulder carries the pole, the left counter-swings.
  channel('chest','rotation',t,[1.5,.65*math.sin(2*math.pi*p),0])
  channel('head','rotation',t,[-1,1*math.sin(2*math.pi*p+.3),0])
  channel('left_upper_arm','rotation',t,[-5*math.cos(2*math.pi*p),0,0])
  channel('left_forearm','rotation',t,[2*math.sin(2*math.pi*p),0,0])
  for n,offset in [('right',0),('left',.5)]:
   q=(p+offset)%1
   if q<.6:z=3.84-7.68*q/.6;lift=0
   else:
    u=(q-.6)/.4;z=-3.84+7.68*(u*u*(3-2*u));lift=1.05*math.sin(math.pi*u)**2
   vertical=18+bob-(2+lift);dist=math.hypot(vertical,z)
   a=math.atan2(z,vertical);bend=math.acos(min(1,dist/16))
   upper=math.degrees(a+bend);lower=-math.degrees(2*bend);foot=-(upper+lower)
   channel(n+'_thigh','rotation',t,[upper,0,0]);channel(n+'_shin','rotation',t,[lower,0,0]);channel(n+'_foot','rotation',t,[foot,0,0])
 for chs in tracks.values():
  for tr in chs.values():tr['4']=tr['0']
 return {'format_version':'1.8.0','animations':{'animation.scenic.idle':{'loop':True,'animation_length':period,'bones':tracks}}}

def build():
 assert len(json.loads((D/'references/selected-100.json').read_text()))==100
 bones,parts=design();islands=[]
 for p in parts:
  w,h,d=p['cube']['size']
  for f,a,b in [('north',w,h),('south',w,h),('west',d,h),('east',d,h),('up',w,d),('down',w,d)]:islands.append({'part':p['label'],'bone':p['bone'],'material':p['material'],'face':f,'rect':[0,0,max(1,round(a)),max(1,round(b))],'cube_origin':p['cube']['origin'],'cube_size':p['cube']['size'],'cube_rotation':p['cube'].get('rotation',[0,0,0]),'cube_pivot':p['cube'].get('pivot'),'direction':'U follows face-local horizontal; V top-to-bottom on walls, X/Z on caps; see cube_rotation/pivot.'})
 lock=D/'UV_LOCK.json'
 if lock.exists():
  old=json.loads(lock.read_text())['islands'];assert [{k:v for k,v in r.items() if k!='rect'} for r in islands]==[{k:v for k,v in r.items() if k!='rect'} for r in old],'Frozen geometry/UV mismatch';islands=old
 else:
  x=y=2;row=0
  for r in sorted(islands,key=lambda r:-r['rect'][3]):
   _,_,w,h=r['rect']
   if x+w+2>SIDE:x=2;y+=row+2;row=0
   assert y+h+2<SIDE
   r['rect']=[x,y,w,h];x+=w+2;row=max(row,h)
 lookup={p['label']:p for p in parts}
 for p in parts:p['cube']['uv']={}
 tex=Image.new('RGB',(SIDE,SIDE),(30,35,36));draw=ImageDraw.Draw(tex)
 checker=Image.new('RGB',(SIDE,SIDE),(30,35,36));cd=ImageDraw.Draw(checker)
 for i,r in enumerate(islands):
  x,y,w,h=r['rect'];lookup[r['part']]['cube']['uv'][r['face']]={'uv':[x,y],'uv_size':[w,h]}
  draw.rectangle((x,y,x+w-1,y+h-1),fill=MATS[r['material']])
  for yy in range(h):
   for xx in range(w):checker.putpixel((x+xx,y+yy),[(200,72,68),(93,166,86),(66,123,190),(191,162,70)][(yy>=h/2)*2+(xx>=w/2)])
  if w>=5 and h>=6:cd.text((x,y),str(i%100),fill='white')
 tex.save(D/'temporary-material-atlas.png');checker.save(D/'uv-direction-check.png')
 overlay=checker.resize((SIDE*3,SIDE*3),Image.Resampling.NEAREST);od=ImageDraw.Draw(overlay)
 for r in islands:
  x,y,w,h=r['rect'];od.rectangle((x*3,y*3,(x+w)*3-1,(y+h)*3-1),outline=(240,240,240))
 overlay.save(D/'uv-overlay-3x.png')
 dump(D/'draft-uv.json',{'atlas_size':[SIDE,SIDE],'islands':islands,'pixels_per_metre':16,'production_png_owner':'texture author; temporary-material-atlas.png is not final'})
 desc={'identifier':'geometry.dynasty.ghost_army_soldier','texture_width':SIDE,'texture_height':SIDE,'visible_bounds_width':3.5,'visible_bounds_height':3.8,'visible_bounds_offset':[0,1.6,0]}
 counts={}
 for suffix,level in [('',0),('_medium',1),('_far',2)]:
  out=[dict(b,cubes=[p['cube'] for p in parts if p['bone']==b['name'] and p['lod']>=level]) for b in bones]
  counts[suffix or 'full']=sum(len(b['cubes']) for b in out)
  dump(A/f'geo/scenic/{NAME}{suffix}.geo.json',{'format_version':'1.12.0','minecraft:geometry':[{'description':dict(desc,identifier=desc['identifier']+suffix),'bones':out}]})
 anim=animation();dump(A/f'animations/scenic/{NAME}.animation.json',anim);dump(D/f'blockbench/{NAME}.animation.json',anim)
 def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty/ghost-army-v2/'+s))
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
 target=D/f'blockbench/{NAME}.bbmodel'
 # A later texture handoff may embed final PNG; generation preserves that owned texture.
 old_textures=json.loads(target.read_text())['textures'] if target.exists() else []
 textures=old_textures if old_textures and (lock.exists() or old_textures[0].get('name')!='temporary-material-atlas.png') else [{'name':'temporary-material-atlas.png','uuid':uid('texture'),'source':'data:image/png;base64,'+base64.b64encode((D/'temporary-material-atlas.png').read_bytes()).decode()}]
 dump(target,{'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},'name':NAME,'model_identifier':NAME,'geckolib_modid':'dynasty','resolution':{'width':SIDE,'height':SIDE},'elements':elements,'outliner':out,'textures':textures})
 dump(D/'design.json',{'bones':[{k:v for k,v in b.items() if k!='cubes'} for b in bones],'parts':[{k:v for k,v in p.items() if k!='cube'} for p in parts],'lod_cubes':counts})
 print('Exported',counts,'bones',len(bones),flush=True)

if __name__=='__main__':build()
