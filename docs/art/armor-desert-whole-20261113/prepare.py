"""Freeze native Atum Desert armor sources and diagnostic pages, never runtime art."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,sys
from PIL import Image,ImageDraw,ImageChops
D=Path(__file__).resolve().parent;R=D.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert not (D/'provenance.json').exists()
protected=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text())
targets=json.loads((R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json').read_text())['targets']
baseline=protected | {p:h for t in targets for p,h in t['files'].items()}
assert all(sha((R/p).read_bytes())==h for p,h in baseline.items())
save('protected-before.json',baseline)
ids=[f'atum:desert_{s}_{m}' for m in ['iron','gold','diamond'] for s in ['helmet','chest','legs','boots']]
subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*ids,
 '--application','D74：研究Atum Desert完整四槽设计及铁/金/钻石三材质的图标、穿戴UV和可染色覆盖层；只作原创方法参考，三材质不拆信用；不制作、不改289保护/70优先资源、不启Java、不改主清单。'],check=True)
archive=R/'docs/art/armor-material-three-20261112/Atum2-fixed.zip'
inv=json.loads((R/'docs/art/armor-material-three-20261112/Atum2-inventory.json').read_text())
entries=[]
with zipfile.ZipFile(archive) as z:
 root=z.namelist()[0]
 for entry in z.namelist():
  rel=entry.removeprefix(root)
  native=rel.startswith('src/main/resources/assets/atum/') and any(k in rel for k in ['desert_helmet_','desert_chest_','desert_legs_','desert_boots_','/armor/desert_iron_','/armor/desert_gold_','/armor/desert_diamond_']) and entry.endswith(('.png','.json'))
  context=rel in ['gradle.properties','build.gradle','LICENSE','src/main/java/com/teammetallurgy/atum/Atum.java',
   'src/main/java/com/teammetallurgy/atum/init/AtumItems.java','src/main/java/com/teammetallurgy/atum/items/TexturedArmorItem.java',
   'src/main/java/com/teammetallurgy/atum/items/WandererDyeableArmor.java','src/main/java/com/teammetallurgy/atum/client/ClientHandler.java']
  compare=rel.startswith('src/main/resources/assets/atum/') and ('/textures/models/armor/wanderer_armor_' in rel or '/textures/item/wanderer_armor_' in rel) and entry.endswith('.png')
  if native or context or compare:
   b=z.read(entry);p=D/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);entries.append({'entry':entry,'path':str(p.relative_to(D)),'sha256':sha(b),'purpose':'prior Wanderer comparison' if compare else 'native Desert or source binding'})
save('provenance.json',{'repository':'https://github.com/'+inv['repository'],'commit':inv['commit'],'archive':str(archive),'archive_sha256':sha(archive.read_bytes()),'entries':entries,'reuse':'Existing fixed source archive; no fresh retrieval or global compatibility claim'})
A=D/'source/src/main/resources/assets/atum'; inventory=[]
for row in entries:
 p=D/row['path']
 if p.suffix=='.png':
  im=Image.open(p).convert('RGBA');inventory.append({'path':row['path'],'size':im.size,'rgba_sha256':sha(im.tobytes()),'alpha_bbox':im.getchannel('A').getbbox(),'visible_pixels':sum(a>0 for a in im.getchannel('A').get_flattened_data())})
save('native-png-index.json',inventory)
bindings=[]
for m in ['iron','gold','diamond']:
 for s in ['helmet','chest','legs','boots']:
  ident=f'desert_{s}_{m}';p=A/'models/item'/f'{ident}.json';model=json.loads(p.read_text()); layers=[]
  for k,v in model['textures'].items():
   ns,path=v.split(':');assert ns=='atum';tex=A/'textures'/f'{path}.png';assert tex.exists()
   layers.append({'layer':k,'texture':v,'path':str(tex.relative_to(D)),'sha256':sha(tex.read_bytes())})
  bindings.append({'id':'atum:'+ident,'model':str(p.relative_to(D)),'parent':model['parent'],'layers':layers,
   'worn_base':f'atum:textures/models/armor/desert_{m}_armor_{2 if s=="legs" else 1}.png',
   'worn_overlay':f'atum:textures/models/armor/desert_{m}_armor_{2 if s=="legs" else 1}_overlay.png'})
save('static-bindings.json',bindings)
def page(title,paths,cols,cell):
 out=Image.new('RGB',(cols*cell[0],42+((len(paths)+cols-1)//cols)*cell[1]),'#555b60');dr=ImageDraw.Draw(out);dr.text((10,10),title,fill='white')
 for i,p in enumerate(paths):
  im=Image.open(p).convert('RGBA');scale=min((cell[0]-16)//im.width,(cell[1]-42)//im.height);im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
  x=i%cols*cell[0];y=42+i//cols*cell[1];out.paste(im,(x+(cell[0]-im.width)//2,y),im);dr.text((x+5,y+cell[1]-32),p.stem,fill='white')
 return out
icons=[A/'textures/item'/f'desert_{s}_{m}{ov}.png' for m in ['iron','gold','diamond'] for s in ['helmet','chest','legs','boots'] for ov in ['', '_overlay']]
worn=[A/'textures/models/armor'/f'desert_{m}_armor_{layer}{ov}.png' for m in ['iron','gold','diamond'] for layer in [1,2] for ov in ['', '_overlay']]
page('NATIVE ICON LAYERS / nearest integer enlargement / NOT GAME',icons,8,(164,184)).save(D/'native-icon-layers.png')
page('NATIVE WORN ATLASES / NOT GAME / no geometry assertion',worn,4,(388,252)).save(D/'native-worn-layers.png')
# Diagnostic tint math only, not proof of exact renderer blending or sRGB behavior.
tint=(14869989>>16&255,14869989>>8&255,14869989&255)
composite=[]
for m in ['iron','gold','diamond']:
 for s in ['helmet','chest','legs','boots']:
  ident=f'desert_{s}_{m}';base=Image.open(A/'textures/item'/f'{ident}.png').convert('RGBA');overlay=Image.open(A/'textures/item'/f'{ident}_overlay.png').convert('RGBA')
  rgb=ImageChops.multiply(base.convert('RGB'),Image.new('RGB',base.size,tint));rgb.putalpha(base.getchannel('A'));rgb.alpha_composite(overlay)
  p=D/'diagnostic'/f'{ident}.png';p.parent.mkdir(exist_ok=True);rgb.save(p);composite.append(p)
page('DEFAULT TINT MATH COMPOSITE / diagnostic ONLY / NOT GAME',composite,4,(222,236)).save(D/'icon-tint-diagnostic.png')
dedup=[]
for layer in [1,2]:
 for ov in ['', '_overlay']:
  paths=[A/'textures/models/armor'/f'{prefix}_{layer}{ov}.png' for prefix in ['wanderer_armor','desert_iron_armor','desert_gold_armor','desert_diamond_armor']]
  images=[Image.open(p).convert('RGBA') for p in paths]
  for i in range(1,4):
   a,b=images[0],images[i];equal=a.size==b.size
   dedup.append({'prior':str(paths[0].relative_to(D)),'candidate':str(paths[i].relative_to(D)),'same_dimensions':equal,
    'same_alpha':equal and a.getchannel('A').tobytes()==b.getchannel('A').tobytes(),'same_RGBA':equal and a.tobytes()==b.tobytes(),
    'changed_RGBA_pixels':sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data())) if equal else None})
save('wanderer-structural-comparison.json',dedup)
print('Prepared',len(entries),'source entries and',len(inventory),'native PNG; actual page review next')
