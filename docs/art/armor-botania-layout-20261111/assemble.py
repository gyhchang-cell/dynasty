"""Static source-declared pose/UV assembly; not Minecraft renderer or equipped acceptance."""
from pathlib import Path
import json,hashlib,importlib.util,inspect,math
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2];HELPER=R/'docs/art/armor-native-face-uv-20261111/render_native.py';CONTRACT=HELPER.parent/'native-uv-contract.json';NATIVE=R/'docs/art/armor-historic-binding-20261104/vanilla-source/a569a8fe46e3-ModelPart.java';RASTER=R/'tools/art/secondary-cuboid/review_models.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mod(p,n):
 s=importlib.util.spec_from_file_location(n,p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);return v
def matrix(p):
 x,y,z=p[3:];cx,cy,cz=map(math.cos,[x,y,z]);sx,sy,sz=map(math.sin,[x,y,z]);rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]);m=np.eye(4);m[:3,:3]=rz@ry@rx;m[:3,3]=p[:3];return m

def main():
 decoded=json.loads((D/'decoded-models.json').read_text());contract=json.loads(CONTRACT.read_text());helper=mod(HELPER,'source_face_only');r=mod(RASTER,'source_layout_raster');native=NATIVE.read_text();assert 'this.normal.mul(-1.0F, 1.0F, 1.0F)' in native and 'p_104362_[i - 1 - j] = modelpart$vertex' in native and 'rotationZYX' in native
 # Native1.20 source read: same six declared rectangles and corner UV association as D33.
 for f in contract['faces']:assert 'Direction.'+f['direction'] in native
 code=inspect.getsource(r.raster).replace(".convert('RGB')",".convert('RGBA')").replace('color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade','mask &= atlas[ty,tx,3]>127\n            color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx,:3]*shade');exec(code,r.__dict__);pages=[]
 for key,model in decoded['models'].items():
  q=[];detail=[]
  for stage,mesh in model['stages'].items():
   world={'root':np.eye(4)}
   for n in mesh['nodes']:
    m=world[n['parent']]@matrix(n['pose']);world[n['name']]=m
    # Union of slot-visible outer head/chest/feet and inner leggings, without inventing body geometry.
    if not n['cubes']:continue
    if stage=='inner':
     ancestor=n['name'];lookup={v['name']:v['parent'] for v in mesh['nodes']}
     while lookup[ancestor]!='root':ancestor=lookup[ancestor]
     assert ancestor in ['body','left_leg','right_leg']
    neutral={**n,'parent':'root','pose':[0]*6};faces,records=helper.quads([neutral],contract)
    for (v,uv,name),record in zip(faces,records):
     mc=v*[1,-1,1];v=(m@np.column_stack((mc,np.ones(4))).T).T[:,:3]*[1,-1,1];q.append((v,uv,stage+'/'+name));detail.append({'stage':stage,**record,'vertices_world_y_up':v.tolist()})
  material=key.split(':')[1];source=R/model['texture'];r.TEX=source;r.TEX_SIZE=128;gray=Image.open(source).convert('RGBA');gray.putdata([(180,180,180,p[3]) for p in gray.getdata()]);gp=D/f'{material}-GRAY-ANALYSIS-ONLY.png';gray.save(gp)
  out=Image.new('RGB',(1800,510),(68,73,78));dr=ImageDraw.Draw(out);dr.text((10,9),'ORIGINAL SOURCE GEOMETRY + UV / SOFTWARE ONLY / NOT GAME / '+key,font=r.font(14),fill='white')
  for i,(yaw,label) in enumerate(zip([0,45,90,180,45,0],['FRONT','45','SIDE','BACK','GRAY','BLACK'])):
   r.TEX=gp if i==4 else source;out.paste(r.raster(q,yaw,6,size=(300,420),silhouette=i==5),(300*i,40));dr.text((300*i+12,474),label,font=r.font(15),fill='white')
  name=f'{material}-source-assembly.png';out.save(D/name);pages.append({'case_key':key,'path':name,'sha256':sha(D/name),'texture':model['texture'],'texture_sha256':sha(source),'gray_analysis_texture':gp.name,'gray_analysis_texture_sha256':sha(gp),'cube_count':len(q)//6,'face_count':len(q),'faces':detail,'runtime_acceptance':False})
 out={'pages':pages,'generic_face_declaration_helper':str(HELPER.relative_to(R)),'generic_face_declaration_helper_sha256':sha(HELPER),'native_1_20_source':str(NATIVE.relative_to(R)),'native_1_20_source_sha256':sha(NATIVE),'decoded_models_sha256':sha(D/'decoded-models.json'),'face_contract_sha256':sha(CONTRACT),'raster':str(RASTER.relative_to(R)),'raster_sha256':sha(RASTER),'limits':['1.20 source face order/mirror and rotation context read, generic software raster only; not engine pixel acceptance','All slots shown as static union; no player, actual animated pose, shader, Forge mixin activation or equipped seam acceptance','Native alpha mask preserved but software cutoff >127 and depth overlaps may produce artifacts; not proof of native PNG noise'],'new_artwork':0,'production_changes':0,'game_starts':0};(D/'assembly-pages.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print({a['case_key']:a['cube_count'] for a in pages})
if __name__=='__main__':main()
