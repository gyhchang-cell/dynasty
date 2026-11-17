"""Native1.19.2 decoded faces, with generic software raster only. Not game QA."""
from pathlib import Path
import json,hashlib,importlib.util,inspect
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent; R=D.parents[2]; P=R/'docs/art/armor-three-slot-closure-20261111'; OLD=R/'docs/art/armor-legacy-layout-source-20261111'; RASTER=R/'tools/art/secondary-cuboid/review_models.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def quads(nodes,contract):
 out=[];records=[]
 for n in nodes:
  assert n['parent']=='root' and n['pose'][3:]==[0,0,0]
  for c in n['cubes']:
   a=np.array(c['origin'],dtype=float)-c['deformation'];b=np.array(c['origin'],dtype=float)+c['size']+c['deformation']
   if c['mirror']:a[0],b[0]=b[0],a[0]
   coord=dict(zip(['x0','y0','z0'],a));coord.update(zip(['x1','y1','z1'],b))
   vertices={k:np.array([coord[t] for t in terms]) for k,terms in contract['vertices'].items()}
   env=dict(zip(['u','v'],c['uv']));env.update(zip(['w','h','d'],c['size']))
   for f in contract['faces']:
    rect=[sum(env[k]*v for k,v in term.items()) for term in f['uv_rectangle']];val=dict(zip(['u0','v0','u1','v1'],rect))
    uv=np.array([[val[t] for t in corner] for corner in contract['polygon_pixel_uv_corner_order']],dtype=float)
    v=np.array([vertices[str(i)] for i in f['vertex_indices']])
    if c['mirror']:v=v[::-1];uv=uv[::-1]
    # Renderer expects 00,10,11,01; keep the native vertex/UV association.
    perm=[1,0,3,2];v=v[perm];uv=uv[perm];assert np.allclose(uv[1]-uv[0],[uv[2,0]-uv[0,0],0]);assert np.allclose(uv[3]-uv[0],[0,uv[2,1]-uv[0,1]])
    records.append({'part':n['name'],'face':f['direction'],'mirror':c['mirror'],'vertices_local':v.tolist(),'pixel_uv_corners':uv.tolist()})
    v=(v+np.array(n['pose'][:3]))*[1,-1,1]
    out.append((v,{'uv':uv[0].tolist(),'uv_size':(uv[2]-uv[0]).tolist()},n['name']))
 return out,records

def main():
 contract=json.loads((D/'native-uv-contract.json').read_text());prior=json.loads((P/'layout-study.json').read_text());nodes=json.loads((OLD/'correction-diagrams.json').read_text())['nodes'];q,records=quads(nodes,contract);assert len(q)==60
 spec=importlib.util.spec_from_file_location('native19_generic_raster',RASTER);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
 code=inspect.getsource(r.raster).replace(".convert('RGB')",".convert('RGBA')").replace('color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade','mask &= atlas[ty,tx,3]>127\n            color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx,:3]*shade');exec(code,r.__dict__);pages=[]
 for src in prior['software_pages']:
  key=src['case_key']
  if key=='theyarewatching:armorv':continue
  r.TEX=P/src['analysis_atlas'];r.TEX_SIZE=64;out=Image.new('RGB',(1500,475),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'NATIVE 1.19.2 FACE UV + MIRROR / SOFTWARE / NOT GAME / '+key,font=r.font(13),fill='white')
  for i,(yaw,label) in enumerate(zip([0,45,90,180,0],['FRONT','45','SIDE','BACK','BLACK'])):
   out.paste(r.raster(q,yaw,6,size=(300,390),silhouette=i==4),(300*i,40));dr.text((300*i+10,440),label,font=r.font(15),fill='white')
  name=key.replace(':','-')+'-native-face-uv.png';out.save(D/name);pages.append({'case_key':key,'path':name,'sha256':sha(D/name),'analysis_atlas':str(r.TEX.relative_to(R)),'analysis_atlas_sha256':sha(r.TEX),'game_acceptance':False})
 save('native-layout-pages.json',{'nodes':nodes,'face_records':records,'pages':pages,'contract_sha256':sha(D/'native-uv-contract.json'),'source_nodes':str((OLD/'correction-diagrams.json').relative_to(R)),'source_nodes_sha256':sha(OLD/'correction-diagrams.json'),'raster':str(RASTER.relative_to(R)),'raster_sha256':sha(RASTER),'limits':contract['limits']+['Generic software raster alpha cutoff and depth overlaps are not engine behavior; no source PNG modifications'],'production_changes':0,'game_starts':0,'reference_credit':0});print('60 native-declared faces including18 mirrored faces; two software pages.')
if __name__=='__main__':main()
