"""Static native ModelPart declaration assembly; not engine or player acceptance."""
from pathlib import Path
import json,hashlib,importlib.util,inspect,math
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2];BORROW=R/'tools/art/secondary-cuboid/review_models.py';VANILLA=R/'docs/art/armor-historic-binding-20261104/vanilla-source/a569a8fe46e3-ModelPart.java'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def matrix(p):
 x,y,z=p[3:];cx,cy,cz=map(math.cos,[x,y,z]);sx,sy,sz=map(math.sin,[x,y,z]);rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]);m=np.eye(4);m[:3,:3]=rz@ry@rx;m[:3,3]=p[:3];return m

def quads(models):
 out=[]
 for model in models.values():
  world={'root':np.eye(4)}
  for n in model['nodes']:
   m=world[n['parent']]@matrix(n['pose']);world[n['name']]=m
   for c in n['cubes']:
    a=np.array(c['origin'])-c['deformation'];b=np.array(c['origin'])+np.array(c['size'])+c['deformation']
    if c['mirror']:a[0],b[0]=b[0],a[0]
    x,y,z=a;X,Y,Z=b;v=np.array([[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]])
    v=(m@np.column_stack((v,np.ones(8))).T).T[:,:3]*[1,-1,1]
    u,t=c['uv'];w,h,d=c['size'];f4=u;f5=u+d;f6=u+d+w;f7=u+d+2*w;f8=u+2*d+w;f9=u+2*d+2*w;v0=t;v1=t+d;v2=t+d+h
    faces=[([5,4,0,1],[f5,v0,f6,v1]),([2,3,7,6],[f6,v1,f7,v0]),([0,4,7,3],[f4,v1,f5,v2]),([1,0,3,2],[f5,v1,f6,v2]),([5,1,2,6],[f6,v1,f8,v2]),([4,5,6,7],[f8,v1,f9,v2])]
    for indices,rect in faces:
     # Vanilla polygon corner0=(u1,v0),1=(u0,v0),2=(u0,v1),3=(u1,v1).
     indices=[indices[i] for i in [1,0,3,2]];u0,t0,u1,t1=rect
     out.append((v[indices],{'uv':[u0,t0],'uv_size':[u1-u0,t1-t0]},n['name']))
 return out

def main():
 p=json.loads((D/'binding-and-geometry-study.json').read_text());q=quads(p['models']);assert len(q)==72*6
 spec=importlib.util.spec_from_file_location('readonly_native_assembly',BORROW);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
 code=inspect.getsource(r.raster).replace(".convert('RGB')",".convert('RGBA')").replace('color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade','mask &= atlas[ty,tx,3]>127\n            color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx,:3]*shade');exec(code,r.__dict__)
 rows=[]
 for case in json.loads((D/'provenance.json').read_text())['cases']:
  chain=next(x for x in p['slot_chains'] if x['case_key']==case['case_key']);a=chain['source_texture'];r.TEX=D/a['local'];r.TEX_SIZE=128
  ims=[r.raster(q,y,6,size=(330,420)) for y in [0,45,90,180]]+[r.raster(q,0,6,size=(330,420),silhouette=True)]
  out=Image.new('RGB',(1650,500),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'SOFTWARE / STATIC NATIVE DECLARATIONS / NOT GAME / '+case['case_key'],font=r.font(15),fill='white')
  for j,(im,label) in enumerate(zip(ims,['FRONT','45','SIDE','BACK','BLACK'])):out.paste(im,(j*330,40));dr.text((j*330+10,468),label,font=r.font(16),fill='white')
  name=case['case_key'].replace(':','-')+'-assembly.png';out.save(D/name);rows.append({'case_key':case['case_key'],'path':name,'sha256':sha(D/name),'source_texture':a,'cubes_in_static_union':72})
 result={'software_analysis_pages':rows,'borrowed_raster':str(BORROW.relative_to(R)),'borrowed_raster_sha256':sha(BORROW),'vanilla_cube_polygon_context':str(VANILLA.relative_to(R)),'vanilla_cube_polygon_context_sha256':sha(VANILLA),'runtime_acceptance':False,'new_artwork':0,'game_starts':0,'limits':['静态主模型/靴模型声明全套组装；不包含玩家或实际姿态','按固定ModelPart源解释常量pose/变形/镜像/boxUV，只作研究，不声明引擎采样、shader、动画、插件兼容或接缝验收','相同模型四张材质软件图不计四个设计']}
 (D/'assembly-study.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('4 software declaration assemblies; 72 source cubes each, zero game starts.')
if __name__=='__main__':main()
