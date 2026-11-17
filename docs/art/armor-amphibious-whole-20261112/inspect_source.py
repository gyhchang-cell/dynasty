"""Reference-only source parser and orthographic diagnostic. Not a game renderer."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import re,json,math
B=Path(__file__).resolve().parent
S=B/'source/src/main'
TEXT=(S/'java/thebetweenlands/client/render/model/armor/ModelAmphibiousArmor.java').read_text()
ctor=TEXT.split('public ModelAmphibiousArmor() {',1)[1].split('@Override',1)[0]
ctor=re.sub(r'//[^\n]*','',ctor)
nodes={}
for name in re.findall(r'(\w+)\s*= new ModelRenderer\(this\);',ctor):
 nodes[name]={'pivot':[0,0,0],'rotation':[0,0,0],'parent':None,'boxes':[]}
roots={'bipedHead':(0,0,0),'bipedHeadwear':(0,0,0),'bipedBody':(0,0,0),'bipedRightArm':(-5,2,0),'bipedLeftArm':(5,2,0),'bipedRightLeg':(-1.9,12,0),'bipedLeftLeg':(1.9,12,0),'bipedRightBoot':(0,0,0),'bipedLeftBoot':(0,0,0),'bipedWaist':(0,0,0)}
for n,p in roots.items():nodes[n]={'pivot':p,'rotation':[0,0,0],'parent':None,'boxes':[]}
nodes['bipedRightBoot']['parent']='bipedRightLeg'
nodes['bipedLeftBoot']['parent']='bipedLeftLeg'
nodes['bipedWaist']['parent']='bipedBody'
def numbers(s):return [float(t.strip().rstrip('Ff')) for t in s.split(',')]
for n,args in re.findall(r'(\w+)\.setRotationPoint\(([^)]+)\);',ctor):nodes[n]['pivot']=numbers(args)
for n,args in re.findall(r'setRotationAngle\((\w+),\s*([^)]+)\);',ctor):nodes[n]['rotation']=numbers(args)
for parent,child in re.findall(r'(\w+)\.addChild\((\w+)\);',ctor):
 assert nodes[child]['parent'] is None
 nodes[child]['parent']=parent
boxes=[]
for n,owner,args in re.findall(r'(\w+)\.cubeList\.add\(new ModelBox\((\w+),\s*(.*?)\)\);',ctor):
 assert n==owner
 tok=args.split(','); a=numbers(','.join(tok[:-1])); assert len(a)==9
 box={'node':n,'uv':a[:2],'origin':a[2:5],'size':a[5:8],'inflate':a[8],'mirror':tok[-1].strip()=='true'}
 assert not box['mirror'] and box['inflate']==0
 boxes.append(box);nodes[n]['boxes'].append(len(boxes)-1)
assert len(boxes)==ctor.count('new ModelBox(')
def transform(n,p):
 x,y,z=p;rx,ry,rz=nodes[n]['rotation']
 y,z=y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
 x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
 x,y=x*math.cos(rz)-y*math.sin(rz),x*math.sin(rz)+y*math.cos(rz)
 p=[a+b for a,b in zip((x,y,z),nodes[n]['pivot'])]
 return transform(nodes[n]['parent'],p) if nodes[n]['parent'] else p
atlas=Image.open(S/'resources/assets/thebetweenlands/textures/armor/amphibious.png').convert('RGBA')
faces=[]
for bi,b in enumerate(boxes):
 x,y,z=b['origin'];w,h,d=b['size'];u,v=b['uv'];X=x+w;Y=y+h;Z=z+d
 vertices=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
 indices=[[5,1,2,6],[0,4,7,3],[5,4,0,1],[2,3,7,6],[1,0,3,2],[4,5,6,7]]
 rects=[(u+d+w,v+d,u+d+w+d,v+d+h),(u,v+d,u+d,v+d+h),(u+d,v,u+d+w,v+d),(u+d+w,v+d,u+d+w+w,v),(u+d,v+d,u+d+w,v+d+h),(u+d+w+d,v+d,u+d+w+d+w,v+d+h)]
 for side,idx,rect in zip(['EAST','WEST','Y_MIN','Y_MAX','NORTH','SOUTH'],indices,rects):
  u1,v1,u2,v2=rect;assert 0<=min(u1,u2)<=max(u1,u2)<=128 and 0<=min(v1,v2)<=max(v1,v2)<=128
  faces.append({'box':bi,'node':b['node'],'side':side,'vertices':[transform(b['node'],vertices[i]) for i in idx],'uv':[(u2,v1),(u1,v1),(u1,v2),(u2,v2)],'rect':rect})
# One whole family, not nodes, boxes, planes, gems or views as separate designs.
report={'reference_only':True,'pose':'constructor rotations, zero biped pose, union of the four slot-selected pieces; no skin/entity/animation','nodes':nodes,'boxes':boxes,'faces':faces,'zero_dimension_boxes':sum(0 in b['size'] for b in boxes),'runtime_validated':False,'culling':'two-sided diagnostic only; upstream explicitly enables cull; not exact OpenGL visibility','uv_implementation':'legacy ModelBox/TexturedQuad ordered endpoints; Y_MAX has reversed V; zero-area faces retained in data but not rasterized'}
(B/'geometry-uv-context.json').write_text(json.dumps(report,indent=2)+'\n')
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',14)
def page(size,title):
 p=Image.new('RGB',size,(80,86,91));ImageDraw.Draw(p).text((12,10),title,font=font,fill='white');return p
p=page((1020,780),'REFERENCE ONLY | native pixels x integer NN | not Dynasty artwork')
draw=ImageDraw.Draw(p)
for i,slot in enumerate(['helmet','chestplate','leggings','boots']):
 im=Image.open(S/f'resources/assets/thebetweenlands/textures/items/amphibious_{slot}.png').convert('RGBA');p.paste(im.resize((128,128),Image.Resampling.NEAREST),(30+i*245,60),im.resize((128,128),Image.Resampling.NEAREST));draw.text((30+i*245,200),slot,font=font,fill='white')
a=atlas.resize((512,512),Image.Resampling.NEAREST);p.paste(a,(30,240),a);draw.text((570,260),'amphibious.png 128 x 128',font=font,fill='white');draw.text((570,290),'No gem recolors counted.',font=font,fill='white');p.save(B/'native-pixels.png')
def raster(angle,mode):
 W,H=320,480;p=Image.new('RGB',(W,H),(80,86,91));pix=p.load();depth=[float('inf')]*(W*H)
 t=math.radians(angle);c,s=math.cos(t),math.sin(t)
 for f in faces:
  coords=[]
  for (x,y,z),uv in zip(f['vertices'],f['uv']):coords.append((W/2+(x*c+z*s)*11,145+y*11,-x*s+z*c,*uv))
  for inds in [(0,1,2),(0,2,3)]:
   a,b,c0=[coords[i] for i in inds];den=(b[1]-c0[1])*(a[0]-c0[0])+(c0[0]-b[0])*(a[1]-c0[1])
   if abs(den)<1e-8:continue
   for py in range(max(0,int(min(a[1],b[1],c0[1]))),min(H,int(max(a[1],b[1],c0[1]))+1)):
    for px in range(max(0,int(min(a[0],b[0],c0[0]))),min(W,int(max(a[0],b[0],c0[0]))+1)):
     ax,ay=px+.5,py+.5
     l=((b[1]-c0[1])*(ax-c0[0])+(c0[0]-b[0])*(ay-c0[1]))/den
     m=((c0[1]-a[1])*(ax-c0[0])+(a[0]-c0[0])*(ay-c0[1]))/den;n=1-l-m
     if min(l,m,n)<-1e-8:continue
     z=l*a[2]+m*b[2]+n*c0[2];di=py*W+px
     if z>=depth[di]-1e-8:continue
     u=l*a[3]+m*b[3]+n*c0[3];v=l*a[4]+m*b[4]+n*c0[4]
     rgba=atlas.getpixel((min(127,max(0,int(u))),min(127,max(0,int(v)))))
     if rgba[3]<128:continue
     depth[di]=z
     pix[px,py]=rgba[:3] if mode=='texture' else (0,0,0) if mode=='black' else (155+10*(f['box']%3),)*3
 return p
p=page((960,1050),'SOURCE BIND POSE | two-sided software diagnostic | NOT GAME / NOT WORN QA')
d=ImageDraw.Draw(p)
for i,(angle,mode,label) in enumerate([(0,'texture','front'),(45,'texture','45 degree'),(90,'texture','side'),(180,'texture','back'),(0,'black','black front'),(45,'gray','gray 45')]):
 x=(i%3)*320;y=40+(i//3)*500;p.paste(raster(angle,mode),(x,y));d.text((x+12,y+475),label,font=font,fill='white')
p.save(B/'whole-static-views.png')
# Raw face rectangles, including transparent borders and orientation annotations; no pixel editing.
for start in range(0,len(boxes),12):
 p=page((1170,12*110+45),f'RAW UV SOURCE ONLY | boxes {start}-{min(start+11,len(boxes)-1)} | empty face = zero UV area')
 d0=ImageDraw.Draw(p)
 for row,bi in enumerate(range(start,min(start+12,len(boxes)))):
  y=45+row*110;d0.text((6,y),f'{bi} {boxes[bi]["node"]}',font=font,fill='white')
  for col,f in enumerate(faces[bi*6:bi*6+6]):
   x=12+col*192;u1,v1,u2,v2=map(int,f['rect']);d0.text((x,y+20),f['side'],font=font,fill='white')
   if u1!=u2 and v1!=v2:
    im=atlas.crop((min(u1,u2),min(v1,v2),max(u1,u2),max(v1,v2)))
    if u2<u1:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if v2<v1:im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    k=min(6,150//im.width,60//im.height);im=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST);p.paste(im,(x,y+43),im)
 p.save(B/f'raw-uv-faces-{start//12+1}.png')
print(json.dumps({'nodes':len(nodes),'boxes':len(boxes),'faces':len(faces),'planes':report['zero_dimension_boxes'],'pages':len(list(B.glob('raw-uv-faces-*.png')))}))
