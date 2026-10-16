from pathlib import Path
import zipfile,json,math,hashlib,importlib.util,concurrent.futures
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'build/creature-mc-v33/reference';D.mkdir(parents=True,exist_ok=True)
s=importlib.util.spec_from_file_location('r',R/'tools/art/steve-fighters-v25/nonhuman_references.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('g',R/'tools/art/secondary-cuboid/review_models.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
records=[]
# Existing source reconstructions are explicitly limited to static geometry, not game captures.
old=R/'docs/art/steve-fighters-v25/nonhuman-references';meta=json.loads((old/'manifest.json').read_text()) if (old/'manifest.json').exists() else None
for f in sorted(old.glob('[0-9][0-9][0-9]-*.png'))[:100]:
 records.append({'name':f.stem[4:],'source':'existing pinned source archive','image':str(f),'type':'source cuboid reconstruction; no texture/animation'})
with zipfile.ZipFile(R/'build/creature-mc-v33/cobblemon-reference.jar')as z:
 groups={}
 for n in sorted(z.namelist()):
  if n.startswith('assets/cobblemon/bedrock/pokemon/models/')and n.endswith('.geo.json'):groups.setdefault(n.split('/')[-2],n)
 selected=list(groups.items())[:1000-len(records)]
 tasks=[(name,path,json.loads(z.read(path)),hashlib.sha256(z.read(path)).hexdigest())for name,path in selected]
def draw(task):
 name,path,data,sha=task;geo=data['minecraft:geometry'][0];bones={b['name']:b for b in geo['bones']};mats={}
 def matrix(n):
  if n in mats:return mats[n]
  b=bones[n];pivot=np.array(b.get('pivot',[0,0,0]),float);parent=b.get('parent');pp=np.array(bones[parent].get('pivot',[0,0,0]),float) if parent in bones else np.zeros(3)
  t=g.transform(pivot-pp,b.get('rotation',[0,0,0]));mats[n]=(matrix(parent)@t if parent in bones else t);return mats[n]
 faces=[];points=[]
 for n,b in bones.items():
  for c in b.get('cubes',[]):
   pivot=np.array(b.get('pivot',[0,0,0]),float);cp=np.array(c.get('pivot',pivot),float);cm=matrix(n)@g.transform(cp-pivot,c.get('rotation',[0,0,0]));origin=np.array(c['origin'],float);size=np.array(c['size'],float)
   inflate=float(c.get('inflate',0));origin-=inflate;size+=2*inflate
   for corners in g.FACES.values():
    p=(np.array(corners)*size+origin-cp)*[-1,1,1];q=(cm@np.column_stack([p,np.ones(4)]).T).T[:,:3];normal=np.cross(q[1]-q[0],q[2]-q[0]);ln=np.linalg.norm(normal)
    if ln>1e-7:faces.append((q,normal/ln,n));points.extend(q)
 if not points:raise ValueError(name+' no geometry')
 points=np.array(points);im=Image.new('RGB',(320,190),'#eeeeee');im.paste(r.render(faces,points,0,(160,166)),(0,0));im.paste(r.render(faces,points,45,(160,166)),(160,0));ImageDraw.Draw(im).text((5,169),name,fill='#223536',font=font);dest=D/(name+'.png');im.save(dest)
 return {'name':name,'source':'Cobblemon 1.8.2 / '+path,'sha256':sha,'image':str(dest),'type':'actual geo bind pose; no animation or texture mask','cuboids':sum(len(b.get('cubes',[]))for b in bones.values())}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  for i,v in enumerate(pool.map(draw,tasks)):
   records.append(v)
   if i%50==0:print('Rendered',i,flush=True)
 assert len(records)==1000,len(records)
 (D/'manifest.json').write_text(json.dumps(records,indent=2))
 for i in range(0,1000,20):
  sheet=Image.new('RGB',(1280,1100),'#e6e9e3');dr=ImageDraw.Draw(sheet)
  for j,record in enumerate(records[i:i+20]):
   src=Image.open(record['image']).convert('RGB');src.thumbnail((320,195));x=j%4*320;y=j//4*220;sheet.paste(src,(x,y));dr.text((x+4,y+196),str(i+j+1)+' '+record['name'][:35],font=font,fill='#192e30')
  sheet.save(D/('sheet-%02d.png'%(i//20+1)))
 print('1000 source bind-pose reconstructions; 50 sheets. Visual review pending.',flush=True)
