"""Read-only local mod artwork study; never copy reference pixels into production."""
from pathlib import Path
import json, zipfile, io, re, hashlib, collections
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/art/inventory-refresh-v1/references'
OUT.mkdir(parents=True,exist_ok=True)
VERS=Path('/Users/a15356015027/Public/.minecraft/versions')
archives=list((VERS/'愚者chishi/mods').glob('*.jar'))
archives += [p for p in VERS.glob('*/mods/*.jar') if any(x in p.name.lower() for x in ['artifacts-','relics-','botania-'])]
seen=set(); ordinary=[]; accessories=[]; create=[]; create_models=[]
reject=re.compile(r'(sword|pickaxe|axe|shovel|hoe|spear|bow|crossbow|dagger|helmet|chestplate|leggings|boots|shield|staff|hammer|scythe|spawn_egg|wand|mace|halberd|trident|cleaver|katana|gauntlet|whip|revolver|gun|cannon|knife|dart|bullet|throwing_card|rifle|debug|missing|logo|_icon|configurator|arrow)',re.I)
for jar in archives:
 if jar.name in seen:continue
 seen.add(jar.name)
 try:
  with zipfile.ZipFile(jar) as z:
   names=set(z.namelist()); wearable=set()
   for n in names:
    if n.startswith('data/curios/tags/items/') and n.endswith('.json'):
     for v in json.loads(z.read(n)).get('values',[]):
      v=v.get('id','') if isinstance(v,dict) else v
      if not v.startswith('#'):wearable.add(v)
   for n in sorted(names):
    if re.fullmatch(r'assets/create/models/item/.+\.json',n):
     create_models.append({'path':n,'model':json.loads(z.read(n)),'jar':str(jar)})
    if not re.fullmatch(r'assets/[^/]+/textures/item/[^/]+\.png',n):continue
    ns=n.split('/')[1];stem=Path(n).stem;ident=ns+':'+stem
    try:im=Image.open(io.BytesIO(z.read(n))).convert('RGBA')
    except:continue
    if im.width>64 or im.height<im.width:continue
    im=im.crop((0,0,im.width,im.width))
    modelpath=f'assets/{ns}/models/item/{stem}.json'
    model=json.loads(z.read(modelpath)) if modelpath in names else {}
    rec={'id':ident,'jar':str(jar),'texture':n,'sha256':hashlib.sha256(z.read(n)).hexdigest(),'size':list(im.size),'modelParent':model.get('parent'),'image':im}
    if ns=='create':create.append(rec)
    if ident in wearable and ns!='flame_chase_artifacts' and not reject.search(stem):accessories.append(rec)
    if ns not in {'flame_chase_artifacts','examplemod','prefab','constructionwand','ftbquests','explorerscompass','naturescompass'} and f'assets/{ns}/blockstates/{stem}.json' not in names and not reject.search(stem) and model.get('parent') in ('item/generated','minecraft:item/generated'):
     ordinary.append(rec)
 except (zipfile.BadZipFile,ValueError):continue
def unique(rows):
 found={}
 for row in rows:found.setdefault(row['id'],row)
 return list(found.values())
ordinary=unique(ordinary);accessories=unique(accessories);create=unique(create)
# Balanced round-robin across namespaces, so 500 samples are not one food pack.
groups=collections.defaultdict(list)
for row in ordinary:groups[row['id'].split(':')[0]].append(row)
balanced=[]
while groups and len(balanced)<500:
 for ns in list(groups):
  balanced.append(groups[ns].pop(0))
  if not groups[ns]:del groups[ns]
  if len(balanced)==500:break
# Balance wearable references across packs rather than taking the first archive.
agroups=collections.defaultdict(list)
for row in accessories:agroups[row['id'].split(':')[0]].append(row)
accessories=[]
while agroups and len(accessories)<100:
 for ns in list(agroups):
  accessories.append(agroups[ns].pop(0))
  if not agroups[ns]:del agroups[ns]
  if len(accessories)==100:break
font=ImageFont.truetype('/System/Library/Fonts/Monaco.ttf',10)
def publish(label,rows):
 dest=OUT/label;dest.mkdir(exist_ok=True)
 for i,row in enumerate(rows):
  row['image'].save(dest/(row['id'].replace(':','--')+'.png'))
 for offset in range(0,len(rows),50):
  sheet=Image.new('RGB',(1100,640),'#34383e');d=ImageDraw.Draw(sheet)
  d.text((12,8),f'{label} {offset+1}-{min(offset+50,len(rows))}; source artwork study, not Dynasty assets',font=font,fill='white')
  for j,row in enumerate(rows[offset:offset+50]):
   x=10+j%10*110;y=35+j//10*120;im=row['image'];im=im.resize((64,64),Image.Resampling.NEAREST)
   sheet.paste(im,(x+20,y),im)
   text=row['id'].split(':')[1]
   d.text((x,y+68),str(offset+j+1)+' '+row['id'].split(':')[0][:12],font=font,fill='#d6c8a7')
   d.text((x,y+82),text[:17],font=font,fill='white');d.text((x,y+95),text[17:34],font=font,fill='white')
  sheet.save(OUT/f'{label}-{offset//50+1:02}.png')
 return [{k:v for k,v in row.items() if k!='image'} for row in rows]
report={'purpose':'Read-only original item references; no blocks/weapons in 500 sample; first authored animation frame. 100 accessories means accessory samples from other installed packs, not a claim of 100 distinct modpacks.',
        'items':publish('items',balanced),'accessories':publish('accessories',accessories[:100]),'create_item_textures':publish('create',create),'create_all_item_models':create_models}
(OUT/'sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print({k:len(v) for k,v in report.items() if isinstance(v,list)})
