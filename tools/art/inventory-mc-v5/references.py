from pathlib import Path
import json,zipfile,io,hashlib,collections,re
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-mc-v5/references';rows={};seen=set()
for jar in Path('/Users/a15356015027/Public/.minecraft/versions').glob('*/mods/*.jar'):
 if jar.name in seen or 'dynasty' in jar.name:continue
 seen.add(jar.name)
 try:
  with zipfile.ZipFile(jar) as z:
   names=set(z.namelist());wear=set()
   for n in names:
    if n.startswith(('data/curios/tags/items/','data/trinkets/tags/items/')) and n.endswith('.json'):
     for v in json.loads(z.read(n)).get('values',[]):
      v=v.get('id','') if isinstance(v,dict) else v
      if ':' in v and not v.startswith('#'):wear.add(v)
   for id in wear:
    ns,stem=id.split(':',1)
    if ns=='flame_chase_artifact' or re.search(r'debug|sword|sniper|pickaxe|cannon|_gun|_bow$|_axe$',stem):continue
    for n in [f'assets/{ns}/textures/item/{stem}.png',f'assets/{ns}/textures/items/{stem}.png']:
     if n not in names:continue
     im=Image.open(io.BytesIO(z.read(n))).convert('RGBA')
     if im.width>128:continue
     if id not in rows:rows[id]={'id':id,'jar':str(jar),'texture':n,'sha256':hashlib.sha256(z.read(n)).hexdigest(),'image':im.crop((0,0,im.width,min(im.width,im.height)))}
 except Exception:continue
pool=collections.defaultdict(list)
for row in sorted(rows.values(),key=lambda r:r['id']):pool[row['id'].split(':')[0]].append(row)
selected=[]
while pool and len(selected)<500:
 for key in list(pool):
  if pool[key]:selected.append(pool[key].pop(0))
  if not pool[key]:del pool[key]
  if len(selected)==500:break
font=ImageFont.load_default()
for start in range(0,len(selected),50):
 sheet=Image.new('RGB',(1250,600),'#565c61');dr=ImageDraw.Draw(sheet)
 for i,r in enumerate(selected[start:start+50]):
  im=r['image'];im.thumbnail((80,80));im=im.resize((80,80),Image.Resampling.NEAREST);x=i%10*125;y=i//10*120;sheet.paste(im,(x+20,y+2),im);label=r['id'];dr.text((x+2,y+83),label.split(':')[0][:20],font=font,fill='white');dr.text((x+2,y+98),label.split(':')[1][:21],font=font,fill='white')
 sheet.save(D/f'study-{start//50+1:02}.png')
(D/'sources.json').write_text(json.dumps([{k:v for k,v in r.items() if k!='image'} for r in selected],indent=2));print('total eligible',len(rows),'selected',len(selected),'mods',len({r['id'].split(':')[0] for r in selected}))
