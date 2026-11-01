"""Read fixed JSON/PNG into offline inspection images; no production asset edits."""
from pathlib import Path
import math,json,hashlib,collections
import numpy as np
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent;S=B.parent/'batch-21/sources/myriantics__klaxon';EX=B/'sources/myriantics__klaxon';roots=[S/'src/main/generated/assets/klaxon',S/'src/main/resources/assets/klaxon',EX/'src/main/resources/assets/klaxon'];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
def asset(kind,id):
 ns,p=id.split(':',1);assert ns=='klaxon';ext='.json' if kind=='models' else '.png'
 return next(r/kind/(p+ext) for r in roots if (r/kind/(p+ext)).is_file())
def model(id,seen=()):
 assert id not in seen
 p=asset('models',id);j=json.loads(p.read_text());parent=j.get('parent');out=model(parent,seen+(id,)) if parent and parent.startswith('klaxon:') else dict(elements=[],textures={},chain=[])
 out['textures'].update(j.get('textures',{}));out['elements']=j.get('elements',out['elements']);out['chain'].append(str(p.relative_to(B,walk_up=True)));return out
texfiles=sorted({p for r in roots for p in (r/'textures').rglob('*.png') if any(t in str(p) for t in ['grapple','empty.png'])});stats=[];sheet=Image.new('RGB',(1080,math.ceil(len(texfiles)/4)*420),'#35414a');draw=ImageDraw.Draw(sheet)
for i,p in enumerate(texfiles):
 im=Image.open(p).convert('RGBA');factor=min(8,320//im.height,250//im.width);x=i%4*270;y=i//4*420;checker=Image.new('RGBA',im.size,'#727a80');checker.alpha_composite(im);sheet.paste(checker.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST).convert('RGB'),(x+10,y+55));draw.text((x+10,y+5),p.parent.name+'/',font=font,fill='white');draw.text((x+10,y+28),p.name+f' {im.width}x{im.height} @{factor}x',font=font,fill='white');stats.append(dict(local=str(p.relative_to(B,walk_up=True)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=list(im.size),alpha=dict(collections.Counter(a for *_,a in im.get_flattened_data())),integer_zoom=factor))
sheet.save(B/'actual-pngs-integer-zoom.png')
texcache={};issues=[];models=[]
def rotation(p,axis,angle,origin):
 a=math.radians(angle);c=math.cos(a);s=math.sin(a);M={'x':[[1,0,0],[0,c,-s],[0,s,c]],'y':[[c,0,s],[0,1,0],[-s,0,c]],'z':[[c,-s,0],[s,c,0],[0,0,1]]}[axis];o=np.array(origin);return (p-o)@np.array(M).T+o
variants={'full-loaded':'klaxon:item/grapple_winch_3d/cable_length_0.0/charged_1_retracting_0','full-unloaded':'klaxon:item/grapple_winch_3d/cable_length_0.0/charged_0_retracting_0','empty-loaded':'klaxon:item/grapple_winch_3d/cable_length_1.0/charged_1_retracting_0','full-retracting':'klaxon:item/grapple_winch_3d/cable_length_0.0/charged_0_retracting_1'}
meshes={}
for variant,id in variants.items():
 m=model(id);faces=[];summary=[]
 for e in m['elements']:
  x0,y0,z0=e['from'];x1,y1,z1=e['to'];q={'north':[(x1,y1,z0),(x1,y0,z0),(x0,y0,z0),(x0,y1,z0)],'south':[(x0,y1,z1),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1)],'east':[(x1,y1,z1),(x1,y0,z1),(x1,y0,z0),(x1,y1,z0)],'west':[(x0,y1,z0),(x0,y0,z0),(x0,y0,z1),(x0,y1,z1)],'up':[(x0,y1,z0),(x0,y1,z1),(x1,y1,z1),(x1,y1,z0)],'down':[(x0,y0,z1),(x0,y0,z0),(x1,y0,z0),(x1,y0,z1)]}
  for side,f in e['faces'].items():
   p=np.array(q[side],dtype=float);r=e.get('rotation')
   if r:p=rotation(p,r['axis'],r['angle'],r['origin'])
   if np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))<1e-10:continue
   tid=f['texture'];visited=set()
   while tid.startswith('#') and tid[1:] in m['textures'] and tid not in visited:visited.add(tid);tid=m['textures'][tid[1:]]
   if tid.startswith('#'):
    issues.append(dict(variant=variant,element=e['name'],side=side,texture=tid,kind='nondegenerate unresolved texture'));continue
   path=asset('textures',tid);tex=np.array(Image.open(path).convert('RGBA'));meta=path.with_suffix('.png.mcmeta')
   if meta.is_file():
    info=json.loads(meta.read_text())['animation'];tex=tex[:info.get('height',tex.shape[1]),:info.get('width',tex.shape[1])]
   texcache[tid]=tex;u0,v0,u1,v1=f['uv'];uv=np.array([[u0,v0],[u0,v1],[u1,v1],[u1,v0]],dtype=float)/16;uv=np.roll(uv,-f.get('rotation',0)//90,axis=0);faces.append(dict(points=p,uv=uv,texture=tid,element=e['name'],side=side))
  summary.append(dict(name=e['name'],from_=e['from'],to=e['to']))
 meshes[variant]=faces;models.append(dict(variant=variant,model=id,chain=m['chain'],elements=len(m['elements']),nondegenerate_resolved_faces=len(faces),bounds_elements=summary,texture_map=m['textures']))
allp=np.concatenate([f['points'] for fs in meshes.values() for f in fs])
def render(fs,yaw,lit=False,width=520,height=430):
 a=math.radians(yaw);e=math.radians(12);toward=np.array([math.sin(a)*math.cos(e),math.sin(e),math.cos(a)*math.cos(e)]);right=np.array([math.cos(a),0,-math.sin(a)]);up=np.cross(toward,right);M=np.stack([right,up,toward]);P=allp@M.T;lo=P.min(0);hi=P.max(0);center=(lo+hi)/2;scale=min((width-55)/(hi[0]-lo[0]),(height-50)/(hi[1]-lo[1]));out=np.full((height,width,3),(214,221,220),dtype=np.uint8);depth=np.full((height,width),-np.inf);light=np.array([-.4,.82,-.4]);light/=np.linalg.norm(light)
 for f in fs:
  points=f['points'];p=(points@M.T-center)*[scale,-scale,1]+[width/2,height/2,0];tex=texcache[f['texture']];h,w=tex.shape[:2];uv=f['uv']*[w,h];n=np.cross(points[1]-points[0],points[2]-points[0]);shade=1 if not lit else .65+.35*abs(float(n/np.linalg.norm(n)@light))
  for idx in [(0,1,2),(0,2,3)]:
   tri=p[list(idx)];tc=uv[list(idx)];x0=max(0,math.floor(tri[:,0].min()));x1=min(width-1,math.ceil(tri[:,0].max()));y0=max(0,math.floor(tri[:,1].min()));y1=min(height-1,math.ceil(tri[:,1].max()))
   if x0>x1 or y0>y1:continue
   xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5);a,b,c=tri;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-10:continue
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;q=1-u-v;z=u*a[2]+v*b[2]+q*c[2];old=depth[y0:y1+1,x0:x1+1];x=np.clip(np.floor(u*tc[0,0]+v*tc[1,0]+q*tc[2,0]).astype(int),0,w-1);y=np.clip(np.floor(u*tc[0,1]+v*tc[1,1]+q*tc[2,1]).astype(int),0,h-1);sample=tex[y,x];mask=(u>=-1e-7)&(v>=-1e-7)&(q>=-1e-7)&(z>old+1e-7)&(sample[:,:,3]>=26);out[y0:y1+1,x0:x1+1][mask]=np.clip(sample[:,:,:3]*shade,0,255).astype(np.uint8)[mask];old[mask]=z[mask]
 return Image.fromarray(out)
for name,fs in meshes.items():
 sheet=Image.new('RGB',(1040,920),'#f2f1e8');d=ImageDraw.Draw(sheet)
 for i,(yaw,lit) in enumerate([(0,False),(45,False),(90,False),(45,True)]):
  x=i%2*520;y=i//2*460;sheet.paste(render(fs,yaw,lit),(x,y+30));d.text((x+10,y+6),name+f' / yaw{yaw} / '+('basic diffuse' if lit else 'raw PNG'),font=font,fill='#27303a')
 sheet.save(B/(name+'-software.png'))
# UV overlay on actual per-material atlases for one loaded variant.
for tid,tex in texcache.items():
 im=Image.fromarray(tex).resize((tex.shape[1]*12,tex.shape[0]*12),Image.Resampling.NEAREST);d=ImageDraw.Draw(im)
 for f in meshes['full-loaded']:
  if f['texture']!=tid:continue
  pts=[(u*tex.shape[1]*12,v*tex.shape[0]*12) for u,v in f['uv']];d.line(pts+[pts[0]],fill=(255,100,70,255),width=1)
 im.save(B/('uv-'+tid.split('/')[-1]+'.png'))
(B/'asset-inspection.json').write_text(json.dumps(dict(kind='ACTUAL_FIXED_JSON_PNG_OFFLINE_INSPECTION',textures=stats,models=models,issues=issues,limitations=['not Minecraft bake/game screenshot; software face convention,depth/diffuse approximation','real PNG sampled per face nearest,not average colors','first atlas animation frame used; no player arm/display-context/mirroring matrices','degenerate faces skipped; unresolved nondegenerate faces reported,never silently invented','no production asset copied/changed; models/states are same family,0 new reference']),ensure_ascii=False,indent=2)+'\n');print('models',[(x['variant'],x['elements'],x['nondegenerate_resolved_faces']) for x in models],'textures',len(stats),'issues',issues)
