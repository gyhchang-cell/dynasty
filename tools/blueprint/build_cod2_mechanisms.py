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
OUT=ROOT/'docs/art/cod2-mechanisms-v1'
sys.path.insert(0,str(ROOT/'tools/art/cod2-voxel'))
from build_models import Rig
import review

PALETTE=['#ffffff','#30443f','#aa874b','#708e86']
PORTRAITS={
 'conveyor':['.22222.','2111112','2133312','2132312','2133312','2111112','.22222.'],
 'crusher_base':['.......','.......','.33333.','.33333.','..111..','.21112.','.22222.'],
 'crusher_head':['..222..','..232..','.22222.','.21112.','.21112.','.23332.','.22222.'],
 'updraft':['...3...','..333..','.3.3.3.','...3...','.22222.','.21312.','.22222.']}
TEXTURE='dynasty:block/cod2_mechanism/{}'
MODELS={
 'conveyor':[("frame",[0,0,0],[16,6,16],2),("left_rail",[0,6,0],[2,16,16],2),
             ("right_rail",[14,6,0],[16,16,16],2),("belt",[2,6,0],[14,14,16],1)],
 'crusher_base':[("base_bottom",[0,0,0],[16,4,16],1),("base_middle",[0,4,0],[16,8,16],2),
                 ("base_upper",[0,8,0],[16,12,16],1),("anvil",[0,12,0],[16,16,16],3)],
 'crusher_head':[("weight",[2,3,2],[14,13,14],1),("lower_ring",[0,0,0],[16,3,16],2),
                 ("upper_ring",[0,13,0],[16,16,16],2),("front_plate",[4,3,0],[12,13,2],3),
                 ("back_plate",[4,3,14],[12,13,16],3)],
 'updraft':[("foundation",[0,0,0],[16,6,16],1),("lower_nozzle",[3,6,3],[13,10,13],2),
            ("upper_nozzle",[4,10,4],[12,14,12],3),("cross_bar",[4,14,6],[12,16,8],1),
            ("north_bar",[6,14,4],[8,16,6],1),("south_bar",[6,14,8],[8,16,12],1)]}
for z in [0,8,12]:
 for x in [2,10]:MODELS['conveyor'].append((f'tread_{x}_{z}',[x,14,z],[x+4,16,z+2],3))
MODELS['conveyor'] += [('arrow_shaft',[6,14,4],[10,16,12],2),('arrow_point',[6,14,0],[10,16,4],2),
                       ('arrow_left',[4,14,2],[6,16,6],2),('arrow_right',[10,14,2],[12,16,6],2)]
for x,z in [(0,0),(14,0),(0,14),(14,14)]:
 MODELS['updraft'].append((f'corner_{x}_{z}',[x,6,z],[x+2,16,z+2],2))


def write_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2)+'\n')


def main():
 OUT.mkdir(exist_ok=True)
 files=[];report=[];review.OUT=OUT
 for name,cubes in MODELS.items():
  rig=Rig(name,PALETTE,PORTRAITS[name])
  tex=ASSETS/f'textures/block/cod2_mechanism/{name}.png';tex.parent.mkdir(parents=True,exist_ok=True)
  rig.image.save(tex);files.append(tex)
  model=ASSETS/f'models/block/cod2_mechanism/{name}.json'
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
 for block,name in [('dungeon_conveyor','conveyor'),('dungeon_crusher','crusher_base'),('updraft_vent','updraft')]:
  state=ASSETS/f'blockstates/{block}.json'
  write_json(state,dict(variants={f'facing={direction}':dict(model=f'dynasty:block/cod2_mechanism/{name}',**({'y':angle} if angle else {})) for direction,angle in [('north',0),('east',90),('south',180),('west',270)]}));files.append(state)
 write_json(OUT/'resource-validation.json',dict(passed=True,models=report,resource_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))
 print('PASS4 Cuboid models /4 strict16 textures /4 editable sources /3 facing-aware blockstates; software fiveviews generated')

if __name__=='__main__':main()
