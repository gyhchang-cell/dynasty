"""Nearest-pixel per-face UV review. Software images, NEVER native game evidence."""
import json,math,sys,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build import A,R,IDS,NAMES
from atlas import CORNERS
D=R/'docs/art/boss-textures-v3'
s=importlib.util.spec_from_file_location('texture_geometry',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);r.CATEGORY='boss_forms'
assert r.FACES=={k:[tuple(v) for v in vs] for k,vs in CORNERS.items()}
FONT='/System/Library/Fonts/STHeiti Medium.ttc'
def font(n):return ImageFont.truetype(FONT,n)
def labelled(im,title,foot='软件预览 · 实际 PNG 逐面采样 · 最近邻 · 无粒子/发光 · 非游戏截图'):
 out=Image.new('RGB',(im.width,im.height+80),(232,233,228));out.paste(im,(0,45));d=ImageDraw.Draw(out);d.text((18,10),title,fill=(37,42,43),font=font(20));d.text((18,out.height-27),foot,fill=(68,73,73),font=font(15));return out

def checker(id):
 path=D/id;im=Image.open(path/'texture.png');out=Image.new('RGB',im.size,(34,36,43));overlay=im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST);od=ImageDraw.Draw(overlay)
 for i,p in enumerate(json.loads((path/'islands.json').read_text())):
  x,y,w,h=p['rect'];tile=Image.new('RGB',(w,h));td=ImageDraw.Draw(tile)
  # Four deliberately asymmetric quadrants: red->green U, red->blue V.
  for yy in range(h):
   for xx in range(w):
    col=[(190,74,68),(100,167,89),(71,127,187),(191,163,76)][(yy>=h/2)*2+(xx>=w/2)]
    if ((xx//4)+(yy//4))%2:col=tuple(max(0,v-22) for v in col)
    tile.putpixel((xx,yy),col)
  if w>=9 and h>=9:
   td.text((1,1),str(i),font=ImageFont.load_default(size=8),fill='white',stroke_width=0)
   td.line((1,h-3,w-3,h-3),fill='white');td.line((w-5,h-5,w-3,h-3,w-5,h-1),fill='white')
  out.paste(tile,(x,y));od.rectangle((x*4,y*4,(x+w)*4-1,(y+h)*4-1),outline=(240,112,164),width=1)
  if w>=6 and h>=5:od.text((x*4+1,y*4+1),str(i),fill=(255,252,238),font=font(10))
 out.save(path/'uv-checker.png');overlay.save(path/'uv-overlay-4x.png')
 return np.array(out)

def cuboid(origin,size,tex):
 q=[]
 for f,corners in r.FACES.items():q.append((np.array(corners)*size+origin,{'uv':[0,0],'uv_size':[tex.shape[1],tex.shape[0]],'_tex':tex},'__reference'))
 return q

def references(offset):
 q=[]
 # Original swatches (not extracted external assets), 16px per block.
 stone=Image.new('RGB',(16,16),(127,130,123));d=ImageDraw.Draw(stone)
 for y in [0,8]:
  d.line((0,y,15,y),fill=(78,83,79))
  for x in [((y//8)*8)%16]:d.line((x,y,x,y+7),fill=(78,83,79));d.line((x+1,y+1,min(15,x+7),y+1),fill=(163,163,150))
 wood=Image.new('RGB',(16,16),(146,114,70));d=ImageDraw.Draw(wood)
 for y in [3,7,11,15]:d.line((0,y,15,y),fill=(91,69,45));d.line((3,y-1,10,y-1),fill=(170,136,86))
 for n,tex in enumerate([np.array(stone),np.array(wood)]):q+=cuboid(offset+np.array([n*18,0,18]),[16,16,16],tex)
 # 1.8m player, simple neutral skin/shirt/trousers; full cuboids retain scale.
 for o,size,col in [([-4,21.6,-4],[8,7.2,8],(174,139,112)),([-4,10.8,-2],[8,10.8,4],(49,122,134)),([-7,10.8,-2],[3,10.8,4],(49,122,134)),([4,10.8,-2],[3,10.8,4],(49,122,134)),([-4,0,-2],[4,10.8,4],(56,66,93)),([0,0,-2],[4,10.8,4],(56,66,93))]:q+=cuboid(np.array(o)+offset+[-12,0,0],size,np.full((2,2,3),col,dtype=np.uint8))
 return q

def raster(quads,texture,yaw=45,elevation=7,size=(1000,760),mode='unlit',distance=None):
 w,h=size;yaw,el=map(math.radians,(yaw,elevation));toward=np.array([math.sin(yaw)*math.cos(el),math.sin(el),-math.cos(yaw)*math.cos(el)]);right=np.array([math.cos(yaw),0,math.sin(yaw)]);up=np.cross(toward,right);up=-up if up[1]<0 else up
 basis=np.vstack([right,up,toward]);points=np.concatenate([q[0] for q in quads]);proj=points@basis.T;lo,hi=proj.min(0),proj.max(0);center=(lo+hi)/2
 if distance:
  # Eye level 1.62m, level horizon, vertical FOV 70 degrees; perspective-correct UV.
  toward=np.array([math.sin(yaw),0,-math.cos(yaw)]);up=np.array([0,1,0]);basis=np.vstack([right,up,toward]);target=np.array([0,25.92,0]);cam=target+toward*(distance*16);focal=h/(2*math.tan(math.radians(35)))
 else:scale=min((w-80)/(hi[0]-lo[0]),(h-60)/(hi[1]-lo[1]))
 rgb=np.empty((h,w,3),dtype=np.uint8);rgb[:]=(214,220,220) if mode!='unlit' else (232,233,228);depth=np.full((h,w),-np.inf);light=np.array([-.4,.82,-.4]);light/=np.linalg.norm(light)
 for vertices,uv,bn in quads:
  atlas=uv.get('_tex',texture);p=vertices@basis.T
  if distance:
   v=(vertices-cam)@basis.T;z=-v[:,2]
   if min(z)<1:continue
   p=np.column_stack([w/2+focal*v[:,0]/z,h/2-focal*v[:,1]/z,1/z])
  else:p=(p-center)*[scale,-scale,1]+[w/2,h/2,0]
  normal=np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]);n=np.linalg.norm(normal)
  if n<1e-9:continue
  # Two-sided cuboids, neutral fill only. No tint, bloom, AO, specular or emissive.
  shade=1 if mode=='unlit' else .65+.35*abs(float(normal/n@light))
  if mode=='dim':shade*=.58
  x,y=uv['uv'];du,dv=uv['uv_size'];tc=np.array([[x,y],[x+du,y],[x+du,y+dv],[x,y+dv]],dtype=float)
  for ii in [(0,1,2),(0,2,3)]:
   tri=p[list(ii)];tex=tc[list(ii)];x0=max(0,math.floor(tri[:,0].min()));x1=min(w-1,math.ceil(tri[:,0].max()));y0=max(0,math.floor(tri[:,1].min()));y1=min(h-1,math.ceil(tri[:,1].max()))
   if x1<x0 or y1<y0:continue
   xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-9:continue
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;ww=1-u-v;zz=u*a[2]+v*b[2]+ww*c[2];old=depth[y0:y1+1,x0:x1+1];mask=(u>=-1e-6)&(v>=-1e-6)&(ww>=-1e-6)&(zz>old)
   if not mask.any():continue
   if distance:
    safe=np.maximum(zz,1e-12);u=u*a[2]/safe;v=v*b[2]/safe;ww=ww*c[2]/safe
   # Clamp within the island: edge samples must not bleed onto adjacent atlas cells.
   tx=np.clip((u*tex[0,0]+v*tex[1,0]+ww*tex[2,0]).astype(int),int(x),int(x+du-1));ty=np.clip((u*tex[0,1]+v*tex[1,1]+ww*tex[2,1]).astype(int),int(y),int(y+dv-1));col=atlas[ty,tx]*shade
   if mode=='gray':col=np.repeat((col@np.array([.2126,.7152,.0722]))[...,None],3,axis=-1)
   rgb[y0:y1+1,x0:x1+1][mask]=np.clip(col,0,255).astype(np.uint8)[mask];old[mask]=zz[mask]
 return Image.fromarray(rgb)

SIGNATURE=[('cast',14),('cast',20),('attack',12),('roar',20),('net',24),('sweep',20),('mirror',20),('slam',28)]
def run(ids,quick=False):
 for id in ids:
  path=D/id;index=IDS.index(id);tex=np.array(Image.open(A/'textures/entity/boss_forms'/(id+'.png')).convert('RGB'));q=r.geometry(id);check=checker(id)
  for view,angle in [('front',0),('side',90),('back',180),('three-quarter',45)]:
   for mode in ['unlit','lit']:
    im=raster(q,tex,yaw=angle,mode=mode);labelled(im,NAMES[index]+' / '+view+' / '+('贴图原色' if mode=='unlit' else '中性漫反射软件光照')).save(path/(view+'-'+mode+'.png'))
  for angle,name in [(45,'uv-direction'),(90,'uv-direction-side')]:labelled(raster(q,check,yaw=angle),NAMES[index]+' / 编号+方向 UV 检查（仅预览）').save(path/(name+'.png'))
  # Same camera + same geometry before/after; prior UV and PNG rendered without old mirror bug.
  bq=r.geometry(id,geo_path=D/'before'/(id+'.geo.json'));bt=np.array(Image.open(D/'before'/(id+'.png')));ims=[raster(bq,bt,size=(900,680)),raster(q,tex,size=(900,680))];out=Image.new('RGB',(1800,760));out.paste(labelled(ims[0],'BEFORE / 原纹理 · 已修正预览镜像'),(0,0));out.paste(labelled(ims[1],'AFTER / 新 PNG + UV · 同一形体 / 原色'),(900,0));out.save(path/'comparison.png')
  if quick:continue
  for mode in ['gray','dim']:labelled(raster(q,tex,mode=mode),NAMES[index]+' / '+mode+' 软件检查').save(path/(mode+'.png'))
  anim=json.loads((A/'animations/boss_forms'/(id+'.animation.json')).read_text())['animations'];requested,tick=SIGNATURE[index];clip=next((a for a in anim if a.endswith(requested)),None)
  if not clip:clip=next(a for a in anim if not a.endswith(('idle','walk','hurt','death')))
  tick=min(tick,anim[clip]['animation_length']*20*.75)
  for t in [0,tick,anim[clip]['animation_length']*20*.9]:
   pq=r.geometry(id,clip=clip,tick=t);labelled(raster(pq,tex,mode='lit'),NAMES[index]+f' / {clip.split(".")[-1]} / {t:.1f} tick').save(path/f'action-{t:.1f}.png')
  frames=[]
  for t in np.linspace(0,anim[clip]['animation_length']*20,20):frames.append(labelled(raster(r.geometry(id,clip=clip,tick=float(t)),tex,mode='lit',size=(720,540)),NAMES[index]+' / 原有动作时间轴'))
  frames[0].save(path/'action.webp',save_all=True,append_images=frames[1:],duration=round(anim[clip]['animation_length']*1000/20),loop=0,lossless=True)
  pts=np.concatenate([v[0] for v in q]);right=np.array([math.sqrt(.5),0,math.sqrt(.5)]);offset=right*(float((pts@right).min())-45);scene=q+references(offset)
  for distance in [10,18,28]:labelled(raster(scene,tex,mode='lit',size=(1280,800),distance=distance),NAMES[index]+f' / 距模型原点 {distance}m · 70°垂直视场 · 1.62m视高','软件透视 · 1.8m玩家、1m石砖/木材自绘参照 · 正常游戏光照待实机').save(path/f'distance-{distance}m.png')
  # Full-size same-scene orthographic reference, no relative scale tricks.
  labelled(raster(scene,tex,mode='lit',size=(1200,800)),NAMES[index]+' / 玩家、石砖、木材比例对照','软件光照 / 原创16px参照纹理 / 非游戏截图').save(path/'scene.png')
  print('reviewed export',id,clip,flush=True)
if __name__=='__main__':run([x for x in sys.argv[1:] if x!='--quick'] or IDS,'--quick' in sys.argv)
