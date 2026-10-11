"""Deterministic hand-directed material regions. 8 logical texels/block; no noise or gradients."""
import math
from PIL import Image, ImageDraw
# Three discrete tones per material, arranged darkest / base / edge.
MATERIALS={
 'iron':('252d32','414c51','687378'), 'wood':('302e27','65563e','a18b5a'),
 'bone':('82765c','c1b391','e6ddbf'), 'jade':('244539','528167','93b69a'),
 'purple':('33273e','63516e','998198'), 'silk':('402832','884955','bb7a7d'),
 'copper':('503f2e','99704a','c6a16a'), 'gold':('68512b','b0914d','deca88'),
 'fur':('adada2','d7d7ca','f2f0df'), 'darkfur':('30303b','525060','757184'),
 'porcelain':('afa99b','dad8c7','f3edda'), 'ember':('6b352d','b35d38','e3a156')}
SETS=[['iron','wood','bone','jade'],['iron','purple','gold','porcelain'],['iron','copper','silk','bone'],['iron','wood','bone','iron'],['iron','copper','jade','bone'],['iron','gold','jade','bone'],['darkfur','silk','fur','fur'],['iron','copper','ember','bone']]
def tile(material,w,h,face):
 colors=[tuple(bytes.fromhex(c)) for c in MATERIALS[material]];lo,mid,hi=colors
 im=Image.new('RGB',(w,h),mid);d=ImageDraw.Draw(im)
 if min(w,h)<3:return im
 if material in ['iron','copper','gold']:
  # Large plate fields, two-pixel edge wear and deliberately placed rivets.
  d.line([(0,0),(w-1,0)],fill=hi);d.line([(0,h-1),(w-1,h-1)],fill=lo)
  if w>9 and h>9:
   for x in [2,w-4]:d.rectangle((x,2,x+1,3),fill=lo)
   if h>18:d.line((2,h-4,w-3,h-4),fill=lo,width=2)
  if material=='gold' and w>=8 and h>=8:
   # Offset stepped scale courses, following the long axis of each plate.
   for y in range(5,h-2,6):
    for x in range((y//6%2)*4,w-2,8):
     d.line((x,y,min(w-1,x+3),y),fill=lo);d.line((min(w-1,x+4),y-2,min(w-1,x+4),y),fill=hi)
 elif material=='wood':
  for x in range(3,w,7):d.line((x,0,x,h-1),fill=lo)
  for x in range(5,w,14):d.line((x,2,x,max(2,h-4)),fill=hi)
  if h>=9:d.rectangle((0,1,w-1,2),fill=lo);d.rectangle((0,h-3,w-1,h-2),fill=lo)
 elif material=='bone':
  d.rectangle((0,0,w-1,min(1,h-1)),fill=hi);d.rectangle((0,h-2,w-1,h-1),fill=lo)
  if w>8:d.rectangle((w//2-1,2,w//2,max(2,h-4)),fill=hi)
 elif material in ['purple','silk']:
  # Woven cloth remains a broad field with a clear seam and hem, never speckle.
  d.rectangle((0,0,1,h-1),fill=lo)
  if w>8:d.rectangle((3,0,4,h-1),fill=hi)
  if h>10:d.rectangle((0,h-4,w-1,h-3),fill=hi)
 elif material in ['fur','darkfur']:
  # Contiguous coarse tufts running down each face. Limited coverage, no noise.
  for y in range(5,h-3,8):
   for x in range(2+(y//8%2)*4,w-3,9):
    d.rectangle((x,y,x+3,min(h-1,y+1)),fill=lo);d.rectangle((x+2,y+2,x+3,min(h-1,y+3)),fill=lo)
  d.line((0,0,w-1,0),fill=hi)
 elif material=='jade':
  d.line((0,0,w-1,0),fill=hi);d.line((w-1,0,w-1,h-1),fill=lo)
  if w>=8 and h>=8:
   x=w//2;y=h//2;d.rectangle((x-2,y-2,x+1,y+1),fill=lo);d.rectangle((x,y,x+1,y+1),fill=hi)
 elif material=='ember':
  d.rectangle((0,0,w-1,h-1),fill=lo)
  if w>3 and h>3:d.rectangle((1,2,w-2,h-2),fill=mid)
  if w>6 and h>6:d.rectangle((w//3,h//3,2*w//3,2*h//3),fill=hi)
 else:
  d.line((0,h-1,w-1,h-1),fill=lo)
  if w>8:d.line((0,0,w-1,0),fill=hi)
 return im

def atlas(g,index):
 patches={};refs=[]
 for b in g.bones:
  for c in b['cubes']:
   material=SETS[index][c.pop('_material')];x,y,z=c['size']
   for face,dim in [('north',(x,y)),('south',(x,y)),('east',(z,y)),('west',(z,y)),('up',(x,z)),('down',(x,z))]:
    w,h=[max(1,round(v*.5)) for v in dim];key=(material,w,h,face in ['up','down'])
    patches.setdefault(key,tile(material,w,h,face));refs.append((c,face,key))
 size=128
 while True:
  layout={};px=1;py=1;row=0
  for key,im in sorted(patches.items(),key=lambda kv:(-kv[1].height,-kv[1].width,kv[0])):
   w,h=im.size
   if px+w+1>size:px=1;py+=row+2;row=0
   layout[key]=(px,py);px+=w+2;row=max(row,h)
  if py+row+1<=size:break
  size*=2
  assert size<=1024
 image=Image.new('RGB',(size,size),tuple(bytes.fromhex(MATERIALS[SETS[index][0]][0])))
 for key,im in patches.items():
  x,y=layout[key];image.paste(im,(x,y))
  # One-pixel duplicate border prevents samples at the face edge reaching another material.
  image.paste(im.crop((0,0,im.width,1)),(x,y-1));image.paste(im.crop((0,im.height-1,im.width,im.height)),(x,y+im.height))
  image.paste(im.crop((0,0,1,im.height)),(x-1,y));image.paste(im.crop((im.width-1,0,im.width,im.height)),(x+im.width,y))
 for c,f,k in refs:c['uv'][f]={'uv':list(layout[k]),'uv_size':list(patches[k].size)}
 return image
