"""Read-only source UV study. Software output is NOT Minecraft or wearing QA."""
from pathlib import Path
import math,json
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent
T=B/'source/src/main/resources/assets/wizards_reborn/textures/models/armor'
textures={i:Image.open(T/f'arcane_gold_layer_{i}.png').convert('RGBA') for i in (1,2)}
# Default HumanoidModel cube origins plus idle parent offsets; both armor layers.
boxes=[('head',[-4,-8,-4],[8,8,8],[0,0],False,1,1),('hat',[-4,-8,-4],[8,8,8],[32,0],False,1.5,1),('body',[-4,0,-2],[8,12,4],[16,16],False,1,1),('right_arm',[-8,0,-2],[4,12,4],[40,16],False,1,1),('left_arm',[4,0,-2],[4,12,4],[40,16],True,1,1),('right_boot',[-3.9,12,-2],[4,12,4],[0,16],False,.9,1),('left_boot',[-.1,12,-2],[4,12,4],[0,16],True,.9,1),('waist',[-4,0,-2],[8,12,4],[16,16],False,.5,2),('right_leg',[-3.9,12,-2],[4,12,4],[0,16],False,.4,2),('left_leg',[-.1,12,-2],[4,12,4],[0,16],True,.4,2)]
face_indices={'DOWN':[5,4,0,1],'UP':[2,3,7,6],'WEST':[0,4,7,3],'NORTH':[1,0,3,2],'EAST':[5,1,2,6],'SOUTH':[4,5,6,7]}
def cube_faces(box):
 name,origin,size,uv,mirror,inflate,layer=box;x,y,z=origin;w,h,d=size;u,v=uv
 x0,y0,z0=x-inflate,y-inflate,z-inflate;x1,y1,z1=x+w+inflate,y+h+inflate,z+d+inflate
 if mirror:x0,x1=x1,x0
 vertices=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]]
 rects={'DOWN':[u+d,v,u+d+w,v+d],'UP':[u+d+w,v+d,u+d+w+w,v],'WEST':[u,v+d,u+d,v+d+h],'NORTH':[u+d,v+d,u+d+w,v+d+h],'EAST':[u+d+w,v+d,u+d+w+d,v+d+h],'SOUTH':[u+d+w+d,v+d,u+d+w+d+w,v+d+h]}
 result=[]
 for face,ids in face_indices.items():
  u1,v1,u2,v2=rects[face];pixels=[[u2,v1],[u1,v1],[u1,v2],[u2,v2]];coords=[vertices[i] for i in ids]
  if mirror:coords=coords[::-1];pixels=pixels[::-1]
  result.append((coords,pixels,layer))
 return result,rects

def render(angle,mode='texture'):
 W,H=220,300;out=Image.new('RGB',(W,H),(101,108,112));depth=[[float('inf')]*W for _ in range(H)]
 a=math.radians(angle);co,si=math.cos(a),math.sin(a)
 def cross(a,b):return a[0]*b[1]-a[1]*b[0]
 def sub(a,b):return [a[0]-b[0],a[1]-b[1]]
 for box in boxes:
  fs,_=cube_faces(box)
  for coords,uv,layer in fs:
   q=[[x*co+z*si,y,-x*si+z*co] for x,y,z in coords];screen=[[x*7+W/2,y*7+85] for x,y,z in q];tex=textures[layer]
   for tri in [[0,1,2],[0,2,3]]:
    pt=[screen[i] for i in tri];zz=[q[i][2] for i in tri];st=[uv[i] for i in tri]
    lo=[max(0,math.floor(min(p[i] for p in pt))) for i in (0,1)];hi=[min(lim,math.ceil(max(p[i] for p in pt))) for i,lim in [(0,W-1),(1,H-1)]];den=cross(sub(pt[1],pt[0]),sub(pt[2],pt[0]))
    if abs(den)<1e-8:continue
    for yy in range(lo[1],hi[1]+1):
     for xx in range(lo[0],hi[0]+1):
      pp=[xx+.5,yy+.5];b=cross(sub(pp,pt[0]),sub(pt[2],pt[0]))/den;c=cross(sub(pt[1],pt[0]),sub(pp,pt[0]))/den;wa=1-b-c
      if min(wa,b,c)<-1e-7:continue
      weights=[wa,b,c];z=sum(w*v for w,v in zip(weights,zz))
      if z>=depth[yy][xx]:continue
      tx,ty=[math.floor(sum(weights[j]*st[j][i] for j in range(3))) for i in (0,1)];tx=min(max(tx,0),63);ty=min(max(ty,0),31);color=tex.getpixel((tx,ty))
      if color[3]<26:continue
      depth[yy][xx]=z
      out.putpixel((xx,yy),color[:3] if mode=='texture' else ((0,0,0) if mode=='silhouette' else (190,190,190)))
 return out
if __name__=='__main__':
 page=Image.new('RGB',(1320,350),(75,81,85));d=ImageDraw.Draw(page)
 for i,(ang,mode,label) in enumerate([(0,'texture','FRONT'),(45,'texture','45 DEG'),(90,'texture','SIDE'),(180,'texture','BACK'),(0,'silhouette','ALPHA BLACK'),(45,'gray','ALPHA GRAY')]):
  page.paste(render(ang,mode),(i*220,25));d.text((i*220+10,8),label,(255,255,255))
 d.text((12,330),'SOFTWARE DEFAULT-CUBE UV CONTEXT / NO BODY / NO GAME / NO POSE OR SEAM ACCEPTANCE',(255,255,255));page.save(B/'whole-static-views.png')
 rows=[]
 for b in boxes:
  _,rects=cube_faces(b);rows.append(dict(part=b[0],origin=b[1],size=b[2],uv=b[3],mirror=b[4],inflate=b[5],layer=b[6],ordered_rects=rects))
 (B/'geometry-uv-context.json').write_text(json.dumps(dict(boxes=rows,slot_masks={'HEAD':['head','hat'],'CHEST':['body','right_arm','left_arm'],'LEGS':['waist','right_leg','left_leg'],'FEET':['right_boot','left_boot']},scope='idle default cube source context; no entity or runtime model instantiated',atlas=[64,32],faces=face_indices,vertex_uv_order=['u2,v1','u1,v1','u1,v2','u2,v2'],runtime_accepted=False),indent=2)+'\n')
