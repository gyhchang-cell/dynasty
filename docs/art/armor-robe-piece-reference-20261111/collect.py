from pathlib import Path
import json,zipfile,hashlib,subprocess
D=Path(__file__).resolve().parent
P=Path('/Users/a15356015027/Public/.minecraft/versions/锻造之旅/mods/[沉浸式盔甲] immersive_armors-1.7.2+1.20.1-forge.jar')
H=lambda b:hashlib.sha256(b).hexdigest()
classes=['Items','ItemsClient','ClientMain','Main','item/ExtendedArmorItem','item/DyeableExtendedArmorItem','item/ExtendedArmorMaterial','mixin/MixinArmorFeatureRenderer','client/render/entity/piece/Piece','client/render/entity/piece/LayerPiece','client/render/entity/piece/LowerBodyLayerPiece','client/render/entity/piece/MiddleBodyLayerPiece','client/render/entity/piece/LowerLeggingsLayerPiece','client/render/entity/piece/MiddleLeggingsLayerPiece','client/render/entity/piece/UpperBodyLayerPiece','client/render/entity/piece/UpperLeggingsLayerPiece']
classes=['immersive_armors/'+n+'.class' for n in classes];rows=[]
with zipfile.ZipFile(P) as z:
 for n in z.namelist():
  if not (n in classes or ('/robe' in n and n.endswith(('.png','.png.mcmeta','.json')) and ('/textures/' in n or '/models/item/' in n)) or n=='immersive_armors.mixins.json'):continue
  b=z.read(n);f=D/'source'/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);r={'entry':n,'local':str(f.relative_to(D)),'sha256':H(b)}
  if n.endswith('.class'):
   out=D/'bytecode'/(f.stem+'.txt');out.parent.mkdir(exist_ok=True);res=subprocess.run(['/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javap','-p','-c','-v',str(f)],capture_output=True,check=True);out.write_bytes(res.stdout);r.update(disassembly=str(out.relative_to(D)),disassembly_sha256=H(res.stdout))
  rows.append(r)
(D/'provenance.json').write_text(json.dumps({'archive':str(P),'archive_sha256':H(P.read_bytes()),'files':rows,'mod_class_execution':False,'game_starts':0},indent=2)+'\n');print(len(rows),'native entries, read-only javap')
