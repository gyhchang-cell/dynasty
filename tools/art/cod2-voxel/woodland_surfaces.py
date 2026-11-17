"""Anatomical bark, carved shell and skull study. Original pixel painting."""
import math
from PIL import Image
from creature_surfaces import shrink
IDS=('juli_bixi_kuilei','kumu_shujing','muxue_feilu')
def forms(name,g):
 for b in g['bones']:
  n=b['name'];cs=b.get('cubes',[])
  if name==IDS[0]:
   if n=='shell':
    shrink(cs[1],[.96,.55,.96],True)
    shrink(cs[2],[1.08,1,1.08]);shrink(cs[3],[1.1,1,1.1])
   elif n.startswith('scutes_'):
    shrink(cs[0],[.9,.55,1]);shrink(cs[1],[.8,.4,.9])
    cs[1]['origin'][1]=cs[0]['origin'][1]+cs[0]['size'][1]-.1
   elif n.endswith('_hip') and len(cs)>1:shrink(cs[1],[.85,.55,.85])
   elif n.endswith('_foot'):shrink(cs[0],[.88,.85,.85],True)
   elif n=='neck_base':shrink(cs[0],[1.1,1,1.15]);shrink(cs[1],[.8,.5,1])
   elif n=='head':
    for i in [2,3]:shrink(cs[i],[.8,.5,1])
  elif name==IDS[1]:
   if n in ['middle_log','upper_log']:shrink(cs[0],[1.05,1,1.03])
   elif n=='lower_log':shrink(cs[1],[.94,.65,1],True)
   elif n.endswith('_root_club'):
    shrink(cs[1],[.88,.4,.88]);cs[1]['origin'][1]=cs[0]['origin'][1]+1
   elif n.startswith('fungus_'):
    for c in cs:shrink(c,[1,.5,1],True)
   elif n=='tree_heart':
    for c in cs[1:]:shrink(c,[1,.8,.45])
   elif n.startswith('crown_branch'):
    for c in cs:shrink(c,[1,1,.8])
  else:
   if n=='head':
    for j in [4,5,6]:shrink(cs[j],[1,1,.4])
    for j in [7,8,9]:shrink(cs[j],[.85,.7,.7])
   elif n=='helmet':
    shrink(cs[0],[.97,.7,.96],True);shrink(cs[1],[.95,.6,.95],True);shrink(cs[2],[.95,.6,.6],True)
   elif n=='brow':
    for c in cs:shrink(c,[1,.7,.55])
   elif n.startswith('viscera_'):
    for c in cs:shrink(c,[.75,1.1,.75])
 return g

def bixi(n,j,f,u,v,w,h,c):
 X=int(c['origin'][0]+u);Y=int(c['origin'][1]+h-1-v);Z=int(c['origin'][2]+(v if f in ('up','down') else u))
 if 'piston' in n:return (66,75,70) if u in (0,w-1) else (94,105,95)
 if n=='stele':
  if j in [3,4,5]:return (128,145,112)
  if f in ['north','south'] and j==0:
   if u in [3,w-4] and 2<v<h-2:return (64,79,66)
   if 4<u<w-4 and v in [3,6]:return (83,99,79)
  return (142,148,121) if f=='up' else (113,126,107)
 if n=='head' and j in [6,7]:return (198,169,84) if u else (55,65,49)
 if n in ['shell','plastron'] or n.startswith('scutes_'):
  if n=='plastron':return (124,128,96) if f!='down' else (89,96,72)
  base=(128,139,113) if f=='up' else (105,119,101)
  if n.startswith('scutes_'):base=(146,132,83) if f=='up' else (116,107,74)
  if f=='up':
   # Plates cross cube boundaries in world coordinates; no individual box borders.
   seam=(X+((Z//8)%2)*4)%8==0 or Z%8==0
   if seam:return (83,99,83)
   if Z%8==1:return (148,155,123)
  return base
 if n=='jaw':return (135,139,105) if f!='down' else (87,101,78)
 if 'foot' in n and j:return (151,153,116)
 if n=='head' and j in [2,3]:return (83,103,74)
 return (138,146,114) if f=='up' else (112,127,103)

def tree(n,j,f,u,v,w,h,c):
 if n=='tree_heart':
  if j in [1,2]:return (186,162,83) if f=='north' else (72,66,39)
  if j==3:return (48,43,30)
  return (64,54,35) if f=='north' else (79,67,41)
 if 'fungus' in n:
  return (160,120,71) if f=='up' else (114,83,49) if f=='down' else (191,155,96)
 horizontal='branch' in n and c['size'][0]>c['size'][1]
 axis=max(range(3),key=lambda k:c['size'][k]);end=(axis==0 and f in ['east','west']) or(axis==1 and f in ['up','down']) or(axis==2 and f in ['north','south'])
 if end:
  a=min(u,w-1-u);b=min(v,h-1-v)
  return (155,120,70) if min(a,b)>1 else (100,77,43)
 world=int(c['origin'][0]+u) if not horizontal else int(c['origin'][1]+h-1-v)
 along=int(c['origin'][1]+h-1-v) if not horizontal else int(c['origin'][0]+u)
 ridge=world%6
 col=(104,79,45)
 if ridge in [0,1]:col=(76,59,36)
 elif ridge==3:col=(131,99,54)
 # Broken bark grooves follow grain rather than enclosing each cuboid.
 if along%17 in [0,1] and ridge in [0,1,2]:col=(62,50,32)
 if ('lower' in n or 'root' in n) and along<5 and ridge in [2,3,4]:col=(79,91,49)
 return col

def skull(n,j,f,u,v,w,h,c):
 if n.startswith('viscera_') or n=='neck_stump':
  return (89,45,43) if u==0 else (127,64,54) if f in ['north','east'] else (100,51,46)
 if 'helmet' in n:
  if 'spike' in n:return (107,116,104) if f=='up' else (67,78,75)
  if f=='up':return (91,104,98)
  return (58,74,73) if v>0 else (117,126,108)
 if n=='brow':return (159,159,119) if f=='up' else (116,124,95)
 if n=='head':
  if j in [4,5]:
   if f=='north' and u==w//2 and v==h//2:return (163,105,62)
   return (45,54,45)
  if j==6:return (66,76,59)
  if j>=7:return (190,185,140) if f!='down' else (113,123,92)
  if j==1:return (149,154,114) if v<h//2 else (125,137,104)
  return (175,175,132) if f=='up' else (154,161,121) if f in ['north','east'] else (126,139,107)
 if n=='jaw':return (182,181,136) if j>=3 else (129,143,106) if v==h-1 else (163,170,126)
 return (141,151,111)

PAINTERS=dict(zip(IDS,[bixi,tree,skull]))
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
