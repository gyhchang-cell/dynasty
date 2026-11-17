"""Read-only source-derived UV/whole-family analysis; not engine rendering."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import ast,operator,re,json,math
B=Path(__file__).resolve().parent;S=B/'source/src/main';F=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',13)
def num(s):
 tree=ast.parse(re.sub(r'(?<=\d)[Ff]\b','',s.strip()),mode='eval')
 def go(n):
  if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)):return float(n.value)
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):return (-1 if isinstance(n.op,ast.USub) else 1)*go(n.operand)
  if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Add,ast.Sub)):return (operator.add if isinstance(n.op,ast.Add) else operator.sub)(go(n.left),go(n.right))
  raise ValueError(ast.dump(n))
 return go(tree.body)
def nums(s):return [num(v) for v in s.split(',')]
allgeo={}
for fam in ['ra','atem']:
 source=(S/f'java/com/teammetallurgy/atum/client/model/armor/{fam.capitalize()}ArmorModel.java').read_text()
 ctor=source.split('public static LayerDefinition createLayer() {')[1].split('return LayerDefinition.create')[0];ctor=re.sub(r'//[^\n]*','',ctor)
 aliases={'partdefinition':'root'};nodes={'root':{'pivot':[0,0,0],'rotation':[0,0,0],'parent':None}};boxes=[]
 for statement in ctor.split(';'):
  m=re.search(r'(\w+)\.addOrReplaceChild\("([^"]+)",\s*CubeListBuilder.create\(\)(.*),\s*PartPose.(ZERO|offsetAndRotation\([^)]*\)|offset\([^)]*\))\)',statement,re.S)
  if not m:continue
  parent,name,builder,pose=m.groups();parent=aliases[parent]
  lhs=re.search(r'PartDefinition\s+(\w+)\s*=',statement)
  if lhs:aliases[lhs[1]]=name
  assert name not in nodes
  a=nums(pose[pose.index('(')+1:-1]) if pose!='ZERO' else [0,0,0]
  nodes[name]={'parent':parent,'pivot':a[:3],'rotation':a[3:] or [0,0,0]}
  uv=[0,0];mirror=False
  for token in re.finditer(r'\.texOffs\(([^)]+)\)|\.mirror\(([^)]*)\)|\.addBox\((.*?),\s*new CubeDeformation\(([^)]+)\)\)',builder,re.S):
   if token[1] is not None:uv=nums(token[1])
   elif token[2] is not None:mirror=token[2].strip()!='false'
   else:
    values=nums(token[3]);assert len(values)==6
    boxes.append({'node':name,'uv':uv[:],'origin':values[:3],'size':values[3:],'inflate':num(token[4]),'mirror':mirror})
 assert len(boxes)==ctor.count('.addBox(')
 # The actual renderToBuffer replaces cape/boot pose from arm/leg before direct render.
 original_nodes=json.loads(json.dumps(nodes))
 for target,fromname in [('left_cape','left_arm'),('right_cape','right_arm'),('left_boot','left_leg'),('right_boot','right_leg')]:
  nodes[target]['pivot']=nodes[fromname]['pivot'][:];nodes[target]['rotation']=nodes[fromname]['rotation'][:]
 def transform(name,p):
  n=nodes[name];x,y,z=p;rx,ry,rz=n['rotation']
  y,z=y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
  x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
  x,y=x*math.cos(rz)-y*math.sin(rz),x*math.sin(rz)+y*math.cos(rz)
  p=[a+b for a,b in zip((x,y,z),n['pivot'])]
  return transform(n['parent'],p) if n['parent'] else p
 atlas=Image.open(S/f'resources/assets/atum/textures/models/armor/{fam}_armor.png').convert('RGBA');faces=[]
 for bi,b in enumerate(boxes):
  x,y,z=b['origin'];w,h,d=b['size'];i=b['inflate'];u,v=b['uv'];X,Y,Z=x+w+i,y+h+i,z+d+i;x-=i;y-=i;z-=i
  if b['mirror']:x,X=X,x
  vertices=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
  indices=[[5,1,2,6],[0,4,7,3],[5,4,0,1],[2,3,7,6],[1,0,3,2],[4,5,6,7]]
  rects=[(u+d+w,v+d,u+d+w+d,v+d+h),(u,v+d,u+d,v+d+h),(u+d,v,u+d+w,v+d),(u+d+w,v+d,u+d+w+w,v),(u+d,v+d,u+d+w,v+d+h),(u+d+w+d,v+d,u+d+w+d+w,v+d+h)]
  for side,idx,rect in zip(['EAST','WEST','DOWN','UP','NORTH','SOUTH'],indices,rects):
   u1,v1,u2,v2=rect;assert 0<=min(u1,u2)<=max(u1,u2)<=64 and 0<=min(v1,v2)<=max(v1,v2)<=96
   verts=[transform(b['node'],vertices[j]) for j in idx];uvs=[(u2,v1),(u1,v1),(u1,v2),(u2,v2)]
   if b['mirror']:verts.reverse();uvs.reverse()
   faces.append({'box':bi,'node':b['node'],'side':side,'rect':rect,'uv':uvs,'vertices':verts})
 allgeo[fam]={'nodes_before_render_copy':original_nodes,'nodes_after_render_copy':nodes,'boxes':boxes,'faces':faces,'full_set_capes':True,'preview':'source-derived fullset union; cape once not once per armorpass, zero biped pose; two-sided, alpha test only; no player/lighting/glint/trim/engine'}
 for start in range(0,len(boxes),12):
  page=Image.new('RGB',(1170,1365),(80,86,91));draw=ImageDraw.Draw(page);draw.text((8,8),f'REFERENCE {fam} RAW UV | box{start}..{min(start+11,len(boxes)-1)} | not game',font=F,fill='white')
  for row,bi in enumerate(range(start,min(start+12,len(boxes)))):
   y=45+110*row;draw.text((8,y),f'{bi} {boxes[bi]["node"]} mirror={boxes[bi]["mirror"]}',font=F,fill='white')
   for j,f in enumerate(faces[6*bi:6*bi+6]):
    x=10+192*j;draw.text((x,y+20),f['side'],font=F,fill='white');u1,v1,u2,v2=map(int,f['rect'])
    if u1==u2 or v1==v2:continue
    im=atlas.crop((min(u1,u2),min(v1,v2),max(u1,u2),max(v1,v2)))
    if v2<v1:im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    k=min(5,150//im.width,60//im.height);im=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST);page.paste(im,(x,y+43),im)
  page.save(B/f'raw-{fam}-{start//12+1}.png')
 def render(angle,mode):
  W,H=320,520;p=Image.new('RGB',(W,H),(80,86,91));pixels=p.load();depth=[float('inf')]*(W*H);t=math.radians(angle);c,s=math.cos(t),math.sin(t)
  for f in faces:
   co=[(160+10*(x*c+z*s),180+y*10,-x*s+z*c,*uv) for (x,y,z),uv in zip(f['vertices'],f['uv'])]
   for tri in [(0,1,2),(0,2,3)]:
    a,b,c0=[co[j] for j in tri];den=(b[1]-c0[1])*(a[0]-c0[0])+(c0[0]-b[0])*(a[1]-c0[1])
    if abs(den)<1e-9:continue
    for py in range(max(0,int(min(a[1],b[1],c0[1]))),min(H,int(max(a[1],b[1],c0[1]))+1)):
     for px in range(max(0,int(min(a[0],b[0],c0[0]))),min(W,int(max(a[0],b[0],c0[0]))+1)):
      ax,ay=px+.5,py+.5;l=((b[1]-c0[1])*(ax-c0[0])+(c0[0]-b[0])*(ay-c0[1]))/den;m=((c0[1]-a[1])*(ax-c0[0])+(a[0]-c0[0])*(ay-c0[1]))/den;n=1-l-m
      if min(l,m,n)<-1e-8:continue
      z=l*a[2]+m*b[2]+n*c0[2];di=py*W+px
      if z>=depth[di]-1e-8:continue
      u=l*a[3]+m*b[3]+n*c0[3];v=l*a[4]+m*b[4]+n*c0[4];rgba=atlas.getpixel((min(63,max(0,int(u))),min(95,max(0,int(v)))))
      if rgba[3]<128:continue
      depth[di]=z;pixels[px,py]=rgba[:3] if mode=='texture' else (0,0,0) if mode=='black' else (150+12*(f['box']%3),)*3
  return p
 page=Image.new('RGB',(960,1140),(80,86,91));draw=ImageDraw.Draw(page);draw.text((8,8),f'REFERENCE {fam} | software source pose | fullset cape once | NOT GAME/WORN QA',font=F,fill='white')
 for j,(angle,mode,label) in enumerate([(0,'texture','front'),(45,'texture','45'),(90,'texture','side'),(180,'texture','back'),(0,'black','silhouette'),(45,'gray','gray')]):
  x=(j%3)*320;y=35+(j//3)*550;page.paste(render(angle,mode),(x,y));draw.text((x+10,y+515),label,font=F,fill='white')
 page.save(B/f'whole-{fam}.png')
(B/'geometry-uv-context.json').write_text(json.dumps(allgeo,indent=2)+'\n')
print({f:{'nodes':len(g['nodes_after_render_copy']),'boxes':len(g['boxes']),'faces':len(g['faces']),'mirror':sum(b['mirror'] for b in g['boxes'])} for f,g in allgeo.items()})
