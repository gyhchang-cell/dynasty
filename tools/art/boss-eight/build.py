"""Eight existing Dynasty encounters: original Cuboid art over frozen local resources.
No entity registration, stats, skills, loot or library versions are generated here.
"""
import copy,json,math,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageColor
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
AS=ROOT/'src/main/resources/assets/dynasty';TARGETS=json.loads((HERE/'targets.json').read_text())
sys.path.insert(0,str(ROOT/'tools/art/secondary-cuboid'))
from rig_bounds import vertices
FACES=['north','south','east','west','up','down']
SPECS={
 'undead_first_emperor':(['#273539','#61796D','#CCB57D'],['.ACCA.','CBAABC','.CBBC.','ABCCBA','CBAABC','.BCCB.']),
 'eunuch_mastermind':(['#302C40','#765874','#D4BC8D'],['..AA..','.ACCA.','..CC..','BAC CAB'.replace(' ',''),'ABB BBA'.replace(' ',''),'.BBBB.']),
 'rebel_general':(['#29353C','#944B40','#D5B986'],['.AAAC.','.CAAC.','..CC..','ABBABC','CBABBC','.ABBA.']),
 'xianzhen_duantoujiang':(['#253C3D','#647E76','#BB9862'],['C.AA.C','CCAACC','BBCCBB','CBABBC','CAB BAC'.replace(' ',''),'.BAAB.']),
 'qianji_bailian_yanshi':(['#293F40','#698678','#C2A36C'],['..AA..','.CACC.','CABBAC','CAB BAC'.replace(' ',''),'CABBAC','.CAAC.']),
 'pilin_zhijinwu':(['#303A45','#963F3A','#D0AB60'],['..CB..','.CAAC.','.ACCA.','CC AACC'.replace(' ',''),'ACAACA','.CAAC.']),
 'baimian_huxiangu':(['#392C42','#BA708A','#D5B575'],['.CAAC.','.WAWC.','..WW..','BWCWBB','ABCCBA','.BBBB.']),
 'juchui_jinjia_lishi':(['#35423D','#9B8562','#C5A458'],['..AA..','.ACCA.','.BAAB.','CCBBCC','CAACAC','.CAAC.'])}
class Art:
 def __init__(self,id):
  self.id=id;self.folder=TARGETS[id]['folder'];self.palette,self.rows=SPECS[id]
  self.islands={};self.im=Image.new('RGB',(16,16),'white');d=ImageDraw.Draw(self.im)
  for y,row in enumerate(self.rows,1):
   assert len(row)==6,(id,row)
   for x,k in enumerate(row,1):
    if k=='.':continue
    d.rectangle((2*x,2*y,2*x+1,2*y+1),fill='white' if k=='W' else self.palette['ABC'.index(k)]);self.islands.setdefault(k,[2*x,2*y])
  self.islands.setdefault('W',[0,0])
  gp=HERE/'baseline/src/main/resources/assets/dynasty/geo'/self.folder/(id+'.geo.json')
  if gp.exists():
   self.doc=json.loads(gp.read_text());self.g=self.doc['minecraft:geometry'][0];self.b=self.g['bones'];self.by={b['name']:b for b in self.b}
   self.a=json.loads((HERE/'baseline/src/main/resources/assets/dynasty/animations'/self.folder/(id+'.animation.json')).read_text())
   old=Image.open(HERE/'baseline/src/main/resources/assets/dynasty/textures/entity'/self.folder/(id+'.png')).convert('RGB')
   # Transfer the old semantic material by its actual pixel colour, not UV slot guesses.
   pals=[ImageColor.getrgb(c) for c in self.palette]
   for b in self.b:
    for c in b.get('cubes',[]):
     for f,v in c['uv'].items():
      u,w=v['uv'];du,dv=v['uv_size'];rgb=old.getpixel((min(15,max(0,int(u+du/2))),min(15,max(0,int(w+dv/2)))))
      k='W' if min(rgb)>245 else 'ABC'[min(range(3),key=lambda i:sum((rgb[j]-pals[i][j])**2 for j in range(3)))]
      c['uv'][f]={'uv':self.islands[k].copy(),'uv_size':[2,2]}
  else:
   self.g={'description':{'identifier':'geometry.boss_cuboid.'+id,'texture_width':16,'texture_height':16,'visible_bounds_width':5,'visible_bounds_height':5,'visible_bounds_offset':[0,1.7,0]},'bones':[]}
   self.doc={'format_version':'1.12.0','minecraft:geometry':[self.g]};self.b=self.g['bones'];self.by={};self.a={'format_version':'1.8.0','animations':{}}
 def bone(self,n,parent,pivot,r=None):
  if n not in self.by:
   b={'name':n,'pivot':list(pivot),'cubes':[]}
   if parent:b['parent']=parent
   if r:b['rotation']=r
   self.b.append(b);self.by[n]=b
  return n
 def clear(self,*names):
  for n in names:self.by[n]['cubes']=[]
 def cube(self,n,o,s,k='B',rot=None,pivot=None,panel=False):
  c={'origin':list(o),'size':list(s),'uv':{f:{'uv':self.islands[k].copy(),'uv_size':[2,2]} for f in FACES}}
  if rot:c.update(rotation=rot,pivot=list(pivot or self.by[n]['pivot']))
  if panel:
   # A contiguous four-pixel portrait tile gives a crisp two-colour inlay.
   found=False
   for y in range(6):
    for x in range(5):
     a,b=self.rows[y][x:x+2]
     if a!=b and a!='.' and b!='.' and 'W' not in (a,b):
      c['uv']['north']={'uv':[2+2*x,2+2*y],'uv_size':[4,2]};found=True;break
    if found:break
  self.by[n].setdefault('cubes',[]).append(c)
 def extra(self,n,parent,pivot,boxes,r=None):
  self.bone(n,parent,pivot,r)
  for o,s,k in boxes:self.cube(n,o,s,k)
 def save(self):
  # Topological order for editor and independent pose checks.
  ordered=[];pending=list(self.b);seen=set()
  while pending:
   ready=[b for b in pending if not b.get('parent') or b['parent'] in seen]
   assert ready,self.id
   for b in ready:ordered.append(b);seen.add(b['name']);pending.remove(b)
  self.g['bones']=ordered;self.b=ordered
  self.g['description'].update(texture_width=16,texture_height=16)
  for folder,ext,data in [('geo','.geo.json',self.doc),('animations','.animation.json',self.a)]:
   p=AS/folder/self.folder/(self.id+ext);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
  p=AS/'textures/entity'/self.folder/(self.id+'.png');p.parent.mkdir(parents=True,exist_ok=True);self.im.save(p)

def core(r):
 emperor=r.id=='undead_first_emperor';general=r.id=='rebel_general'
 if general:
  for n,p,v in [('root',None,[0,0,0]),('body','root',[0,15,0]),('pelvis','body',[0,12,0]),('waist','pelvis',[0,15,0]),('chest','waist',[0,18,0]),('neck','chest',[0,26,0]),('head','neck',[0,27,0]),('jaw','head',[0,27,-2]),('hat','head',[0,33,0])]:r.bone(n,p,v)
  for side,s in [('left',1),('right',-1)]:
   for n,p,v in [('arm','chest',[s*6.5,25,0]),('elbow',side+'_arm',[s*6.5,19,0]),('forearm',side+'_elbow',[s*6.5,19,0]),('hand',side+'_forearm',[s*6.5,13,-1]),('grip',side+'_hand',[s*6.5,12,-1]),('leg','pelvis',[s*3,12,0]),('foot',side+'_leg',[s*3,2,-1])]:r.bone(side+'_'+n,p,v)
 for b in r.b:b['cubes']=[]
 py=r.by['pelvis']['pivot'][1];cy=r.by['chest']['pivot'][1];hy=r.by['head']['pivot'][1]
 # Chest/waist/pelvis each have their own volume; narrowing under the rib cage.
 r.cube('pelvis',[-4,py-2,-3],[8,4,6],'A');r.cube('pelvis',[-4.5,py,-3.5],[9,2,7],'C',panel=True)
 wy=r.by['waist']['pivot'][1];r.cube('waist',[-2.8,wy-.6,-2.6],[5.6,cy-wy+1.1,5.2],'A')
 width=11 if emperor else 10 if general else 8.4
 r.cube('chest',[-width/2,cy+3,-3.7],[width,hy-cy-4,7.4],'B')
 r.cube('chest',[-width/2+.8,cy,-3],[width-1.6,3.1,6],'B')
 r.cube('chest',[-width/2,cy+3,-4.5],[width,3,1.1],'A',panel=True)
 if emperor:
  r.cube('coffin_plate',[-4.4,cy+.2,-4.4],[8.8,8.5,1.5],'A');r.cube('coffin_plate',[-2.7,cy+1,-5.2],[5.4,6.5,1],'C',panel=True)
  r.extra('back_shell','chest',[0,cy+4,3], [([-5,cy,3.4],[10,8,2.3],'A'),([-3,cy+1,5.5],[6,6,1],'C')])
 else:
  r.extra('lapel_left','chest',[-3,cy+5,-3.8],[([-3.3,cy+1,-4.2],[2,6,1],'C')],[0,0,-20])
  r.extra('lapel_right','chest',[3,cy+5,-3.8],[([1.3,cy+1,-4.3],[2,6,1],'A')],[0,0,20])
 r.cube('neck',[-1.5,hy-1,-1.5],[3,1.5,3],'C')
 r.cube('head',[-2.8,hy,-2.8],[5.6,5,5.1],'C');r.cube('head',[-2.8,hy+3,-3.4],[5.6,1,1],'A')
 r.cube('head',[-.8,hy+1,-4],[1.6,2,1.3],'C');r.cube('jaw',[-2,hy-.5,-3],[4,1.7,3.5],'A')
 for x in [-2.5,1]:r.cube('head',[x,hy+2.5,-3.6],[1.5,.8,.6],'A')
 if emperor:
  r.cube('hat',[-5,hy+5,-4],[10,1.2,8],'A');r.cube('hat',[-3,hy+6,-2],[6,2,4],'C')
  for i in range(5):r.cube('crown_bead_'+str(i),[-4.4+i*2,hy+2,-4.6],[.8,4,.8],'C')
 elif general:
  r.cube('hat',[-3,hy+4,-3],[6,1.5,6],'A');r.cube('hat',[-2.5,hy+5,-2.5],[5,1.8,5],'A');r.cube('hat',[-1,hy+6,-2],[2,3,4],'C')
  r.extra('helmet_flare','head',[0,hy+2,0],[([-3.6,hy,-.5],[1.2,4,4],'A'),([2.4,hy,-.5],[1.2,4,4],'A')])
  r.extra('banner_root','chest',[3,cy+6,4],[([2.5,cy+1,4],[1.5,14,1.5],'C')])
  r.extra('banner_cloth','banner_root',[3,cy+13,5],[([3,cy+6,4.2],[9,7,1],'B'),([3,cy+4,4.2],[5,2,1],'B'),([5,cy+8,3.5],[3,3,.8],'A')])
 else:
  r.cube('hat',[-3.5,hy+5,-3],[7,1,6],'A');r.cube('hat',[-2.5,hy+6,-2],[5,4,4],'A');r.cube('hat',[-1,hy+6,-2.6],[2,3,1],'C')
  r.extra('hat_wings','hat',[0,hy+6,0],[([-7,hy+6,-.5],[4,1.5,1.5],'A'),([3,hy+6,-.5],[4,1.5,1.5],'A')])
  r.cube('mask',[-2.4,hy,-3.5],[4.8,2,1],'A')
  r.extra('raised_collar','chest',[0,hy-1,2],[([-4,hy-3,1.5],[8,4,1.7],'A'),([-4.3,hy-3,-1],[1.5,3,3],'B'),([2.8,hy-3,-1],[1.5,3,3],'B')])
  r.cube('ritual_case',[-2,cy,3.5],[4,8,3],'A');r.cube('ritual_case',[-1,cy+1,6.2],[2,6,1],'C')
 for side,s in [('left',1),('right',-1)]:
  x,ay,_=r.by[side+'_arm']['pivot'];fy=r.by[side+'_forearm']['pivot'][1];handy=r.by[side+'_hand']['pivot'][1]
  r.cube(side+'_arm',[x-1.6,fy,-2],[3.2,ay-fy,4],'B')
  r.cube(side+'_forearm',[x-1.7,handy,-2],[3.4,fy-handy,4],'C' if not general else 'A')
  r.cube(side+'_hand',[x-1.7,handy-2,-2.4],[3.4,2.5,3.8],'C')
  if emperor or general:
   n=r.bone('mantle_'+side,'chest',[x,ay,0]);r.cube(n,[x-3,ay-1,-3.8],[6,2,7.6],'A');r.cube(n,[x-2.5,ay+1,-3.2],[5,1.4,6.4],'C')
   r.cube(n,[x+(1.8 if s>0 else -3.4),ay-3,-3.4],[1.6,3,6.8],'B')
  else:
   r.cube(side+'_sleeve',[x-2.7,handy-1,-1.6],[5.4,7,5.6],'B');r.cube(side+'_sleeve',[x-2.9,handy-1,-2],[5.8,1.7,6],'A',panel=True)
  lx,ly,_=r.by[side+'_leg']['pivot'];knee=(ly+2)/2
  r.cube(side+'_leg',[lx-1.5,knee,-1.7],[3,ly-knee,3.4],'A')
  r.bone(side+'_knee',side+'_leg',[lx,knee,0]);r.cube(side+'_knee',[lx-1.6,2,-2],[3.2,knee-2,4],'A');r.cube(side+'_knee',[lx-1.9,knee-1,-2.7],[3.8,2,1.5],'C')
  r.by[side+'_foot']['parent']=side+'_knee';r.cube(side+'_foot',[lx-1.9,0,-3.7],[3.8,2,5.5],'A')
  skirt='coffin_skirt_'+side if emperor else side+'_robe'
  r.bone(skirt,'pelvis',[s*3,py+1,0]);r.cube(skirt,[s*3-2,py-5,-3.8],[4,5,1.4],'B');r.cube(skirt,[s*3-2.5,2,-4.3],[5,py-7,1.6],'B');r.cube(skirt,[s*3-2,2,3],[4,py-2,1.5],'A')
  r.extra('side_robe_'+side,'pelvis',[s*4,py,0],[([s*4-1,2,-2.5],[2,py-2,5.5],'B')])
 if general:
  def ch(v):return {'rotation':{str(t):p for t,p in v}}
  for name,L,loop in [('idle',2,True),('walk',1,True),('attack',.8,False),('cast',1.2,False),('hurt',.35,False),('death',.7,False)]:
   b={}
   if name in ['idle','walk']:
    b['chest']=ch([(0,[2,0,-1]),(L/2,[3,0,1]),(L,[2,0,-1])])
    if name=='walk':
     for side,s in [('left',1),('right',-1)]:b[side+'_leg']=ch([(0,[s*20,0,0]),(L/2,[-s*20,0,0]),(L,[s*20,0,0])]);b[side+'_arm']=ch([(0,[-s*12,0,0]),(L/2,[s*12,0,0]),(L,[-s*12,0,0])])
   elif name=='death':b={'body':ch([(0,[0,0,0]),(.2,[0,0,12]),(.7,[0,0,90])])}
   else:
    b={'chest':ch([(0,[0,0,0]),(L*.45,[-6,-24,0]),(L*.58,[12,18,0]),(L,[0,0,0])]),'right_arm':ch([(0,[0,0,0]),(L*.45,[-125,10,-15]),(L*.58,[-30,-10,0]),(L,[0,0,0])]),'right_elbow':ch([(0,[0,0,0]),(L*.45,[-38,0,0]),(L,[0,0,0])])}
   r.a['animations'][name]={'loop':loop,'animation_length':L,'bones':b}
 # Secondary channels preserve original attack/cast durations and hit timing.
 for name,a in r.a['animations'].items():
  L=a['animation_length'];bs=a['bones']
  if name=='walk':
   for side,s in [('left',1),('right',-1)]:bs[side+'_knee']={'rotation':{'0':[16 if s>0 else 0,0,0],str(L/2):[0 if s>0 else 16,0,0],str(L):[16 if s>0 else 0,0,0]}}
  if general:bs['banner_cloth']={'rotation':{'0':[3,0,0],str(L/2):[-5,0,0],str(L):[3,0,0]}}

def headless(r):
 r.clear('chest','chest_front','chest_back')
 r.cube('chest',[-7,25,-4.5],[14,4,9],'B');r.cube('chest',[-8,29,-5],[16,8,10],'B')
 r.cube('chest_front',[-7,26,-6.4],[14,6,1.8],'A',panel=True);r.cube('chest_front',[-8.5,32,-7],[17,4,2.2],'A');r.cube('chest_front',[-6.5,36,-6],[13,1.8,1.7],'C')
 r.cube('chest_back',[-7.5,28,4.8],[15,8,2],'A');r.cube('chest_back',[-5,30,6.3],[10,4,1.2],'C',panel=True)
 r.extra('broken_gorget','chest',[0,38,0],[([-5,36,-5],[10,2,2],'A'),([-5,36,3],[10,2,2],'A'),([-5,36,-3],[2,3,6],'C'),([3,36,-3],[2,3,6],'C')])
 # Existing blade, carried head and original four-piece grip are retained.
 for side,s in [('left',1),('right',-1)]:
  r.extra('segmented_tasset_'+side,'pelvis',[s*5,18,-5],[([s*5-2.2,12,-6.4],[4.4,5,1.8],'B'),([s*5-2.5,9,-6.8],[5,3,2],'A')])
  n=side+'_beast_shoulder';r.cube(n,[s*10-2,34,-5.6],[4,2,1.5],'C',panel=True)

def mechanist(r):
 r.clear('chest','head','backpack')
 r.cube('chest',[-4.5,17,-3.2],[9,4,6.4],'B');r.cube('chest',[-5.5,21,-3.7],[11,4,7.4],'B')
 r.cube('chest',[-4,18,-4.6],[8,5,1.5],'A',panel=True)
 r.cube('head',[-3,25.5,-3.3],[6,5.2,5.8],'C');r.cube('head',[-3,25.5,-4],[6,1.6,1.1],'A')
 r.cube('backpack',[-4,14.5,3.5],[8,13,7.7],'A');r.cube('backpack',[-3,17,10.6],[6,8,1.5],'C',panel=True)
 for x in [-4,2]:r.cube('backpack',[x,15,10.3],[2,11,2],'B')
 r.extra('tool_hood','head',[0,29,0],[([-3.6,30,-3.4],[7.2,1.6,6.4],'A'),([-2.6,31.5,-2],[5.2,1,4],'B')])
 # Fan the existing six-arm rig outward; retain all names, pivots, parents and clips.
 for i in range(4):
  side=1 if i%2==0 else -1;r.by['aux_'+str(i)]['rotation']=[0,0,side*(28 if i<2 else -22)]
 r.extra('pressure_stack','backpack',[3,25,6],[([2,25,5],[2.5,7,2.5],'A'),([1.5,31,4.5],[3.5,1.5,3.5],'C')])
 for side,s in [('left',1),('right',-1)]:r.extra('apron_lap_'+side,'pelvis',[s*3,14,-3],[([s*3-2,6,-4.2],[4,8,1.5],'B'),([s*3-1,7,-4.7],[2,3,.8],'C')])

def jinwu(r):
 r.clear('chest','head','helmet_crest')
 r.cube('chest',[-5,21,-3.4],[10,3,6.8],'A');r.cube('chest',[-6,24,-4],[12,5,8],'A');r.cube('chest',[-4.5,22,-5],[9,6,1.5],'C',panel=True)
 for b in r.b:
  if b['name'].startswith('scale_'):b['cubes']=[]
 r.cube('head',[-3.4,30,-3.3],[6.8,5.6,6.6],'A');r.cube('head',[-3,31,-4],[6,3,.9],'C',panel=True);r.cube('head',[-1,30.5,-5],[2,3,1.2],'C')
 for s in [-1,1]:r.cube('head',[s*3-1,30,0],[2,4,4],'A')
 r.cube('helmet_crest',[-1,35,-3],[2,4,6],'C');r.cube('helmet_crest',[-1,37,1],[2,3,5],'B');r.cube('helmet_crest',[-1,36,5],[2,2,3],'B')
 for side,s in [('left',1),('right',-1)]:
  r.extra('collar_'+side,'chest',[s*4,28,0],[([s*4-1,27,1],[2,4,3],'C')])
  r.extra('lamellar_hip_'+side,'pelvis',[s*5,17,0],[([s*5-1.5,11,-3.6],[3,6,1.7],'C'),([s*5-2,8,-4],[4,3,1.8],'A')])
 # IK-authored hands/shaft keyframes are intentionally untouched.

def fox(r):
 r.clear('head','hair_bun','chest','skirt_left','skirt_right','fan')
 r.cube('chest',[-3.5,17,-2.5],[7,3,5],'B');r.cube('chest',[-4,20,-3],[8,3,6],'B');r.cube('chest',[-1.5,17,-3.6],[3,6,1],'C',panel=True)
 r.cube('head',[-3,24,-2.8],[6,5,5.6],'W');r.cube('head',[-3.4,24,1.7],[6.8,6,2],'A');r.cube('head',[.7,26,-3.2],[1.8,1,.8],'A')
 r.cube('hair_bun',[-2,29,-1],[4,3,3.5],'A');r.cube('hair_bun',[-5,29,0],[10,1.4,1.6],'C')
 r.extra('hair_fall','head',[0,28,2],[([-3,20,2.5],[6,7,1.7],'A'),([-2,18,3],[4,3,1.5],'A')])
 for side,s in [('left',1),('right',-1)]:
  x=s*3;r.cube('skirt_'+side,[x-2,6,-3.1],[4,6,6.2],'B');r.cube('skirt_'+side,[x-3,0,-3.6],[6,6,7.2],'B');r.cube('skirt_'+side,[x-3,0,-4],[6,1.6,1],'A');r.cube('skirt_'+side,[x-1,1,-4],[2,9,1],'C')
  r.extra('hanging_sleeve_'+side,side+'_forearm',[s*5.5,16,0],[([s*5.5-2.4,8,.5],[4.8,7,3],'B'),([s*5.5-2.6,7.5,.3],[5.2,2,3.5],'A')])
 r.cube('fan',[4.8,7,-.5],[1.4,5,1],'C')
 for x,y,w in [(1.5,11,8),(2.5,13,6),(3.5,15,4)]:r.cube('fan',[x,y,-.9],[w,2,1.6],'W')
 r.cube('fan',[3.5,12,-1.6],[4,2,1],'B',panel=True)
 # Three tails and the existing same-actor death fox remain intact.

def hammer(r):
 r.clear('chest','head')
 r.cube('chest',[-6.7,25,-4.4],[13.4,4,8.8],'B');r.cube('chest',[-8,29,-5.3],[16,7,10.6],'B')
 r.cube('chest',[-8.5,30,-6],[17,5,1.7],'C',panel=True);r.cube('chest',[-6,26,-5.5],[12,4,1.6],'A');r.cube('chest',[-3,28,-6.5],[6,6,1.3],'C',panel=True)
 r.cube('chest',[-7.5,28,5],[15,7,1.8],'C');r.cube('chest',[-3.5,29,6.3],[7,5,1.5],'A',panel=True)
 r.cube('head',[-3.5,37.5,-3.6],[7,6,7.2],'B');r.cube('head',[-4,40,-4],[8,2.5,8],'C');r.cube('head',[-2.7,38,-4.5],[5.4,2,1.2],'A');r.cube('head',[-1,41,-4.6],[2,4,1.3],'C')
 for s in [-1,1]:r.cube('head',[s*3-1,36.5,-2],[2,3,5],'A')
 r.extra('ridge_helmet','head',[0,43,0],[([-3,43,-3],[6,1.5,6],'A'),([-1,44,-2],[2,2,4],'C')])
 for side,s in [('left',1),('right',-1)]:
  x=s*10.5;r.cube(side+'_shoulder',[x-3,31,-5.2],[6,3,1.5],'A',panel=True)
  r.cube(side+'_forearm',[x-2.8,18,-4.3],[5.6,3,1.5],'C')
  # Socket visually encloses the existing shaft; weapon pivots stay on the hand.
  r.cube(side+'_hand',[x-2.1,14.5,-5],[4.2,2.5,1.7],'A')
  n=side+'_hammer';p=r.by[n]['pivot'];r.cube(n,[p[0]-3,5.5,-9.7],[6,6,1],'A',panel=True)

def enrich(r):
 for name,a in r.a['animations'].items():
  short=name.rsplit('.',1)[-1];L=a['animation_length'];bs=a['bones']
  if short in ['idle','walk'] and r.id not in ['pilin_zhijinwu']:
   if r.id=='qianji_bailian_yanshi':
    for i in range(4):bs['aux_'+str(i)+'_elbow']={'rotation':{'0':[0,0,(-1 if i%2 else 1)*8],str(L/2):[0,0,(-1 if i%2 else 1)*17],str(L):[0,0,(-1 if i%2 else 1)*8]}}
   if r.id=='juchui_jinjia_lishi' and short=='walk':
    for side,s in [('left',1),('right',-1)]:bs[side+'_knee']={'rotation':{'0':[16 if s>0 else 0,0,0],str(L/2):[0 if s>0 else 16,0,0],str(L):[16 if s>0 else 0,0,0]}}
   if r.id=='baimian_huxiangu':bs['hair_fall']={'rotation':{'0':[3,0,0],str(L/2):[-4,0,0],str(L):[3,0,0]}}
 # Non-contact recoil only; retain every elite skill's original timing and grip tracks.
 if r.id in ['xianzhen_duantoujiang','qianji_bailian_yanshi']:
  for name,a in r.a['animations'].items():
   if name.endswith('.hurt'):a['bones'].setdefault('waist_upper',{'rotation':{'0':[0,0,0],str(a['animation_length']*.25):[-7,0,4],str(a['animation_length']):[0,0,0]}})

def polish(r):
 from cull_internal_faces import cull
 from rig_bounds import sample
 if r.id in ['undead_first_emperor','eunuch_mastermind','rebel_general']:
  r.by['chest']['rotation']=[9 if r.id=='eunuch_mastermind' else 4,0,0]
  for side,s in [('left',1),('right',-1)]:
   r.by[side+'_forearm']['rotation']=[-24 if r.id=='eunuch_mastermind' else -12,0,s*5]
  if r.id=='eunuch_mastermind':
   r.by['left_arm']['rotation']=[-20,0,10]
   r.extra('court_sash','waist',[0,14,-3],[([-2,8,-4.5],[4,6,1.3],'C'),([-1,5,-4.8],[2,3,1.4],'A')])
 if r.id=='qianji_bailian_yanshi':
  for i in range(4):
   n='aux_'+str(i);s=1 if i%2==0 else -1;r.by[n]['rotation']=[0,0,s*(-24 if i<2 else 20)]
   for b in r.b:
    if b['name']==n or b['name'].startswith(n+'_'):
     b['pivot'][0]=s*4+(b['pivot'][0]-s*4)*1.35
     for c in b.get('cubes',[]):c['origin'][0]=s*4+(c['origin'][0]-s*4)*1.35;c['size'][0]*=1.35
 # Separate previously coincident armour surfaces by < 0.03 model units.
 # Same-bone fully enclosed faces are removed first; animated joints are never culled together.
 cull(r.doc)
 index=0
 for b in r.b:
  for c in b.get('cubes',[]):
   index+=1;epsilon=index*.0002
   c['origin']=[round(x-epsilon,5) for x in c['origin']];c['size']=[round(x+2*epsilon,5) for x in c['size']]
 # Sort before kinematics, since added knee/cloth bones can parent existing parts.
 pending=list(r.b);ordered=[];seen=set()
 while pending:
  ready=[b for b in pending if not b.get('parent') or b['parent'] in seen];assert ready
  for b in ready:ordered.append(b);seen.add(b['name']);pending.remove(b)
 r.b=ordered;r.g['bones']=ordered
 death=next(a for n,a in r.a['animations'].items() if n.rsplit('.',1)[-1]=='death');ch=death['bones'];L=death['animation_length']
 if r.id=='qianji_bailian_yanshi':
  # The disabled six-arm mechanism collapses on its side after the box opens.
  ch['root'].pop('position',None);ch['root']['rotation']={'0':[0,0,0],'1.1':[0,0,12],'2.1':[0,0,82],str(L):[0,0,82]}
 if r.id=='juchui_jinjia_lishi':
  for side,s in [('left',1),('right',-1)]:
   n='dropped_'+side+'_hammer';r.by[n]['rotation']=[0,0,s*90]
   ch[n]={'position':[0,0,0]}
 if r.id=='baimian_huxiangu':
  # Keep the compressed robe above the floor; the escaping fox remains independently grounded.
  ch['robe_root']['position']={'0':[0,0,0],'1.2':[0,.04,0],str(L):[0,.04,0]}
  return
 # Correct world-floor contact against actual visible Cuboids, not a hard-coded root height.
 old=copy.deepcopy(ch.get('root',{}).get('position',[0,0,0]));ch.setdefault('root',{}).pop('position',None)
 body=copy.deepcopy(r.b)
 hidden={'dropped_left_hammer','dropped_right_hammer'} if r.id=='juchui_jinjia_lishi' else set()
 for b in body:
  if b['name'] in hidden:b['cubes']=[]
 steps=round(L*80);positions={}
 for i in range(steps+1):
  t=L*i/steps;oldpos=sample(old,t);ch['root']['position']=oldpos
  if r.id=='juchui_jinjia_lishi' and t>=.6:
   for b in body:
    if b['name'] in ['left_hammer','right_hammer']:b['cubes']=[]
  low=min(v[1] for v in vertices(body,ch,t));positions[str(round(t,5))]=[oldpos[0],round(oldpos[1]+.025-low,5),oldpos[2]]
 ch['root']['position']=positions
 if r.id=='juchui_jinjia_lishi':
  for side in ['left','right']:
   n='dropped_'+side+'_hammer';only=copy.deepcopy(r.b)
   for b in only:
    if b['name']!=n:b['cubes']=[]
   vals={}
   for i in range(steps+1):
    t=L*i/steps;ch[n]['position']=[0,0,0];lo=min(v[1] for v in vertices(only,ch,t));vals[str(round(t,5))]=[0,round(.025-lo,5),0]
   ch[n]['position']=vals


for id in TARGETS:
 r=Art(id)
 if id in ['undead_first_emperor','eunuch_mastermind','rebel_general']:core(r)
 else:{'xianzhen_duantoujiang':headless,'qianji_bailian_yanshi':mechanist,'pilin_zhijinwu':jinwu,'baimian_huxiangu':fox,'juchui_jinjia_lishi':hammer}[id](r)
 enrich(r);polish(r);r.save()
 print(id,len(r.b),'bones',sum(len(b.get('cubes',[])) for b in r.b),'cuboids')
# The existing thrown hammer shares the guardian's atlas: remap its UVs as well.
id='juchui_jinjia_lishi';r=Art(id)
p=Path('src/main/resources/assets/dynasty/geo/blueprint/elite/hammer_chain.geo.json')
doc=json.loads((HERE/'baseline'/p).read_text());old=Image.open(HERE/'baseline/src/main/resources/assets/dynasty/textures/entity/blueprint/elite/juchui_jinjia_lishi.png').convert('RGB')
pals=[ImageColor.getrgb(c) for c in r.palette]
for b in doc['minecraft:geometry'][0]['bones']:
 for c in b.get('cubes',[]):
  for face,v in c['uv'].items():
   rgb=old.getpixel((int(v['uv'][0]+v['uv_size'][0]/2),int(v['uv'][1]+v['uv_size'][1]/2)));k='ABC'[min(range(3),key=lambda i:sum((rgb[j]-pals[i][j])**2 for j in range(3)))];c['uv'][face]={'uv':r.islands[k],'uv_size':[2,2]}
(ROOT/p).write_text(json.dumps(doc,indent=2)+'\n')
