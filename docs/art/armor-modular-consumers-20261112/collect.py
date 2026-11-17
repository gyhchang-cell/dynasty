from pathlib import Path
import zipfile,hashlib,json,subprocess
B=Path(__file__).resolve().parent
P=Path('/Users/a15356015027/Public/.minecraft/versions/锻造之旅/mods')
H=lambda b:hashlib.sha256(b).hexdigest()
choices={'geckolib-forge-1.20.1-4.8.3.jar':['software/bernie/geckolib/renderer/GeoArmorRenderer.class','software/bernie/geckolib/renderer/GeoArmorRenderer$1.class','software/bernie/geckolib/renderer/GeoArmorRenderer$2.class','META-INF/mods.toml'], 'tetra-1.20.1-6.9.0.jar':['se/mickelus/tetra/client/model/ModularModelLoader.class','se/mickelus/tetra/client/model/ModularModelLoader$1.class'], 'GeoTetraArmor-6.9.0-1.0.4-fix.jar':['META-INF/mods.toml','META-INF/MANIFEST.MF','geotetraarmor.mixins.json','geotetraarmor.refmap.json']}
with zipfile.ZipFile(P/'tetra-1.20.1-6.9.0.jar') as z:
 choices['tetra-1.20.1-6.9.0.jar']=[n for n in z.namelist() if n.startswith('se/mickelus/tetra/client/model/') and n.endswith('.class')]+['se/mickelus/tetra/ClientSetup.class']
prov=[]
for fn,names in choices.items():
 row={'archive':str(P/fn),'sha256':H((P/fn).read_bytes()),'entries':{},'disassemblies':{}}
 with zipfile.ZipFile(P/fn) as z:
  for n in names:
   b=z.read(n); f=B/'source'/fn/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);row['entries'][str(f.relative_to(B))]=H(b)
   if n.endswith('.class'):
    d=B/'bytecode'/fn/(n+'.txt');d.parent.mkdir(parents=True,exist_ok=True);d.write_text(subprocess.run(['/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javap','-p','-c','-v',str(f)],check=True,capture_output=True,text=True).stdout);row['disassemblies'][str(d.relative_to(B))]=H(d.read_bytes())
 prov.append(row)
(B/'provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
print('collected',sum(len(r['entries']) for r in prov))
