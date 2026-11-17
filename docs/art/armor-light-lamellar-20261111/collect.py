from pathlib import Path
import zipfile,json,hashlib,subprocess
D=Path(__file__).resolve().parent;P=Path('/Users/a15356015027/Public/.minecraft/versions/剑痕纪元/mods/[时代铠甲] Armor of the Ages-forge-1.20.1-1.3.11.jar');H=lambda b:hashlib.sha256(b).hexdigest()
classes=['registry/ItemRegistry','registry/ModelProviderRegistry','client/ArmorModelProvider','client/ArmorModelProvider$MixedArmorModelProvider','client/ArmorModelSupplier','item/HumanoidArmorItem','item/ForgeHumanoidArmorItem','item/ForgeHumanoidArmorItem$1','mixin/MixinHumanoidArmorLayer','config/PreferredModel','ArmorOfTheAgesForge$ItemRegistryImpl','client/models/ArmorModel']
classes=['org/dawnoftime/armoroftheages/'+n+'.class' for n in classes];rows=[]
with zipfile.ZipFile(P) as z:
 for n in z.namelist():
  pick=n in classes or n.endswith('.class') and '/models/japanese_light_armor/' in n
  pick=pick or ('japanese_light_armor' in n and n.endswith(('.png','.json')) and ('/models/item/' in n or '/textures/' in n))
  if not pick:continue
  b=z.read(n);f=D/'source'/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);r={'entry':n,'local':str(f.relative_to(D)),'sha256':H(b)}
  if n.endswith('.class'):
   o=D/'bytecode'/(f.stem+'.txt');o.parent.mkdir(exist_ok=True);res=subprocess.run(['/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javap','-p','-c','-v',str(f)],capture_output=True,check=True);o.write_bytes(res.stdout);r.update(disassembly=str(o.relative_to(D)),disassembly_sha256=H(res.stdout))
  rows.append(r)
(D/'provenance.json').write_text(json.dumps({'archive':str(P),'archive_sha256':H(P.read_bytes()),'files':rows,'game_starts':0,'mod_execution':False},indent=2)+'\n');print(len(rows),'native entries fixed')
