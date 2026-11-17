"""Original face-aware pixel materials for the EXISTING registered WoodKite.

Does not author geometry, animations, weapons, particles or gameplay. The legacy
generator calls this final stage so another export cannot restore flat swatches.
Each texel is sampled in model coordinates: timber follows the visible long
axis; bronze contact areas, optical lenses and motors have distinct treatments.
No random texture/noise, borrowed pixels, antialiasing or full-face box outlines.
"""
from pathlib import Path
import copy, hashlib, json, math
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'src/main/resources/assets/dynasty'
HERE = Path(__file__).resolve().parent
DOC = ROOT / 'docs/art/bestiary-v43/wood-kite'

CORNERS = {
 'north': [(0,1,0),(1,1,0),(1,0,0),(0,0,0)],
 'south': [(1,1,1),(0,1,1),(0,0,1),(1,0,1)],
 'west': [(1,1,0),(1,1,1),(1,0,1),(1,0,0)],
 'east': [(0,1,1),(0,1,0),(0,0,0),(0,0,1)],
 'up': [(0,1,1),(1,1,1),(1,1,0),(0,1,0)],
 'down': [(0,0,0),(1,0,0),(1,0,1),(0,0,1)],
}

PALETTE = {
 'wood': ['#3c2b29','#56372f','#704936','#8e6242','#ae8055'],
 'bronze': ['#443c2e','#68563a','#92764b','#b59a61','#d3bd86'],
 'iron': ['#293638','#405052','#5d6d6b','#8a9990','#bbc2ac'],
 'ivory': ['#667979','#8f9e97','#bdc7b7','#e3e5ce'],
 'core': ['#2a293b','#51405f','#816090','#b38abb','#e3cadd'],
}
RGB = {key:np.array([[int(c[i:i+2],16) for i in (1,3,5)] for c in colors],dtype=np.uint8) for key,colors in PALETTE.items()}

def geometry_signature(geo):
 bones=copy.deepcopy(geo['bones'])
 for b in bones:
  for c in b.get('cubes',[]):c.pop('uv',None)
 return hashlib.sha256(json.dumps(bones,sort_keys=True).encode()).hexdigest()

def tile(bone, index, cube, face, material, metal):
 corners=np.array(CORNERS[face],dtype=float)*np.array(cube['size'])
 across=corners[1]-corners[0];down=corners[3]-corners[0]
 w=max(1,math.ceil(np.linalg.norm(across)));h=max(1,math.ceil(np.linalg.norm(down)))
 u,v=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h)
 p=np.array(cube['origin'])+corners[0]+u[...,None]*across+v[...,None]*down
 spans=np.ptp(corners,axis=0);long_axis=int(np.argmax(spans))
 secondary=next(a for a in range(3) if spans[a]>.01 and a!=long_axis)
 long=p[...,long_axis];cross=p[...,secondary]
 name=bone.lower()
 if material=='wood' and not metal:
  # Long growth bands form broad connected clusters, not random scratches.
  band=np.floor(cross).astype(int)%11;along=np.floor(long).astype(int)%23
  level=np.full((h,w),2 if face=='up' else 1,dtype=int)
  level[(band>=3)&(band<=5)]=min(3,level[0,0]+1)
  level[(band==8)&(along>=5)&(along<=16)]=0
  level[(band==2)&(along>=9)&(along<=18)]=3
  if 'vanes' in name:
   # The warm attachment band joins the whole wing's root; the tip stays quiet.
   z=p[...,2];root=z<6;level[root]=2
   level[(z>6)&(z<8)]=3
  if name=='eagle_tool_head':
   # One continuous dark brow supports the existing separate lenses.
   level[p[...,1]>38]=0
   level[(p[...,1]>=29)&(p[...,1]<31)]=3
  return RGB['wood'][level]
 if material=='core':
  # Optical mineral and exhaust recess share a palette, not the same pattern.
  du=np.abs(u-.5);dv=np.abs(v-.5)
  level=np.ones((h,w),dtype=int)
  central=(du<.28)&(dv<.33);level[central]=2
  level[(du<.15)&(dv<.25)]=3
  if name=='forehead_thunder_core':
   level[(du+dv<.22)]=4
   level[(u<.32)&(v>.55)]=1
  else:
   level[(du<.12)&(dv<.14)]=0
  return RGB['core'][level]
 if material=='white':
  if 'focusing_lens' in name:
   # Literal 2x3x5 lens housing: a dark socket, small iris, single catchlight.
   level=np.full((h,w),1,dtype=int);level[(np.abs(u-.5)<.33)&(np.abs(v-.5)<.31)]=3
   level[(u<.45)&(v<.5)&(np.abs(v-.5)<.31)]=4
   return RGB['core'][level]
  level=np.full((h,w),2 if face in ('up','north') else 1,dtype=int)
  # Scraping edges only on the shear beak and claw tips, not every rail border.
  if 'beak' in name or 'tip' in name:
   level[(v<.32)&(u>.22)]=3
   level[(v>.78)&(u<.8)]=0
  elif 'folding_rail' in name:
   level[:]=1
   level[(v<.3)&(np.floor(long).astype(int)%14<5)]=2
  return RGB['ivory'][level]
 # Bronze structure, with dark iron only at functional contacts / bays.
 iron=('landing_lower' in name or 'four_claw' in name or 'open_bomb' in name or 'tail_link' in name or 'gear_' in name or (metal and material=='wood'))
 palette=RGB['iron' if iron else 'bronze']
 level=np.full((h,w),2 if face=='up' else 1,dtype=int)
 if face in ('north','east'):level[:]=2
 # A broad facet separates outer casing from its under-side, no nested borders.
 if h>=6 and w>=6:
  level[(v>.68)&(u>.18)]=max(0,level[0,0]-1)
  level[(v<.18)&(u>.15)&(u<.8)]=min(3,level[0,0]+1)
 if 'folding_rail' in name:
  level[:]=1 if face=='down' else 2
  # Functional sleeve ends and sliding track, shared model-space direction.
  end=(np.abs(p[...,0])%1<.4) & (np.abs(p[...,0])%13<2)
  level[end]=3
  if face=='up':level[(v>.38)&(v<.68)]=0
 elif 'gear_' in name:
  level[:]=1;level[(np.floor(cross).astype(int)%6<2)]=2
 elif 'oil_jet_' in name:
  # Warm motor casing; outlet and top grilles are spatially constrained.
  if face=='south':
   level[:]=0;level[(u>.2)&(u<.8)&(v>.2)&(v<.8)]=2
  elif face=='up' and h>=5 and w>=4:
   level[(np.floor(p[...,2]).astype(int)%4<2)&(u>.18)&(u<.82)]=0
 elif 'engine_' in name or 'wing_bearing' in name:
  level[(v>.24)&(v<.62)&(u>.28)&(u<.65)]=0
 elif name=='mortise_airframe':
  level[:]=1
  # A sparse cross-tie wrap, not an outline on each rectangular frame piece.
  tie=(np.floor(long).astype(int)%19<3)
  level[tie]=2
 elif 'focusing_lens' in name:
  level[:]=1
  level[(v<.3)&(u>.2)&(u<.8)]=3
 elif 'claw' in name:
  level[:]=1
  level[(v<.3)&(u>.3)]=2
 elif 'eagle_tool_head' in name or 'head_carriage' in name:
  level[:]=2 if face=='up' else 1
  level[(v<.25)&(u>.2)&(u<.8)]=3
 return palette[level]

def pack(records, size=512):
 x=y=row_h=0
 for item in sorted(records,key=lambda q:(-q['tile'].shape[0],-q['tile'].shape[1],q['key'])):
  h,w=item['tile'].shape[:2]
  if x+w+2>size:x=0;y+=row_h;row_h=0
  assert y+h+2<=size,'Atlas overflow: do not silently reduce pixel density'
  item['rect']=[x+1,y+1,w,h];x+=w+2;row_h=max(row_h,h+2)

def export_materials(asset=ASSET):
 reference=json.loads((ROOT/'docs/art/bestiary-v43/wing-reference-review.json').read_text())
 assert reference['target']=='dynasty:luban_yisha' and reference['accepted_for_target']>=100
 maps=json.loads((HERE/'wood-kite-material-map.json').read_text());report={}
 for ident,mapping in maps.items():
  gp=asset/f'geo/blueprint/boss/{ident}.geo.json';tp=asset/f'textures/entity/blueprint/boss/{ident}.png'
  doc=json.loads(gp.read_text());geo=doc['minecraft:geometry'][0]
  assert geometry_signature(geo)==mapping['geometry_signature'],'Existing form changed; reassess instead of overwriting'
  materials={(m['bone'],m['index']):m['material'] for m in mapping['cubes']};records=[]
  for bone in geo['bones']:
   for i,cube in enumerate(bone.get('cubes',[])):
    cube['uv']={}
    for face in CORNERS:
     records.append(dict(key=(bone['name'],i,face),cube=cube,face=face,
      material=materials[(bone['name'],i)],tile=tile(bone['name'],i,cube,face,materials[(bone['name'],i)],ident.endswith('_metal'))))
  pack(records)
  atlas=np.full((512,512,3),(30,36,38),dtype=np.uint8)
  for item in records:
   x,y,w,h=item['rect'];pixels=item['tile'];atlas[y:y+h,x:x+w]=pixels
   # One duplicated texel gutter. Runtime uses nearest filtering, no black seams.
   atlas[y-1:y+h+1,x-1:x+w+1]=np.pad(pixels,((1,1),(1,1),(0,0)),mode='edge')
   item['cube']['uv'][item['face']]={'uv':[x,y],'uv_size':[w,h]}
  geo['description']['texture_width']=geo['description']['texture_height']=512
  assert geometry_signature(geo)==mapping['geometry_signature']
  gp.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');Image.fromarray(atlas).save(tp)
  out=DOC/ident;out.mkdir(parents=True,exist_ok=True)
  Image.fromarray(atlas).save(out/'texture.png')
  Image.fromarray(atlas).resize((1536,1536),Image.Resampling.NEAREST).save(out/'texture-3x.png')
  islands=[dict(bone=q['key'][0],cube=q['key'][1],face=q['face'],material=q['material'],rect=q['rect']) for q in records]
  (out/'uv-islands.json').write_text(json.dumps(islands,ensure_ascii=False,indent=2)+'\n')
  report[ident]=dict(geometry_preserved=True,geometry_signature=geometry_signature(geo),
   texture_size=[512,512],density='16 texels per metre (1 per model unit; fractional widths rounded up)',
   face_islands=len(records),painted_texels=sum(q['tile'].shape[0]*q['tile'].shape[1] for q in records),
   nonconstant_faces=sum(len(np.unique(q['tile'].reshape(-1,3),axis=0))>1 for q in records),
   pixel_palette=len(np.unique(atlas.reshape(-1,3),axis=0)),
   geo_sha256=hashlib.sha256(gp.read_bytes()).hexdigest(),texture_sha256=hashlib.sha256(tp.read_bytes()).hexdigest())
 (DOC/'material-export.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('WoodKite: two existing forms received original directional pixel atlases; geometry and actions preserved.')
 return report

if __name__=='__main__':export_materials()
