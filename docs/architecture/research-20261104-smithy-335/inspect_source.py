"""Offline research only. Does not modify production or grant credit."""
import json,hashlib,sys,zipfile,itertools,collections
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,iso,color
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(f,d):(OUT/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
member='data/radiation_zone_reborn/structures/damaged_wasteland_fortress.nbt'
mfile=ROOT/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json'
s=next(r for r in json.loads(mfile.read_text())['entries'] if r['member']==member)
a=Path(s['source_archive']);assert sha(a.read_bytes())=='945a88383c0d9efa0d481957daebdf6cc299e6dd8cec675a451efae2ee156ddd'
with zipfile.ZipFile(a) as z:
 raw=z.read(member);assert sha(raw)==s['nbt_sha256'];n=read(raw)
 contexts=[]
 for name in z.namelist():
  if name.endswith('.json') and 'damaged_wasteland_fortress' in z.read(name).decode('utf8',errors='replace'):
   b=z.read(name);contexts.append({'member':name,'sha256':sha(b),'object':json.loads(b),'read_scope':'whole JSON; static only'})
 save('source-contexts.json',contexts)
save('original.json',n)
pal=n['palette'];st={tuple(b['pos']):b for b in n['blocks']};sx,sy,sz=n['size']
assert len(st)==len(n['blocks'])
rows=[{'y':y,'z':z,'runs_x':[[s,len(list(g))] for s,g in itertools.groupby(st.get((x,y,z),{}).get('state') for x in range(sx))]} for y in range(sy) for z in range(sz)]
be=[b for b in n['blocks'] if 'nbt' in b]
save('full-space.json',{'palette':pal,'block_entities':be,'entities':n.get('entities',[]),'rows':rows})
counts=collections.Counter(pal[b['state']]['Name'] for b in st.values());save('source-binding.json',{'archive':str(a),'archive_sha256':sha(a.read_bytes()),'member':member,'nbt_sha256':sha(raw),'metadata_sha256':sha(mfile.read_bytes()),'DataVersion':n.get('DataVersion'),'size':n['size'],'stored':len(st),'omitted_unknown':sx*sy*sz-len(st),'nonair':sum(v for k,v in counts.items() if k not in AIR),'materials':dict(counts),'palette_states':len(pal),'block_entities':len(be),'entities':len(n.get('entities',[])),'new_network_access':False,'publisher_attribution':'Local fixed archive, no independently verified publisher URL in this batch.'})
cells={p:pal[b['state']]['Name'] for p,b in st.items() if pal[b['state']]['Name'] not in AIR}
im=Image.new('RGB',(1520,680),'#edf0f2')
for r in range(2):im.paste(iso(cells,n['size'],r,'Damaged wasteland fortress: source occupancy; not native meshes'),(760*r,0))
im.save(OUT/'whole.png')
im=Image.new('RGB',(1520,1360),'#edf0f2')
for i,y in enumerate([4,8]):
 for r in range(2):im.paste(iso(cells,n['size'],r,f'One source cut y<={y}',y),(760*r,680*i))
im.save(OUT/'cutaways.png')
for start in range(0,sy,3):
 u=18;w=sx*u+55;h=sz*u+55;im=Image.new('RGB',(w*3,h),'#edf0f2');d=ImageDraw.Draw(im)
 for i,y in enumerate(range(start,min(start+3,sy))):
  l=i*w+30;t=30;d.text((l,5),f'y={y}; +X right / +Z down',fill='black')
  for x in range(sx):
   for z in range(sz):
    name=pal[st[x,y,z]['state']]['Name'] if (x,y,z) in st else None;c='#ff00ff' if name is None else '#e3e6e9' if name in AIR else color(name)
    d.rectangle((l+x*u,t+z*u,l+(x+1)*u,t+(z+1)*u),fill=c,outline='#bfc6ca')
  for z in range(0,sz,3):d.text((l-22,t+z*u),str(z),fill='black')
  for x in range(0,sx,2):d.text((l+x*u,t+sz*u+5),str(x),fill='black')
 im.save(OUT/f'layers-{start:02d}-{min(start+2,sy-1):02d}.png')
im=Image.new('RGB',(1400,1000),'#edf0f2');d=ImageDraw.Draw(im)
for i,(axis,fixed) in enumerate([('x',5),('x',10),('z',10),('z',20)]):
 u=21;l=40+(i%2)*700;t=50+(i//2)*500;width=sz if axis=='x' else sx
 d.text((l,t-25),f'{axis}={fixed} y up; cubes not collision',fill='black')
 for y in range(sy):
  d.text((l-23,t+(sy-1-y)*u),str(y),fill='black')
  for h in range(width):
   p=(fixed,y,h) if axis=='x' else (h,y,fixed);name=pal[st[p]['state']]['Name'] if p in st else None;c='#ff00ff' if name is None else '#e3e6e9' if name in AIR else color(name)
   d.rectangle((l+h*u,t+(sy-1-y)*u,l+(h+1)*u,t+(sy-y)*u),fill=c,outline='#bfc6ca')
 for h in range(0,width,2):d.text((l+h*u,t+sy*u+5),str(h),fill='black')
im.save(OUT/'sections.png')
print('SUMMARY',json.dumps(json.loads((OUT/'source-binding.json').read_text()),ensure_ascii=False))
print('PALETTE')
for i,v in enumerate(pal):print(i,json.dumps(v,separators=(',',':')))
print('BE',json.dumps(be,separators=(',',':')))
print('ENTITIES',json.dumps(n.get('entities',[]),separators=(',',':')))
print('CONTEXT',json.dumps(contexts,separators=(',',':')))
