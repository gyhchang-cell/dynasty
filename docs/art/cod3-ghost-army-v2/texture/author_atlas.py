"""Original finite-color pixel brushes against frozen face islands. No reference copying."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[3];M=D.parent;sys.path.insert(0,str(R/'tools/art/boss-forms'))
from atlas import CORNERS
P={
 'clay_face':[(70,64,54),(117,106,86),(150,137,110),(171,157,128)],
 'fired_clay':[(74,70,60),(106,101,85),(133,126,106),(150,142,121)],
 'lamellar':[(38,46,43),(58,69,62),(80,91,78),(102,111,94)],
 'undercloth':[(39,38,34),(58,56,47),(77,73,60),(91,85,70)],
 'binding':[(41,32,25),(67,49,33),(93,69,43),(113,86,55)],
 'old_bronze':[(55,49,34),(88,75,45),(115,99,60),(137,120,78)],
 'haft':[(40,30,23),(66,47,30),(90,66,40),(110,82,50)],
 'blade':[(48,57,56),(79,93,88),(122,136,123),(158,168,150)],
 'recess':[(31,33,30)]*4}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def xyz(r,u,v):
 a,b,c,e=np.array(CORNERS[r['face']],float);return np.array(r['cube_origin'])+np.array(r['cube_size'])*(a+(b-a)*u+(e-a)*v)
def tile(r):
 w,h=r['rect'][2:];mat=r['material'];part=r['part'];face=r['face'];p=P[mat];wall=face not in ('up','down');base=1 if wall else (2 if face=='up' else 0)
 im=Image.new('RGB',(w,h),p[base]);d=ImageDraw.Draw(im)
 if mat in ('fired_clay','clay_face'):
  if wall and w>=3:
   d.rectangle((0,0,0,h-1),fill=p[0]);d.rectangle((max(1,w//3),0,max(1,w//3),max(0,h-2)),fill=p[2])
  if part=='terracotta_face' and face=='south':
   im=Image.new('RGB',(w,h),p[2]);d=ImageDraw.Draw(im)
   for yy in range(h):
    for xx in range(w):
     x,y,z=xyz(r,(xx+.5)/w,(yy+.5)/h)
     if abs(x)>2.3:im.putpixel((xx,yy),p[1])
     # Two narrow shadowed eye sockets on the actual small face, neutral mouth.
     if 38.1<y<39.2 and 1.0<abs(x)<2.5:im.putpixel((xx,yy),p[0])
     # Mouth belongs on the projecting chin cube, not behind the nose.
  if part=='nose_plane':
   d=ImageDraw.Draw(im);d.rectangle((0,0,w-1,h-1),fill=p[3 if face in ('south','up') else 1])
  if 'palm' in part or 'fingers' in part or 'thumb' in part or 'knuckles' in part:
   # Hands carry broad ceramic planes, never facial motifs or tiny nails.
   d=ImageDraw.Draw(im);d.rectangle((0,0,w-1,h-1),fill=p[2 if face in ('south','up') else 1])
   if w>=3 and h>=3 and 'palm' in part:d.line((0,h-1,w-1,h-1),fill=p[0])
  if part=='chin_plane' and face=='south':
   d.line((0,h-1,w-1,h-1),fill=p[1]);d.line((max(0,w//2-1),0,w//2,0),fill=p[0])
 elif mat=='lamellar':
  if wall:
   if w>=4:d.rectangle((0,0,max(0,w//3-1),h-1),fill=p[2])
   # Broad courses spaced in model units; no 1px checkerboard studs.
   if 'course' in part or 'cuirass' in part or 'apron' in part or 'greave' in part or 'sleeve' in part:
    for yy in range(h):
     y=xyz(r,.5,(yy+.5)/h)[1]
     if yy%3==2 and h>=4:
      d.line((0,yy,w-1,yy),fill=p[0])
    if w>=7 and h>=5:
     x=w//2;d.line((x,0,x,1),fill=p[0]);d.line((x-2,3,x-2,4),fill=p[0])
     d.point((1,0),fill=p[3]);d.point((w-2,3),fill=p[2])
   if 'helmet' in part or 'guard' in part:
    if h>=2:d.line((0,h-1,w-1,h-1),fill=p[0])
   if part=='helmet_brow':d.line((0,0,w-1,0),fill=p[2])
  elif w>=3 and h>=3:d.rectangle((1,1,max(1,w-2),max(1,h-2)),fill=p[2 if face=='up' else 0])
 elif mat=='undercloth':
  if wall and w>=3:
   d.rectangle((max(1,w//3),0,max(1,w//3),h-1),fill=p[2]);d.line((w-1,0,w-1,h-1),fill=p[0])
 elif mat=='binding':
  if wall:
   d.line((0,0,w-1,0),fill=p[2]);
   if h>=3:d.line((0,h-1,w-1,h-1),fill=p[0])
 elif mat=='old_bronze':
  if wall and w>=2:d.line((0,0,0,h-1),fill=p[2])
  if face=='up':d.line((0,0,w-1,0),fill=p[3])
  if part=='belt_fastening' and face=='south':d.point((w//2,0),fill=p[3])
 elif mat=='haft':
  for yy in range(h):
   for xx in range(w):
    x,y,z=xyz(r,(xx+.5)/w,(yy+.5)/h)
    n=2 if face in ('south','east','up') else 1
    if 20<=y<=24:n=max(0,n-1)
    im.putpixel((xx,yy),p[n])
 elif mat=='blade':
  if wall:
   for yy in range(h):
    for xx in range(w):
     # One edge light and darker central spine on actual frozen blade.
     n=3 if xx==0 else (0 if xx==w//2 and w>=3 else 2)
     im.putpixel((xx,yy),p[n])
 return im
if __name__=='__main__':
 hand=json.loads((M/'TEXTURE_HANDOFF.json').read_text());frozen={p:sha(R/p) for p in hand['files']};save(D/'source-before.json',frozen) if not (D/'source-before.json').exists() else None
 b=M/'blockbench/ghost_army_soldier.bbmodel';(D/'before').mkdir(exist_ok=True);(D/'before/ghost_army_soldier.bbmodel').write_bytes(b.read_bytes()) if not (D/'before/ghost_army_soldier.bbmodel').exists() else None
 rows=json.loads((M/'UV_LOCK.json').read_text())['islands'];atlas=Image.new('RGB',(256,256),P['recess'][0]);occupied=np.zeros((256,256),bool)
 for r in rows:
  x,y,w,h=r['rect'];assert not occupied[y:y+h,x:x+w].any();occupied[y:y+h,x:x+w]=True;atlas.paste(tile(r),(x,y))
 # Explicit one-texel extrusion into unoccupied gutters, no UV modification.
 pixels=atlas.load()
 for r in rows:
  x,y,w,h=r['rect']
  for yy in range(max(0,y-1),min(256,y+h+1)):
   for xx in range(max(0,x-1),min(256,x+w+1)):
    if not occupied[yy,xx]:pixels[xx,yy]=pixels[min(x+w-1,max(x,xx)),min(y+h-1,max(y,yy))]
 atlas.save(D/'texture.png');save(D/'palette.json',P)
 print('Authored',len(rows),'islands;',len(atlas.getcolors(65536)),'solid colors; source snapshot saved')
