from pathlib import Path
import zipfile,json,hashlib,shutil
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent
commit='f017b15a2b23a6474d03d8e4b4e9e244247ffa24';archive=B/'frostiful-fixed-source.zip';shutil.copyfile('/tmp/dynasty-frostiful-d51.zip',archive)
sha=lambda b:hashlib.sha256(b).hexdigest();entries={}
with zipfile.ZipFile(archive) as z:
 prefix=z.namelist()[0]
 for n in z.namelist():
  rel=n.removeprefix(prefix)
  if n.endswith('/'):continue
  keep=rel in ['LICENSE','CREDITS.md','gradle.properties','README.md','src/main/resources/fabric.mod.json']
  keep|=rel.endswith('.java') and any(rel.endswith('/'+x+'.java') for x in ['Frostiful','FItems','FrostResistantArmorMaterial','FrostResistantArmorMaterials','FrostifulClient','FrostifulModelLoadingPlugin','ArmorFeatureRendererMixin'])
  keep|=rel.startswith('src/main/resources/assets/frostiful/models/item/fur_') and rel.endswith('.json')
  keep|=rel.startswith('src/main/resources/assets/frostiful/textures/item/fur_') and rel.endswith('.png')
  keep|=rel.startswith('src/main/resources/assets/minecraft/textures/models/armor/frostiful_fur_') and rel.endswith('.png')
  keep|=rel.startswith('src/main/resources/') and rel.endswith('.mixins.json')
  if not keep:continue
  f=B/'source'/rel;f.parent.mkdir(parents=True,exist_ok=True);b=z.read(n);f.write_bytes(b);entries[rel]=sha(b)
prov={'official_repository':'https://github.com/TheDeathlyCow/frostiful','branch_context':'1.20.1','commit':commit,'url':'https://codeload.github.com/TheDeathlyCow/frostiful/zip/'+commit,'archive':str(archive),'archive_sha256':sha(archive.read_bytes()),'entries':entries,'not_executed':True}
(B/'provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
# Only native source contact sheets: no pixel edits to the originals, integer enlargement.
icons=sorted((B/'source/src/main/resources/assets/frostiful/textures/item').glob('fur_*.png'));atlases=sorted((B/'source/src/main/resources/assets/minecraft/textures/models/armor').glob('*.png'))
for filename,files,columns,w,h in [('native-icons.png',icons,4,250,210),('native-wear.png',atlases,2,550,330)]:
 im=Image.new('RGB',(columns*w,((len(files)+columns-1)//columns)*h),'#555b60');draw=ImageDraw.Draw(im)
 for i,f in enumerate(files):
  a=Image.open(f).convert('RGBA');x=i%columns*w+12;y=i//columns*h+10;k=min((w-24)//a.width,(h-50)//a.height);draw.text((x,y),f.name,fill='white');a=a.resize((a.width*k,a.height*k),Image.Resampling.NEAREST);im.paste(a,(x,y+30),a)
 im.save(B/filename)
print('entries',len(entries),'icon_png',len(icons),'worn_png',len(atlases))
