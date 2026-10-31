"""Read-only fixed-source OBJ/PNG inspection. Software images are not game evidence."""
from pathlib import Path
import math,json,hashlib,collections
import numpy as np
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent
O=B/'reference-assets/src/main/resources/assets/immersiveengineering/models/item/chemthrower.obj.ie'
T=B/'reference-assets/src/main/resources/assets/immersiveengineering/textures/item/chemthrower.png'
verts=[];uvs=[];faces=[];groups={};group=None;material=None
for line_no,l in enumerate(O.read_text().splitlines(),1):
 t=l.split()
 if not t or t[0].startswith('#'):continue
 if t[0]=='v':verts.append(list(map(float,t[1:4])))
 elif t[0]=='vt':uvs.append(list(map(float,t[1:3])))
 elif t[0]=='o':group=t[1];groups[group]=dict(faces=0,source_line=line_no)
 elif t[0]=='usemtl':material=t[1]
 elif t[0]=='f':
  idx=[tuple(int(a)-1 for a in v.split('/')[:2]) for v in t[1:]];assert len(idx)==4 and all(0<=v<len(verts) and 0<=u<len(uvs) for v,u in idx);faces.append(dict(group=group,material=material,indices=idx,line=line_no));groups[group]['faces']+=1
V=np.array(verts);U=np.array(uvs);tex=np.array(Image.open(T).convert('RGBA'));h,w=tex.shape[:2];uvgood=bool(np.all((0<=U)&(U<=1)));assert uvgood
for g,info in groups.items():
 ids={v for f in faces if f['group']==g for v,u in f['indices']};pts=V[sorted(ids)];info.update(min=pts.min(0).tolist(),max=pts.max(0).tolist(),vertices_referenced=len(ids))
base={'base','grip','cage','tanks','tank'}
variants={'default':base,'capacity':base|{'large_tank'},'multitank':base|{'multi_tank'},'both':base|{'large_tank','multi_tank'}}
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
def render(visible,yaw,lit=False,size=(600,430)):
 width,height=size;a=math.radians(yaw);e=math.radians(10);toward=np.array([math.sin(a)*math.cos(e),math.sin(e),math.cos(a)*math.cos(e)]);right=np.array([math.cos(a),0,-math.sin(a)]);up=np.cross(toward,right);M=np.stack([right,up,toward]);P=V@M.T;lo=P.min(0);hi=P.max(0);center=(lo+hi)/2;scale=min((width-55)/(hi[0]-lo[0]),(height-60)/(hi[1]-lo[1]));out=np.full((height,width,3),(222,226,224),dtype=np.uint8);depth=np.full((height,width),-np.inf);light=np.array([-.4,.82,-.4]);light/=np.linalg.norm(light)
 for face in faces:
  if face['group'] not in visible:continue
  ids=[v for v,u in face['indices']];p=(P[ids]-center)*[scale,-scale,1]+[width/2,height/2,0];tc=U[[u for v,u in face['indices']]]*[w,-h]+[0,h];points=V[ids];n=np.cross(points[1]-points[0],points[2]-points[0]);length=np.linalg.norm(n)
  if length<1e-10:continue
  shade=1 if not lit else .65+.35*abs(float(n/length@light))
  for idx in [(0,1,2),(0,2,3)]:
   tri=p[list(idx)];uv=tc[list(idx)];x0=max(0,math.floor(tri[:,0].min()));x1=min(width-1,math.ceil(tri[:,0].max()));y0=max(0,math.floor(tri[:,1].min()));y1=min(height-1,math.ceil(tri[:,1].max()))
   if x0>x1 or y0>y1:continue
   xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-10:continue
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;q=1-u-v;z=u*a[2]+v*b[2]+q*c[2];old=depth[y0:y1+1,x0:x1+1];x=np.clip(np.floor(u*uv[0,0]+v*uv[1,0]+q*uv[2,0]).astype(int),0,w-1);y=np.clip(np.floor(u*uv[0,1]+v*uv[1,1]+q*uv[2,1]).astype(int),0,h-1);sample=tex[y,x];mask=(u>=-1e-7)&(v>=-1e-7)&(q>=-1e-7)&(z>old)&(sample[:,:,3]>=26);out[y0:y1+1,x0:x1+1][mask]=np.clip(sample[:,:,:3]*shade,0,255).astype(np.uint8)[mask];old[mask]=z[mask]
 return Image.fromarray(out)
for variant,visible in variants.items():
 sheet=Image.new('RGB',(1200,920),(240,241,235));d=ImageDraw.Draw(sheet)
 for i,(angle,lit) in enumerate([(0,False),(45,False),(90,False),(45,True)]):
  im=render(visible,angle,lit);x=(i%2)*600;y=(i//2)*460;sheet.paste(im,(x,y+30));d.text((x+16,y+5),f'{variant} / OBJ yaw {angle} / '+('basic diffuse' if lit else 'PNG original colour'),font=font,fill=(30,35,40))
 sheet.save(B/(variant+'-software.png'))
# Each raw OBJ group separately, common framing within each view (no fitted per-group scaling).
img=Image.new('RGB',(1800,1380),(240,241,235));d=ImageDraw.Draw(img)
for i,g in enumerate(groups):
 x=i%3*600;y=i//3*460;img.paste(render({g},45),(x,y+30));d.text((x+16,y+5),g+' / same framing / raw PNG',font=font,fill=(30,35,40))
img.save(B/'groups-software.png')
# UV edges over nearest-neighbour atlas, explicit OBJ-v flip from PolygonUtils.
im=Image.open(T).convert('RGBA').resize((w*12,h*12),Image.Resampling.NEAREST);d=ImageDraw.Draw(im);colors=[(250,130,100,255),(80,220,210,255),(160,140,255,255),(245,210,80,255),(100,210,120,255),(240,130,200,255),(100,170,245,255)]
for face in faces:
 pts=[(U[u,0]*w*12,(1-U[u,1])*h*12) for v,u in face['indices']];d.line(pts+[pts[0]],fill=colors[list(groups).index(face['group'])],width=1)
im.save(B/'uv-overlay-12x.png')
v=dict(kind='ACTUAL_FIXED_OBJ_PNG_STATIC_INSPECTION_NOT_GAME',source_obj_sha256=hashlib.sha256(O.read_bytes()).hexdigest(),source_png_sha256=hashlib.sha256(T.read_bytes()).hexdigest(),vertices=len(V),texture_coordinates=len(U),faces=len(faces),all_faces_quads=True,materials=sorted({f['material'] for f in faces}),groups=groups,uv_in_0_1=uvgood,uv_min=U.min(0).tolist(),uv_max=U.max(0).tolist(),png_size=[w,h],alpha_histogram={str(k):int(v) for k,v in zip(*np.unique(tex[:,:,3],return_counts=True))},pixel_sampling='nearest; pixel UV=(u*width,(1-v)*height), clamp at full atlas borders',variants={k:dict(groups=sorted(val),faces=sum(g['faces'] for n,g in groups.items() if n in val)) for k,val in variants.items()},limitations=['仅源OBJ与PNG、不含Minecraft烘焙精度/光照贴图/玩家手臂/物品display矩阵','基础漫反射图为软件近似，无PBR/AO/发光/粒子；不作游戏截图','参考资产只在研究目录，不导出到Dynasty生产资源','source group分解和渲染不新增独立参考计数'])
(B/'asset-inspection.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in v.items() if k in ['vertices','texture_coordinates','faces','png_size','alpha_histogram','uv_min','uv_max','variants']})
