from pathlib import Path
import json,zipfile,hashlib,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2];old=R/'docs/art/armor-biome-shell-reference-20261104';a=json.loads((old/'provenance.json').read_text())['archives'][0];p=Path(a['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'];z=zipfile.ZipFile(p);rows=[]
for n in z.namelist():
 pick=n.endswith('.class') and ('HardenedChitinArmorAquaticItem' in n or n.endswith(('PathogenModItems.class','Modelhardened_chitin_armor.class','PathogenModModels.class')))
 pick=pick or n.startswith('assets/pathogen/models/item/hardened_chitin_armor_aquatic_') and n.endswith('.json')
 pick=pick or n in ['assets/pathogen/textures/items/hardened_'+part+'_aquatic.png' for part in ['helmet','chestplate','leggings','boots']] or n=='assets/pathogen/textures/entities/armor_hardened_aquatic.png'
 if pick:
  f=D/'source'/n;f.parent.mkdir(parents=True,exist_ok=True);b=z.read(n);f.write_bytes(b);r={'entry':n,'local':str(f.relative_to(D)),'sha256':hashlib.sha256(b).hexdigest()}
  if n.endswith('.class'):
   out=D/'bytecode'/(f.name+'.txt');out.parent.mkdir(exist_ok=True);res=subprocess.run(['/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/bin/javap','-p','-c','-v',str(f)],capture_output=True,check=True);out.write_bytes(res.stdout);r.update(disassembly=str(out.relative_to(D)),disassembly_sha256=hashlib.sha256(res.stdout).hexdigest())
  rows.append(r)
(D/'provenance.json').write_text(json.dumps({'archive':str(p),'archive_sha256':a['sha256'],'prior_source':str(old/'provenance.json'),'files':rows,'mod_class_execution':False,'game_starts':0},indent=2)+'\n');print(len(rows),'native entries; only readonly disassembly')
