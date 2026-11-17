"""Original model-coordinate pixels for the existing oath-shrine/bone horse.

No remesh, pose, animation, weapon design or item export. Legacy 16px texture
consumers remain untouched; only the actor renderer selects new *_body atlases.
"""
from pathlib import Path
import copy, hashlib, json, math
import numpy as np
from PIL import Image
from wood_kite_materials import CORNERS, geometry_signature, pack
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'src/main/resources/assets/dynasty'
DOC=ROOT/'docs/art/bestiary-v43/marshal'
PALETTE={
 'iron':['#263234','#39494b','#536568','#7b8a87','#a6b2a4'],
 'bone':['#575d52','#8b8c76','#b6b59a','#d5d2b4','#e9e3c5'],
 'oath':['#332c37','#543843','#784650','#a1696b','#c69b90'],
 'inside':['#292a30','#41313d','#69414e','#aa7679','#d9bbaa'],
}
RGB={k:np.array([[int(c[i:i+2],16) for i in (1,3,5)] for c in v],dtype=np.uint8) for k,v in PALETTE.items()}
LEGACY={(3,3):'iron',(9,3):'bone',(3,9):'oath',(9,9):'white'}

def paint(name,index,cube,face,material,stage):
 corners=np.array(CORNERS[face],float)*cube['size'];across=corners[1]-corners[0];down=corners[3]-corners[0]
 w=max(1,math.ceil(np.linalg.norm(across)));h=max(1,math.ceil(np.linalg.norm(down)))
 u,v=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h)
 origin=np.array(cube['origin']);size=np.array(cube['size']);p=origin+corners[0]+u[...,None]*across+v[...,None]*down
 local=p-origin;name=name.removeprefix('old_');base=33 if stage==1 else 17
 # The weapon is deliberately not redesigned in this creature-art assignment.
 if name=='four_metre_glaive':
  col={'iron':'#313d40','bone':'#cebd96','oath':'#73454b','white':'#ffffff'}[material]
  return np.full((h,w,3),[int(col[i:i+2],16) for i in (1,3,5)],dtype=np.uint8)
 if name=='empty_oath_cavity':
  level=np.zeros((h,w),int);x=p[...,0];y=p[...,1]-base
  # A broken oath-crest, not text, a painted hole or an emissive effect.
  if face=='north':
   level[(np.abs(x)<4)&(y>7)&(y<15)]=1
   level[(np.abs(x)>1)&(np.abs(x)<3)&(y>8)&(y<14)]=2
   level[(np.abs(x)<1.1)&(y>9)&(y<13)]=4
   level[(y>12)&(y<14)&(x>-3)&(x<1)]=3
  else:level[:]=1
  return RGB['inside'][level]
 if material=='oath':
  level=np.full((h,w),1 if face in ('south','down') else 2,int)
  # Continuous vertical fold along each actual mourning strip, not a box frame.
  if name.startswith('mourning_strip_'):
   level[(u<.34)&(v>.15)]=1;level[(u>.62)&(v<.7)]=3
   level[(v>.78)&(u<.68)]=0
  elif name=='oath_shrine':
   level[:]=1;level[(v<.18)]=2
  return RGB['oath'][level]
 if material in ('bone','white'):
  level=np.full((h,w),3 if face=='up' else 2,int)
  axis=int(np.argmax(size));s=local[...,axis];length=size[axis]
  # Joint roots and end grain only; keep most long bone surfaces intact.
  level[(s<1.5)|(s>length-1.5)]=1
  if face=='down':level[:]=1
  if name=='blind_visor_hinge':
   y=p[...,1]-base;x=p[...,0]
   if face=='north':
    level[:]=2;level[(y>18)&(np.abs(x)<7)]=3
    level[(y<8)&(np.abs(x)>5)]=1
    level[(np.abs(x)<1.1)&(y>16)&(y<20)]=1
    level[(np.abs(x-4)<1)&(y>6)&(y<8)]=3
   elif face=='south':level[:]=0
  elif name=='horse_skull' and material=='bone':
   if face in ('east','west'):
    # Eyes are empty sockets, not a universal red-eye template.
    socket=(p[...,2]>-44)&(p[...,2]<-39)&(p[...,1]>49)&(p[...,1]<53)
    level[socket]=0;level[(p[...,2]>-44)&(p[...,2]<-39)&(p[...,1]>=53)]=3
    level[(p[...,1]<47)&(p[...,2]<-44)]=1
   if face=='north':level[(np.abs(p[...,0])<2)&(p[...,1]<49)]=0
  elif name=='horse_lower_jaw':
   if face in ('east','west'):
    level[(p[...,1]>44)&(np.floor(p[...,2]).astype(int)%4<2)]=0
    level[(p[...,1]<43.5)]=1
  elif name=='horse_neck_base':
   level[(local[...,1]<2)|(local[...,1]>size[1]-2)]=1
  return RGB['bone'][level]
 level=np.full((h,w),2 if face=='up' else 1,int)
 if face=='north':level[:]=2
 if name=='oath_shrine':
  # The thick outside frame stays quiet; interior-facing planes are darker.
  if index==1:level[:]=0 if face=='north' else 1
  if (index==2 and face=='west') or (index==3 and face=='east'):level[:]=0
  if index==0 and face=='up':level[:]=0
  if index==4 and face=='down':level[:]=0
  # Sparse worn top lip, not a border/rivets on every cuboid.
  if face=='north' and index in (0,4):
   level[:]=1;level[(v<.34)&(np.abs(p[...,0])>8)]=3
  if index in (2,3) and face=='north':level[:]=1
  if index>=5:level[:]=1 if face!='up' else 2
 elif name in ('glaive_bearing','two_grip_yoke'):
  level[:]=1;level[(v<.25)&(u>.2)&(u<.8)]=2
  if name=='glaive_bearing' and face=='north':
   level[(np.abs(u-.5)<.2)&(v>.3)&(v<.7)]=0
 elif name.startswith('mourning_tip_'):
  level[:]=0 if face=='down' else 1
  level[(v<.2)&(face!='south')]=2
 elif name=='bone_horse':
  level[:]=1
  if index in (13,14):level[(local[...,1]>5)&(face!='down')]=2
 elif name=='horse_neck_upper':
  level[:]=1;level[(local[...,1]>7)&(face!='down')]=2
  if face in ('east','west'):level[(local[...,2]>9)]=0
 elif name=='horse_skull':
  level[:]=1
  if index==1 and face=='north':
   # Existing muzzle armour: two restrained nasal recesses.
   level[(np.abs(p[...,0])>2)&(np.abs(p[...,0])<4)&(p[...,1]>47)&(p[...,1]<49)]=0
   level[(p[...,1]>49)&(np.abs(p[...,0])<3)]=2
 elif name.endswith('_upper'):
  level[:]=1;level[(local[...,1]>size[1]-3)]=0
  level[(local[...,1]<2)&(face=='north')]=2
 elif name.endswith('_hoof'):
  level[:]=1;level[(local[...,1]<2)]=0
  if face=='north':level[(np.abs(u-.5)<.15)]=0
 elif name in ('left_rocker','right_rocker'):
  level[:]=1 if face!='down' else 0
  if index==0 and face in ('east','west'):
   level[(local[...,1]>3)&(local[...,2]>7)&(local[...,2]<28)]=2
   level[(local[...,2]<4)|(local[...,2]>32)]=0
  if index==2 and face=='north':level[(v<.25)&(u>.2)&(u<.8)]=2
 return RGB['iron'][level]

def export_materials(asset=ASSET):
 refs=json.loads((ROOT/'docs/art/bestiary-v43/marshal-reference-review.json').read_text())
 assert refs['target']=='dynasty:gongsun_wuwang' and refs['accepted_for_target']>=100
 report={}
 mapping_path=Path(__file__).with_name('marshal-material-map.json')
 maps=json.loads(mapping_path.read_text())
 for stage,ident in enumerate(('gongsun_wuwang','gongsun_wuwang_foot'),1):
  gp=asset/f'geo/blueprint/boss/{ident}.geo.json';doc=json.loads(gp.read_text());geo=doc['minecraft:geometry'][0]
  assert geometry_signature(geo)==maps[ident]['geometry_signature'],'Body changed; refuse to overwrite concurrent work'
  materials={(x['bone'],x['index']):x['material'] for x in maps[ident]['cubes']};records=[]
  for bone in geo['bones']:
   for i,c in enumerate(bone.get('cubes',[])):
    c['uv']={}
    for face in CORNERS:
     records.append({'key':(bone['name'],i,face),'cube':c,'face':face,'material':materials[(bone['name'],i)],'tile':paint(bone['name'],i,c,face,materials[(bone['name'],i)],stage)})
  pack(records);atlas=np.full((512,512,3),(38,44,46),dtype=np.uint8);islands=[]
  for q in records:
   x,y,w,h=q['rect'];pixels=q['tile'];atlas[y-1:y+h+1,x-1:x+w+1]=np.pad(pixels,((1,1),(1,1),(0,0)),mode='edge')
   q['cube']['uv'][q['face']]={'uv':[x,y],'uv_size':[w,h]}
   islands.append({'bone':q['key'][0],'cube':q['key'][1],'face':q['face'],'material':q['material'],'rect':q['rect']})
  geo['description']['texture_width']=geo['description']['texture_height']=512
  assert geometry_signature(geo)==maps[ident]['geometry_signature']
  gp.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
  texture=asset/f'textures/entity/blueprint/boss/{ident}_body.png';Image.fromarray(atlas).save(texture)
  out=DOC/ident;out.mkdir(parents=True,exist_ok=True);Image.fromarray(atlas).save(out/'texture.png');Image.fromarray(atlas).resize((1536,1536),Image.Resampling.NEAREST).save(out/'texture-3x.png')
  (out/'uv-islands.json').write_text(json.dumps(islands,indent=2)+'\n')
  report[ident]={'geometry_preserved':True,'geometry_signature':geometry_signature(geo),'texture_size':[512,512],
   'density':'One original texel per model unit; fractional dimensions rounded up. No upscaled old texture.',
   'face_islands':len(records),'painted_texels':sum(q['tile'].shape[0]*q['tile'].shape[1] for q in records),
   'nonconstant_faces':sum(len(np.unique(q['tile'].reshape(-1,3),axis=0))>1 for q in records),
   'legacy_effects_and_socket':'Original16px PNG preserved, new actor-only *_body.png binding.',
   'weapon':'Geometry and original swatch colours retained; no weapon/item redesign.',
   'geo_sha256':hashlib.sha256(gp.read_bytes()).hexdigest(),'texture_sha256':hashlib.sha256(texture.read_bytes()).hexdigest()}
 (DOC/'material-export.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return report
if __name__=='__main__':print(json.dumps(export_materials(),indent=2))
