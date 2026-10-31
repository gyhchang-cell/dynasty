"""Original cauldron body pixels with a shared two-form UV layout.

Both atlases include every union island, including the hidden transition legs.
The phase2 model can therefore use the phase1 atlas during the existing32ticks.
Legacy spell/block PNGs, geometry and animation data are not modified here.
"""
from pathlib import Path
import hashlib, json, math
import numpy as np
from PIL import Image
from wood_kite_materials import CORNERS, geometry_signature, pack
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'src/main/resources/assets/dynasty'
DOC=ROOT/'docs/art/bestiary-v43/taoyan'
IDS=('taoyan_zhishi','taoyan_zhishi_phase2')
PALETTE={
 'bronze':['#393d34','#5d533b','#8e7249','#ad925f','#c4b17d'],
 'hotbronze':['#403b31','#71503b','#a56d45','#c68c59','#d3b27a'],
 'iron':['#222f30','#354645','#536360','#7e8a7b','#a5b09b'],
 'bone':['#575c4b','#888975','#b5b297','#d7ceb0','#e9ddbf'],
 'oil':['#232c2e','#344440','#4c5b50','#76816c','#a3a788'],
 'patina':['#344c43','#506959','#718774','#94a38a','#b0b89b'],
 'white':['#716b52','#a29270','#c8ba8e','#e1d5ac','#f2e6c3']}
RGB={k:np.array([[int(c[i:i+2],16) for i in (1,3,5)] for c in v],dtype=np.uint8) for k,v in PALETTE.items()}

def canonical(name):return name.removeprefix('old_')

def paint(name,index,cube,face,material,stage):
 corners=np.array(CORNERS[face],float)*cube['size'];across=corners[1]-corners[0];down=corners[3]-corners[0]
 w=max(1,math.ceil(np.linalg.norm(across)));h=max(1,math.ceil(np.linalg.norm(down)))
 u,v=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h)
 p=np.array(cube['origin'])+corners[0]+u[...,None]*across+v[...,None]*down
 local=p-np.array(cube['origin']);size=np.array(cube['size']);x,y,z=[p[...,i] for i in range(3)];name=canonical(name)
 if name=='boiling_oil':
  if index==0:
   level=np.ones((h,w),int)
   if face=='up':
    # Broken broad circulation arcs on the existing liquid plane, no noise.
    d=np.maximum(np.abs(x+2),np.abs(z-1));level[(d>10)&(d<13)&(z<7)]=2
    level[(x>3)&(x<10)&(z>-9)&(z<-6)]=3
    level[(x<-8)&(z>2)&(z<6)]=0
   return RGB['oil'][level]
  level=np.full((h,w),2 if face!='up' else 3,int);level[(local[...,1]<1)]=1
  return RGB['bone'][level]
 if name.startswith('shell_fracture_') or name=='ram_burning_cast':
  level=np.full((h,w),3 if face in ('north','up') else 2,int)
  level[local[...,1]<2]=1
  return RGB['white'][level]
 if material=='bone':
  level=np.full((h,w),3 if face=='up' else 2,int)
  if face=='down':level[:]=1
  if name=='cauldron_maw':
   # The back rank recedes; upper roots are visibly socketed, tips stay intact.
   level[:]=max(1,3-(index-5)//3) if face=='north' else 2
   level[local[...,1]>size[1]-2]=1
  elif name=='maw_lower_hinge':
   level[local[...,1]<1.5]=1
   if face=='north':level[(u>.3)&(u<.7)&(v<.4)]=3
  elif name.startswith('bone_whip_'):
   level[(local[...,0]<1.5)]=1
   if face=='up':level[(local[...,0]>2)&(local[...,0]<5)]=3
  elif name=='war_relic_crest':
   level[(local[...,1]<3)|(local[...,1]>size[1]-1)]=1
  else:
   axis=int(np.argmax(size));level[(local[...,axis]<2)|(local[...,axis]>size[axis]-2)]=1
  return RGB['bone'][level]
 if material=='dark':
  level=np.full((h,w),2 if face=='up' else 1,int)
  if face=='down':level[:]=0
  if name=='war_cauldron':
   level[:]=0 if face=='up' else 1
  elif name=='cauldron_maw':
   # Dark recessed central opening is real space between these existing cubes.
   level[:]=1
   if index==0 and face=='north':
    level[(y>45)&(np.abs(x)>11)]=2
    level[(np.abs(x)<7)&(y<44)]=0
   elif face=='north':level[(np.abs(x)>16)]=2
   if face in ('south','down'):level[:]=0
  elif name=='maw_lower_hinge':
   level[:]=1
   if face=='north':level[(y>29)&(np.abs(x)<13)]=2
   if face=='up':level[:]=0
  elif name=='siege_piston':
   if face in ('east','west'):level[(local[...,1]>2)&(local[...,1]<5)]=2
   level[(local[...,2]>19)]=0
  elif name=='siege_ram':
   # Actual forward striking plate gets directional contact wear.
   if face=='north':
    level[:]=2;level[(np.abs(x+30)<3)&(y>33)&(y<39)]=3
    level[(np.abs(x+30)>3)&(y<33)]=1
  elif name=='war_relic_crest':level[:]=1
  elif name.endswith('_foot'):
   level[:]=1;level[(y<2)]=0
  return RGB['iron'][level]
 level=np.full((h,w),3 if face=='up' else 2,int)
 if face=='down':level[:]=0
 if name=='war_cauldron':
  # Large cast walls read as one vessel, rather than framed individual boxes.
  if index in (3,4,5,8,9,10,11) and face not in ('up','down'):
   level[(y<23)]=1
   level[(y>37)&(y<39)]=1
   level[(y>=39)&(y<40)]=3
   # Restrained cast motif on the front's two existing corner plates.
   if face=='north' and index in (8,9):
    edge=np.abs(x);level[(edge>17)&(edge<20)&(y>29)&(y<35)]=1
    level[(edge>16)&(edge<21)&(y>33)&(y<35)]=3
  inside=(index==3 and face=='west')or(index==4 and face=='east')or(index==5 and face=='north')
  if inside:level[:]=1;level[(y<28)]=0
  if index>=12:
   level[:]=2 if face=='up' else 1
   if face=='north':level[(y>49)&(np.abs(x)>12)]=3
 elif 'mourning_bell' in name:
  level[:]=2
  # One band aligned across all four separate wall cubes.
  level[(y>33)&(y<35)]=1
  if face=='up':level[:]=3
  if index<4 and face in ('north','south'):level[(y>38)&(y<40)]=1
 elif name.endswith('bell_yoke'):
  level[:]=1 if face!='up' else 2
 elif name=='siege_socket':
  level[:]=1 if face not in ('north','up') else 2
  if face=='north':level[(np.abs(x+28)<3)&(y>33)&(y<39)]=0
 elif name=='siege_ram':
  level[:]=2 if face!='down' else 0
  if face in ('east','west'):level[(local[...,2]<5)]=1
  if face=='up':level[(local[...,2]<9)]=3
 elif name=='whip_slide':
  level[:]=1
  if face=='north':level[(y>22)&(y<38)]=2
 elif name.startswith('bone_whip_'):
  level[:]=1 if face!='up' else 2
 elif 'tripod_' in name or 'bone_strut_' in name:
  level[:]=1 if face not in ('up','north') else 2
  level[(local[...,1]<2)]=0
 elif name=='war_relic_crest':level[:]=1 if face!='up' else 2
 pixels=RGB['hotbronze' if stage==2 else 'bronze'][level]
 # Patina belongs only to wet lower casting seams, never scattered rectangles.
 if name=='war_cauldron' and index in (3,4,5,8,9,10,11) and face not in ('up','down'):
  mask=(y<24)&(y>21)&((np.abs(x)>20)|(np.abs(z)>20))
  pixels[mask]=RGB['patina'][1]
 return pixels

def export_materials(asset=ASSET):
 refs=json.loads((ROOT/'docs/art/bestiary-v43/taoyan-reference-review.json').read_text())
 assert refs['target']=='dynasty:taoyan_zhishi' and refs['accepted_for_target']>=100
 maps=json.loads(Path(__file__).with_name('taoyan-material-map.json').read_text())
 docs={};union={};facekeys={}
 for ident in IDS:
  doc=json.loads((asset/f'geo/blueprint/boss/{ident}.geo.json').read_text());geo=doc['minecraft:geometry'][0]
  assert geometry_signature(geo)==maps[ident]['geometry_signature'],'Existing body changed; refuse concurrent overwrite'
  mats={(q['bone'],q['index']):q['material'] for q in maps[ident]['cubes']};docs[ident]=doc;facekeys[ident]=[]
  for b in geo['bones']:
   for i,c in enumerate(b.get('cubes',[])):
    material=mats[(b['name'],i)];c['uv']={}
    for face in CORNERS:
     key=(canonical(b['name']),i,face)
     if key in union:
      assert union[key]['cube']['origin']==c['origin'] and union[key]['cube']['size']==c['size']
      assert union[key]['material']==material
     else:union[key]={'key':key,'name':b['name'],'index':i,'cube':c,'face':face,'material':material,'tile':paint(b['name'],i,c,face,material,1)}
     facekeys[ident].append((b['name'],i,face,c,key))
 pack(list(union.values()))
 report={}
 for stage,ident in enumerate(IDS,1):
  atlas=np.full((512,512,3),(34,43,43),dtype=np.uint8)
  for q in union.values():
   x,y,w,h=q['rect'];tile=paint(q['name'],q['index'],q['cube'],q['face'],q['material'],stage)
   atlas[y-1:y+h+1,x-1:x+w+1]=np.pad(tile,((1,1),(1,1),(0,0)),mode='edge')
  islands=[]
  for name,i,face,c,key in facekeys[ident]:
   q=union[key];x,y,w,h=q['rect'];c['uv'][face]={'uv':[x,y],'uv_size':[w,h]}
   islands.append({'bone':name,'cube':i,'face':face,'material':q['material'],'rect':q['rect']})
  doc=docs[ident];geo=doc['minecraft:geometry'][0];geo['description']['texture_width']=geo['description']['texture_height']=512
  assert geometry_signature(geo)==maps[ident]['geometry_signature']
  gp=asset/f'geo/blueprint/boss/{ident}.geo.json';gp.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
  png=asset/f'textures/entity/blueprint/boss/{ident}_body.png';Image.fromarray(atlas).save(png)
  out=DOC/ident;out.mkdir(parents=True,exist_ok=True);Image.fromarray(atlas).save(out/'texture.png');Image.fromarray(atlas).resize((1536,1536),Image.Resampling.NEAREST).save(out/'texture-3x.png')
  (out/'uv-islands.json').write_text(json.dumps(islands,indent=2)+'\n')
  report[ident]={'geometry_preserved':True,'geometry_signature':geometry_signature(geo),'texture_size':[512,512],
   'face_islands':len(islands),'union_islands_in_each_atlas':len(union),'density':'One original texel per model unit; fractional widths rounded up',
   'transition_compatibility':'Both atlases contain every shared-layout island, including growing phase2 legs. Existing32tick switch preserved.',
   'legacy_spell_and_block_PNGs':'UNCHANGED','geo_sha256':hashlib.sha256(gp.read_bytes()).hexdigest(),'texture_sha256':hashlib.sha256(png.read_bytes()).hexdigest()}
 (DOC/'material-export.json').write_text(json.dumps(report,indent=2)+'\n')
 (DOC/'union-islands.json').write_text(json.dumps([{'key':q['key'],'material':q['material'],'rect':q['rect']} for q in union.values()],indent=2)+'\n')
 return report
if __name__=='__main__':print(json.dumps(export_materials(),indent=2))
