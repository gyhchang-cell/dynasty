"""Authored focal hierarchy for three approved bodies. No geometry or external pixels.

Draw in face-local pixels; the established atlas controls UV density and padding.
The eyes, corpse, firebed and hammer faces have separate designs, not a shared decal.
"""
from PIL import ImageDraw

def palette(*hexes):
 return [tuple(bytes.fromhex(h)) for h in hexes]

BRONZE=palette('544833','776238','99804b','b7a264','d9c891')
GOLD=palette('514333','806339','ac8950','cfb875','ebdbab')
HORN=palette('3e4440','626b5b','87947b','b4bba0','d6d7b9')
SCALE=palette('36483d','475b46','5b7052','728567','939f7f')
BONE=palette('56564d','7b7c68','a3a38a','c4c5a7','e2dfc3')
IRON=palette('292f34','3c474c','566268','778386','aab4af')
COPPER=palette('483a35','694b3e','8d644a','b28860','d0af7d')
FIRE=palette('322e30','693a30','b66033','e89b4e','f7d891')
INK=(36,43,38)

def fill(im,p,tone=2):
 im.paste(p[min(tone,len(p)-1)],(0,0,*im.size));return ImageDraw.Draw(im)

def line(d,pts,c,width=1):
 d.line([(round(x),round(y)) for x,y in pts],fill=c,width=width)

def plate(im,p,face,edge=False):
 w,h=im.size;d=fill(im,p,3 if face=='up' else 1 if face=='down' else 2)
 # Only the actual top fold; no riveted border around every cuboid.
 if h>5 and face in ('north','west','east'):
  d.rectangle((0,0,w-1,1),fill=p[3 if edge else 2])
  d.line((0,h-1,w-1,h-1),fill=p[1])
 if edge and w>12 and h>10:
  line(d,[(2,3),(w//3,3),(w//3+2,5)],p[3])
 return d

def beast(n,j,c,f,im,role,mat):
 w,h=im.size
 if n=='beast_mask':
  if j in (3,6):
   # Existing lateral eye volumes: dark socket, ivory amber iris and a pupil.
   d=fill(im,[INK]);
   if f in ('east','west'):
    d.rectangle((1,1,max(1,w-2),max(1,h-2)),fill=(133,139,93))
    cx=w//3 if f=='west' else w*2//3
    d.rectangle((cx,1,min(w-2,cx+1),max(1,h-2)),fill=(233,212,139))
    d.point((cx,1),fill=(39,44,35))
    d.line((0,0,w-1,0),fill=(64,62,44))
   return
  if j in (4,7,5,8):
   p=HORN if j in (5,8) else BRONZE;plate(im,p,f,True);return
  p=GOLD if j in (0,2) else SCALE;d=plate(im,p,f,True)
  if j==0:
   if f=='north':
    # Narrow imperial brow, converging toward the eyes; center stays quiet.
    line(d,[(2,4),(6,4),(8,6)],p[0],2)
    line(d,[(w-3,4),(w-7,4),(w-9,6)],p[0],2)
    line(d,[(w//2,2),(w//2,6)],p[4]);d.rectangle((w//2-1,8,w//2+1,10),fill=p[1])
   elif f in ('east','west'):
    line(d,[(2,4),(w-5,4),(w-2,6)],p[0],2)
    line(d,[(2,2),(w-5,2)],p[3])
    line(d,[(w//2,h-5),(w-3,h-5)],p[1])
  elif j==1:
   # Closed upper muzzle and lower lip are readable, but there is no jaw bone.
   if f=='north':
    d.rectangle((0,h-3,w-1,h-1),fill=(74,76,56))
    for x in (2,w-5):
     d.rectangle((x,2,x+2,4),fill=INK);d.point((x+1,1),fill=(131,142,109))
    line(d,[(1,h-4),(w//3,h-4),(w//3+1,h-3),(w*2//3,h-3),(w*2//3+1,h-4),(w-2,h-4)],INK)
    line(d,[(4,h-1),(w-5,h-1)],(142,147,112))
   elif f in ('east','west'):
    d.rectangle((0,h-3,w-1,h-1),fill=(74,76,56))
    line(d,[(1,h-4),(w-3,h-4),(w-2,h-6)],INK)
  return
 if n=='pole_turret':
  if j>=2:
   d=plate(im,palette('46504b','72776b','abb19d','d1d3b8','ece8cf'),f,True)
   if f in ('north','up') and w>2:d.line((0,0,w-1,0),fill=(229,226,194))
  else:plate(im,IRON if j==1 else BRONZE,f)
  return
 if mat=='gold':
  p=GOLD if n=='beast_body' and j==1 else BRONZE
  d=plate(im,p,f,n=='beast_body')
  if n=='beast_body' and j==1 and f in ('east','west'):
   line(d,[(w-3,4),(w-3,h-6),(w-7,h-2)],p[1],2)
  return
 if mat=='scale':
  # Quiet limbs, directional groups on the body; no equally loud all-over scales.
  d=fill(im,SCALE,1 if f=='down' else 2)
  stride=9 if n=='beast_body' else 12
  for y in range(5,h-2,stride):
   for x in range(3+(y//stride%2)*5,w-3,12):
    line(d,[(x,y),(x+2,y+2),(min(w-2,x+6),y+2)],SCALE[1])
  if n=='beast_neck' and f!='down':line(d,[(2,2),(max(2,w-3),2)],SCALE[3])

def emperor(n,j,c,f,im,role,mat):
 w,h=im.size
 if n=='imperial_mask':
  if j==1:
   d=fill(im,[INK]);d.line((0,0,w-1,0),fill=(146,179,158))
   if w>=4:d.point((1,0),fill=(221,228,194));d.point((w-2,0),fill=(221,228,194))
  else:
   d=fill(im,BONE,4 if f=='north' else 3)
   if f=='north':
    d.rectangle((0,2,w-1,4),fill=(53,65,59));d.line((2,h-3,w-3,h-3),fill=(89,87,70))
    d.line((w//2,5,w//2,6),fill=BONE[1]);d.point((w-2,h-2),fill=BONE[2])
  return
 if n=='regalia':plate(im,GOLD,f,True);return
 if n=='coffin':
  if mat=='gold':plate(im,BRONZE,f)
  elif j==0:
   # The inner wall is visibly behind the pale remains, not the exterior lacquer.
   p=palette('252e2c','36403b','444b40','59604d','79745b');d=fill(im,p,1)
   if f=='north' and w>12:
    for x in (4,w-6):line(d,[(x,5),(x,h-5)],p[2])
  else:
   p=palette('342a28','4b322b','654332','805c40','a37b50');d=fill(im,p,2 if f=='up' else 1)
   if w>7 and h>10:
    line(d,[(w//3,3),(w//3,h-5)],p[2]);line(d,[(w*2//3,9),(w*2//3,h-3)],p[0])
  return
 if n.startswith('lid'):
  if j>0:plate(im,BRONZE,f);return
  # Keep only the original sparse seal; quiet its repeated gold strokes.
  mapping={(177,151,74):(139,107,54),(210,188,108):(171,137,75)}
  im.putdata([mapping.get(p,p) for p in im.getdata()]);return
 if n=='relic':
  if j==0:
   p=palette('303f39','546b58','7e9478','aaba95','cfceb0');d=fill(im,p,2)
   if f=='north':
    d.rectangle((w//2-1,0,w//2+1,h-1),fill=p[0])
    for y in (5,11,17):line(d,[(1,y),(w-2,y+1)],p[3])
  else:plate(im,BONE,f)
  return
 if n=='dragon_skull':
  if j in (2,4):
   d=fill(im,[INK]);
   if f in ('west','east') and w>=4:
    d.line((1,h//2,w-2,h//2),fill=(129,157,125));d.point((w//3,h//2),fill=(203,209,169))
  else:
   d=plate(im,BONE,f,True)
   if j==0 and f in ('east','west'):
    d.polygon([(1,2),(w-3,2),(w-3,5),(w//2,6),(1,4)],fill=BONE[0])
    line(d,[(2,1),(w-3,1)],BONE[3])
   elif j==1 and f=='north':
    for x in (2,w-4):d.rectangle((x,2,x+1,4),fill=BONE[0])
   if f=='down':im.paste(BONE[0],(0,0,w,h))
  return
 if n=='dragon_jaw':
  d=plate(im,BONE,f,True)
  if f=='up':fill(im,palette('3b443c','556153','7e8c72'),0)
  return
 if n.startswith('dragon_spine') or n=='coil_base':
  if mat=='iron':plate(im,IRON,f);return
  p=palette('52594e','737c67','969d81','b4b89a','d0ceb0');d=fill(im,p,2 if f!='down' else 1)
  if w>5 and h>5:
   d.rectangle((0,h-2,w-1,h-1),fill=p[1]);line(d,[(2,2),(max(2,w//2),2)],p[3])
  return
 if n=='edict_arm':
  if j==2:plate(im,[(39,63,56),(60,91,72),(103,140,106),(149,178,135),(191,205,169)],f,True)
  else:plate(im,BONE,f)

def furnace(n,j,c,f,im,role,mat):
 w,h=im.size
 if n=='inset_face':
  if j==0:
   d=plate(im,IRON,f)
   if f=='north':d.rectangle((1,2,w-2,h-3),fill=IRON[0]);d.line((2,1,w-3,1),fill=COPPER[3])
  else:
   d=fill(im,[FIRE[1]]);d.rectangle((1,0,max(1,w-2),h-1),fill=FIRE[3]);d.point((w//2,0),fill=FIRE[4])
  return
 if n=='furnace' and j==7:
  d=fill(im,FIRE,0)
  # The hearth is brightest at pressure vents behind the two gaps in the grate.
  # A single coherent firebed, not random glowing rectangles across the armor.
  if f=='north':
   for x0 in (3,11):
    d.polygon([(x0,h-2),(x0,6),(x0+2,3),(x0+4,6),(x0+4,h-2)],fill=FIRE[2])
    d.rectangle((x0+1,7,x0+3,h-4),fill=FIRE[3]);d.line((x0+2,9,x0+2,h-6),fill=FIRE[4])
   d.rectangle((1,h-4,w-2,h-2),fill=FIRE[2]);d.line((2,h-3,w-3,h-3),fill=FIRE[3])
  return
 if n in ('hammer_-1','hammer_1'):
  if j==3:
   # One contiguous battered striking slab; remove the previous concentric badge.
   p=palette('424b4e','697577','9ea9a5','c8cebf','e2dfc9');d=fill(im,p,2)
   if f=='north':
    d.line((0,0,w-1,0),fill=p[3]);d.line((0,h-1,w-1,h-1),fill=p[1])
    line(d,[(2,h//2+1),(w//2,h//2),(w-2,h//2)],p[1])
    line(d,[(w//3,2),(w//3+1,3),(w//3+4,3)],p[3])
  elif j==1 and f=='down':
   # At the slam contact pose this underside meets the ground. Treat the whole
   # load-bearing sole as forged steel, distinct from the copper side casing.
   p=palette('414c50','67777a','929f9d','bcc4b7','d5d6c1');d=fill(im,p,2)
   d.rectangle((0,0,w-1,1),fill=p[1]);d.rectangle((0,h-2,w-1,h-1),fill=p[1])
   d.polygon([(2,2),(w-3,2),(w-5,5),(5,5),(3,h-5),(1,h-3)],fill=p[3])
   line(d,[(w//3,h//3),(w//3+2,h//3+1),(w-4,h//3+1)],p[1])
   line(d,[(4,2*h//3),(w//2,2*h//3),(w//2+2,2*h//3-1)],p[3])
  elif j==2:
   d=plate(im,IRON,f,True)
   if f=='north' and w>8:d.line((2,2,w-3,2),fill=IRON[3])
  else:plate(im,COPPER if j==1 else IRON,f,j==1)
  return
 if n=='furnace' and j>=11:
  # Stacks stay secondary: no bright copper rings or false lens rivets.
  plate(im,palette('353737','454b49','61695e','7c826f','999b85'),f);return
 if mat=='iron' or mat=='steel':
  d=plate(im,IRON,f)
  if role=='vent' and w>2:
   d.line((0,0,0,h-1),fill=IRON[1]);d.line((w-1,1,w-1,h-2),fill=IRON[3])
  if role=='piston' and w>4:d.line((w//2,1,w//2,h-2),fill=IRON[3])
  return
 if mat=='copper':
  d=plate(im,COPPER,f,n.startswith('hammer_'))
  # Oxidation belongs on the rear body seam only, never stamped onto every panel.
  if n=='furnace' and j==0 and f=='south' and w>20:
   d.line((w-4,4,w-4,h-4),fill=COPPER[1])
   d.rectangle((w-5,h-6,w-3,h-3),fill=(62,80,64))
  if n.startswith('hammer_piston') and min(w,h)>5:
   d.rectangle((1,1,w-2,3),fill=IRON[1]);d.line((2,4,w-3,4),fill=COPPER[3])

def paint_focus(index,n,j,c,face,im,role,mat):
 if index==5:beast(n,j,c,face,im,role,mat)
 elif index==0:emperor(n,j,c,face,im,role,mat)
 elif index==7:furnace(n,j,c,face,im,role,mat)
