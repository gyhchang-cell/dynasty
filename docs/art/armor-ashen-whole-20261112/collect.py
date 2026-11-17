from pathlib import Path
import hashlib,json,zipfile,shutil
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;a=B/'embers-fixed-source.zip';shutil.copyfile('/tmp/dynasty-embers-d55.zip',a);H=lambda b:hashlib.sha256(b).hexdigest();entries={}
with zipfile.ZipFile(a) as z:
 root=z.namelist()[0]
 for n in z.namelist():
  rel=n.removeprefix(root)
  if n.endswith('/'):continue
  keep=Path(rel).name in ['AshenArmorItem.java','AshenArmorModel.java','AshenArmorMaterial.java','EmbersClientEvents.java','Embers.java','gradle.properties','build.gradle','LICENSE','LICENSE.md','LICENSE.txt','README.md']
  data=z.read(n)
  keep|=rel.endswith('.java') and any(x in data for x in [b'new AshenArmorItem',b'new AshenArmorModel'])
  keep|=('/models/item/' in rel or '/textures/item/' in rel) and Path(rel).stem in ['ashen_goggles','ashen_cloak','ashen_leggings','ashen_boots']
  keep|=rel.endswith('/textures/models/armor/robe.png')
  if not keep:continue
  p=B/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);entries[rel]=H(data)
(B/'provenance.json').write_text(json.dumps({'repository':'https://github.com/RCXcrafter/EmbersRekindled','branch':'rekindled','commit':'c900e391c21d21ec35f17f17fba92b96a6fee37e','url':'https://codeload.github.com/RCXcrafter/EmbersRekindled/zip/c900e391c21d21ec35f17f17fba92b96a6fee37e','archive_sha256':H(a.read_bytes()),'entries':entries,'external_code_executed':False},indent=2)+'\n')
ims=[(r,Image.open(B/'source'/r).convert('RGBA')) for r in entries if r.endswith('.png')];can=Image.new('RGB',(1200,720),'#555b60');d=ImageDraw.Draw(can)
for i,(r,im) in enumerate(ims):
 x=10+i%3*400;y=10+i//3*350;k=min(365//im.width,300//im.height);d.text((x,y),Path(r).name+' '+str(im.size),fill='white');t=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST);can.paste(t,(x,y+24),t)
can.save(B/'native-source-images.png');print('entries',len(entries),'png',len(ims))
