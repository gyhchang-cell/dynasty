"""Power/readability pass over the accepted V11 human rigs, with no external assets."""
from pathlib import Path
import importlib.util,json,copy,sys,hashlib,os
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/boss-human-v12';A=R/'src/main/resources/assets/dynasty'
spec=importlib.util.spec_from_file_location('human_v11',R/'tools/art/boss-human-v11/create.py');v11=importlib.util.module_from_spec(spec);spec.loader.exec_module(v11)
IDS=v11.IDS;NAMES=v11.NAMES;SCALE=v11.SCALE;vertices=v11.vertices
ROUND=int(os.environ.get('DYNASTY_POWER_ROUND','8'))
def reshape(c,factors):
 centre=[c['origin'][i]+c['size'][i]/2 for i in range(3)]
 c['size']=[c['size'][i]*factors[i] for i in range(3)];c['origin']=[centre[i]-c['size'][i]/2 for i in range(3)]
def power(g):
 for b in g.bones:
  n=b['name']
  for j,c in enumerate(b.get('cubes',[])):
   role=c['_role']
   if n=='chest':
    if c['size'][2]>5:reshape(c,[1.13,1,1.17])
    else:
     reshape(c,[1.13,1.07,1.25]);centre=c['origin'][2]+c['size'][2]/2
     c['origin'][2]+=(-1 if centre<0 else 1)*1.3
   if n in ['waist','pelvis']:reshape(c,[1.06,1,1.08])
   if 'pauldron' in n and role=='steel':reshape(c,[1.10,1.4,1.13])
   if any(n.endswith(s) for s in ['_arm','_forearm']) and role in ['sleeve','cuff','steel','joint']:reshape(c,[1.13,1,1.12])
   if n.endswith('_hand'):reshape(c,[1.16,1.12,1.12])
   if n.endswith('_collar') and g.id==IDS[0]:c['_role']='collar_steel'
   if n=='weapon':
    if role in ['shaft','leather']:reshape(c,[1.22,1,1.22])
    if role=='blade':reshape(c,[1.35,1.12,1.3])
    if g.id==IDS[1] and role=='gold':reshape(c,[1.2,1.25,1.2])
   if n=='seal':reshape(c,[1.28,1.18,1.3])
   if ROUND>=2:
    if n=='head' and role=='face':reshape(c,[.97,.95,1])
    if n.endswith('_mantle') or n.endswith('_shoulder'):
     # Weight moves into the shoulder itself, not taller poles or a larger head.
     if role=='gold':reshape(c,[1.03,1.28,1.14])
    if n.startswith('royal_fin'):
     c['origin'][2]+=3
     if '_2' in n:reshape(c,[.9,1,1])
  if ROUND>=3:
   for j,c in enumerate(b.get('cubes',[])):
    if g.id==IDS[0] and n=='head' and c['_role']=='steel':reshape(c,[1.2,1.12,1.08])
    if g.id==IDS[0] and n=='crown' and c['_role']=='steel':reshape(c,[1.05,1.35,1.08])
    if n.endswith('_hand') and g.id==IDS[0]:c['_role']='gauntlet'
    if ROUND>=4:
     if n=='beard':
      c['origin'][2]-=3.8
      if ROUND>=5:
       # Existing beard root touches the jaw; the lower tier projects over the collar.
       cy=c['origin'][1]+c['size'][1]/2
       if g.id==IDS[1]:depth,cz=(6,-8.2) if cy>=48 else (8,-10) if cy>=45 else (6,-12.8)
       else:depth,cz=(8,-10) if cy>=51 else (6,-12.8)
       c['size'][2]=depth;c['origin'][2]=cz-depth/2
       if ROUND>=6 and g.id==IDS[2] and cy>=51:c['origin'][1]+=1
     if g.id==IDS[1] and n.startswith('royal_fin'):c['origin'][2]-=2.5
     if g.id!=IDS[0] and (n.endswith('_mantle') or n.endswith('_shoulder')):reshape(c,[1.12,1.12,1.18])
     if g.id==IDS[0] and n=='crown' and c['_role']=='steel':reshape(c,[1,1.32,1])
    if ROUND>=6:
     if n=='head' and c['_role']=='face':
      top=c['origin'][1]+c['size'][1];c['size'][1]*=.85;c['origin'][1]=top-c['size'][1]
     if g.id==IDS[0] and n=='weapon':
      if j==1:
       cy=c['origin'][1]+c['size'][1]/2;c['size'][1]=13.5;c['origin'][1]=cy+2.3-6.75
      if j==2:c['origin'][1]+=5
      if j==3:c['origin'][1]+=5.2
  if ROUND>=7:
   for c in b.get('cubes',[]):
    if g.id==IDS[0] and n.endswith('_pauldron') and c['_role']=='steel':
     c['rotation']=[0,0,-(1 if n.startswith('left') else -1)*12];c['pivot']=list(b['pivot'])
    if g.id!=IDS[0] and n.endswith('_forearm') and c['_role']=='robe':reshape(c,[.84,1.03,.94])
    if n in ['left_mantle','right_mantle','left_shoulder','right_shoulder'] and 'rotation' in c:
     c['rotation'][2]*=1.35
 return g

def paint(id,b,j,c,face,w,h):
 role=c['_role'];n=b['name'];base=v11.base
 cc=dict(c,_role='steel' if role in ['collar_steel','gauntlet'] else role)
 im,meta=v11.paint(id,b,j,cc,face,w,h);dr=ImageDraw.Draw(im)
 if role=='face' and face=='north' and w>=7 and h>=8:
  p=base.PAL['skin'];ink=(34,31,34);shadow=(112,79,67)
  im=Image.new('RGB',(w,h),p[2]);dr=ImageDraw.Draw(im)
  dr.rectangle((0,0,w-1,1),fill=p[1]);dr.rectangle((0,2,0,h-1),fill=shadow);dr.rectangle((w-1,2,w-1,h-1),fill=p[1])
  eyeY=max(3,h//3);cx=w//2
  for s in [-1,1]:
   x=cx+s*max(2,w//4);dr.line((x-s,eyeY-1,x+s,eyeY-2),fill=ink,width=1)
   if ROUND==1:
    dr.rectangle((x-1,eyeY,x+1,eyeY+1),fill=shadow)
    dr.point((x,eyeY),fill=(114,165,160) if id==IDS[1] else (187,164,111) if id==IDS[2] else (186,198,199));dr.point((x+s,eyeY+1),fill=ink)
   else:
    dr.line((x-s,eyeY,x+s,eyeY),fill=(190,198,185));dr.point((x,eyeY),fill=ink)
  dr.line((cx,eyeY+2,cx,eyeY+3),fill=p[1]);dr.line((cx-1,h-3,cx+1,h-3),fill=shadow)
  # Closed, severe mouth; cheek planes stay clean. No oversized villager nose.
  if id==IDS[0]:
   if ROUND==1:dr.line((cx-2,h-4,cx+2,h-4),fill=(58,46,41))
   else:dr.line((cx-1,h-3,cx+1,h-3),fill=p[1])
   dr.point((cx,h-2),fill=p[3])
  return im,dict(meta,role=role,focus='gaze and compressed brow; calm closed mouth')
 if role=='gauntlet':
  p=base.PAL['steel'];im=Image.new('RGB',(w,h),p[1]);dr=ImageDraw.Draw(im)
  if face=='north':
   dr.rectangle((1,1,w-2,max(1,h//2)),fill=p[2]);dr.line((1,h-1,w-2,h-1),fill=base.PAL['joint'][1])
   if w>6:dr.line((w//2,1,w//2,max(1,h//2)),fill=p[1])
  elif face=='up':dr.rectangle((1,0,w-2,h-1),fill=p[2])
  return im,dict(meta,role=role,focus='steel knuckle plate and dark leather gripping palm')
 if face not in ['north','south'] or min(w,h)<5:return im,meta
 gold=base.PAL['gold'];p=base.palette(id,'robe')
 if n=='chest' and role=='robe':
  # One garment field with two lapel regions. No small isolated central squiggle.
  im=Image.new('RGB',(w,h),p[2]);dr=ImageDraw.Draw(im)
  cx=w//2;dr.polygon([(0,0),(cx-2,0),(cx,h//2),(cx,h-1),(0,h-1)],fill=p[1])
  dr.line([(cx-2,0),(cx+2,h//2),(cx+1,h-1)],fill=gold[1],width=1)
  if id==IDS[1]:
   for x in [2,w-4]:dr.line([(x,h//2),(x+2,h//2),(x+2,h//2+2),(x,h//2+2),(x,h//2+4)],fill=(74,128,132),width=1)
   dr.line([(2,h-2),(w//3,h-3),(w//2,h-2),(w*2//3,h-3),(w-3,h-2)],fill=gold[2],width=1)
  else:
   # Sparse heraldic cloud branches around the lapel, not a copied faction emblem.
   for s in [-1,1]:
    x=cx+s*max(3,w//3);y=h//2
    dr.line([(x,y+3),(x-s*2,y+3),(x-s*2,y),(x-s*4,y),(x-s*4,y-2)],fill=gold[2],width=1)
    dr.point((x,y+1),fill=gold[3])
  return im,dict(meta,focus='coherent royal garment, overlapping lapel, subordinate cloud/tide motifs')
 if ROUND>=4 and id!=IDS[0] and role=='robe' and n.endswith(('_arm','_forearm')):
  # Woven fields run along the limb; patterned cuff is subordinate to the face and weapon.
  p=base.palette(id,'robe');dr.rectangle((0,0,w-1,h-1),fill=p[2])
  dr.rectangle((0,0,max(0,w//5-1),h-1),fill=p[1]);dr.line((w-1,0,w-1,h-1),fill=p[1])
  if id==IDS[1]:
   for row,y in enumerate(range(3,h-4,4)):
    for x in range(3+(row%2)*2,w-2,5):dr.line([(x-1,y),(x,y+1),(x+1,y)],fill=p[1],width=1)
  else:
   yy=h//2;dr.line([(w//3,yy-2),(w//3+2,yy-2),(w//3+2,yy+1),(w//3+4,yy+1)],fill=p[3],width=1)
  dr.line((1,h-3,w-2,h-3),fill=gold[1]);return im,dict(meta,focus='continuous sleeve woven field; cuff hem only, no boxed outlines')
 if ROUND>=4 and role=='gold' and n.endswith(('_mantle','_shoulder')):
  p=base.PAL['gold'];im=Image.new('RGB',(w,h),p[2]);dr=ImageDraw.Draw(im)
  # Two broad overlapping armour planes; no same-width outline on all sides.
  yy=max(2,h//2);dr.rectangle((0,yy,w-1,h-1),fill=p[1]);dr.line((1,yy-1,w-2,yy-1),fill=p[3]);dr.rectangle((0,0,1,h-1),fill=p[1])
  dr.line((w//2,1,w//2+2,yy-2),fill=p[1]);return im,dict(meta,focus='two load-bearing mantle planes, warm dark underside')
 if role=='steel' and n=='chest':
  p=base.PAL['steel'];im=Image.new('RGB',(w,h),p[1]);dr=ImageDraw.Draw(im)
  dr.polygon([(1,1),(w-2,1),(w-2,h//2),(w//2,h-2),(1,h//2)],fill=p[2])
  dr.line([(2,h//2),(w//2,h-2),(w-3,h//2)],fill=p[1],width=1)
  dr.line((3,2,w-4,2),fill=p[3]);return im,dict(meta,focus='broad convex breastplate with lower load-bearing fold')
 if role=='collar_steel':
  p=base.PAL['steel'];dr.rectangle((0,0,w-1,h-1),fill=p[1]);dr.line((w-1,1,w-1,h-1),fill=gold[2]);dr.line((0,0,0,h//2),fill=p[3])
 if role=='blade':
  p=base.PAL['blade'];dr.rectangle((0,0,w-1,h-1),fill=p[1]);dr.polygon([(w//2,0),(w-1,0),(w-1,h-1),(w//2,h-2)],fill=p[2]);dr.line((w-1,1,w-1,h-1),fill=p[3]);dr.line((w//2,1,w//2,h-2),fill=p[0])
 if ROUND>=2 and role in ['banner','screen']:
  # Recurring banners/screens are kept quiet, so silhouette does not outshine the face.
  a=np.array(im);a=np.clip(a*.83,0,255).astype('uint8');im=Image.fromarray(a)
 return im,dict(meta,role=role)

def motion(g):
 an=v11.motion(g)
 for clip,a in an['animations'].items():
  ch=a['bones'];L=a['animation_length'];ch.pop('root',None)
  if clip=='idle':
   lean,turn={IDS[0]:(11,-9),IDS[1]:(6,7),IDS[2]:(5,-7)}[g.id]
   ch['chest']['rotation']={'0':[lean,turn,-1],str(L/2):[lean+1,turn+1,-1],str(L):[lean,turn,-1]}
   ch['head']['rotation']={'0':[6,-turn*.65,0],str(L/2):[7,-turn*.65+1,0],str(L):[6,-turn*.65,0]}
   ch['right_arm']={'rotation':[-22,-12,9]};ch['right_forearm']={'rotation':[-38,0,0]}
   ch['left_arm']={'rotation':[-18,12,-12]};ch['left_forearm']={'rotation':[-38,0,0]}
   if 'weapon' in g.by:ch['weapon']={'rotation':[28 if ROUND==1 else 5 if ROUND==2 else 80,0,-8 if ROUND==1 else -13]}
   if ROUND>=2 and g.id==IDS[0]:
    ch['left_arm']={'rotation':[-48,12,-14] if ROUND>=6 else [-26,12,-14]};ch['left_forearm']={'rotation':[-62,0,0] if ROUND>=6 else [-52,0,0]}
   if g.id==IDS[2]:
    ch['left_arm']={'rotation':[-44,8,-26] if ROUND>=6 else [-26,8,-17]};ch['left_forearm']={'rotation':[-62,0,0] if ROUND>=6 else [-60,0,0]}
    ch['right_arm']={'rotation':[-30,-18,22] if ROUND>=6 else [-9,-9,14]};ch['right_forearm']={'rotation':[-36,0,0] if ROUND>=6 else [-27,0,0]}
   if ROUND>=6 and g.id==IDS[1]:
    ch['left_arm']={'rotation':[-32,25,-20]};ch['left_forearm']={'rotation':[-55,0,0]}
   if ROUND>=7:
    if 'weapon' in g.by:ch['weapon']={'rotation':[80,0,-38]}
    if g.id==IDS[1]:ch['left_arm']={'rotation':[-22,25,-27]};ch['left_forearm']={'rotation':[-36,0,0]}
    if g.id==IDS[2]:ch['right_arm']={'rotation':[-20,-18,28]};ch['right_forearm']={'rotation':[-28,0,0]}
   ch['left_leg']={'rotation':[5,0,-6]};ch['right_leg']={'rotation':[-7,0,7]}
  if ROUND>=8 and clip=='death':
   def folded(bone,end,channel='rotation'):
    ch[bone]={channel:{'0':[0,0,0],format(L/3,'.7g'):[v*.18 for v in end],format(L*2/3,'.7g'):[v*.82 for v in end],format(L,'.7g'):end}}
   if g.id==IDS[0]:
    for side,s in [('left',1),('right',-1)]:folded('edict_flag_'+side,[0,s*76,0])
   elif g.id==IDS[1]:
    for side,s in [('left',1),('right',-1)]:
     for i in range(3):folded('royal_fin_'+side+'_'+str(i),[0,s*78,0])
   else:
    for side,s in [('left',1),('right',-1)]:folded('floating_gui_'+side,[-s*17,0,-5],'position')
    for s in [-1,1]:folded('screen_panel_'+str(s),[0,-s*65,0])
   if 'weapon' in g.by:folded('weapon',[0,0,12])
  # Keep the existing six clips/contact times. Recompute floor compensation after body changes.
  ch['root']={'position':{format(t,'.7g'):[0,round(float(.03-min(p[1] for p in vertices(g.bones,ch,float(t)))),6),0] for t in np.linspace(0,L,161)}}
 return an

def targets():return v11.targets()
def hashes():return v11.hashes()
def export():
 D.mkdir(exist_ok=True);owner=D/'export-owner.json';before=D/'before';before.mkdir(exist_ok=True)
 if owner.exists():assert hashes()==json.loads(owner.read_text()),'Manual/concurrent edit: export refused'
 else:
  assert hashes()==json.loads((v11.D/'export-owner.json').read_text()),'Expected accepted V11 baseline'
  for p in targets():(before/p.name).write_bytes(p.read_bytes())
  (D/'before-hashes.json').write_text(json.dumps(hashes(),indent=2)+'\n')
 v11.packing.paint=paint
 for id,fn in zip(IDS,[v11.base.general,v11.base.king,v11.base.emperor]):
  g=power(v11.enrich(fn()));texture,islands=v11.packing.atlas(id,g.bones,density=1);an=motion(g);k=SCALE[id]
  for b in g.bones:
   b['pivot']=[v*k for v in b['pivot']]
   for c in b.get('cubes',[]):
    for f in ['origin','size','pivot']:
     if f in c:c[f]=[v*k for v in c[f]]
    c.pop('_material',None);c.pop('_role',None)
  for a in an['animations'].values():
   for ch in a['bones'].values():
    if 'position' in ch:ch['position']={t:[v*k for v in x] for t,x in ch['position'].items()} if isinstance(ch['position'],dict) else [v*k for v in ch['position']]
  desc={'identifier':'geometry.'+id,'texture_width':texture.width,'texture_height':texture.height,'visible_bounds_width':10,'visible_bounds_height':10,'visible_bounds_offset':[0,1.8,0]}
  (A/f'geo/boss_cuboid/{id}.geo.json').write_text(json.dumps({'format_version':'1.12.0','minecraft:geometry':[{'description':desc,'bones':g.bones}]},indent=2)+'\n')
  (A/f'animations/boss_cuboid/{id}.animation.json').write_text(json.dumps(an,indent=2)+'\n');texture.save(A/f'textures/entity/boss_cuboid/{id}.png')
  dst=D/id;dst.mkdir(exist_ok=True);texture.save(dst/'texture.png');texture.resize((1024,1024),Image.Resampling.NEAREST).save(dst/'texture-4x.png');(dst/'islands.json').write_text(json.dumps(islands,indent=2)+'\n')
  print(id,'round',ROUND,'bones',len(g.bones),'cubes',sum(len(b.get('cubes',[])) for b in g.bones),flush=True)
 owner.write_text(json.dumps(hashes(),indent=2)+'\n');(D/'current-round.txt').write_text(str(ROUND)+'\n')
if __name__=='__main__':export()
