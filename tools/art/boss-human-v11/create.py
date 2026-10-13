"""Incremental Boss presence edit of the V10 rigs, not another character redesign."""
from pathlib import Path
import sys,json,copy,hashlib,math,importlib.util
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/boss-human-v11'
spec=importlib.util.spec_from_file_location('human_v10',R/'tools/art/boss-human-v10/create.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
IDS=base.IDS;NAMES=base.NAMES;vertices=base.vertices;packing=base.packing
SCALE={IDS[0]:.65,IDS[1]:.64,IDS[2]:.64}
box=base.box;beam=base.beam

def widen(g):
 # Keep every existing bone, parent, limb and carrier. Redistribute upper-body volume.
 for b in g.bones:
  b['pivot'][0]*=1.10
  for c in b.get('cubes',[]):
   c['origin'][0]*=1.10;c['size'][0]*=1.10
   if 'pivot' in c:c['pivot'][0]*=1.10
   if b['name'] in ['chest','waist','pelvis']:
    centre=c['origin'][2]+c['size'][2]/2;c['size'][2]*=1.18;c['origin'][2]=centre-c['size'][2]/2
   if any(x in b['name'] for x in ['pauldron','mantle','shoulder']):
    centre=[c['origin'][i]+c['size'][i]/2 for i in range(3)]
    c['size']=[c['size'][0]*1.18,c['size'][1]*1.2,c['size'][2]*1.12];c['origin']=[centre[i]-c['size'][i]/2 for i in range(3)]
 # Feet remain support-sized, slightly broader to match the lower, widened body.
 for side,s in [('left',1),('right',-1)]:
  c=g.by[side+'_foot']['cubes'][0];c['size']=[8.4,4.2,10.8];c['origin']=[s*6.05-4.2,0,-7]
 return g

def enrich(g):
 widen(g)
 chest=g.by['head']['pivot'][1]-9;pelvis=g.by['pelvis']['pivot'][1]
 # Actual overlapped collar and second cloth layer, not painted holes.
 for s,side in [(-1,'right'),(1,'left')]:
  n=g.bone(side+'_collar','chest',[s*5,chest+6,-7]);box(g,n,[s*5,chest+5,-8.7],[4,9,2],'gold' if g.id==IDS[0] else 'collar',rot=[0,0,s*22],pivot=[s*5,chest+6,-8.7])
  n=g.bone(side+'_waist_lappet','waist',[s*7,pelvis+4,-6]);box(g,n,[s*7,pelvis-1,-8],[6,10,2],'lamellar' if g.id==IDS[0] else 'brocade')
  n=g.bone(side+'_sash','waist',[s*10,pelvis+3,3]);box(g,n,[s*12,pelvis-7,4],[3,20,2],'ribbon' if g.id==IDS[0] else 'jade_cord')
 if g.id==IDS[0]:
  g.bone('commander_cape','chest',[0,47,10]);box(g,'commander_cape',[0,38,11],[22,20,3],'cape')
  g.bone('cape_lower','commander_cape',[0,30,11]);box(g,'cape_lower',[0,25,14],[26,10,3],'cape')
  for s,side in [(-1,'right'),(1,'left')]:
   n=g.bone('edict_flag_'+side,'chest',[s*13,46,12]);beam(g,n,[s*13,42,12],[s*24,70,15],2.2,'shaft')
   box(g,n,[s*25,58,15],[11,24,2],'banner',rot=[0,0,-s*10],pivot=[s*25,69,15]);box(g,n,[s*27,45,15],[7,6,2],'banner')
   box(g,side+'_pauldron',[s*21,48,-2],[9,3,13],'gold',rot=[0,0,-s*12],pivot=[s*21,48,-2])
  # Retain the main spear carrier. A stepped side blade and cord make its grip legible.
  box(g,'weapon',[-17.05,61,-1.6],[8,7,2.6],'blade');box(g,'weapon',[-17.05,21,-1.6],[4,7,4],'leather')
 elif g.id==IDS[1]:
  g.bone('tide_ring','chest',[0,45,17]);points=[[math.cos(k*math.pi/4)*20,45+math.sin(k*math.pi/4)*20,18] for k in range(8)]
  for k in range(8):beam(g,'tide_ring',points[k],points[(k+1)%8],1.8,'jade')
  g.bone('tide_pearl','tide_ring',[0,60,18]);box(g,'tide_pearl',[0,60,18],[6,6,5],'pearl')
  for s,side in [(-1,'right'),(1,'left')]:
   for i in range(3):
    n=g.bone('royal_fin_'+side+'_'+str(i),'chest',[s*9,44,11])
    for dx,dy,ww,hh in [(0,0,9,16-i*2),(0,10-i,5,6),(-s*2,-9+i,12,4)]:
     box(g,n,[s*(20+i*5)+dx,47-i*7+dy,14+i],[ww,hh,3],'fin',rot=[0,0,-s*(28+i*10)],pivot=[s*9,44,11])
   box(g,side+'_mantle',[s*16,46,-1],[10,4,14],'gold',rot=[0,0,-s*18],pivot=[s*12,46,0])
  for b in g.bones:
   if b['name']=='crown':
    for c in b['cubes'][2:]:c['size'][0]*=1.1;c['size'][1]*=1.15
  box(g,'weapon',[-15.4,19,-1.6],[4,7,4],'leather')
 elif g.id==IDS[2]:
  g.bone('imperial_screen','chest',[0,48,14])
  # Three stepped imperial tablets leave the head clear and read as a regnal back screen.
  for s in [-1,0,1]:
   n=g.bone('screen_panel_'+str(s),'imperial_screen',[s*17,46,15]);y=53 if s else 50
   box(g,n,[s*17,y,16],[13,31 if s else 25,3],'screen',rot=[0,s*16,0],pivot=[s*17,46,15])
   box(g,n,[s*17,y+16 if s else y+13,16],[15,3,4],'gold');box(g,n,[s*17,y-16 if s else y-13,16],[14,3,4],'gold')
  for s,side in [(-1,'right'),(1,'left')]:
   n=g.bone('floating_gui_'+side,'imperial_screen',[s*30,43,15]);box(g,n,[s*30,43,15],[4,17,2],'jade_tablet');box(g,n,[s*30,53,15],[4,3,2],'gold')
   box(g,side+'_shoulder',[s*20,49,0],[10,4,14],'gold',rot=[0,0,-s*15],pivot=[s*13,49,0])
  # Extend the existing left palm imperial seal; no unrelated sword or combat mechanism.
  box(g,'seal',[17.6,23,-6],[5,5,2],'jade');box(g,'seal',[17.6,26,-6],[3,2,2],'gold')
 return g

EXTRA={
 'cape':[(19,30,45),(30,45,63),(48,66,84),(88,107,125)],
 'banner':[(21,33,52),(35,53,73),(57,79,99),(122,158,167)],
 'leather':[(36,27,24),(59,43,34),(92,64,44),(127,95,62)],
 'fin':[(13,43,53),(25,72,87),(48,112,127),(94,160,163)],
 'screen':[(40,18,26),(64,26,34),(98,37,42),(143,60,53)],
}
def paint(id,b,j,c,face,w,h):
 role=c['_role'];n=b['name'];gold=base.PAL['gold'];jade=base.PAL['jade']
 mapped={'collar':'robe','brocade':'robe','jade_cord':'jade','jade_tablet':'jade'}.get(role,role)
 if mapped in EXTRA:
  p=EXTRA[mapped];im=Image.new('RGB',(w,h),p[2]);dr=ImageDraw.Draw(im)
  if face in ['east','west','down']:dr.rectangle((0,0,w-1,h-1),fill=p[1])
 else:
  cc=dict(c,_role=mapped);im,_=base.paint(id,b,j,cc,face,w,h);dr=ImageDraw.Draw(im);p=base.palette(id,mapped)
 if face not in ['north','south'] or min(w,h)<5:return im,{'role':role,'material':mapped}
 if role=='face':
  # Narrow heavy brow and an inward eye. No villager nose, oversized eye patch or cheap glow.
  ey=h*2//5;dr.rectangle((1,ey-2,w-2,ey+2),fill=p[2])
  for s in [-1,1]:
   x=w//2+s*w//4;dr.line((x-s*2,ey-2,x+s*1,ey-1),fill=base.PAL['hair'][0],width=1)
   dr.line((x-1,ey,x+1,ey),fill=base.PAL['pearl'][2]);dr.point((x,ey),fill=jade[0] if id==IDS[1] else base.PAL['hair'][0])
 elif role in ['banner','screen']:
  dr.rectangle((0,0,w-1,1),fill=gold[2]);dr.rectangle((0,h-3,w-1,h-2),fill=gold[1])
  if w>=8 and h>=14:
   cx=w//2;cy=h//2
   if role=='banner':
    dr.line([(cx-3,cy-5),(cx+2,cy-5),(cx+2,cy-2),(cx-2,cy-2),(cx-2,cy+3),(cx+3,cy+3)],fill=base.PAL['pearl'][2],width=1)
    dr.line((cx-4,cy+6,cx+4,cy+6),fill=gold[2])
   else:
    dr.line([(cx-3,cy-6),(cx+2,cy-8),(cx+3,cy-4),(cx-2,cy),(cx-3,cy+5),(cx+3,cy+7)],fill=gold[2],width=2)
    dr.line((cx-3,cy+2,cx+3,cy+2),fill=gold[1])
 elif role in ['fin','cape','brocade']:
  # Broad directional folds; trim only on real hems, not a frame on every box.
  dr.rectangle((0,0,max(0,w//5),h-1),fill=p[1]);dr.line((w//2,2,w//2,max(2,h-4)),fill=p[3])
  dr.rectangle((0,h-3,w-1,h-2),fill=gold[2] if role!='fin' else jade[2])
  if role=='fin':
   for y in range(5,h-3,7):dr.line([(w//3,y),(w*2//3,y-2),(w-2,y)],fill=p[1])
 elif role=='jade_tablet':
  if h>=10:dr.line([(w//2,2),(w//2,h-3)],fill=gold[2]);dr.line((1,h//2,w-2,h//2),fill=gold[1])
 elif role in ['robe','hem','sleeve','cuff'] and n!='chest':
  # Distribute the garment rhythm away from one chest badge.
  if w>=8 and h>=8:
   yy=h-5;dr.line([(1,yy),(w//3,yy-2),(w*2//3,yy),(w-2,yy-2)],fill=gold[1],width=1)
   if 'arm' in n or 'hem' in n:dr.line((2,yy+2,w-3,yy+2),fill=p[3])
 elif role=='steel' and 'pauldron' in n and w>=10:
  dr.line([(2,h-3),(w//2,h-5),(w-3,h-3)],fill=gold[1],width=1)
 return im,{'role':role,'material':mapped}

def motion(g):
 an=base.animations(g)
 for clip,a in an['animations'].items():
  L=a['animation_length'];ch=a['bones'];ch.pop('root',None)
  def key(n,field,vals):ch.setdefault(n,{})[field]={format(L*i/(len(vals)-1),'.7g'):v for i,v in enumerate(vals)}
  if clip=='idle':
   angles={IDS[0]:(8,-6),IDS[1]:(4,4),IDS[2]:(3,-3)};lean,turn=angles[g.id]
   key('chest','rotation',[[lean,turn,0],[lean+1,turn+1,0],[lean,turn,0]])
   key('head','rotation',[[3,-turn*.7,0],[4,-turn*.7+2,0],[3,-turn*.7,0]])
   ch['pelvis']={'rotation':[0,-turn/2,0]}
   ch['right_arm']={'rotation':[-18,-6,9]};key('right_forearm','rotation',[[-24,0,0],[-27,0,0],[-24,0,0]])
   ch['left_arm']={'rotation':[-7,6,-9]};key('left_forearm','rotation',[[-18,0,0],[-20,0,0],[-18,0,0]])
   if 'weapon' in g.by:ch['weapon']={'rotation':[18,0,-5]}
   for side,s in [('left',1),('right',-1)]:
    ch[side+'_leg']={'rotation':[s*3,0,-s*4]};ch[side+'_knee']={'rotation':[6,0,0]}
    key(side+'_hem','rotation',[[0,0,s*1],[2,0,s*2],[0,0,s*1]])
  if clip in ['idle','walk','cast','attack']:
   for b in g.bones:
    n=b['name']
    if n.startswith(('edict_flag','royal_fin','floating_gui','screen_panel')) or n in ['commander_cape','cape_lower']:
     amp=2 if clip=='idle' else 4;sign=-1 if 'right' in n or n.endswith('-1') else 1
     key(n,'rotation',[[0,0,sign*amp],[2,0,-sign*amp],[0,0,sign*amp]])
     if n.startswith('floating_gui'):key(n,'position',[[0,0,0],[0,.7,0],[0,0,0]])
   if 'tide_pearl' in g.by:key('tide_pearl','position',[[0,0,0],[0,.6,0],[0,0,0]])
  # Additions follow the existing chest/waist. Preserve the six clips and their exact durations.
  pos={}
  for t in np.linspace(0,L,161):
   low=min(p[1] for p in vertices(g.bones,ch,float(t)));pos[format(t,'.7g')]=[0,round(float(.03-low),6),0]
  ch['root']={'position':pos}
 return an

def targets():return base.targets()
def hashes():return base.hashes()
def export():
 D.mkdir(exist_ok=True);owner=D/'export-owner.json';before=D/'before';before.mkdir(exist_ok=True)
 if owner.exists():assert hashes()==json.loads(owner.read_text()),'Concurrent/manual edit: export refused'
 else:
  assert hashes()==json.loads((base.D/'export-owner.json').read_text()),'Expected the accepted V10 resources'
  for p in targets():(before/p.name).write_bytes(p.read_bytes())
  (D/'before-hashes.json').write_text(json.dumps(hashes(),indent=2)+'\n')
 packing.paint=paint
 for id,fn in zip(IDS,[base.general,base.king,base.emperor]):
  g=enrich(fn());texture,islands=packing.atlas(id,g.bones,density=1);an=motion(g);k=SCALE[id]
  for b in g.bones:
   b['pivot']=[v*k for v in b['pivot']]
   for c in b.get('cubes',[]):
    for field in ['origin','size','pivot']:
     if field in c:c[field]=[v*k for v in c[field]]
    c.pop('_material',None);c.pop('_role',None)
  for a in an['animations'].values():
   for channels in a['bones'].values():
    if 'position' in channels:
     track=channels['position'];channels['position']={t:[v*k for v in vec] for t,vec in track.items()} if isinstance(track,dict) else [v*k for v in track]
  description={'identifier':'geometry.'+id,'texture_width':texture.width,'texture_height':texture.height,'visible_bounds_width':10,'visible_bounds_height':10,'visible_bounds_offset':[0,1.8,0]}
  (A/f'geo/boss_cuboid/{id}.geo.json').write_text(json.dumps({'format_version':'1.12.0','minecraft:geometry':[{'description':description,'bones':g.bones}]},indent=2)+'\n')
  (A/f'animations/boss_cuboid/{id}.animation.json').write_text(json.dumps(an,indent=2)+'\n');texture.save(A/f'textures/entity/boss_cuboid/{id}.png')
  out=D/id;out.mkdir(exist_ok=True);texture.save(out/'texture.png');texture.resize((texture.width*4,texture.height*4),Image.Resampling.NEAREST).save(out/'texture-4x.png');(out/'islands.json').write_text(json.dumps(islands,indent=2)+'\n')
  print(id,len(g.bones),sum(len(b.get('cubes',[])) for b in g.bones),texture.size,flush=True)
 owner.write_text(json.dumps(hashes(),indent=2)+'\n')
if __name__=='__main__':export()
