"""Original stone guardian, bronze-winged demon and silt spirit surfaces."""
import math
from PIL import Image
from creature_surfaces import shrink
IDS=('jubi_shigandang','tongbi_feitian_yecha','shashui_funigui')
def forms(name,g):
 for b in g['bones']:
  n=b['name'];cs=b.get('cubes',[])
  if name==IDS[0]:
   if n in ['foot','body','waist','chest','left_stump','right_shoulder','right_upper','right_elbow','right_fist']:
    index=2 if n=='foot' else 1
    if len(cs)>index:shrink(cs[index],[.92,.5,.92])
   if n=='waist':shrink(cs[0],[1.12,1,1.12])
   elif n=='head':shrink(cs[1],[.94,.65,.94])
   elif n=='face':
    for c in cs:shrink(c,[1,1,.45])
  elif name==IDS[1]:
   if n in ['torso','waist','chest']:
    shrink(cs[1],[.92,.5,.92])
    if n=='waist':shrink(cs[0],[1.1,1,1.15])
   elif '_wing_' in n:
    shrink(cs[0],[1,.65,.55],True)
    for c in cs[1:]:shrink(c,[1,1,.3])
   elif n.startswith('giant_arm_'):
    shrink(cs[0],[1,1.05,1]);shrink(cs[1],[.87,.45,.85]);shrink(cs[2],[1,1,.4])
   elif n=='head':
    shrink(cs[1],[.94,.65,.8])
    for j in [2,3]:shrink(cs[j],[1,1,.45])
   elif n.endswith('_thigh'):shrink(cs[1],[.8,.55,.6])
  else:
   if n=='body':shrink(cs[1],[1.12,1,1.12])
   elif n in ['pelvis','waist']:
    shrink(cs[0],[1.1,1,1.1]);shrink(cs[1],[.9,.5,.9])
   elif n=='wave_1':
    shrink(cs[0],[1.05,1,1.08]);shrink(cs[1],[.9,.7,.5])
   elif n=='wave_2':
    shrink(cs[1],[.9,.5,.85]);shrink(cs[5],[.65,.7,.4])
    for c in cs[2:5]:shrink(c,[1,1,.4])
   elif n.startswith('hair_'):
    for c in cs:shrink(c,[.75,1,.5])
   elif '_whip_0' in n:shrink(cs[1],[.8,.5,.7])
 return g

def stone(n,j,f,u,v,w,h,c):
 X=int(c['origin'][0]+u);Y=int(c['origin'][1]+h-1-v)
 if n.startswith('chain_'):return (107,100,67) if f=='up' else (65,70,59)
 if n=='inscription':return (158,140,82) if f=='north' else (100,102,73)
 if n=='face':
  if j<2:return (162,159,101) if f=='north' and u==w//2 else (53,65,57)
  return (65,77,64)
 base=(142,150,130) if f=='up' else (113,127,112) if f in ['north','east'] else (96,111,101)
 # Rock strata continue at a common height, with selected discontinuities.
 if Y in [14,15,25] and X%13<6 and n not in ['head','neck']:base=(91,108,95)
 if n=='right_fist' and j==0 and f=='down':
  base=(113,127,113)
  if (u<3 and v<6) or (u>w-4 and v>h-6):base=(159,164,143)
  if v==h//2+u//5 and 3<u<w-2:base=(77,94,84)
  if v==h//2+u//5+1 and 3<u<w-2:base=(137,148,129)
 if n=='right_fist' and f=='north':
  if j>=2:return (164,167,143) if v<2 else (124,139,119)
  if v>h-3 and (u<4 or u>w-4):base=(153,158,136)
 if n in ['head','right_shoulder','left_stump'] and f=='up' and (X//3)%4==0:base=(107,127,89)
 if n=='foot' and j==0 and v>h-2:base=(77,97,73)
 return base

def demon(n,j,f,u,v,w,h,c):
 if '_wing_' in n:
  if j==0:return (116,131,104) if f=='up' else (65,86,76)
  # Parallel feather vanes along the existing long panels, no extra tiny cubes.
  col=(51,65,70) if v<h//2 else (36,49,57)
  if u==w//2:col=(85,105,96)
  elif (v+u//2)%5==0 and v>1:col=(67,84,82)
  return col
 if n.startswith('giant_arm_') or n=='palm':
  if j==1:return (109,87,51) if f!='up' else (159,129,72)
  if j==2:return (74,91,70)
  if f=='up':return (166,135,78)
  if f=='down':return (89,70,45)
  return (146,111,61) if u<w//2 else (124,94,54)
 if n.startswith('finger_'):return (166,145,95) if j else (124,99,60)
 if n=='head':
  if j in [2,3]:return (174,151,85) if f=='north' and u==w//2 else (34,52,48)
  if j==4:return (155,163,121) if v==0 else (56,74,66)
  if j>=5:return (177,173,124) if f=='up' else (116,133,101)
  return (112,145,119) if f=='up' else (80,116,100)
 if n in ['chest','torso','waist']:
  if j==0:return (56,76,76) if f in ['north','east'] else (42,60,65)
  if j==1:return (79,102,91)
  return (105,135,110) if v<h//2 else (71,103,90)
 if n.endswith('_shin') and j>=2:return (164,165,121)
 return (79,107,92) if f=='up' else (57,85,78)

def silt(n,j,f,u,v,w,h,c):
 Y=int(c['origin'][1]+h-1-v);X=int(c['origin'][0]+u)
 if n.startswith('hair_'):
  return (37,62,60) if u==0 else (49,82,73) if f=='north' else (32,54,55)
 if n=='wave_2':
  if j in [2,3]:return (164,177,132) if f=='north' else (51,85,76)
  if j==4:return (36,67,65)
  if j==5:return (81,124,107)
  return (100,144,120) if f=='up' else (72,117,104)
 if n=='body':
  col=(71,91,66) if f=='up' else (58,76,59)
  if f=='up' and j==0:
   # Broad sediment arcs with gaps, not a random noise field.
   rad=max(abs(X),abs(int(c['origin'][2]+v)))
   if rad in [5,6] and X>-5:col=(96,113,78)
  return col
 if n in ['wave_1','pelvis','waist','neck'] or '_whip_' in n or '_spray_' in n:
  col=(66,107,93) if f in ['north','up','east'] else (46,81,77)
  # Flow bands use common height coordinates across the trunk and arms.
  stripe=(Y+X//3)%12
  if stripe in [1,2]:col=(86,131,106)
  elif stripe==0:col=(54,95,86)
  if Y<8:col=(62,88,66) if stripe>2 else (86,107,75)
  return col
 return (64,102,89)
PAINTERS=dict(zip(IDS,[stone,demon,silt]))

def finish(name,geo,image):
 if name not in IDS:return image
 g=forms(name,geo['minecraft:geometry'][0]);faces=[]
 for b in g['bones']:
  for j,c in enumerate(b.get('cubes',[])):
   sx,sy,sz=c['size'];c['uv']={}
   for f,(a,z) in {'north':(sx,sy),'south':(sx,sy),'east':(sz,sy),'west':(sz,sy),'up':(sx,sz),'down':(sx,sz)}.items():
    w,h=max(1,math.ceil(a)),max(1,math.ceil(z));faces.append((h,w,b['name'],j,c,f))
 faces.sort(key=lambda v:(-v[0],-v[1]));width=256;atlas=Image.new('RGB',(width,1024),(31,35,29));x=y=1;row=0
 for h,w,n,j,c,f in faces:
  if x+w+1>width:x=1;y+=row+2;row=0
  tile=Image.new('RGB',(w,h));tile.putdata([PAINTERS[name](n,j,f,u,v,w,h,c) for v in range(h) for u in range(w)])
  atlas.paste(tile,(x,y));c['uv'][f]={'uv':[x,y],'uv_size':[w,h]};x+=w+2;row=max(row,h)
 height=2**math.ceil(math.log2(y+row+2));assert height<=1024
 atlas=atlas.crop((0,0,width,height));g['description'].update(texture_width=width,texture_height=height)
 return atlas
