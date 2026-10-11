"""Original part-directed pixel painting, 16 texels/block. No external artwork input.

Each physical face has its own island. Material ownership, local grain axes,
anatomical colour regions and focal marks are authored below, not randomized.
"""
import math
from PIL import Image, ImageDraw

PALETTES={
 'iron':['273039','3c4851','55636b','78858b','a0a9a7'],
 'steel':['343c44','52616a','71838a','98a9ac','c1ccca'],
 'wood':['3a2922','624232','855b3d','a77a50','c39b66'],
 'lacquer':['302629','482f2b','664133','8b6146','af8b5b'],
 'copper':['493b36','775544','a27859','c69870','dfc398'],
 'gold':['554831','826836','b1974a','d2bc6c','ecdc9d'],
 'bone':['706b5c','a49b80','cbc1a0','e1d8bb','eee6ce'],
 'purple':['29263b','41354e','59445f','775879','9d7797'],
 'silk':['402630','653743','8f4b59','b66b76','d39497'],
 'jade':['263f3d','3e635b','638a75','93b099','bfccb0'],
 'porcelain':['87847e','b9b6a9','dddacf','efeada','f6f1e4'],
 'fur':['a0a9aa','bec4c1','d9ddd4','e9eadd','f5f1e3'],
 'darkfur':['353742','555864','767b86','999faa','b9bdc1'],
 'scale':['293f3c','3f5b4d','65805b','92a276','b8bd8c'],
 'ember':['392d32','63383a','a35338','d88a48','f2c77c'],
 'flesh':['3b3c38','616458','858b73','a5ad8d','c9c8a7'],
}
COLORS={k:[tuple(bytes.fromhex(v)) for v in vs] for k,vs in PALETTES.items()}
# UV top-left, top-right, bottom-right, bottom-left, in raw Bedrock coordinates.
# Verified against GeckoLib 1.20.1 VertexSet + GeoQuad !mirror U swap.
CORNERS={
 'north':[(0,1,0),(1,1,0),(1,0,0),(0,0,0)],
 'south':[(1,1,1),(0,1,1),(0,0,1),(1,0,1)],
 'west':[(1,1,0),(1,1,1),(1,0,1),(1,0,0)],
 'east':[(0,1,1),(0,1,0),(0,0,0),(0,0,1)],
 'up':[(0,1,1),(1,1,1),(1,1,0),(0,1,0)],
 'down':[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]}


def recipe(index,n,j,c):
 """Actual component assignments. A beam and its hinge never share an island."""
 m=c['_material'];axis=max(range(3),key=lambda a:c['size'][a]);role='plate'
 if index==6:
  mat='fur';role='coat'
  if n in ['forehead_knot','silk_knot']:mat='silk';role='knot'
  elif n=='fox_body' and j==2:mat='darkfur';role='saddle'
  elif n=='fox_head':
   if j==2:mat='darkfur';role='nose'
   elif j in [3,6]:mat='darkfur';role='eye'
   elif j in [4,7]:mat='darkfur';role='ear'
   elif j in [5,8]:mat='fur';role='ear_tip'
   else:role='face' if j==0 else 'muzzle'
  elif n.endswith('_sole'):mat='darkfur';role='paw'
  elif n.startswith('tail_'):role='tail_'+n.split('_')[-1] if j==0 else 'tail_end'
  elif n.startswith(('front_','rear_')):role='leg'
  elif n=='fox_neck':role='ruff'
  return mat,role,1 if c.get('rotation') else axis
 if index==4:
  if n.endswith('_sole'):mat='iron';role='shoe'
  elif n=='chassis':mat='wood' if j in [1,2,3,4,5] else 'iron';role='deck' if j==1 else 'beam' if j>=2 else 'housing'
  elif n.startswith('outrigger'):mat='copper' if j==0 else 'wood';role='hinge' if j==0 else 'beam'
  elif n.startswith('link_'):mat=['copper','wood','iron'][j];role=['hinge','beam','shoe'][j]
  elif n.startswith('manipulator'):mat='wood' if j==0 else 'copper';role='beam' if j==0 else 'hinge'
  elif n.startswith('tool_'):mat='wood' if j==0 else 'steel';role='beam' if j==0 else 'tool'
  elif n=='pilot':mat=['copper','jade','iron'][j];role=['mask_case','core','eye'][j]
  elif n=='drive_shaft':mat='steel';role='shaft'
  else:mat='copper' if j==0 else 'iron';role='boiler' if j==0 else 'vent'
  return mat,role,axis
 if index==0:
  mat=['iron','lacquer','bone','jade'][m]
  if n=='coffin':
   mat='lacquer' if j in [0,1,3] else 'gold';role='coffin_panel' if j==0 else 'rail'
  elif n.startswith('lid'):mat='lacquer' if j==0 else 'gold';role='imperial_lid' if j==0 else 'inlay'
  elif n=='relic':mat='flesh' if j==0 else 'bone';role='corpse' if j==0 else 'rib'
  elif n=='regalia':mat='gold';role='crown'
  elif n=='imperial_mask':mat='bone' if j==0 else 'jade';role='mask' if j==0 else 'eye'
  elif n=='edict_arm':mat='bone' if j<2 else 'jade';role='bone' if j<2 else 'seal'
  elif n.startswith('dragon_spine'):mat='bone' if m==2 else 'iron';role='joint' if j==1 else 'bone'
  elif n=='dragon_skull':role='skull' if j==0 else 'bone'
  else:role='bone'
 elif index==1:
  mat=['iron','purple','gold','porcelain'][m];role='cloth' if m==1 else 'trim' if m==2 else 'mask' if m==3 else 'interior'
  if n=='mask':role='mask' if j==0 else 'cheek' if j>=4 else 'eye';mat='porcelain' if j in [0,4,5,6] else 'iron'
  elif n.startswith('curtain_fan'):role='fan' if j==0 else 'brocade'
  elif n.startswith('sleeve'):role='sleeve' if m==1 else 'hem'
  elif n.startswith('fingers'):role='bone'
 elif index==2:
  mat=['iron','steel','silk','steel'][m];role='battle_plate' if m==1 else 'frame'
  if n=='war_core':mat='ember';role='war_core'
  elif n=='war_banner':role='banner'
  elif n=='broken_helm':role='mask' if j==1 else 'eye' if j==2 else 'helm';mat='ember' if j==2 else mat
  elif n=='war_glaive':role='blade' if j in [1,2] else 'shaft';mat='copper' if j==3 else mat
  elif n=='breach_arm' and j in [0,2]:role='breach_plate'
 elif index==3:
  mat='iron';role='chain'
  if n=='yoke':
   if j in [0,2,4]:mat='wood';role='yoke'
   elif m==1:mat='steel';role='plate'
  elif n.startswith('giant_arm'):mat='steel';role='battle_plate' if j==1 else 'joint'
  elif n.startswith('forearm'):mat='bone' if m==2 else 'steel';role='bone' if m==2 else 'battle_plate'
  elif n=='bound_head':
   if j==16:mat='flesh';role='head'
   elif j==17:mat='iron';role='helm'
   elif j>17:mat='ember';role='eye'
  elif n=='blade_mount':mat='steel';role='blade'
  elif n.startswith('drag_runner') and j==0:mat='steel';role='battle_plate'
 elif index==5:
  mat=['scale','gold','jade','bone'][m];role='scales' if m==0 else 'gold_plate'
  if n.startswith('dorsal'):role='dorsal'
  elif n=='beast_mask':role='mask' if j==0 else 'muzzle' if j==1 else 'eye' if m==2 else 'gold_plate'
  elif n in ['weapon_saddle','pole_turret']:mat='iron' if m==0 else 'gold';role='blade' if j>=2 else 'saddle'
  elif n.endswith('_sole'):mat='gold';role='paw_plate'
 elif index==7:
  mat=['iron','copper','ember','steel'][m];role='cast_plate' if m==1 else 'joint'
  if n=='furnace':role='coal' if m==2 else 'shell' if j==0 else 'vent' if m==0 else 'cast_plate'
  elif n=='inset_face':role='eye' if j==1 else 'helm'
  elif n.startswith('hammer_') and n in ['hammer_-1','hammer_1']:
   role=['shaft','hammer_shell','impact_rim','impact'][j]
  elif n.startswith('hammer_piston'):role='piston'
 else:raise ValueError(index)
 return mat,role,axis


def mark(d,points,color,width=1):
 d.line([(round(x),round(y)) for x,y in points],fill=color,width=width)


def wood(im,face,axis,role,c,variant):
 """Grain in local member coordinates; end grain only normal to its long axis."""
 w,h=im.size;p=COLORS['lacquer' if role in ['coffin_panel','imperial_lid','rail'] else 'wood'];d=ImageDraw.Draw(im)
 q=CORNERS[face];ua=q[1][axis]-q[0][axis];va=q[3][axis]-q[0][axis]
 if ua==va==0:
  im.paste(p[2],(0,0,w,h));d=ImageDraw.Draw(im)
  for inset in [2,5,9]:
   if min(w,h)>inset*2+2:d.line([(inset,h-1-inset),(inset,inset),(w-1-inset,inset),(w-1-inset,h-1-inset)],fill=p[1 if inset!=5 else 3])
  return
 # Draw on a canonical across-grain x / along-grain y canvas, then orient.
 across,along=(w,h) if va else (h,w);tile=Image.new('RGB',(across,along),p[2]);td=ImageDraw.Draw(tile)
 for k,x in enumerate(range(3,across-1,7)):
  bend=1 if (k+variant)%2 else -1;start=1+((k+variant)%3)*2;end=max(start,along-3-((k+variant)%2)*3)
  fork=along*(2+variant%3)//6
  pts=[(x,start),(x,fork),(x+bend,fork+2),(x+bend,end)]
  mark(td,pts,p[1]);mark(td,[(x+2,max(2,along//4)),(x+2,max(2,along//2))],p[3])
 # A single knot only on a large structural plank, not every narrow leg.
 if across>=18 and along>=26:
  x=across//3+variant%3;y=along*2//3;mark(td,[(x-2,y),(x,y-3),(x+2,y),(x,y+4),(x-2,y)],p[1])
 if role in ['beam','yoke','deck'] and across>=6 and along>=10:
  td.rectangle((0,0,across-1,1),fill=p[1]);td.rectangle((1,2,min(across-2,3),3),fill=p[3])
 if role=='imperial_lid' and across>8 and along>24:
  gold=COLORS['gold'];cx=across//2
  mark(td,[(cx-3,8),(cx+3,8),(cx+3,12),(cx-2,12),(cx-2,18),(cx+3,18)],gold[2]);mark(td,[(cx,5),(cx,22)],gold[3])
 if not va:tile=tile.transpose(Image.Transpose.TRANSPOSE)
 # Keep the grain's fixed root and end in the correct UV direction.
 if va<0:tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
 if ua<0:tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 im.paste(tile)


def metal(im,mat,role,face,variant):
 w,h=im.size;p=COLORS[mat];d=ImageDraw.Draw(im)
 # Broad quiet plate, one fold on a designated edge, not a perimeter box.
 if min(w,h)<3:return
 if face in ['up','north','west']:
  d.rectangle((0,0,w-1,min(h-1,1)),fill=p[3])
 if w>=5 and h>=5:
  if role in ['hinge','shaft','piston','joint']:
   cx,cy=w//2,h//2;r=max(2,min(w,h)//3)
   d.rectangle((cx-r,cy-r,cx+r,cy+r),fill=p[0]);d.rectangle((cx-r+1,cy-r+1,cx+r-1,cy+r-1),fill=p[1])
   d.rectangle((cx-1,cy-1,cx+1,cy+1),fill=p[3]);d.point((cx-1,cy-1),fill=p[4])
  elif role not in ['interior','chain','frame','vent'] and w>=9 and h>=9:
   # Recessed join only on wide plates, three pixels from the trailing edge.
   d.line((2,h-4,w-3,h-4),fill=p[1]);d.line((3,h-3,w-4,h-3),fill=p[3])
   for x in [3,w-5]:
    d.rectangle((x,3,x+1,4),fill=p[0]);d.point((x,3),fill=p[4])
  if role in ['battle_plate','breach_plate','impact','impact_rim','shoe','tool','blade']:
   # Deliberate scuff clusters at impact/ground contact, not random full-surface spots.
   marks=[(.20,.76,4),(.64,.81,3)] if role!='breach_plate' else [(.24,.31,7),(.51,.39,5),(.73,.72,4)]
   for u,v,l in marks:
    x=int(w*u);y=int(h*v);mark(d,[(x,y),(min(w-2,x+l),y),(min(w-2,x+l),y-1)],p[3]);d.point((x,y+1),fill=p[1])
  if role in ['boiler','cast_plate','shell','hammer_shell'] and w>=15:
   # Small oxidized area beside the seam; large copper field is left clean.
   patina=COLORS['jade'];d.polygon([(w-8,h-5),(w-3,h-5),(w-3,h-9),(w-5,h-9),(w-5,h-7),(w-8,h-7)],fill=patina[1])
  if role=='impact':
   d.rectangle((2,2,w-3,h-3),fill=p[3]);mark(d,[(3,h//2),(w-4,h//2-1)],p[1]);mark(d,[(w//2,3),(w//2+1,h-4)],p[2]);d.rectangle((3,3,5,4),fill=p[4])
 if role=='vent' and w>=6 and h>=8:
  for x in range(2,w-1,4):d.line((x,3,x,h-3),fill=p[0]);d.point((x+1,3),fill=p[3])
 if role in ['mask_case','crown','inlay','seal'] and w>7 and h>7:
  cx,cy=w//2,h//2;mark(d,[(cx-2,cy-3),(cx+2,cy-3),(cx+2,cy),(cx-2,cy),(cx-2,cy+3)],p[4])


def fox_paint(im,n,j,c,face,role,mat):
 w,h=im.size;p=COLORS[mat];d=ImageDraw.Draw(im)
 # Local surface coordinates avoid disconnected face-by-face coat patches.
 q=CORNERS[face];o=c['origin'];s=c['size']
 for y in range(h):
  for x in range(w):
   u=(x+.5)/w;v=(y+.5)/h;pos=[o[k]+s[k]*(q[0][k]+u*(q[1][k]-q[0][k])+v*(q[3][k]-q[0][k])) for k in range(3)]
   tone=2
   if role in ['coat','ruff','face','muzzle']:
    # Continuous shoulder/back -> side -> belly, stepped transition at real height.
    boundary=28+(2 if pos[2]<-9 else 0)-(1 if pos[2]>17 else 0)
    # Broad flank colour joins the ruff and belly; small steps follow the coat edge.
    fringe=(0,0,1,2,1,0)[int(abs(pos[2]))//3%6]
    tone=1 if pos[1]>35 else 2 if pos[1]>boundary+fringe else 3
    if role in ['face','muzzle']:tone=3 if pos[1]<40 else 2
    if face=='down':tone=3
   elif role=='saddle':tone=3 if face=='up' else 2
   elif role.startswith('tail_'):
    tone=2 if role=='tail_root' else 3
    if face in ['north','south','east','west']:
     local=1-v
     if role=='tail_mid' and local<.36:tone=2
     if role=='tail_tip' and local>.6:tone=4
   elif role=='leg':tone=2 if v<.5 else 3
   elif role in ['paw','nose','eye','ear']:tone=1
   im.putpixel((x,y),p[tone])
 d=ImageDraw.Draw(im)
 if role in ['coat','ruff','face','muzzle','saddle'] and min(w,h)>=10:
  # Sparse, hand-placed fur groups. Shoulder/back flow to rear, cheek flow to muzzle.
  horizontal=face in ['east','west'];tufts=[(.18,.27),(.47,.38),(.76,.29)] if role in ['coat','saddle'] else [(.22,.68),(.63,.75)]
  for u,v in tufts:
   x=int(w*u);y=int(h*v);tone=1 if role=='saddle' else 2
   if horizontal:mark(d,[(x,y),(x+3,y),(x+3,y+1),(x+6,y+1)],p[tone])
   else:mark(d,[(x,y),(x,y+3),(x+1,y+3),(x+1,y+5)],p[tone])
 if role.startswith('tail_') or role=='leg':
  if min(w,h)>=5:
   # Tapering chevrons point along the actual beam/root-to-tip axis.
   if face in ['north','south','east','west']:
    base=COLORS['fur'][2 if role!='tail_root' else 1]
    if role=='leg':
     mark(d,[(w//3,1),(w//3,h//3),(w//3+1,h//3),(w//3+1,h//2)],base)
    else:
     # One broken, tapered root stripe; not scattered grey islands on every face.
     x=max(1,w//4);d.polygon([(x,h-1),(x+3,h-1),(x+3,h*2//3),(x+2,h*2//3),(x+2,h//3),(x+1,h//3),(x+1,h//2),(x,h//2)],fill=base)
  if role=='tail_end' and face not in ['up','down']:
   red=COLORS['silk'];d.rectangle((0,h-3,w-1,h-2),fill=red[2]);d.point((w//2,h-2),fill=red[4])
 if role=='paw' and face=='north':
  for x in [2,w-3]:d.line((x,h-3,x,h-1),fill=COLORS['fur'][3])
 if role=='ear' and face=='north' and w>4:
  d.polygon([(2,h-2),(w-3,h-2),(w-3,3),(w//2,2),(2,4)],fill=COLORS['silk'][1]);d.line((w//2,4,w//2,h-4),fill=COLORS['silk'][3])
 if role=='eye' and face in ['east','west','north']:
  d.rectangle((max(0,w//3),max(0,h//2-1),min(w-1,w//3+2),min(h-1,h//2)),fill=COLORS['silk'][3]);d.point((min(w-1,w//3+1),max(0,h//2-1)),fill=COLORS['fur'][4])
 if role=='nose' and face=='north':
  d.line((2,1,max(2,w-3),1),fill=p[2]);d.point((w//2,h-1),fill=p[0])
 if role=='muzzle' and face in ['east','west']:
  mark(d,[(1,h-3),(w//2,h-3),(w//2+2,h-4)],COLORS['fur'][0])
 if role=='face' and face in ['east','west']:
  # Two restrained vermilion mask tears, not a human painted face.
  red=COLORS['silk'];x=w//3 if face=='east' else w*2//3
  mark(d,[(x,h//3),(x,h//3+3),(x+1,h//3+3),(x+1,h//3+5)],red[2])
 if role=='knot':cloth(im,'silk',role,face,0)


def cloth(im,mat,role,face,variant):
 w,h=im.size;p=COLORS[mat];d=ImageDraw.Draw(im)
 im.paste(p[1 if face=='down' or (face=='south' and role!='fan') else 2],(0,0,w,h));d=ImageDraw.Draw(im)
 if min(w,h)<3:return
 # Fold ridges follow fan/sleeve/cloth local long axis, no rings around every cube.
 for x in range(3,w-1,9):
  mark(d,[(x,1),(x,max(1,h//3)),(x+1,max(1,h//3+1)),(x+1,h-3)],p[1],2)
  if face!='down' and (face!='south' or role=='fan'):mark(d,[(x+3,2),(x+3,max(2,h*2//3))],p[3])
 if h>=10 and role in ['hem','banner','cloth','knot','fan']:
  d.line((1,h-3,w-2,h-3),fill=p[3]);
  if role=='banner' and w>5:
   d.rectangle((w//2,5,w//2+1,h//2),fill=COLORS['bone'][1]);d.line((1,h//3,w-2,h//3),fill=COLORS['bone'][1])


def paint(index,n,j,c,face,w,h):
 mat,role,axis=recipe(index,n,j,c);p=COLORS[mat]
 tone=3 if face=='up' else 1 if face=='down' else 2
 im=Image.new('RGB',(w,h),p[tone]);d=ImageDraw.Draw(im)
 if index==6:fox_paint(im,n,j,c,face,role,mat)
 elif mat in ['wood','lacquer']:
  # Member station changes where a grain line forks; it is not a random texture seed.
  station=int(n.split('_')[1]) if n.startswith(('outrigger_','link_','manipulator_','tool_')) else 0
  wood(im,face,axis,role,c,j+station)
 elif mat in ['iron','steel','copper','gold']:metal(im,mat,role,face,j)
 elif mat in ['purple','silk']:cloth(im,mat,role,face,j)
 elif mat in ['bone','porcelain','flesh']:
  if w>3 and h>4:
   # Root occlusion and one worn ridge; mostly quiet bone surface.
   d.rectangle((0,h-2,w-1,h-1),fill=p[1]);d.line((1,1,max(1,w//3),1),fill=p[3])
   if role in ['joint','skull','head','mask'] and w>8 and h>8:
    d.line((w-3,3,w-3,h//2),fill=p[1]);d.point((w-4,h//2),fill=p[0])
   if role in ['mask','head'] and face=='north' and w>8:
    eye=COLORS['iron'][0]
    for x in [w//4,w*3//4-2]:d.rectangle((x,h//3,x+2,h//3+1),fill=eye)
    d.line((w//2-2,h*2//3,w//2+2,h*2//3),fill=p[0])
 elif mat=='jade':
  if w>3 and h>3:
   d.rectangle((1,1,w-2,2),fill=p[3]);d.rectangle((1,h-2,w-2,h-1),fill=p[1])
   if role in ['core','seal'] and w>5 and h>5:
    cx,cy=w//2,h//2;mark(d,[(cx,1),(cx-2,cy),(cx,cy+2),(cx+2,cy),(cx,1)],p[4])
 elif mat=='ember':
  im.paste(p[0],(0,0,w,h));d=ImageDraw.Draw(im)
  # Bottom-up fractured coal bed; no concentric glow/pillow shading.
  for x in range(w):
   ridge=h//3+(x//3%3)*2
   d.line((x,min(h-1,ridge),x,h-1),fill=p[2])
   if x%7 in [2,3]:d.line((x,min(h-1,ridge+1),x,max(min(h-1,ridge+1),h-2)),fill=p[3])
  if role=='eye':d.rectangle((1,0,max(1,w-2),h-1),fill=p[3])
 elif mat=='scale':
  # Laid out in local face space; long body faces run head-to-tail, legs along Y.
  horizontal=n=='beast_body' and face in ['east','west']
  ww,hh=(h,w) if horizontal else (w,h)
  t=Image.new('RGB',(ww,hh),p[tone]);td=ImageDraw.Draw(t)
  for row,y in enumerate(range(1,hh,6)):
   for x in range(-3+(row%2)*4,ww,8):
    mark(td,[(x,y),(x,y+2),(x+2,y+4),(x+5,y+4),(x+7,y+2)],p[1]);mark(td,[(x+2,y+1),(x+5,y+1)],p[3])
  im.paste(t.transpose(Image.Transpose.TRANSPOSE) if horizontal else t)
 detail(index,n,j,c,face,im,role,mat)
 return im,{'material':mat,'role':role,'grain_axis':'XYZ'[axis]}



def detail(index,n,j,c,face,im,role,mat):
 w,h=im.size;d=ImageDraw.Draw(im);p=COLORS[mat]
 if min(w,h)<4:return
 if index==0:
  if n.startswith('lid') and j==0 and face=='north':
   # Original sparse imperial seal, confined to the inner lacquer lid.
   gold=COLORS['gold'];cx=w//2;cy=h//2
   mark(d,[(cx-3,cy-6),(cx+3,cy-6),(cx+3,cy-2),(cx-3,cy-2),(cx-3,cy+3),(cx+3,cy+3)],gold[2])
   mark(d,[(cx,cy-9),(cx,cy+7)],gold[3]);d.rectangle((cx-1,cy+9,cx+1,cy+10),fill=gold[1])
  elif n=='dragon_skull' and j==0 and face in ['east','west']:
   # Socket under the skull ridge, preserves mostly unbroken ivory.
   x=w//2;y=h//3;d.rectangle((x-2,y,x+3,y+2),fill=COLORS['iron'][0]);d.line((x-1,y+3,x+2,y+3),fill=COLORS['bone'][1])
  elif n=='relic' and j==0:
   for y in [h//3,h*2//3]:mark(d,[(1,y),(w-2,y+1)],p[1])
 elif index==1:
  if role=='brocade' and w>=8 and h>=4:
   purple=COLORS['purple'];gold=COLORS['gold'];im.paste(purple[1],(0,0,w,h));d=ImageDraw.Draw(im);d.line((0,h-1,w-1,h-1),fill=gold[2])
   for x in range(2,w-2,6):mark(d,[(x,1),(x+2,1),(x+2,2),(x,2)],gold[2])
  elif n=='mask' and j==0 and face=='north':
   ink=COLORS['purple'][0];verm=COLORS['silk'][2]
   for x in [3,w-5]:mark(d,[(x,4),(x+2,5),(x+2,6)],ink);d.line((x+1,8,x+1,10),fill=verm)
   d.rectangle((w//2-1,2,w//2+1,3),fill=COLORS['gold'][2]);mark(d,[(4,h-4),(w-5,h-4)],COLORS['porcelain'][0])
  elif role=='fan' and face in ['north','south']:
   purple=COLORS['purple'];fold=w//2
   d.rectangle((fold,2,fold+1,h-6),fill=purple[1]);d.line((fold+2,4,fold+2,h-9),fill=purple[3 if face=='north' else 2])
 elif index==2:
  if role=='breach_plate' and face in ['north','west'] and min(w,h)>=12:
   # Damaged flag-shaped battle mark on one large arm only, red stays secondary.
   red=COLORS['silk'];x=w//3;y=h//3
   mark(d,[(x,y+7),(x,y),(x+5,y),(x+5,y+3),(x+2,y+3)],red[2],2)
   d.line((w-8,2,w-3,7),fill=p[0]);d.line((w-7,2,w-2,7),fill=p[3])
  elif n=='broken_helm' and j==1 and face=='north':
   d.line((1,2,w-2,2),fill=COLORS['copper'][2]);d.rectangle((2,h-3,w-3,h-2),fill=p[0])
 elif index==3:
  if role=='yoke' and face in ['north','south'] and w>=20:
   # Peg joints at chain-bearing ends, not arbitrary metal painted in mid wood.
   iron=COLORS['iron']
   for x in [2,w-4]:d.rectangle((x,2,x+1,h-3),fill=iron[1]);d.point((x,3),fill=iron[3])
  elif role=='head' and face=='north':
   d.rectangle((3,h-5,w-4,h-3),fill=p[0]);d.line((4,h-5,w-5,h-5),fill=COLORS['bone'][2]);mark(d,[(w-4,4),(w-4,8),(w-3,9)],p[1])
  elif role=='battle_plate' and face=='north' and w>=10:
   d.line((w-4,3,w-4,h-4),fill=p[0]);d.line((w-3,3,w-3,h-7),fill=p[3])
 elif index==5:
  if role=='dorsal' and face in ['north','south','east','west']:
   # The existing large geometric scute stays a single plate, small nested growth at its tip.
   gold=COLORS['gold'];cx=w//2
   mark(d,[(max(1,cx-4),h-4),(cx,h-2),(min(w-2,cx+4),h-4)],gold[1]);mark(d,[(max(1,cx-3),h-6),(cx,h-4),(min(w-2,cx+3),h-6)],gold[3])
  elif n=='beast_mask' and j==0 and face=='north':
   # Formal central brow and nose line, original gate-beast insignia.
   gold=COLORS['gold'];cx=w//2
   mark(d,[(3,3),(cx-3,3),(cx,6),(cx+3,3),(w-4,3)],gold[4],2);mark(d,[(cx,6),(cx,h-4)],gold[1],2)
  elif role=='muzzle' and face=='north':
   for x in [3,w-5]:d.rectangle((x,2,x+2,4),fill=COLORS['iron'][0])
 elif index==7:
  if role=='shell' and face=='south' and w>20:
   # Broad rear casting, two original foundry seams and a quiet central field.
   d.line((w//3,5,w//3,h-5),fill=p[1]);d.line((w*2//3,5,w*2//3,h-5),fill=p[1])
  elif role=='cast_plate' and face=='north' and w>25 and h>7:
   cx=w//2;mark(d,[(cx-4,2),(cx-4,h-3),(cx+4,h-3),(cx+4,2)],p[1]);d.line((cx,3,cx,h-4),fill=p[3])
  elif role=='coal' and face=='north':
   coal=COLORS['ember']
   for x,y in [(2,h-5),(w//2,h-9),(w-6,h-4)]:
    d.rectangle((x,y,min(w-1,x+3),min(h-1,y+2)),fill=coal[1]);d.line((x,y,min(w-1,x+2),y),fill=coal[4])


def atlas(g,index):
 patches=[]
 for b in g.bones:
  for j,c in enumerate(b['cubes']):
   sx,sy,sz=c['size']
   for face,dim in [('north',(sx,sy)),('south',(sx,sy)),('east',(sz,sy)),('west',(sz,sy)),('up',(sx,sz)),('down',(sx,sz))]:
    w,h=[max(1,round(v)) for v in dim];im,meta=paint(index,b['name'],j,c,face,w,h)
    patches.append({'cube':c,'face':face,'image':im,'bone':b['name'],'cube_index':j,**meta})
 size=128
 while True:
  x=y=1;row=0
  for patch in sorted(patches,key=lambda p:(-p['image'].height,-p['image'].width,p['bone'],p['cube_index'],p['face'])):
   w,h=patch['image'].size
   if x+w+1>size:x=1;y+=row+2;row=0
   patch['xy']=(x,y);x+=w+2;row=max(row,h)
  if y+row+1<=size:break
  size*=2
  assert size<=1024
 out=Image.new('RGB',(size,size),(43,42,46));islands=[]
 for p in patches:
  im=p['image'];x,y=p['xy'];w,h=im.size;out.paste(im,(x,y))
  # Duplicate all four edges and corners to isolate texture sampling at seams.
  for dx,dy,box in [(0,-1,(0,0,w,1)),(0,h,(0,h-1,w,h)),(-1,0,(0,0,1,h)),(w,0,(w-1,0,w,h))]:out.paste(im.crop(box),(x+dx,y+dy))
  for dx,dy,sx,sy in [(-1,-1,0,0),(w,-1,w-1,0),(-1,h,0,h-1),(w,h,w-1,h-1)]:out.putpixel((x+dx,y+dy),im.getpixel((sx,sy)))
  p['cube']['uv'][p['face']]={'uv':[x,y],'uv_size':[w,h]}
  islands.append({k:p[k] for k in ['bone','cube_index','face','material','role','grain_axis']}|{'rect':[x,y,w,h]})
 for b in g.bones:
  for c in b['cubes']:c.pop('_material',None)
 g.texture_islands=islands
 return out
