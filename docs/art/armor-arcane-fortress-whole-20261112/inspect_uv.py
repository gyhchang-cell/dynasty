"""Reference-only source cubes and raw UVs. Not Minecraft or worn acceptance."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,re,ast,copy
B=Path(__file__).resolve().parent
S=B/'source/src/main'
J=S/'java/mod/maxbogomol/wizards_reborn/client/model/armor'
T=S/'resources/assets/wizards_reborn/textures'
# Reuse audited cube-face ordering, not the previous family's geometry or textures.
helper=Path('docs/art/armor-arcane-gold-whole-20261112/static_uv_analysis.py').read_text()
a=ast.parse(helper)
selected=[n for n in a.body if isinstance(n,(ast.FunctionDef,ast.Assign)) and (isinstance(n,ast.FunctionDef) and n.name in ['cube_faces','render'] or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='face_indices' for t in n.targets))]
code=ast.unparse(ast.Module(body=selected,type_ignores=[])).replace('63)', 'tex.width - 1)').replace('31)', 'tex.height - 1)')
ns={};exec('import math\nfrom PIL import Image,ImageDraw\n'+code,ns)
def values(s):return [float(x.strip().rstrip('Ff')) for x in s.split(',')]
def parse(text):
 aliases={n:n for n in ['root','head','body','pelvis','right_arm','left_arm','right_legging','left_legging','right_foot','left_foot']}
 nodes={n:{'parent':None,'pivot':[0,0,0]} for n in aliases}
 boxes=[]
 for m in re.finditer(r'PartDefinition\s+(\w+)\s*=\s*(\w+)\.addOrReplaceChild\("([^"]+)",\s*CubeListBuilder.create\(\)\.texOffs\(([^)]+)\)\s*\.addBox\((.*?),\s*new CubeDeformation\(([^)]+)\)\),\s*PartPose\.(ZERO|offset\([^)]*\))\)',text,re.S):
  var,parent,name,uv,dimensions,inflate,pose=m.groups();parent=aliases[parent];aliases[var]=name
  nodes[name]={'parent':parent,'pivot':values(pose[7:-1]) if pose!='ZERO' else [0,0,0]}
  v=values(dimensions);assert len(v)==6
  boxes.append({'node':name,'origin':v[:3],'size':v[3:],'uv':values(uv),'inflate':float(inflate.rstrip('Ff'))})
 assert len(boxes)==text.count('.addBox('),(len(boxes),text.count('.addBox('))
 return nodes,boxes
base=(J/'ArcaneFortressArmorModel.java').read_text()
normal=base.split('public static void rootNormalBodyLayer')[1].split('public static void rootArmsBodyLayer')[0]
arms=base.split('public static void rootArmsBodyLayer')[1]
slim=(J/'ArcaneFortressSlimArmorModel.java').read_text().split('public static void rootArmsBodyLayer')[1]
geometry={}
for variant,armtext in [('standard',arms),('slim',slim)]:
 nodes,boxes=parse(normal+armtext)
 # Neutral source-context transforms: copyFromDefault replaces pelvis/leg/foot pivots;
 # HumanoidModel supplies head and arm idle pivots. No body, swing, crouch or baby pose.
 for n,p in {'right_arm':[-5,2,0],'left_arm':[5,2,0],'right_legging':[-1.9,12,0],'left_legging':[1.9,12,0],'right_foot':[-1.9,12,0],'left_foot':[1.9,12,0]}.items():nodes[n]['pivot']=p
 def offset(n):
  p=nodes[n]['pivot'];parent=nodes[n]['parent']
  return [a+b for a,b in zip(p,offset(parent))] if parent else p
 tex=Image.open(T/'models/armor'/('arcane_fortress'+('_slim' if variant=='slim' else '')+'.png')).convert('RGBA');assert tex.size==(128,64)
 renderboxes=[];rows=[]
 for i,b in enumerate(boxes):
  o=[x+y for x,y in zip(b['origin'],offset(b['node']))]
  box=(b['node'],o,b['size'],b['uv'],False,b['inflate'],1);renderboxes.append(box)
  _,rects=ns['cube_faces'](box);faces=[]
  for side,r in rects.items():
   u,v,U,V=map(int,r);assert 0<=min(u,U)<=max(u,U)<=128 and 0<=min(v,V)<=max(v,V)<=64
   crop=tex.crop((min(u,U),min(v,V),max(u,U),max(v,V)))
   alpha=list(crop.getchannel('A').getdata())
   faces.append({'side':side,'rect':r,'nonzero':sum(x>0 for x in alpha),'pixels':len(alpha)})
  rows.append({**b,'neutral_global_origin':o,'faces':faces})
 geometry[variant]={'boxes':rows,'nodes':nodes,'face_count':len(rows)*6,'slot_roots':{'HEAD':['head'],'CHEST':['body','right_arm','left_arm'],'LEGS':['pelvis','right_legging','left_legging'],'FEET':['right_foot','left_foot']},'not_game':True,'scope':'neutral four-slot union; pinned mod geometry plus non-exact-version FluffyFur alias context; no body, pose, lighting, trims/glint or game seam acceptance'}
 for start in range(0,len(rows),9):
  page=Image.new('RGB',(1080,1025),(85,92,98));d=ImageDraw.Draw(page);d.text((10,8),f'REFERENCE {variant} RAW UV {start}..{min(start+8,len(rows)-1)} / NOT GAME',fill='white')
  for rr,row in enumerate(rows[start:start+9]):
   y=35+rr*110;d.text((10,y),row['node'],fill='white')
   for j,f in enumerate(row['faces']):
    x=j*180+10;u,v,U,V=map(int,f['rect']);crop=tex.crop((min(u,U),min(v,V),max(u,U),max(v,V)))
    if V<v:crop=crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    crop=crop.resize((crop.width*5,crop.height*5),Image.Resampling.NEAREST)
    page.paste(crop,(x,y+28),crop);d.text((x,y+14),f"{f['side']} {f['nonzero']}/{f['pixels']}",fill='white')
  page.save(B/f'raw-{variant}-{start//9+1}.png')
 ns['boxes']=renderboxes;ns['textures']={1:tex}
 page=Image.new('RGB',(1320,350),(75,81,85));d=ImageDraw.Draw(page)
 for k,(angle,mode,label) in enumerate([(0,'texture','FRONT'),(45,'texture','45'),(90,'texture','SIDE'),(180,'texture','BACK'),(0,'silhouette','BLACK'),(45,'gray','GRAY')]):
  page.paste(ns['render'](angle,mode),(k*220,25));d.text((k*220+8,8),label,fill='white')
 d.text((10,330),f'{variant.upper()} SOFTWARE SOURCE-CUBE UNION / NOT GAME / NOT WORN QA',fill='white');page.save(B/f'whole-{variant}.png')
(B/'geometry-uv-context.json').write_text(json.dumps(geometry,indent=2)+'\n')
page=Image.new('RGB',(1080,540),(85,92,98));d=ImageDraw.Draw(page)
for i,part in enumerate(['helmet','chestplate','leggings','boots']):
 im=Image.open(T/f'item/arcane_fortress_{part}.png').convert('RGBA');assert im.size==(16,16)
 d.text((i*250+15,10),part,fill='white');im=im.resize((128,128),Image.Resampling.NEAREST);page.paste(im,(i*250+15,30),im)
for i,variant in enumerate(['','_slim']):
 im=Image.open(T/f'models/armor/arcane_fortress{variant}.png').convert('RGBA');d.text((i*530+10,195),'RAW ATLAS '+(variant or 'standard'),fill='white');im=im.resize((512,256),Image.Resampling.NEAREST);page.paste(im,(i*530+10,220),im)
d.text((10,515),'ACTUAL REFERENCE PNGs / nearest enlargement only / NO GAME / NO DYNASTY ASSET',fill='white');page.save(B/'native-pixels.png')
print({v:{'boxes':len(g['boxes']),'faces':g['face_count']} for v,g in geometry.items()})
