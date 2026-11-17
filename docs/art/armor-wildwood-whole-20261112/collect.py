from pathlib import Path
import zipfile,hashlib,json,shutil
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;a=B/'roots-fixed-source.zip';shutil.copyfile('/tmp/dynasty-roots-d54.zip',a);H=lambda b:hashlib.sha256(b).hexdigest();entries={}
names=['ItemSylvanArmor.java','ItemWildwoodArmor.java','ModelSylvanArmor.java','ModelWildwoodArmor.java','ModItems.java','RegistryManager.java','ClientProxy.java','Roots.java','build.gradle','gradle.properties','LICENSE','LICENSE.md','LICENSE.txt','README.md']
with zipfile.ZipFile(a) as z:
 root=z.namelist()[0]
 for n in z.namelist():
  rel=n.removeprefix(root)
  if n.endswith('/'):continue
  keep=Path(rel).name in names
  keep|=any(rel.endswith('/'+family+'_'+part+ext) for family in ['wildwood','sylvan'] for part in ['helmet','chestplate','leggings','boots'] for ext in ['.json','.png'])
  keep|=any(rel.endswith('/textures/models/armor/'+family+'_armor.png') for family in ['wildwood','sylvan'])
  if not keep:continue
  p=B/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);data=z.read(n);p.write_bytes(data);entries[rel]=H(data)
(B/'provenance.json').write_text(json.dumps({'repository':'https://github.com/MysticMods/Roots','branch':'1.12.2','commit':'27dc32ecf4dfffbc67790bc69ed0b405137dee2f','url':'https://codeload.github.com/MysticMods/Roots/zip/27dc32ecf4dfffbc67790bc69ed0b405137dee2f','archive_sha256':H(a.read_bytes()),'entries':entries,'external_code_executed':False},indent=2)+'\n')
ims=[(r,Image.open(B/'source'/r).convert('RGBA')) for r in entries if r.endswith('.png')];can=Image.new('RGB',(1200,1050),'#555b60');d=ImageDraw.Draw(can)
for i,(r,im) in enumerate(ims):
 x=10+i%4*300;y=10+i//4*340;k=min(270//im.width,280//im.height);d.text((x,y),Path(r).name+' '+str(im.size),fill='white');t=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST);can.paste(t,(x,y+24),t)
can.save(B/'native-source-images.png');print('entries',len(entries),'png',len(ims))
