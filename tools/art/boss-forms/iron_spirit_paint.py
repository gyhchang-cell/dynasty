"""Two authored material treatments on approved cuboids, in physical face coordinates.
No random marks, external pixels, geometry changes, shared box-border recipe or bloom.
"""
from PIL import ImageDraw

def colors(*s):return [tuple(bytes.fromhex(x)) for x in s]
WAR=colors('30343c','454c55','62707a','87949a','b1bab8')
INNER=colors('272c34','343b43','4a525a','646c70','828b87')
PAINT=colors('392b30','55333a','774348','985e59','b88270')
EDGE=colors('39434b','606e75','8e9fa2','bcc9c3','dbe0cc')
BIND=colors('30343b','44494e','5b6467','7c8482','9ca49b')
WOOD=colors('372b28','54382d','754d34','966a46','b18b60')
BONE=colors('505a5e','7f8a88','aab2a4','cbd0b9','e3e2ca')
HIDE=colors('414044','615953','83796a','a09781','bbb09a')
BRASS=colors('413830','605039','88704a','ad945f','c9b580')
FACES={
 'north':[(0,1,0),(1,1,0),(0,0,0)],'south':[(1,1,1),(0,1,1),(1,0,1)],
 'west':[(1,1,0),(1,1,1),(1,0,0)],'east':[(0,1,1),(0,1,0),(0,0,1)],
 'up':[(0,1,1),(1,1,1),(0,1,0)],'down':[(0,0,0),(1,0,0),(0,0,1)]}

def base(im,p,k):
 im.paste(p[k],(0,0,*im.size));return ImageDraw.Draw(im)
def path(d,pts,col,width=1):d.line([(round(x),round(y)) for x,y in pts],fill=col,width=width)
def face_point(c,f,x,y,w,h):
 a,b,d=FACES[f];u=(x+.5)/w;v=(y+.5)/h
 return tuple(c['origin'][i]+c['size'][i]*(a[i]+(b[i]-a[i])*u+(d[i]-a[i])*v) for i in range(3))
def field(im,c,f,paint):
 w,h=im.size
 for y in range(h):
  for x in range(w):im.putpixel((x,y),paint(*face_point(c,f,x,y,w,h)))

def wrapped_grip(im,f):
 w,h=im.size;d=base(im,HIDE,1 if f in ('down','south') else 2)
 # A functional wrapping, not armor drawn as fabric. Diagonals continue along shaft.
 for y in range(2,h,5):path(d,[(0,y),(w-1,y-2)],HIDE[1]);path(d,[(0,y+1),(w-1,y-1)],HIDE[3])
 return d

def blade(im,c,f,cut_right,short_tip=False):
 w,h=im.size
 if f in ('north','south'):
  # Same physical cutting side on both faces: south reverses U.
  right=cut_right if f=='north' else not cut_right
  d=base(im,EDGE,1)
  poly=[(w-1,0),(w-1,h-1),(w-4,h-1),(w-3,h//2),(w-4,2)] if right else [(0,0),(0,h-1),(3,h-1),(2,h//2),(3,2)]
  d.polygon(poly,fill=EDGE[3])
  shoulder=[(w-5,0),(w-4,h//2),(w-5,h-1)] if right else [(4,0),(3,h//2),(4,h-1)]
  path(d,shoulder,EDGE[2])
  edge=w-1 if right else 0;d.line((edge,1,edge,h-2),fill=EDGE[4])
  # Two blade-edge contact nicks; spine and broad blade retain quiet dark steel.
  if h>12:
   for yy in (h//3,h*3//4):
    xx=w-2 if right else 1;d.point((xx,yy),fill=EDGE[1]);d.point((edge,yy+1),fill=EDGE[2])
   sx=1 if right else w-2;path(d,[(sx,3),(sx,h//2),(sx+1 if right else sx-1,h//2+2)],EDGE[0])
 elif f in ('east','west'):
  # The physical +/-X face is the edge, never both long sides.
  is_edge=(f=='west')==cut_right;base(im,EDGE,3 if is_edge else 0)
 else:base(im,EDGE,2 if short_tip and f=='up' else 1)

def war(n,j,c,f,im,role,mat):
 w,h=im.size
 if n=='broken_helm':
  if j==2:
   d=base(im,INNER,0)
   if f=='north':
    d.line((0,0,w-1,0),fill=(166,143,92));d.point((1,0),fill=(230,207,142));d.point((2,1),fill=(119,98,66))
  elif j==1:
   # Faceplate folds point inward to a deep visor slit. No white perimeter.
   d=base(im,WAR,2)
   if f=='north':
    d.polygon([(0,0),(2,0),(3,2),(4,2),(5,0),(7,0),(7,2),(5,4),(2,4),(0,2)],fill=WAR[3])
    d.rectangle((1,3,6,4),fill=INNER[0])
    d.polygon([(0,4),(2,5),(3,7),(0,7)],fill=WAR[1]);d.polygon([(7,4),(5,5),(4,7),(7,7)],fill=WAR[1])
    d.line((3,5,4,5),fill=WAR[3]);d.line((3,6,4,7),fill=WAR[2])
  else:
   d=base(im,WAR,1 if f in ('south','down') else 2)
   if f in ('north','up'):
    # Broad, worn former crest, tied to the existing red battle cloth palette.
    d.rectangle((w//2-2,0,w//2+1,h-1),fill=PAINT[1]);d.line((w//2-1,0,w//2-1,h//2),fill=PAINT[2])
    if f=='north':d.rectangle((0,h-3,w-1,h-1),fill=INNER[0])
   elif f in ('east','west'):
    d.polygon([(0,0),(w-1,0),(w-1,2),(w//2,3),(1,2)],fill=WAR[2])
    d.rectangle((0,h-3,w-1,h-1),fill=INNER[1]);path(d,[(2,h-4),(w-3,h-4)],WAR[1])
  return
 if n=='war_frame':
  if j<3:
   # Inside bearing beams: distinguish from the shell, without painting fake cavities.
   d=base(im,INNER,1 if f in ('south','down') else 2)
   if min(w,h)>3:
    d.rectangle((0,0,w-1,2),fill=INNER[0]);d.line((w//2,3,w//2,h-3),fill=INNER[3])
  else:
   # The existing curved ribs are armor overlaps, not six identical glowing bars.
   d=base(im,WAR,1 if f in ('south','down') else 2)
   if f=='north':
    d.rectangle((0,h-4,w-1,h-1),fill=INNER[1]);d.line((1,2,w-2,2),fill=WAR[3])
    if j in (5,8):d.rectangle((0,h//3,w-1,h//3+2),fill=PAINT[1])
  return
 if n=='war_core':
  p=colors('342d32','543a33','82523a','ae7a4b','d0af71');d=base(im,p,1)
  if f in ('north','east','west'):
   # One restricted ember flow down the extant spirit core, not a metal battery stripe.
   d.polygon([(w//2-1,1),(w//2+1,3),(w//2,5),(w//2+2,7),(w//2,h-2),(w//2-2,6)],fill=p[2]);d.line((w//2,3,w//2,6),fill=p[3])
  return
 if n=='breach_arm':
  if j==1:
   d=base(im,INNER,1 if f=='down' else 2)
   if h>6:d.rectangle((0,h//2-1,w-1,h//2+1),fill=HIDE[1]);d.line((1,h//2+2,w-2,h//2+2),fill=HIDE[2])
  elif j in (0,2):
   # Paint belongs to the whole distorted arm. Its strip follows shared model X,
   # crossing the front/top/side islands, with wear removed at the working fist.
   def armor(x,y,z):
    shade=2 if f not in ('south','down') else 1
    # recessed inner facing is darker than the exposed outer guard.
    if f=='west':shade=1
    col=WAR[shade]
    center=-28 if j==0 else -31
    # Shoulder retains a broad stepped livery field; lower gauntlet retains only
    # a remnant near the cuff. Neither reads as a new factory-painted racing stripe.
    stripe=x<(-23 if y>49 else -25 if y>45 else -26 if y>40 else -29) if j==0 else abs(x-center)<(3.5 if y>29 else 2.5)
    if j==2 and y<20:stripe=False
    if stripe:
     tone=2 if f in ('north','up') else 1
     col=PAINT[tone]
     # Two authored areas where old paint peels at exposed corners/contact.
     if (j==0 and 41<y<44 and -33<x<-29) or (j==0 and y>52 and -31<x<-28) or (j==2 and 23<y<26 and x>center):col=WAR[2]
    if j==2 and y<18:col=WAR[3 if f=='north' else 2]
    return col
   field(im,c,f,armor);d=ImageDraw.Draw(im)
   if j==0 and f=='north':
    # A single old armor overlap crosses the lower third, not a box border.
    path(d,[(0,h-5),(7,h-5),(10,h-3),(w-1,h-3)],WAR[1])
    path(d,[(1,h-4),(6,h-4)],WAR[3])
    # The paint isn't a new heraldic symbol: a worn existing red livery field.
    path(d,[(5,3),(7,3),(8,4)],WAR[3])
   elif j==0 and f in ('east','west'):
    path(d,[(0,h-5),(w-1,h-5)],WAR[1]);d.line((3,h-4,w//2,h-4),fill=WAR[2])
   elif j==2 and f=='north':
    # Abrasion belongs to the knuckle contact zone across the entire broad gauntlet.
    path(d,[(2,h-4),(8,h-4),(10,h-5),(17,h-5)],WAR[4])
    path(d,[(7,h-3),(12,h-3),(14,h-4)],WAR[1])
    d.polygon([(0,h-8),(3,h-6),(3,h-1),(0,h-1)],fill=INNER[2])
   elif j==2 and f=='up':
    d.rectangle((0,0,w-1,2),fill=INNER[1]);path(d,[(3,4),(w-4,4)],WAR[1])
  else:
   d=base(im,INNER,2 if f!='down' else 1)
   if f in ('north','east','west'):
    d.rectangle((0,h-3,w-1,h-1),fill=WAR[3]);d.line((0,h-4,w-1,h-4),fill=WAR[1])
  return
 if n=='war_glaive':
  if j in (1,2):blade(im,c,f,True,j==2)
  elif j==0:
   wrapped_grip(im,f)
   # Only the grip below the existing guard is wrapped; the blade tang above is iron.
   for y in range(h):
    for x in range(w):
     _,py,_=face_point(c,f,x,y,w,h)
     if py>42:im.putpixel((x,y),EDGE[0 if f in ('south','down') else 1])
  else:
   d=base(im,BRASS,2 if f!='down' else 1)
   if f=='north':d.line((1,0,w-2,0),fill=BRASS[3])
  return
 if n=='weapon_arm':
  d=base(im,INNER if j==0 else WAR,2 if f!='down' else 1)
  if j==1 and f in ('north','east','west'):
   d.rectangle((0,h-4,w-1,h-2),fill=INNER[1]);d.line((1,h-5,w-2,h-5),fill=WAR[3])
  return
 if n=='right_grip':
  d=base(im,INNER,2)
  if f in ('north','east','west'):
   d.rectangle((0,0,w-1,1),fill=WAR[2]);d.line((1,h-2,w-2,h-2),fill=HIDE[2])
  return
 if n=='war_banner':
  d=base(im,PAINT,1 if f!='north' else 2)
  if f in ('north','south'):
   d.rectangle((0,0,1,h-1),fill=PAINT[1]);d.line((w-2,4,w-2,h-5),fill=PAINT[3])
  return
 if n=='old_blades':
  d=base(im,INNER,2)
  if w>2 and f=='north':d.line((0,1,0,h-4),fill=WAR[2])
  return
 if n.startswith('support'):
  d=base(im,INNER if j in (0,2) else WAR,1 if f in ('down','south') else 2)
  if j==1 and f=='north':d.polygon([(1,0),(w-2,0),(w-2,2),(w//2,4),(1,2)],fill=WAR[1])
  if j==3:
   if f=='north':d.rectangle((0,h-2,w-1,h-1),fill=INNER[1])
   if f=='up':path(d,[(2,h//2),(w//2,h//2),(w//2+1,h//2+1),(w-3,h//2+1)],INNER[2])
  return
 base(im,INNER,2)

def penal_wood(im,c,f,j):
 w,h=im.size
 # Growth bands run along local X across the two halves of the same penal beam.
 if f in ('east','west'):
  d=base(im,WOOD,2)
  d.line((2,h-3,2,2,w-3,2),fill=WOOD[1]);d.line((5,h-2,5,5,w-2,5),fill=WOOD[3])
  return
 def grain(x,y,z):
  v=z if f in ('up','down') else y
  tone=2 if f not in ('down','south') else 1
  # Finite, wide growth bands. No random pixels or tiled border around the timber.
  bend=1 if x<-21 else 0 if x<11 else -1
  if int(v+bend)%9 in (0,1):tone=max(1,tone-1)
  if int(v+bend)%9==4 and -24<x<24:tone=min(3,tone+1)
  if f=='north' and (24<abs(x)<27):tone=1 # Compression beside the actual iron straps.
  return WOOD[tone]
 field(im,c,f,grain);d=ImageDraw.Draw(im)
 if f=='north' and j in (0,2):
  # Split initiates near the inner end, opposite the iron strap; left/right differ.
  if j==0:
   path(d,[(w-1,5),(w-5,5),(w-7,6),(w-11,6)],WOOD[0]);path(d,[(w-5,4),(w-7,4)],WOOD[3])
  else:path(d,[(0,3),(4,3),(6,4),(10,4),(12,5)],WOOD[0]);path(d,[(4,2),(8,2)],WOOD[3])

def bound(n,j,c,f,im,role,mat):
 w,h=im.size
 if n=='bound_head':
  if j<16:
   # Thick dark chain, rubbing faces only; isolated chain pixels aren't white rivets.
   d=base(im,BIND,2 if f in ('north','up') else 1)
   if f=='up':d.line((0,0,w-1,0),fill=BIND[3])
  elif j==16:
   d=base(im,BONE,2 if f!='north' else 3)
   if f=='north':
    # Actual existing eyes sit at x1..4 / 11..14, y5..7 beneath the helmet brim.
    d.rectangle((0,0,w-1,4),fill=BONE[2])
    d.polygon([(0,5),(3,5),(5,6),(5,8),(2,8),(0,7)],fill=BONE[0])
    d.polygon([(15,5),(12,5),(10,6),(10,8),(13,8),(15,7)],fill=BONE[0])
    d.polygon([(0,8),(2,9),(3,11),(2,13),(0,12)],fill=BONE[1])
    d.polygon([(15,8),(13,9),(12,11),(13,13),(15,12)],fill=BONE[1])
    d.rectangle((7,7,8,9),fill=BONE[2]);d.line((7,10,8,10),fill=BONE[0])
    # Clenched mouth, broad cheek planes and clear lower jaw, not a black bib.
    path(d,[(4,13),(5,12),(6,11),(9,11),(10,12),(11,13)],BONE[0],2)
    d.line((6,12,9,12),fill=BONE[2]);d.point((6,12),fill=BONE[4]);d.point((9,12),fill=BONE[3]);d.rectangle((5,14,10,15),fill=BONE[2])
   elif f in ('east','west'):
    d.rectangle((0,0,w-1,4),fill=BONE[1]);d.polygon([(0,8),(4,10),(4,13),(w-1,13),(w-1,15),(0,15)],fill=BONE[1])
    d.line((2,7,3,9),fill=BONE[3])
   elif f=='south':
    d.rectangle((0,0,w-1,5),fill=BONE[1]);d.rectangle((3,h-3,w-4,h-1),fill=BONE[1])
  elif j==17:
   # Extant heavy helmet is muted, with a rubbed lower lip near the chain/head only.
   d=base(im,BIND,1 if f!='up' else 2)
   if f=='north':d.line((5,h-2,w-6,h-2),fill=BIND[2])
   elif f in ('east','west'):d.rectangle((0,h-2,w-1,h-1),fill=BIND[0])
  else:
   d=base(im,BONE,0)
   if f=='north':
    # Sloped upper lids aim inward; iris is a subdued narrow bone-grey glint.
    if j==18:d.line((0,0,1,0),fill=BONE[2]);d.point((2,1),fill=BONE[3]);d.point((3,2),fill=BONE[1])
    else:d.line((2,0,3,0),fill=BONE[2]);d.point((1,1),fill=BONE[3]);d.point((0,2),fill=BONE[1])
  return
 if n=='yoke':
  if j in (0,2,4):penal_wood(im,c,f,j)
  elif j in (1,3):
   d=base(im,BIND,1)
   if f=='north':
    d.rectangle((0,0,w-1,1),fill=BIND[2]);d.rectangle((1,h-4,w-2,h-3),fill=BIND[2])
    d.line((w//2,3,w//2,5),fill=(99,77,60)) # Old pin seat at the timber strap.
  elif j==5:base(im,BIND,1 if f!='up' else 2)
  else:
   d=base(im,BIND,1 if f in ('south','down') else 2)
   if f=='north' and w>3:d.line((w-2,2,w-2,h-3),fill=BIND[3])
  return
 if n=='blade_mount':
  if j==1:blade(im,c,f,False)
  else:
   d=wrapped_grip(im,f)
   if f in ('north','east','west'):
    d.rectangle((0,0,w-1,2),fill=BIND[2]);d.line((0,3,w-1,3),fill=BIND[3])
  return
 if n.startswith('giant_arm'):
  if j==0:
   d=base(im,BIND,1 if f!='up' else 2)
   if f in ('north','east','west') and h>8:
    d.rectangle((0,h//2-1,w-1,h//2+1),fill=HIDE[1]);d.line((1,h//2+2,w-2,h//2+2),fill=HIDE[2])
  else:
   # Penal arm plating: heavy dark fluted iron, distinct from red-lacquer war armor.
   d=base(im,BIND,2)
   if f=='north':
    d.polygon([(0,0),(3,0),(3,h-5),(1,h-2),(0,h-2)],fill=BIND[1])
    d.polygon([(w-1,0),(w-4,0),(w-4,h-5),(w-2,h-2),(w-1,h-2)],fill=BIND[1])
    path(d,[(w//2,3),(w//2,10)],BIND[3]);path(d,[(3,h-3),(w-4,h-3)],BIND[1])
   elif f in ('east','west'):d.rectangle((0,h-5,w-1,h-3),fill=BIND[1])
  return
 if n.startswith('forearm'):
  if j==0:
   # Existing broad forearm carries old binding straps over a dark body, not another box face.
   d=base(im,BIND,1 if f in ('down','south') else 2)
   if f in ('north','east','west'):
    for y in (h//3,h*2//3):
     d.rectangle((0,y,w-1,y+2),fill=HIDE[1]);d.line((1,y+3,w-2,y+3),fill=HIDE[2])
  elif j==1:
   d=base(im,BIND,2)
   if f=='north':
    # Hand guard reveals the bone finger roots in the next existing pieces.
    d.rectangle((0,h-4,w-1,h-1),fill=BIND[1]);d.line((2,2,w-3,2),fill=BIND[3])
    d.polygon([(2,3),(5,3),(5,6),(3,7),(2,6)],fill=HIDE[1])
   elif f=='up':d.rectangle((2,1,w-3,3),fill=BIND[1])
  else:
   # Bone/hide finger groups: dim roots, lengthwise dry ridges, worn joint tips.
   d=base(im,HIDE,2 if f in ('north','up') else 1)
   if f=='north':
    d.rectangle((0,0,w-1,1),fill=HIDE[1]);d.line((1,2,1,h-2),fill=BONE[2]);d.point((1,h-1),fill=BONE[3]);d.point((0,3+(j%2)),fill=HIDE[1])
   if f=='up':d.line((0,1,w-1,1),fill=HIDE[3])
  return
 if n.startswith('drag_runner'):
  d=base(im,BIND,1 if f in ('down','south') else 2)
  if j==0:
   # Long dragged remnant, rubbed below; no paired boxed shin badges.
   if f=='north':d.rectangle((0,h-5,w-1,h-2),fill=BIND[1]);d.line((w//2,4,w//2,h//2),fill=BIND[3])
  elif j==1 and f=='north':d.line((0,h-2,w-1,h-2),fill=BIND[1])
  elif j>1 and f=='up':d.line((0,0,w-1,0),fill=BIND[3])
  return
 base(im,BIND,2)
