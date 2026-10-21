"""Native 512px UV authoring: deliberate flat pixel motifs, no image resampling/noise.
Authored against TEXTURE_HANDOFF physical directions; outputs owned texture files only.
"""
from pathlib import Path
import json,hashlib,math
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parent;H=D.parent/'TEXTURE_HANDOFF.json'
PALETTES={
 'wet_hull':[(29,41,39),(39,51,46),(50,62,52),(64,72,59),(23,33,32)],
 'deck':[(105,83,54),(125,100,65),(146,119,79),(164,138,94),(73,60,43)],
 'timber':[(65,53,39),(83,68,48),(104,85,59),(121,103,73),(46,40,33)],
 'iron':[(35,44,49),(54,66,72),(79,91,93),(103,112,109),(30,38,43)],
 'bamboo':[(93,88,56),(123,114,72),(150,138,86),(170,156,102),(75,77,51)],
 'sail':[(129,153,143),(149,169,156),(170,185,169),(111,135,128),(143,148,112)],
 'canopy':[(40,65,62),(55,82,76),(72,103,91),(90,118,102),(31,53,52)],
 'seal':[(125,117,81),(151,139,93),(174,159,112),(111,92,62),(76,76,57)]}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def physical(row,u,v):
 co={};o=row['origin_units'];s=row['size_units']
 for t,ax in zip((u,v),row['face_axes']):
  j='xyz'.index(ax[-1]);co[ax[-1]]=(o[j]+s[j]*(1-t if ax.startswith('-') else t))*.5
 return co

def pixel(row,u,v,xx,yy):
 m=row['material'];p=PALETTES[m];co=physical(row,u,v);axis=row['long_axis'];along=co.get(axis);others=[v for k,v in co.items() if k!=axis];end=along is None
 if m in ('wet_hull','deck','timber'):
  if end:
   # Cut timber uses square end-grain rings, not longitudinal stripes.
   w,h=row['rect'][2:];q=min(xx,yy,w-1-xx,h-1-yy)
   return p[0 if q%5==0 and min(w,h)>=6 else 1 if q%5<3 else 2]
  long=math.floor(along);cross=math.floor(others[0]);board=cross//6;across=cross%6
  idx=1 if board%3!=1 else 2
  if across==0 and len(others)>0:idx=4
  # Sparse tapered wood grain: two long clusters per 36px, never speckle.
  phase=(long+board*7)%36
  if across in (2,3) and 4<=phase<=12:idx=0
  if across==4 and 19<=phase<=26:idx=2
  if across in (2,3) and phase in (13,14):idx=1
  # Staggered plank end joints; no per-Cuboid bright border.
  if long%36==(board%3)*12 and across>0:idx=0
  # Restrained faded seal strip on ONE main mast wall, attached to existing wood.
  if row['part']=='main_mast_column' and row['face']=='north' and 10<=co.get('y',0)<16 and -1<=co.get('x',0)<1:
   return PALETTES['seal'][1 if math.floor(co['y'])%4!=0 else 3]
  return p[idx]
 if m=='bamboo':
  if end:return p[0 if xx==0 or yy==0 else 2]
  long=math.floor(along);cross=math.floor(others[0]);joint=long%12
  if joint==0:return p[0]
  if joint==1:return p[3]
  return p[1 if cross%4<2 else 2]
 if m=='iron':
  w,h=row['rect'][2:];idx=1
  if yy==0 and xx<max(1,w*2//3):idx=2
  if yy==h-1 and h>2:idx=0
  if w>=7 and h>=5 and 2<=xx<=4 and yy in (2,3):idx=3
  # Large recessed hatch slot, not uniform surface distress.
  if row['part'].startswith('hatch_lid') and row['face']=='up' and 3<=xx<w-3 and h//2-1<=yy<=h//2:idx=4
  return p[idx]
 if m=='sail':
  # Continuous WORLD-ALIGNED layout across all five cloth sections.
  # U reversals are handled by physical(), so back faces do not mirror the weave.
  x=math.floor(co.get('x',row['origin_units'][0]*.5));y=math.floor(co.get('y',row['origin_units'][1]*.5));idx=1
  if x%18 in (0,1):idx=0                 # broad restrained fold cluster
  if x%18 in (3,4,5):idx=2
  if x%12==7:idx=0                     # vertical panel seam
  if x%12==8 and y%6 in (0,1):idx=2    # sparse short stitch beside seam
  # ONE broad stepped repair patch, shared by both visible cloth sides.
  # It occupies world-space coordinates, so no unconnected per-island stamps.
  if row['bone']=='main_sail' and 5<=x<12 and 37<=y<42:
   idx=0 if x in (5,11) or y in (37,41) else 2
  if row['part'].endswith('tab_0') or row['part'].endswith('tab_1'):idx=0 if xx%3==0 else 1
  return p[idx]
 if m=='canopy':
  x=math.floor(co.get('x',0));z=math.floor(co.get('z',0));idx=1
  if x%7==0:idx=4
  elif x%7 in (1,2):idx=2
  if x%7 in (4,5) and z%21 in range(3,9):idx=0
  return p[idx]
 return p[1]

def main():
 data=json.loads(H.read_text());assert data['atlas_size']==[512,512]
 im=Image.new('RGB',(512,512),(25,33,34));occupied=np.zeros((512,512),dtype=np.int16);rows=data['islands'];records=[]
 for row in rows:
  x,y,w,h=row['rect'];assert 1<=x and 1<=y and x+w<512 and y+h<512
  assert not occupied[y:y+h,x:x+w].any(),row['part'];occupied[y:y+h,x:x+w]=1
  tile=Image.new('RGB',(w,h));px=tile.load()
  for yy in range(h):
   for xx in range(w):px[xx,yy]=pixel(row,(xx+.5)/w,(yy+.5)/h,xx,yy)
  # One-pixel nearest edge extrusion fits the existing two-pixel gutters.
  im.paste(tile,(x,y));im.paste(tile.crop((0,0,w,1)),(x,y-1));im.paste(tile.crop((0,h-1,w,h)),(x,y+h));im.paste(tile.crop((0,0,1,h)),(x-1,y));im.paste(tile.crop((w-1,0,w,h)),(x+w,y))
  for dx,dy,sx,sy in [(-1,-1,0,0),(w,-1,w-1,0),(-1,h,0,h-1),(w,h,w-1,h-1)]:im.putpixel((x+dx,y+dy),px[sx,sy])
  records.append({'part':row['part'],'face':row['face'],'material':row['material'],'rect':row['rect'],'colors':len(tile.getcolors(w*h)),'face_axes':row['face_axes'],'long_axis':row['long_axis']})
 im.save(D/'ghost_ship.png')
 (D/'authoring.json').write_text(json.dumps({'workflow':'Native-resolution deterministic pixel painting against authored UV islands; no AI image sampling, resizing, quantization, gradients or random noise','palettes':PALETTES,'atlas':[512,512],'handoffSha256':digest(H),'sha256':digest(D/'ghost_ship.png'),'islands':len(rows),'usedTexels':int(occupied.sum()),'gutter':1,'reviewedReferenceSheets':['references/viewed-1.jpg'],'inheritedReferenceStudy':'Model chat:100 images/16 projects; not all personally reviewed by texture author','islandChecks':records},ensure_ascii=False,indent=2)+'\n')
 print('Authored',len(rows),'UV islands;',int(occupied.sum()),'sampled texels; palette',len(im.getcolors(512*512)))
if __name__=='__main__':main()
