from pathlib import Path
import zipfile,json,hashlib,shutil
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent; a=B/'eidolon-fixed-source.zip';shutil.copyfile('/tmp/dynasty-eidolon-d53.zip',a);H=lambda b:hashlib.sha256(b).hexdigest();entries={}
names=['SilverArmorItem.java','SilverArmorModel.java','ArmorModel.java','WarlockRobesItem.java','WarlockArmorModel.java','ClientRegistry.java','ClientEvents.java','Registry.java','Eidolon.java','build.gradle','gradle.properties','LICENSE','LICENSE.txt','README.md']
with zipfile.ZipFile(a) as z:
 root=z.namelist()[0]
 for n in z.namelist():
  rel=n.removeprefix(root)
  if n.endswith('/'):continue
  keep=Path(rel).name in names
  keep|=('/models/item/' in rel or '/textures/item/' in rel) and any(Path(rel).stem==k for k in ['silver_helmet','silver_chestplate','silver_leggings','silver_boots','warlock_hat','warlock_cloak','warlock_boots'])
  keep|=rel.endswith('/textures/entity/silver_armor.png') or rel.endswith('/textures/entity/warlock_robes.png')
  if not keep:continue
  p=B/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);b=z.read(n);p.write_bytes(b);entries[rel]=H(b)
(B/'provenance.json').write_text(json.dumps({'repository':'https://github.com/Alexthw46/Eidolon-Repraised','branch':'1.20.1','commit':'f53707d478f91496a07c9646f603d433a273d57f','url':'https://codeload.github.com/Alexthw46/Eidolon-Repraised/zip/f53707d478f91496a07c9646f603d433a273d57f','archive_sha256':H(a.read_bytes()),'entries':entries,'external_code_executed':False},indent=2)+'\n')
ims=[(r,Image.open(B/'source'/r).convert('RGBA')) for r in entries if r.endswith('.png')]
canvas=Image.new('RGB',(1200,1050),'#555b60');d=ImageDraw.Draw(canvas)
for i,(r,im) in enumerate(ims):
 x=i%4*300+10;y=i//4*340+10;k=min(275//im.width,280//im.height);d.text((x,y),Path(r).name+' '+str(im.size),fill='white');t=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST);canvas.paste(t,(x,y+24),t)
canvas.save(B/'native-source-images.png');print('entries',len(entries),'png',len(ims))
