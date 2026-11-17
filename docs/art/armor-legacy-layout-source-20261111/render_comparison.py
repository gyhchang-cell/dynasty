"""1.19.2 native-dimension correction diagrams, with retained1.20 polygon-sampling limit."""
from pathlib import Path
import json,hashlib,importlib.util,inspect
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'docs/art/armor-three-slot-closure-20261111';HELPER=R/'docs/art/armor-simian-kit-reference-20261104/assemble.py';RASTER=R/'tools/art/secondary-cuboid/review_models.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mod(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 native=json.loads((D/'native-layout-comparison.json').read_text());prior=json.loads((P/'layout-study.json').read_text());helper=mod(HELPER,'readonly_native_cube_helper');r=mod(RASTER,'readonly_legacy_layout_raster');code=inspect.getsource(r.raster).replace(".convert('RGB')",".convert('RGBA')").replace('color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade','mask &= atlas[ty,tx,3]>127\n            color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx,:3]*shade');exec(code,r.__dict__);nodes=[]
 for name,origin,size,uv,mirror,pos,deformation,slot in prior['mesh_declarations']:
  if 'leg_' in name:deformation=.5 if slot=='leggings' else 1.0
  tex=[uv[0],uv[1]+(32 if slot=='leggings' else 0)];nodes.append({'name':name,'parent':'root','pose':pos+[0,0,0],'cubes':[{'origin':origin,'size':size,'uv':tex,'mirror':mirror,'deformation':deformation}]})
 q=helper.quads({'stock_legacy':{'nodes':nodes}});assert len(q)==60;pages=[]
 for source in prior['software_pages']:
  key=source['case_key']
  if key=='theyarewatching:armorv':continue
  r.TEX=P/source['analysis_atlas'];r.TEX_SIZE=64;ims=[r.raster(q,y,6,size=(300,390)) for y in [0,45,90,180]]+[r.raster(q,0,6,size=(300,390),silhouette=True)];out=Image.new('RGB',(1500,475),(68,73,78));dr=ImageDraw.Draw(out);dr.text((8,8),'1.19.2 NATIVE MESH DIMENSIONS / 1.20 POLYGON SAMPLER / NOT GAME / '+key,font=r.font(13),fill='white')
  for i,(im,label) in enumerate(zip(ims,['FRONT','45','SIDE','BACK','BLACK'])):out.paste(im,(i*300,40));dr.text((i*300+10,440),label,font=r.font(15),fill='white')
  n=key.replace(':','-')+'-native-dimensions.png';out.save(D/n);pages.append({'case_key':key,'path':n,'sha256':sha(D/n),'source_analysis_atlas':str(r.TEX.relative_to(R)),'source_analysis_atlas_sha256':sha(r.TEX),'corrected_only_leg_deformation':True,'game_acceptance':False})
 (D/'correction-diagrams.json').write_text(json.dumps({'nodes':nodes,'pages':pages,'borrowed_geometry_helper':str(HELPER.relative_to(R)),'borrowed_geometry_helper_sha256':sha(HELPER),'borrowed_raster':str(RASTER.relative_to(R)),'borrowed_raster_sha256':sha(RASTER),'prior_layout':str((P/'layout-study.json').relative_to(R)),'prior_layout_sha256':sha(P/'layout-study.json'),'native_mesh_comparison_sha256':sha(D/'native-layout-comparison.json'),'limits':native['limits'],'game_starts':0,'production_changes':0,'reference_credit':0},ensure_ascii=False,indent=2)+'\n');print('Two corrected legacy-dimension diagrams, not game captures or new designs.')
if __name__=='__main__':main()
