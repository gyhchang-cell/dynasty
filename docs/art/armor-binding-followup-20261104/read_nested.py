"""Extract nested static dependencies as evidence, never load their code."""
from pathlib import Path
import json,hashlib,zipfile,subprocess
D=Path(__file__).resolve().parent
p=json.loads((D/'class-provenance.json').read_text()); a=next(a for a in p['archives'] if 'celestial_core' in a['path']); j=p['javap']
with zipfile.ZipFile(a['path']) as z:
 entry='META-INF/jarjar/l2damagetracker-0.3.8.jar'; b=z.read(entry); out=D/'nested'/Path(entry).name;out.parent.mkdir(exist_ok=True);out.write_bytes(b)
 local={'container':a,'entry':entry,'local':str(out.relative_to(D)),'sha256':hashlib.sha256(b).hexdigest()}
 records=[]
 with zipfile.ZipFile(out) as nested:
  classes=[e for e in nested.namelist() if e.endswith('.class') and any(k in e for k in ['/materials/generic/GenericArmorItem','/materials/generic/ExtraArmorConfig','/materials/api/ArmorConfig','/materials/api/IMatArmorType','/materials/vanilla/GenItemVanillaType','/materials/vanilla/SimpleArmorMaterial','/materials/vanilla/ArmorMaterial','/materials/api/MatRegistrate'])]
  print('classes',classes)
  for entry in classes:
   b=nested.read(entry);cp=Path('classes/l2damagetracker')/Path(entry).name;(D/cp).parent.mkdir(exist_ok=True);(D/cp).write_bytes(b)
   text=subprocess.run([j,'-c','-p','-v',str(D/cp)],capture_output=True,text=True,check=True).stdout;dest=Path('disassembly/l2damagetracker')/(Path(entry).stem+'.txt');(D/dest).parent.mkdir(exist_ok=True);(D/dest).write_text(text)
   records.append({'nested_archive':local,'entry':entry,'local':str(cp),'sha256':hashlib.sha256(b).hexdigest(),'disassembly':str(dest),'disassembly_sha256':hashlib.sha256((D/dest).read_bytes()).hexdigest()})
(D/'nested-class-provenance.json').write_text(json.dumps({'nested_archive':local,'classes':records},ensure_ascii=False,indent=2)+'\n')
