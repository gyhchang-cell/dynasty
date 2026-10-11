"""Original Java-block Cuboids with strict16 solid islands and editable Blockbench sources."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import uuid

from PIL import Image, ImageDraw
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'src/main/resources/assets/dynasty'
OUT=ROOT/'docs/art/cod2-vents-v1'
sys.path.insert(0,str(ROOT/'tools/art/cod2-voxel'))
from build_models import Rig
import review

PALETTES={'steam':['#ffffff','#30443f','#aa874b','#708e86'],'flame':['#ffffff','#302d36','#954b37','#e6a14b']}
PORTRAITS={'steam':['..333..','..333..','.22222.','.21112.','.21312.','.21112.','.22222.'],'flame':['.2...2.','.22.22.','.22222.','.21112.','.21312.','.21112.','.22222.']}
TEXTURE='dynasty:block/cod2_vents/{}'
COMMON=[('base',[0,0,0],[16,2,16],2),('chamber',[2,2,5],[14,14,16],1),('top_band',[2,14,5],[14,16,16],2),('lower_lip',[3,2,0],[13,4,5],2),('upper_lip',[3,12,0],[13,14,5],2),('left_lip',[3,4,0],[5,12,5],2),('right_lip',[11,4,0],[13,12,5],2),('throat',[5,4,2],[11,12,5],1)]
MODELS={'steam':COMMON+[('pipe',[6,14,8],[10,16,14],3),('left_grille',[5,4,0],[7,12,2],3),('right_grille',[9,4,0],[11,12,2],3)],'flame':COMMON+[('left_heat_block',[0,10,8],[2,16,14],2),('right_heat_block',[14,10,8],[16,16,14],2),('igniter',[7,6,0],[9,10,2],3)]}
MODELS['steam']=[e for e in MODELS['steam'] if e[0]!='top_band']+[('left_band',[2,14,5],[6,16,16],2),('right_band',[10,14,5],[14,16,16],2),('front_band',[6,14,5],[10,16,8],2),('back_band',[6,14,14],[10,16,16],2)]


def write_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+'\n')


def main():
 OUT.mkdir(exist_ok=True)
 files=[];report=[];review.OUT=OUT
 for name,cubes in MODELS.items():
  rig=Rig(name,PALETTES[name],PORTRAITS[name])
  tex=ASSETS/f'textures/block/cod2_vents/{name}.png';tex.parent.mkdir(parents=True,exist_ok=True)
  rig.image.save(tex);files.append(tex)
  model=ASSETS/f'models/block/cod2_vents/{name}.json'
  faces=lambda material:{face:dict(uv=[*rig.islands[material],rig.islands[material][0]+2,rig.islands[material][1]+2],texture='#atlas') for face in review.FACES}
  elements=[dict(name=n,**{'from':lo,'to':hi},faces=faces(material)) for n,lo,hi,material in cubes]
  write_json(model,dict(ambientocclusion=False,textures={'atlas':TEXTURE.format(name),'particle':TEXTURE.format(name)},elements=elements));files.append(model)
  namespace=uuid.UUID('621e8cc1-6c5d-46bd-8dd2-d9e46881cb6f');uid=lambda key:str(uuid.uuid5(namespace,name+'/'+key))
  bb_elements=[dict(e,type='cube',uuid=uid(e['name']),origin=[8,8,8],rotation=[0,0,0],faces={f:dict(uv=d['uv'],texture=0) for f,d in e['faces'].items()}) for e in elements]
  bb=OUT/f'blockbench/{name}.bbmodel'
  write_json(bb,dict(meta={'format_version':'4.10','model_format':'java_block','box_uv':False},name=name,resolution={'width':16,'height':16},elements=bb_elements,
      outliner=[{'name':'head' if name=='crusher_head' else 'base','origin':[8,0,8],'uuid':uid('group'),'children':[e['uuid'] for e in bb_elements]}],
      textures=[dict(name=tex.name,id='0',uuid=uid('atlas'),width=16,height=16,uv_width=16,uv_height=16,source='data:image/png;base64,'+base64.b64encode(tex.read_bytes()).decode())]));files.append(bb)
  quads=[]
  for n,lo,hi,material in cubes:
   for face,corners in review.FACES.items():
    vertices=np.array(corners)*(np.array(hi)-lo)+lo-np.array([8,0,8])
    quads.append((vertices,{'uv':rig.islands[material],'uv_size':[2,2]},n))
  review.TEX=tex
  images=[review.raster(quads,yaw,elev,size=(420,360),silhouette=i==4) for i,(yaw,elev) in enumerate([(0,0),(45,12),(90,0),(180,0),(0,0)])]
  review.sheet(images,['FRONT','45 DEGREES','SIDE90','BACK','BLACK SILHOUETTE'],name+'-review.png',name+' / actual exported Java Cuboids',cols=3)
  assert len(rig.image.getcolors())==4
  assert all(rig.image.getpixel((x,y))==(255,255,255) for x,y in [(x,y) for x in range(16) for y in range(16) if x in (0,15) or y in (0,15)])
  for e in elements:
   assert all(0<=a<b<=16 for a,b in zip(e['from'],e['to']))
   for f in e['faces'].values():
    u,v,u2,v2=f['uv'];assert u2-u==v2-v==2
    region=set(rig.image.crop((u,v,u2,v2)).get_flattened_data());assert len(region)==1 and (255,255,255) not in region
  report.append(dict(id=name,cuboids=len(cubes),texture=[16,16],colors=4,white_margin=1,uv_islands=[2,2],model=str(model.relative_to(ROOT)),editable=str(bb.relative_to(ROOT))))
 for block,name in [('dungeon_steam_nozzle','steam'),('flame_vent','flame')]:
  state=ASSETS/f'blockstates/{block}.json'
  write_json(state,dict(variants={f'facing={direction}':dict(model=f'dynasty:block/cod2_vents/{name}',**({'y':angle} if angle else {})) for direction,angle in [('north',0),('east',90),('south',180),('west',270)]}));files.append(state)
 write_json(OUT/'resource-validation.json',dict(passed=True,models=report,resource_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))
 print('PASS2 Cuboid nozzles /2 strict16 textures /2 editable sources /2 facing-aware blockstates; software fiveviews generated')

if __name__=='__main__':main()
