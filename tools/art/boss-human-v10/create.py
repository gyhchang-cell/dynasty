"""Original humanoid replacement for three registered bosses, per user 2026-10-12.
Only atlas packing and Cuboid math are reused; no external art is imported.
"""
from pathlib import Path
import sys,json,copy,math,hashlib,importlib.util
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/boss-human-v10'
sys.path.insert(0,str(R/'tools/art/boss-forms'));sys.path.insert(1,str(R/'tools/art/secondary-cuboid'))
from build import Rig
from rig_bounds import vertices
spec=importlib.util.spec_from_file_location('v9_packing',R/'tools/art/boss-checklist/refine.py');packing=importlib.util.module_from_spec(spec);spec.loader.exec_module(packing)
IDS=['nine_heaven_general','dragon_king','dragon_emperor'];NAMES=dict(zip(IDS,['九霄天将','东海龙王','龙帝']))
def box(g,n,c,s,role,**kw):
 q=g.box(n,c,s,0,**kw);q['_role']=role;return q
def beam(g,n,a,b,w,role,d=None):
 q=g.beam(n,a,b,w,0,d=d);q['_role']=role;return q

def anatomy(id,shoulder,chest,pelvis,height,arm_width=7):
 """Human articulation, absolute pivots. Proportions are separately authored per role."""
 g=Rig(id);g.bone('body','root',[0,pelvis,0]);g.bone('pelvis','body',[0,pelvis,0]);g.bone('waist','pelvis',[0,pelvis+3,0]);g.bone('chest','waist',[0,chest-7,0])
 box(g,'pelvis',[0,pelvis,0],[18,7,11],'cloth');box(g,'waist',[0,pelvis+6,0],[15,10,10],'cloth')
 box(g,'chest',[0,chest,-.5],[22,14,12],'cloth')
 # Neck, full human face, back hair volume. No snout or animal legs.
 g.bone('neck','chest',[0,chest+7,0]);box(g,'neck',[0,chest+8,0],[6,4,6],'skin')
 g.bone('head','neck',[0,chest+9,0]);box(g,'head',[0,chest+15,-.5],[10,12,9],'face')
 g.bone('hair','head',[0,chest+16,0]);box(g,'hair',[0,chest+18,3.6],[10.5,7,2],'hair');box(g,'hair',[0,chest+21,0],[10.5,2,9.5],'hair')
 g.bone('crown','head',[0,chest+21,0])
 for side,s in [('left',1),('right',-1)]:
  # Hip -> thigh -> knee -> shin -> ankle -> modest foot. Feet are narrower than hands/shoulders.
  x=s*5.5;hip=g.bone(side+'_leg','pelvis',[x,pelvis-1,0]);box(g,hip,[x,pelvis-6,0],[7.5,12,8],'trousers')
  knee=g.bone(side+'_knee',hip,[x,14,0]);box(g,knee,[x,14,-.5],[7,4,8],'joint')
  shin=g.bone(side+'_shin',knee,[x,13,0]);box(g,shin,[x,8.5,0],[6.5,10,7],'boot')
  foot=g.bone(side+'_foot',shin,[x,3.5,0]);box(g,foot,[x,2,-1.5],[7.5,4,10],'boot')
  box(g,shin,[x,10,-3.7],[6,6,1.5],'shin_plate')
  arm=g.bone(side+'_arm','chest',[s*shoulder,chest+4,0]);box(g,arm,[s*shoulder,chest-2,-.2],[arm_width,12,9],'sleeve')
  elbow=g.bone(side+'_elbow',arm,[s*shoulder,chest-8,-.2]);box(g,elbow,[s*shoulder,chest-8,-.5],[arm_width-1,3,8],'joint')
  fore=g.bone(side+'_forearm',elbow,[s*shoulder,chest-8,-.5]);box(g,fore,[s*shoulder,chest-13,-1],[arm_width+1,10,9],'cuff')
  hand=g.bone(side+'_hand',fore,[s*shoulder,chest-18,-1]);box(g,hand,[s*shoulder,chest-20,-1],[6.5,5,7],'hand')
  g.bone(side+'_grip',hand,[s*shoulder,chest-20,-1.6])
  # Every character has a split hem, not a single rigid skirt covering both knees.
  panel=g.bone(side+'_hem','pelvis',[s*8,pelvis+1,0]);box(g,panel,[s*10,pelvis-7,1],[4,17,13],'hem')
 return g

def general():
 g=anatomy(IDS[0],15.5,41,25,64,8)
 box(g,'chest',[0,41,-7],[21,13,2.5],'steel');box(g,'chest',[0,40,6.5],[20,13,2],'steel')
 box(g,'waist',[0,29,-.5],[18,4,12],'belt');box(g,'waist',[0,29,-7],[6,4,1.5],'jade')
 for s,side in [(1,'left'),(-1,'right')]:
  n=g.bone(side+'_pauldron',side+'_arm',[s*15.5,46,0]);box(g,n,[s*16,46,0],[13,6,13],'steel')
  box(g,n,[s*20.5,42,0],[5,6,12],'gold')
  box(g,side+'_forearm',[s*15.5,29,-6],[8,8,2],'steel');box(g,side+'_hem',[s*10,18,-6],[5,15,2],'lamellar')
  box(g,'head',[s*5.5,52,0],[1.5,7,8],'steel')
 box(g,'crown',[0,63,0],[12,3,11],'steel');box(g,'crown',[0,65,-2],[3,6,5],'gold')
 g.bone('plume','crown',[0,66,1]);box(g,'plume',[0,67,2],[4,7,5],'ribbon');box(g,'plume',[0,69,7],[4,4,8],'ribbon')
 # Small articulated back regalia, subordinate to the man, retaining existing VFX bone names.
 g.bone('storm_ring_outer','chest',[0,35,9]);g.bone('storm_ring_inner','storm_ring_outer',[0,35,9])
 for side,s in [('left',1),('right',-1)]:
  drum=g.bone('thunder_drum_'+side,'chest',[s*13,41,9]);box(g,drum,[s*13,41,10],[7,7,4],'gold')
  g.bone('storm_wedge_'+side,drum,[s*13,45,10])
 g.bone('weapon','right_grip',[-15.5,21,-1.6]);beam(g,'weapon',[-15.5,8,-1.6],[-15.5,60,-1.6],2.5,'shaft')
 box(g,'weapon',[-15.5,61,-1.6],[5,8,2.5],'blade');box(g,'weapon',[-15.5,66.5,-1.6],[3,3,2.5],'blade');box(g,'weapon',[-15.5,69,-1.6],[1.5,2,2.5],'blade');box(g,'weapon',[-15.5,58,-1.6],[9,2,4],'gold')
 box(g,'weapon',[-15.5,56,1],[3,9,2],'ribbon')
 return g

def king():
 g=anatomy(IDS[1],14,39,24,64,9)
 box(g,'chest',[0,39,-7],[19,13,2],'robe');box(g,'chest',[0,39,6.5],[21,14,2],'robe')
 box(g,'waist',[0,28,0],[18,3.5,12],'belt');box(g,'waist',[0,28,-7],[5,4,1.5],'pearl')
 for s,side in [(1,'left'),(-1,'right')]:
  box(g,side+'_arm',[s*14,38,0],[12,11,11],'robe');box(g,side+'_forearm',[s*14,26,0],[13,11,12],'robe')
  box(g,side+'_forearm',[s*14,21,-1],[13.5,3,12.5],'gold')
  box(g,side+'_hem',[s*5.2,17,-6],[8.5,18,2],'robe')
  n=g.bone(side+'_mantle','chest',[s*9,46,1]);box(g,n,[s*11,43,2],[9,6,12],'gold',rot=[0,0,-s*12],pivot=[s*9,46,1])
 box(g,'crown',[0,60,0],[13,4,11],'gold');box(g,'crown',[0,62,-5],[5,5,2],'jade')
 for s in [-1,1]:
  beam(g,'crown',[s*5,61,1],[s*9,68,2],2.5,'horn');beam(g,'crown',[s*9,68,2],[s*12,68,0],2.5,'horn')
 g.bone('beard','head',[0,50,-5]);box(g,'beard',[0,47,-5.8],[7,7,2.5],'beard');box(g,'beard',[0,42,-5.4],[4,5,2],'beard')
 for s in [-1,1]:box(g,'beard',[s*3,49,-5.8],[4,2,2],'beard')
 g.bone('back_robe','pelvis',[0,25,6]);box(g,'back_robe',[0,17,7],[16,18,2.5],'robe')
 g.bone('weapon','right_grip',[-14,19,-1.6]);beam(g,'weapon',[-14,6,-1.6],[-14,58,-1.6],2.5,'shaft')
 box(g,'weapon',[-14,59,-1.6],[15,3,3],'gold')
 for x,L in [(-20,8),(-14,13),(-8,8)]:
  box(g,'weapon',[x,60+L/2,-1.6],[2.5,L,2.5],'blade');box(g,'weapon',[x,61+L,-1.6],[1.5,2,2.5],'blade')
 return g

def emperor():
 g=anatomy(IDS[2],16,44,27,70,9)
 box(g,'chest',[0,43,-7.3],[23,14,2.5],'robe');box(g,'chest',[0,44,6.7],[23,15,2.5],'robe')
 box(g,'waist',[0,31,0],[20,4,13],'belt');box(g,'waist',[0,31,-7.5],[6,4,2],'jade')
 for s,side in [(1,'left'),(-1,'right')]:
  box(g,side+'_arm',[s*16,42,0],[12,13,12],'robe');box(g,side+'_forearm',[s*16,31,-1],[13,13,12],'robe')
  box(g,side+'_forearm',[s*16,25,-1],[13.5,3,12.5],'gold');box(g,side+'_hem',[s*5.5,20,-6.5],[9,18,2],'robe')
  n=g.bone(side+'_shoulder','chest',[s*10,49,0]);box(g,n,[s*12.5,47,0],[11,5,13],'gold',rot=[0,0,-s*10],pivot=[s*10,49,0])
 g.bone('back_robe','pelvis',[0,27,6]);box(g,'back_robe',[0,19,7.5],[18,20,3],'robe')
 box(g,'crown',[0,67,0],[12,4,11],'crown');box(g,'crown',[0,70,0],[16,2,15],'gold')
 # Sparse imperial tassels at the board edges, kept out of the gaze.
 for x in [-6,6]:
  n=g.bone('tassel_'+str(x),'crown',[x,70,-7]);box(g,n,[x,65,-7],[1.5,9,1.5],'gold');box(g,n,[x,60.5,-7],[2.5,2,2.5],'jade')
 g.bone('beard','head',[0,54,-5.3]);box(g,'beard',[0,52,-5.5],[6,4,2],'beard');box(g,'beard',[0,49,-5.5],[3,4,2],'beard')
 # Fireball/flame-burst are existing skills; an open casting hand instead of an invented sword.
 g.bone('seal','left_hand',[16,24,-1]);box(g,'seal',[16,23,-5.3],[4,4,1],'jade')
 return g

PAL={
 'skin':[(105,72,58),(149,106,80),(188,142,107),(215,171,132)],
 'hair':[(26,28,36),(40,43,51),(56,58,64),(75,75,80)],
 'steel':[(46,58,72),(82,101,118),(139,157,168),(184,197,199)],
 'gold':[(87,61,36),(143,105,49),(194,155,80),(228,196,120)],
 'jade':[(20,65,69),(34,103,109),(67,147,151),(140,198,184)],
 'pearl':[(89,110,111),(148,173,167),(205,221,205),(235,239,218)],
 'horn':[(114,107,91),(169,161,133),(207,198,164),(234,225,190)],
 'blade':[(45,60,72),(86,112,128),(160,184,192),(223,233,227)],
 'joint':[(26,34,44),(42,51,62),(60,70,78),(86,95,101)],
 'boot':[(24,28,35),(41,43,49),(64,62,60),(94,88,73)],
 'shaft':[(38,37,44),(65,56,51),(105,82,53),(140,112,73)],
 'ribbon':[(74,25,39),(120,42,53),(165,63,65),(190,94,82)],
}
def palette(id,role):
 if role in ['face','hand']:return PAL['skin'] if id!=IDS[1] else [(109,81,63),(151,120,91),(191,158,118),(221,191,150)]
 if role=='beard':return PAL['pearl'] if id==IDS[1] else PAL['hair']
 if role in ['steel','shin_plate','lamellar']:return PAL['steel'] if id==IDS[0] else PAL['gold']
 if role in ['belt','crown']:return PAL['gold']
 if role in ['cloth','robe','sleeve','cuff','hem','trousers']:
  return ([(25,36,55),(38,56,80),(54,80,106),(85,114,134)] if id==IDS[0] else [(20,56,65),(30,82,91),(47,112,117),(83,142,137)] if id==IDS[1] else [(48,24,35),(81,34,47),(123,48,57),(161,72,68)])
 return PAL[role]

def paint(id,b,j,c,face,w,h):
 role=c['_role'];p=palette(id,role);im=Image.new('RGB',(w,h),p[2]);d=ImageDraw.Draw(im);n=b['name'];gold=PAL['gold'];dark=PAL['hair'][0]
 if min(w,h)<4:
  d.rectangle((0,0,w-1,h-1),fill=p[3] if face=='up' else p[1] if face=='down' else p[2])
  if role=='blade':d.line((w-1,0,w-1,h-1),fill=p[3])
  return im,{'material':role,'role':role}
 # All textures have a surface purpose; deterministic directional pixel clusters, no noise.
 if role=='face':
  if face=='north':
   # Face is the visual centre: eyebrows frame directional eyes, cheeks remain quiet.
   d.rectangle((0,0,w-1,max(1,h//6)),fill=PAL['hair'][1]);d.rectangle((0,h//6,max(1,w//8),h-1),fill=p[1]);d.rectangle((w-w//8-1,h//6,w-1,h-1),fill=p[1])
   ey=h*2//5
   for x in [w//5,w*3//5]:
    d.line((x,ey-1,x+w//5,ey-1),fill=dark)
    d.line((x,ey,x+w//5,ey),fill=PAL['pearl'][2]);d.rectangle((x+w//10,ey,x+w//10,ey+1),fill=PAL['jade'][0] if id==IDS[1] else dark)
   d.rectangle((w//2-1,ey+3,w//2+1,h*3//4),fill=p[1]);d.rectangle((w//2-1,ey+3,w//2,ey+4),fill=p[3])
   d.line((w//3,h*4//5,w*2//3,h*4//5),fill=p[0],width=2)
   if id==IDS[0]:d.rectangle((w//4,h-3,w*3//4,h-1),fill=p[1])
  else:
   d.rectangle((0,0,w-1,h//4),fill=PAL['hair'][1])
   if face=='south':d.rectangle((0,0,w-1,h-1),fill=PAL['hair'][1])
 elif role in ['cloth','robe','sleeve','cuff','hem','trousers']:
  # Folds follow body/limb length. Large surfaces carry one clothing seam, not boxed borders.
  if face in ['east','west','south']:d.rectangle((0,0,max(1,w//5),h-1),fill=p[1])
  if w>10:d.rectangle((w*2//3,2,min(w-1,w*2//3+2),h-2),fill=p[1])
  if role in ['robe','hem'] and face in ['north','south']:
   if n=='chest':
    # Authored overlapping collar, chest heraldry and lower sash. Identity uses original dragon/cloud language.
    d.line([(2,1),(w//2,h//2),(w-3,1)],fill=gold[2],width=2)
    if id!=IDS[0] and min(w,h)>10:
     cx=w//2;cy=h*2//3
     d.line([(cx-5,cy-4),(cx,cy-7),(cx+5,cy-4),(cx+5,cy),(cx,cy+3),(cx-4,cy),(cx,cy-2)],fill=gold[2],width=2)
     d.rectangle((cx+2,cy-6,cx+3,cy-5),fill=gold[3]);d.line((cx-6,cy+5,cx+6,cy+5),fill=p[3])
   elif 'hem' in n or n=='back_robe':
    d.rectangle((0,max(0,h-5),w-1,h-3),fill=gold[1]);
    if w>12:d.line([(2,h-9),(w//3,h-11),(w*2//3,h-9),(w-3,h-11)],fill=p[3],width=2)
  if role in ['cuff','sleeve'] and face=='north' and id!=IDS[0]:d.rectangle((0,h-4,w-1,h-3),fill=gold[2])
 elif role in ['steel','gold','shin_plate','lamellar','belt','crown']:
  # One load-bearing edge only, quiet broad field. Metal/fabric stay separate in grayscale.
  if face=='up':d.rectangle((0,0,w-1,h-1),fill=p[3])
  elif face=='down':d.rectangle((0,0,w-1,h-1),fill=p[1])
  elif face=='north':
   d.rectangle((0,0,w-1,1),fill=p[3]);d.rectangle((max(0,w-2),2,w-1,h-1),fill=p[1])
   if n=='chest' and role=='steel' and min(w,h)>=10:
    # Connected lamellar band beneath the torso rather than a framed metal box.
    for y in range(h//2,h-2,6):
     d.line((2,y,w-4,y),fill=p[1]);
     for x in range(5,w-4,8):d.line((x,y,x,y+3),fill=p[2])
    cx=w//2;d.line([(cx-5,3),(cx-2,3),(cx-2,6),(cx+2,6),(cx+2,3),(cx+5,3)],fill=PAL['jade'][1],width=1)
    d.line([(2,2),(w//2,4),(w-3,2)],fill=p[1],width=1)
   if role=='lamellar':
    for y in range(4,h,6):d.line((1,y,w-2,y),fill=p[1])
   if role=='belt' and w>12:
    d.rectangle((0,h//3,w-1,h*2//3),fill=p[1])
  else:d.rectangle((0,0,min(1,w-1),h-1),fill=p[1])
 elif role in ['jade','pearl']:
  d.rectangle((0,0,w-1,1),fill=p[3]);d.rectangle((0,max(0,h-2),w-1,h-1),fill=p[1])
  if min(w,h)>5:d.line([(2,h//2),(w//2,2),(w-3,h//2),(w//2,h-3),(2,h//2)],fill=p[3])
 elif role=='blade':
  # Actual blade edge, spine, and worn cutting face.
  d.rectangle((0,0,1,h-1),fill=p[1]);d.rectangle((max(0,w-2),0,w-1,h-1),fill=p[3]);
  if w>7:d.line((w//2,2,w//2,max(2,h-3)),fill=p[2])
 elif role=='beard':
  for x in range(2,w-1,4):d.rectangle((x,1,x+1,h-2),fill=p[1]);
  d.rectangle((0,h-2,w-1,h-1),fill=p[1])
 elif role=='hand':
  if face=='north':
   for x in range(3,w-2,4):d.line((x,h//2,x,h-2),fill=p[1])
   d.line((1,h//2,w-2,h//2),fill=p[3])
 elif role=='boot':
  d.rectangle((0,h-3,w-1,h-1),fill=p[0]);
  if face=='north':d.rectangle((2,2,w-3,3),fill=p[3])
 elif role=='joint':d.rectangle((0,h//3,w-1,h*2//3),fill=p[0])
 elif role=='shaft':
  if face in ['north','south']:d.rectangle((0,0,0,h-1),fill=p[1])
  for y in range(0,h,18):d.rectangle((0,y,w-1,min(h-1,y+2)),fill=PAL['gold'][1])
 elif role=='ribbon':d.rectangle((w//2,0,min(w-1,w//2+1),h-1),fill=p[1])
 elif role=='horn':d.rectangle((0,h*2//3,w-1,h-1),fill=p[1])
 elif role=='hair':
  if face in ['east','west','south']:
   for x in range(3,w,5):d.line((x,1,x,h-1),fill=p[1])
 return im,{'material':role,'role':role}

def animations(g):
 old=json.loads((D/'before'/f'{g.id}.animation.json').read_text());an=copy.deepcopy(old)
 for clip,a in an['animations'].items():
  L=a['animation_length'];a['bones']={};ch=a['bones']
  def key(n,field,vals):ch.setdefault(n,{})[field]={format(L*i/(len(vals)-1),'.7g'):v for i,v in enumerate(vals)}
  # Slight forward authority in spine, not backward lean. Lower support remains upright.
  ch['chest']={'rotation':[4,0,0]}
  if clip=='idle':
   key('chest','rotation',[[4,0,0],[5,0,0],[4,0,0]]);key('head','rotation',[[0,-3,0],[1,3,0],[0,-3,0]])
   for side,s in [('left',1),('right',-1)]:
    ch[side+'_arm']={'rotation':[-6,0,-s*4]};key(side+'_forearm','rotation',[[-12,0,0],[-14,0,0],[-12,0,0]])
   if g.id!=IDS[0]:key('beard','rotation',[[0,0,0],[3,0,0],[0,0,0]])
  elif clip=='walk':
   # Alternating hip motion, bent recovering knee, counter-swinging arms. Full cycle closes exactly.
   for side,s in [('left',1),('right',-1)]:
    vals=[-20,0,20,0,-20] if s==1 else [20,0,-20,0,20]
    key(side+'_leg','rotation',[[x,0,0] for x in vals]);key(side+'_knee','rotation',[[0,0,0],[30 if s==-1 else 0,0,0],[0,0,0],[30 if s==1 else 0,0,0],[0,0,0]])
    key(side+'_foot','rotation',[[6,0,0],[0,0,0],[-6,0,0],[0,0,0],[6,0,0]] if s==1 else [[-6,0,0],[0,0,0],[6,0,0],[0,0,0],[-6,0,0]])
    key(side+'_arm','rotation',[[s*x-6,0,-s*4] for x in [12,0,-12,0,12]]);ch[side+'_forearm']={'rotation':[-12,0,0]}
    key(side+'_hem','rotation',[[s*x,0,0] for x in [5,0,-5,0,5]])
   key('chest','rotation',[[4,-2,0],[5,0,0],[4,2,0],[5,0,0],[4,-2,0]])
  elif clip=='attack':
   if g.id==IDS[2]:
    key('right_arm','rotation',[[-6,0,4],[25,-12,8],[-100,10,3],[-6,0,4]]);key('right_forearm','rotation',[[-12,0,0],[-50,0,0],[-10,0,0],[-12,0,0]])
   else:
    key('right_arm','rotation',[[-6,0,4],[25,-15,8],[-100,12,8],[-6,0,4]]);key('right_forearm','rotation',[[-12,0,0],[-45,0,0],[-10,0,0],[-12,0,0]])
    key('weapon','rotation',[[0,0,0],[50,0,0],[200,0,0],[0,0,0]])
   key('chest','rotation',[[4,0,0],[2,-10,0],[9,12,0],[4,0,0]])
   key('left_arm','rotation',[[-6,0,-4],[-15,0,-10],[-20,0,-4],[-6,0,-4]])
   # Align the visual contact with the middle of the inherited 6-tick swing, retaining length.
   for tracks in ch.values():
    for field,track in list(tracks.items()):
     if isinstance(track,dict) and len(track)==4:
      tracks[field]={format(t,'.7g'):v for t,v in zip([0,L*.3,L*.5,L],track.values())}
  elif clip=='cast':
   for side,s in [('left',1),('right',-1)]:
    # Character-specific casting: commander one hand; king two hands; emperor imposing open arms.
    amount=50 if g.id==IDS[0] and s==-1 else 75 if g.id==IDS[1] else 65
    key(side+'_arm','rotation',[[-6,0,-s*4],[-amount,0,-s*(12 if g.id!=IDS[2] else 30)],[-amount+4,0,-s*16],[-6,0,-s*4]])
    key(side+'_forearm','rotation',[[-12,0,0],[-25,0,0],[-18,0,0],[-12,0,0]])
   key('chest','rotation',[[4,0,0],[0,0,0],[3,0,0],[4,0,0]])
   if 'weapon' in g.by:
    amount=50 if g.id==IDS[0] else 75
    key('weapon','rotation',[[0,0,0],[amount+7,0,0],[amount-4,0,0],[0,0,0]])
  elif clip=='hurt':key('chest','rotation',[[4,0,0],[-7,0,5],[4,0,0]])
  elif clip=='death':
   key('body','rotation',[[0,0,0],[0,0,12],[0,0,65],[0,0,87]]);key('chest','rotation',[[4,0,0],[12,0,0],[15,0,0],[15,0,0]])
   for side,s in [('left',1),('right',-1)]:key(side+'_arm','rotation',[[5,0,s*4],[10,0,s*12],[15,0,s*18],[15,0,s*18]])
   if 'weapon' in g.by:key('weapon','rotation',[[0,0,0],[0,0,-10],[0,0,-55],[0,0,-60]])
  # Clamp actual full-clip lower surface to ground. This avoids the old dragon/feet floor bug.
  if clip in ['walk','attack','cast','hurt','death']:
   pos={}
   for t in np.linspace(0,L,161):
    low=min(p[1] for p in vertices(g.bones,ch,float(t)));pos[format(t,'.7g')]=[0,round(float(.03-low),6),0]
   ch['root']={'position':pos}
 return an

def targets():return [A/f'{folder}/{id}{ext}' for id in IDS for folder,ext in [('geo/boss_cuboid','.geo.json'),('animations/boss_cuboid','.animation.json'),('textures/entity/boss_cuboid','.png')]]
def hashes():return {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in targets()}
def export():
 D.mkdir(parents=True,exist_ok=True);before=D/'before';before.mkdir(exist_ok=True);owner=D/'export-owner.json'
 if owner.exists():
  assert hashes()==json.loads(owner.read_text()),'Concurrent/manual art edit: nothing exported'
 else:
  for p in targets():(before/p.name).write_bytes(p.read_bytes())
  (D/'before-hashes.json').write_text(json.dumps(hashes(),indent=2)+'\n')
 packing.paint=paint
 for id,fn in zip(IDS,[general,king,emperor]):
  rig=fn();an=animations(rig);tex,islands=packing.atlas(id,rig.bones,density=1)
  for b in rig.bones:
   for c in b.get('cubes',[]):c.pop('_material',None);c.pop('_role',None)
  desc={'identifier':'geometry.'+id,'texture_width':tex.width,'texture_height':tex.height,'visible_bounds_width':12,'visible_bounds_height':12,'visible_bounds_offset':[0,2.5,0]}
  geo={'format_version':'1.12.0','minecraft:geometry':[{'description':desc,'bones':rig.bones}]}
  (A/f'geo/boss_cuboid/{id}.geo.json').write_text(json.dumps(geo,indent=2)+'\n');(A/f'animations/boss_cuboid/{id}.animation.json').write_text(json.dumps(an,indent=2)+'\n');tex.save(A/f'textures/entity/boss_cuboid/{id}.png')
  out=D/id;out.mkdir(exist_ok=True);tex.save(out/'texture.png');tex.resize((tex.width*4,tex.height*4),Image.Resampling.NEAREST).save(out/'texture-4x.png');(out/'islands.json').write_text(json.dumps(islands,indent=2)+'\n')
  print(id,len(rig.bones),sum(len(b['cubes']) for b in rig.bones),tex.size,flush=True)
 owner.write_text(json.dumps(hashes(),indent=2)+'\n')
if __name__=='__main__':export()
