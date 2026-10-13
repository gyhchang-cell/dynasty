"""Cod6 remaining core bosses: original thunder vessel, conserved dragon geometry.
Authoritative per-part painting and animations; never opens a user save.
"""
from pathlib import Path
import sys,json,copy,math,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/boss-checklist-night-v9'
sys.path.insert(0,str(R/'tools/art/boss-forms'));sys.path.insert(1,str(R/'tools/art/secondary-cuboid'))
from build import Rig
from atlas import COLORS
from rig_bounds import vertices
IDS=['nine_heaven_general','dragon_king','dragon_emperor']

def thunder():
 g=Rig(IDS[0]);g.bone('body','root',[0,32,0]);g.bone('chest','body',[0,32,0])
 # Hollow bronze ritual vessel, four connected load-bearing sides; no torso, waist or legs.
 g.box('body',[0,53,0],[28,7,23],1)
 g.box('body',[0,50,0],[22,4,17],1)
 for side in [-1,1]:
  g.box('body',[side*15,34,0],[6,32,24],1)
  g.box('body',[side*17,18,0],[10,8,29],1)
 for z in [-1,1]:
  if z==1:g.box('body',[0,34,z*11],[24,30,4],1)
  g.box('body',[0,18,z*14],[27,8,5],1)
 # Actual open front observation aperture between crossbars, with recessed driving seal.
 # Two front crossbars frame the open aperture; side walls stay intact.
 g.box('body',[0,24,-11],[24,10,4],1);g.box('body',[0,46,-11],[24,6,4],1)
 g.bone('head','chest',[0,37,-5]);g.box('head',[0,36,-5],[16,16,8],2);g.box('head',[0,37,-10],[12,6,3],3)
 g.bone('pendulum','body',[0,26,0]);g.box('pendulum',[0,19,0],[5,14,5],0);g.box('pendulum',[0,11,0],[12,6,12],2)
 g.bone('crown','body',[0,55,0]);g.box('crown',[0,58,0],[14,6,12],1)
 for side in [-1,1]:
  g.beam('crown',[side*5,58,0],[side*10,67,0],4,2);g.box('crown',[side*12,66,0],[8,3,4],2)
 g.bone('storm_ring_outer','chest',[0,34,6]);g.bone('storm_ring_inner','chest',[0,34,9])
 # Octagonal continuous angular rails, not a circular pile of cubes.
 for n,rad,y,z in [('storm_ring_outer',32,34,7),('storm_ring_inner',27,34,10)]:
  pts=[[math.cos(k*math.pi/4)*rad,y+math.sin(k*math.pi/4)*rad,z] for k in range(8)]
  for k in range(8):g.beam(n,pts[k],pts[(k+1)%8],3,0,d=3)
 for side,label in [(-1,'right'),(1,'left')]:
  drum=g.bone('thunder_drum_'+label,'chest',[side*29,35,1]);g.beam(drum,[side*16,49,3],[side*29,41,3],4,0)
  g.box(drum,[side*30,34,2],[17,20,12],1);g.box(drum,[side*30,34,-5],[13,16,2],2)
  g.bone('storm_wedge_'+label,drum,[side*30,43,2]);g.box('storm_wedge_'+label,[side*30,46,2],[5,6,6],0)
  for i in range(3):
   b=g.bone('thunder_blade_'+label+'_'+str(i),'chest',[side*(23+i*5),23+i*10,8])
   g.box(b,[side*(23+i*5),21+i*10,8],[4,11,4],0);g.box(b,[side*(23+i*5),28+i*10,8],[3,5,3],3)
  arm=g.bone(label+'_arm','chest',[side*16,25,0]);g.beam(arm,[side*16,25,0],[side*27,24,-10],5,0)
  hand=g.bone(label+'_hand',arm,[side*27,24,-10]);g.box(hand,[side*27,24,-12],[10,6,10],1)
  grip=g.bone(label+'_grip',hand,[side*27,24,-15])
  # Thunder prongs are connected to the striking carrier, not floating equipment.
  for x in [-3,3]:g.box(hand,[side*27+x,26,-18],[2,12,4],3)
 return g

def anim(g):
 old=json.loads((D/'before'/f'{g.id}.animation.json').read_text())
 result=copy.deepcopy(old)
 for clip,a in result['animations'].items():
  L=a['animation_length'];a['bones']={};tracks=a['bones']
  def key(n,ch,values):tracks.setdefault(n,{})[ch]={format(L*i/(len(values)-1),'.7g'):v for i,v in enumerate(values)}
  if clip in ['idle','walk']:
   key('body','position',[[0,0,0],[0,.65,0],[0,0,0]])
   key('pendulum','rotation',[[0,0,-3],[0,0,3],[0,0,-3]])
   key('head','rotation',[[0,-5,0],[0,5,0],[0,-5,0]])
   for side,sgn in [('left',1),('right',-1)]:key('thunder_drum_'+side,'rotation',[[0,-sgn*3,0],[0,sgn*3,0],[0,-sgn*3,0]])
   if clip=='walk':key('body','rotation',[[0,-4,-2],[0,4,2],[0,-4,-2]])
  elif clip=='attack':
   key('right_arm','rotation',[[0,0,0],[-32,-15,5],[34,15,-5],[0,0,0]])
   key('body','rotation',[[0,0,0],[-3,-7,0],[4,6,0],[0,0,0]])
   key('pendulum','rotation',[[0,0,0],[-12,0,0],[8,0,0],[0,0,0]])
  elif clip=='cast':
   for side,sgn in [('left',1),('right',-1)]:key('thunder_drum_'+side,'rotation',[[0,0,0],[0,-sgn*18,0],[0,sgn*4,0],[0,0,0]])
   key('storm_ring_inner','rotation',[[0,0,0],[0,0,-14],[0,0,10],[0,0,0]])
  elif clip=='hurt':key('body','rotation',[[0,0,0],[0,0,6],[0,0,0]])
  elif clip=='death':
   key('body','rotation',[[0,0,0],[0,0,16],[0,0,74],[0,0,86]])
   key('pendulum','rotation',[[0,0,0],[0,0,10],[0,0,0]])
   pos={}
   for t in np.linspace(0,L,113):
    low=min(p[1] for p in vertices(g.bones,tracks,float(t)));pos[format(t,'.7g')]=[0,round(float(.03-low),6),0]
   tracks['root']={'position':pos}
 return result

P={k:COLORS[k] for k in ['iron','copper','gold','jade','scale','bone']}

def role(id,n,j):
 if id=='nine_heaven_general':
  if n=='head':return ('jade','seal_eye') if j==1 else ('iron','seal_frame')
  if n.startswith('thunder_drum'):return ('bone','drum_skin') if j==2 else ('iron','connector') if j==0 else ('copper','drum_shell')
  if n.startswith('storm_ring'):return 'iron','rail'
  if n=='pendulum':return ('iron','shaft') if j==0 else ('copper','clapper')
  if n.startswith(('left_arm','right_arm')):return 'iron','connector'
  if n.endswith('_hand'):return ('jade','edge') if j>0 else ('copper','carrier')
  if n.startswith('thunder_blade'):return ('jade','edge') if j==1 else ('iron','rail')
  return 'copper','bell'
 if 'eye' in n:return 'gold','eye'
 if 'brow' in n:return 'jade','brow'
 if n.startswith(('coral','whisker')):return 'bone','horn'
 if n.startswith('fin'):return 'jade','edge'
 if id=='dragon_king' and n=='head':
  if j in [3,5]:return 'gold','eye'
  return ('jade','dragon_face') if j==0 else ('jade','muzzle') if j==1 else ('jade','brow')
 if id=='dragon_king' and n=='chest' and j==1:return 'bone','belly'
 if 'snout' in n:return 'jade','muzzle'
 if any(x in n for x in ['horn','fork','claw']):return 'bone','horn'
 if n=='head':return ('jade','dragon_face') if j==0 else ('jade','brow')
 if n=='jaw':return 'iron','jaw'
 if any(x in n for x in ['crown','helmet','pauldron','backplate','spine','armour']):return 'copper','regalia'
 if 'grip' in n or 'hand' in n:return 'iron','joint'
 if 'coil' in n or n.startswith('tail'):return 'scale','tail'
 if any(x in n for x in ['arm','leg','shin']):return 'scale','limb'
 return 'scale','body'

def paint(id,b,j,c,face,w,h):
 n=b['name'];mat,r=role(id,n,j)
 if n=='pendulum':mat,r=('iron','shaft') if j==0 else ('copper','clapper')
 pal=P[mat]
 if id=='dragon_king' and mat in ['scale','jade']:pal=[(24,44,52),(43,75,82),(65,105,112),(99,146,146),(145,183,176)]
 if id=='nine_heaven_general' and mat=='copper':pal=[(46,51,42),(90,83,53),(141,117,65),(184,160,96),(214,201,153)]
 base=pal[2];base=pal[1] if r in ['rail','connector','joint','jaw','seal_frame'] else base
 im=Image.new('RGB',(w,h),base);d=ImageDraw.Draw(im)
 if r in ['body','tail','limb']:
  # Larger orderly scales on flank/back, simple longitudinal belly plates on underside.
  if face=='down' or (face=='north' and n in ['chest','neck','neck_0','neck_1','neck_2','neck_3']):
   d.rectangle((1,0,max(1,w-2),h-1),fill=P['bone'][1]);
   for y in range(4,h,7):d.line((1,y,w-2,y),fill=P['bone'][0])
  else:
   for y in range(4,h-2,8):
    for x in range(2+(4 if (y//8)%2 else 0),w-3,9):
     d.line([(x,y),(x+2,y+2),(min(w-1,x+5),y)],fill=pal[1],width=1)
     if face in ['up','north'] and r!='limb':d.line((x+1,y-1,min(w-1,x+4),y-1),fill=pal[3])
   if face=='up' and r in ['body','tail'] and w>=6:d.rectangle((w//2-1,0,w//2+1,h-1),fill=pal[1])
 elif r=='eye':
  d.rectangle((0,0,w-1,h-1),fill=P['iron'][0])
  if w>=2 and h>=2:d.rectangle((0,max(0,h//3),w-1,max(0,h*2//3)),fill=pal[3]);d.line((w//2,0,w//2,h-1),fill=P['iron'][0])
  else:d.rectangle((0,0,w-1,h-1),fill=pal[3])
 elif r=='belly':
  for y in range(3,h,5):d.line((0,y,w-1,y),fill=pal[1])
 elif r=='muzzle':
  if face=='north':
   for x in [w//4,w*3//4]:d.rectangle((x,max(0,h//3),min(w-1,x+1),min(h-1,h//3+1)),fill=P['iron'][0])
   d.line((0,h-1,w-1,h-1),fill=P['iron'][1])
  elif face in ['east','west']:d.line((0,h-1,w-1,h-1),fill=pal[1])
 elif r=='dragon_face':
  if face=='north':
   d.rectangle((0,h//4,w-1,h//4+2),fill=pal[1]);d.rectangle((max(0,w//2-1),h//3,min(w-1,w//2+1),max(h//3,h-2)),fill=pal[3])
   d.line((w//3,h-3,w*2//3,h-3),fill=P['iron'][0],width=2)
  else:d.line((1,max(1,h//3),w-2,max(1,h//3)),fill=pal[1])
 elif r=='seal_eye':
  # Single inset storm-eye with dark socket, narrow ivory focus; not a red face template.
  d.rectangle((0,0,w-1,h-1),fill=P['iron'][0]);cx=w//2;cy=h//2
  d.rectangle((max(0,cx-4),max(0,cy-1),min(w-1,cx+4),min(h-1,cy+1)),fill=(95,180,185));d.line((cx,0,cx,h-1),fill=P['bone'][3])
 elif r in ['bell','drum_shell','regalia','carrier','clapper']:
  # Quiet bronze fields; construction seam on the trailing edge only. No cuboid-wide border/noise.
  if face in ['up','north']:d.rectangle((0,0,w-1,min(1,h-1)),fill=pal[3])
  if min(w,h)>7:
   d.line((w-3,2,w-3,h-3),fill=pal[1]);d.line((w-2,3,w-2,h-4),fill=pal[2])
  if id=='nine_heaven_general' and n=='body' and face=='north' and j in [0,1,8,9]:
   cx=w//2
   for y in range(4,h-2,9):d.line([(cx-4,y),(cx,y+3),(cx+4,y)],fill=P['jade'][1],width=2)
  if r=='regalia' and min(w,h)>8:d.line([(w//3,3),(w//3,h-4),(w*2//3,h-4)],fill=pal[1],width=2)
 elif r=='drum_skin':
  d.rectangle((0,0,w-1,h-1),fill=P['bone'][1]);cx=w//2;cy=h//2
  for k in [2,4]:d.line([(cx-k,cy),(cx,cy-k),(cx+k,cy),(cx,cy+k),(cx-k,cy)],fill=P['iron'][1])
  d.rectangle((cx-1,cy-1,cx+1,cy+1),fill=P['jade'][2])
 elif r in ['edge','horn']:
  if face in ['north','up','west']:d.rectangle((0,0,min(1,w-1),h-1),fill=pal[3])
  if face in ['down','south']:d.rectangle((max(0,w-2),0,w-1,h-1),fill=pal[1])
 else:
  if h>3:d.line((0,1,w-1,1),fill=pal[2])
  if w>7 and r=='joint':d.rectangle((w//3,1,w*2//3,max(1,h-2)),fill=pal[0])
 return im,{'material':mat,'role':r}

def atlas(id,bones,density=1):
 patches=[]
 for b in bones:
  for j,c in enumerate(b.get('cubes',[])):
   sx,sy,sz=c['size']
   for f,dims in [('north',(sx,sy)),('south',(sx,sy)),('east',(sz,sy)),('west',(sz,sy)),('up',(sx,sz)),('down',(sx,sz))]:
    w,h=[max(1,round(v*density)) for v in dims];im,meta=paint(id,b,j,c,f,w,h);patches.append(dict(c=c,face=f,im=im,bone=b['name'],index=j,**meta))
 size=128
 while True:
  x=y=1;row=0
  for p in sorted(patches,key=lambda p:(-p['im'].height,-p['im'].width,p['bone'],p['index'],p['face'])):
   w,h=p['im'].size
   if x+w+1>size:x=1;y+=row+2;row=0
   p['xy']=(x,y);x+=w+2;row=max(row,h)
  if y+row+1<=size:break
  size*=2;assert size<=1024
 out=Image.new('RGB',(size,size),P['iron'][0]);islands=[]
 for p in patches:
  x,y=p['xy'];w,h=p['im'].size;out.paste(p['im'],(x,y))
  for dx,dy,box in [(0,-1,(0,0,w,1)),(0,h,(0,h-1,w,h)),(-1,0,(0,0,1,h)),(w,0,(w-1,0,w,h))]:out.paste(p['im'].crop(box),(x+dx,y+dy))
  for dx,dy,sx,sy in [(-1,-1,0,0),(w,-1,w-1,0),(-1,h,0,h-1),(w,h,w-1,h-1)]:out.putpixel((x+dx,y+dy),p['im'].getpixel((sx,sy)))
  p['c']['uv'][p['face']]={'uv':[x,y],'uv_size':[w,h]};islands.append({k:p[k] for k in ['bone','index','face','material','role']}|{'rect':[x,y,w,h]})
 return out,islands

def destinations():
 return [A/f'{folder}/{id}{suffix}' for id in IDS for folder,suffix in [('geo/boss_cuboid','.geo.json'),('animations/boss_cuboid','.animation.json'),('textures/entity/boss_cuboid','.png')]]
def output_hashes():
 return {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in destinations()}
def check_ownership():
 manifest=D/'export-owner.json'
 if manifest.exists():
  expected=json.loads(manifest.read_text());actual=output_hashes()
  changed=[p for p in expected if actual.get(p)!=expected[p]]
  if changed:raise SystemExit('Preserve concurrent/manual art edits; no outputs written: '+', '.join(changed))
 else:
  for p in destinations():
   id=next(i for i in IDS if p.name.startswith(i));suffix='.geo.json' if p.name.endswith('.geo.json') else '.animation.json' if p.name.endswith('.animation.json') else '.png'
   if p.read_bytes()!=(D/'before'/f'{id}{suffix}').read_bytes():raise SystemExit('Unowned resource; no outputs written: '+str(p))
def export():
 check_ownership()
 for id in IDS:
  geo=json.loads((D/'before'/f'{id}.geo.json').read_text());g=geo['minecraft:geometry'][0]
  if id=='nine_heaven_general':
   rig=thunder();g['bones']=rig.bones;a=anim(rig);(A/f'animations/boss_cuboid/{id}.animation.json').write_text(json.dumps(a,indent=2)+'\n');g['description'].update(visible_bounds_width=6,visible_bounds_height=6,visible_bounds_offset=[0,2,0])
  if id=='dragon_emperor':
   authored=json.loads((D/'before'/f'{id}.animation.json').read_text())
   for clip in ['walk','attack']:
    a=authored['animations'][clip];tracks=a['bones'];pos={}
    for t in np.linspace(0,a['animation_length'],161):
     low=min(p[1] for p in vertices(g['bones'],tracks,float(t)))
     pos[format(t,'.8g')]=[0,round(max(0,-low+.01),6),0]
    tracks.setdefault('root',{})['position']=pos
   (A/f'animations/boss_cuboid/{id}.animation.json').write_text(json.dumps(authored,indent=2)+'\n')
  # The imperial dragon renderer scales 1.4, compensate UV density rather than inflate geometry.
  im,islands=atlas(id,g['bones'],1.4 if id=='dragon_emperor' else 1.35 if id=='dragon_king' else 1)
  for b in g['bones']:
   for c in b.get('cubes',[]):c.pop('_material',None)
  g['description'].update(texture_width=im.width,texture_height=im.height)
  (A/f'geo/boss_cuboid/{id}.geo.json').write_text(json.dumps(geo,indent=2)+'\n');im.save(A/f'textures/entity/boss_cuboid/{id}.png')
  o=D/id;o.mkdir(exist_ok=True);im.save(o/'texture.png');im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(o/'texture-4x.png');(o/'islands.json').write_text(json.dumps(islands,indent=2)+'\n')
  print(id,len(g['bones']),sum(len(b.get('cubes',[])) for b in g['bones']),im.size,flush=True)
 (D/'export-owner.json').write_text(json.dumps(output_hashes(),indent=2)+'\n')
if __name__=='__main__':export()
