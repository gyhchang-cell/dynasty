from pathlib import Path
import zipfile,hashlib,json,subprocess
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent
P=Path('/Users/a15356015027/Public/.minecraft/versions/锻造之旅/mods/GeoTetraArmor-6.9.0-1.0.4-fix.jar')
classes=['GeoTetraArmor','items/ModularArmorItem','items/ModularHeadItem','items/ModularChestItem','items/ModularLegsItem','items/ModularFeetItem','model/ModularArmorModel','model/ModularGeoArmorRenderer','core/mixins/HumanoidArmorLayerMixin']
files={}
with zipfile.ZipFile(P) as z:
 names=[n for n in z.namelist() if not n.endswith('/') and (n in ['ovo/yiran/geotetraarmor/'+x+'.class' for x in classes] or (n.startswith('data/tetra/modules/armor/') and n.endswith('/heavy.json')) or (n.startswith('assets/geotetraarmor/') and any(t in n for t in ['/armor/heavy/','/item/module/armor/'])) or (n.startswith('assets/geotetraarmor/models/item/') and n.endswith('.json')) or (n.startswith('data/tetra/replacements/armor/') and n.endswith('.json')))]
 for n in names:
  data=z.read(n);out=B/'source'/n;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);files[n]=hashlib.sha256(data).hexdigest()
  if n.endswith('.class'):
   d=B/'bytecode'/(n+'.txt');d.parent.mkdir(parents=True,exist_ok=True);d.write_text(subprocess.run(['/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javap','-p','-c','-v',str(out)],capture_output=True,text=True,check=True).stdout)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prov={'archive':str(P),'archive_sha256':sha(P),'entries':files,'disassemblies':{str(f.relative_to(B)):sha(f) for f in (B/'bytecode').rglob('*.txt')},'scope':'fixed native source extraction; files are not reference count'}
(B/'provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
imgs=[n for n in names if n.endswith('.png')];canvas=Image.new('RGB',(1200,1100),'#555b60');d=ImageDraw.Draw(canvas)
for i,n in enumerate(imgs):
 im=Image.open(B/'source'/n).convert('RGBA');x=15+i%3*395;y=15+i//3*260;d.text((x,y),n.split('textures/')[1],fill='white');d.text((x,y+18),str(im.size)+' native original',fill='white');k=min(8,360//im.width,200//im.height);large=im.resize((im.width*k,im.height*k),Image.Resampling.NEAREST);canvas.paste(large,(x,y+45),large)
canvas.save(B/'whole-native-source.png');print('entries',len(names),'png',len(imgs))
