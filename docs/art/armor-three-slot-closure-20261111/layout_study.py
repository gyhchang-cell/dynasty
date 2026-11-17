"""Source-pinned stock armor UV layout illustration. Not a game/runtime screenshot."""
from pathlib import Path
import json,hashlib,zipfile,inspect,importlib.util
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2];BORROW=R/'tools/art/secondary-cuboid/review_models.py';JAR=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 sources=[]
 with zipfile.ZipFile(JAR) as z:
  for e in ['net/minecraft/client/model/HumanoidModel.java','net/minecraft/client/model/HumanoidArmorModel.java','net/minecraft/client/renderer/entity/layers/HumanoidArmorLayer.java','net/minecraft/client/model/geom/ModelPart.java','net/minecraft/client/model/geom/LayerDefinitions.java']:
   b=z.read(e);h=hashlib.sha256(b).hexdigest();p='vanilla-source/'+h[:12]+'-'+Path(e).name;(D/p).parent.mkdir(exist_ok=True);(D/p).write_bytes(b);sources.append({'entry':e,'local':p,'sha256':h})
 spec=importlib.util.spec_from_file_location('readonly_stock_layout',BORROW);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
 code=inspect.getsource(r.raster).replace(".convert('RGB')",".convert('RGBA')").replace('color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade','mask &= atlas[ty,tx,3]>127\n            color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx,:3]*shade');exec(code,r.__dict__)
 # Stock declaration: local origin, size, native texOffs, mirror, PartPose.offset, deformation.
 mesh=[('head',[-4,-8,-4],[8,8,8],[0,0],False,[0,0,0],1.0,'helmet'),('hat',[-4,-8,-4],[8,8,8],[32,0],False,[0,0,0],1.5,'helmet'),('body',[-4,0,-2],[8,12,4],[16,16],False,[0,0,0],1.0,'chestplate'),('right_arm',[-3,-2,-2],[4,12,4],[40,16],False,[-5,2,0],1.0,'chestplate'),('left_arm',[-1,-2,-2],[4,12,4],[40,16],True,[5,2,0],1.0,'chestplate'),('body_inner',[-4,0,-2],[8,12,4],[16,16],False,[0,0,0],.5,'leggings'),('right_leg_inner',[-2,0,-2],[4,12,4],[0,16],False,[-1.9,12,0],.4,'leggings'),('left_leg_inner',[-2,0,-2],[4,12,4],[0,16],True,[1.9,12,0],.4,'leggings'),('right_leg_outer',[-2,0,-2],[4,12,4],[0,16],False,[-1.9,12,0],.9,'boots'),('left_leg_outer',[-2,0,-2],[4,12,4],[0,16],True,[1.9,12,0],.9,'boots')]
 quads=[]
 for name,origin,size,uv,mirror,pos,inflate,slot in mesh:
  a=np.array(origin,dtype=float)-inflate;b=np.array(origin,dtype=float)+size+inflate
  if mirror:a[0],b[0]=b[0],a[0]
  x,y,z=a;X,Y,Z=b;v=(np.array([[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]])+pos)*[1,-1,1]
  u,t=uv;t+=32 if slot=='leggings' else 0;w,h,d=size;f4=u;f5=u+d;f6=u+d+w;f7=u+d+2*w;f8=u+2*d+w;f9=u+2*d+2*w;v0=t;v1=t+d;v2=t+d+h
  faces=[([5,4,0,1],[f5,v0,f6,v1]),([2,3,7,6],[f6,v1,f7,v0]),([0,4,7,3],[f4,v1,f5,v2]),([1,0,3,2],[f5,v1,f6,v2]),([5,1,2,6],[f6,v1,f8,v2]),([4,5,6,7],[f8,v1,f9,v2])]
  for ids,rect in faces:
   u0,t0,u1,t1=rect;quads.append((v[[ids[i] for i in [1,0,3,2]]],{'uv':[u0,t0],'uv_size':[u1-u0,t1-t0]},name))
 bind=json.loads((D/'closed-static-bindings.json').read_text());pages=[]
 for key in sorted({x['case_key'] for x in bind['rows']}):
  rows=[x for x in bind['rows'] if x['case_key']==key];outer=next(x for x in rows if x['explicit_slot_literal'] in ['HEAD','HELMET'])['actual_worn_texture'];inner=next(x for x in rows if x['explicit_slot_literal'] in ['LEGS','LEGGINGS'])['actual_worn_texture'];prior=R/'docs/art/armor-candidate-resolution-20261109';im1=Image.open(prior/outer['local']).convert('RGBA');im2=Image.open(prior/inner['local']).convert('RGBA');assert im1.size==im2.size==(64,32)
  study=Image.new('RGBA',(64,64));study.paste(im1,(0,0));study.paste(im2,(0,32));n=key.replace(':','-');atlas=D/(n+'-ANALYSIS-ONLY-atlas.png');study.save(atlas);r.TEX=atlas;r.TEX_SIZE=64
  ims=[r.raster(quads,y,6,size=(300,390)) for y in [0,45,90,180]]+[r.raster(quads,0,6,size=(300,390),silhouette=True)]
  out=Image.new('RGB',(1500,475),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'OFFLINE STOCK 1.20 UV LAYOUT STUDY / NOT GAME / '+key,font=r.font(14),fill='white')
  for i,(im,label) in enumerate(zip(ims,['FRONT','45','SIDE','BACK','BLACK'])):out.paste(im,(i*300,40));dr.text((i*300+10,440),label,font=r.font(15),fill='white')
  p=n+'-layout-study.png';out.save(D/p);pages.append({'case_key':key,'path':p,'sha256':sha(D/p),'native_outer':outer,'native_leggings':inner,'analysis_atlas':atlas.name,'analysis_atlas_sha256':sha(atlas),'source_version_context_exact':key=='theyarewatching:armorv','live_rendering_proven':False})
 save('layout-study.json',{'mesh_declarations':mesh,'software_pages':pages,'sources':sources,'sources_jar':str(JAR),'sources_jar_sha256':sha(JAR),'borrowed_raster':str(BORROW.relative_to(R)),'borrowed_raster_sha256':sha(BORROW),'limits':['Research-only geometry reconstructed from pinned Forge1.20.1 vanilla source; NOT added to Dynasty body/model assets','Infectum and Poppy are1.19.2: comparison on1.20.1 stock UV is a bounded illustrative layout, NOT version-exact rendering acceptance','RGBA originals unchanged; two textures stacked only in ANALYSIS-ONLY atlas for software diagram, never runtime asset','No real engine, resource-pack hooks, player pose, animation, lighting/transparent blending, seams or registration runtime acceptance'],'reference_credit':0,'game_starts':0,'production_changes':0})
 print('Three standard-UV layout diagrams generated; two legacy versions explicitly bounded, no runtime claim.')
if __name__=='__main__':main()
