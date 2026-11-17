"""Freeze the remaining Forge item factory and client lifecycle used by the selected source pack."""
from pathlib import Path
import json,hashlib,subprocess,zipfile
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (D/'factory-provenance.json').exists()
    prior=json.loads((D/'class-provenance.json').read_text());jar=Path(prior['archive']['path']);assert sha(jar)==prior['archive']['sha256'];rows=[]
    with zipfile.ZipFile(jar) as z:
        for name in ['ArmorOfTheAgesForge$ItemRegistryImpl','ArmorOfTheAgesForge','CommonClass','client/ArmorOfTheAgesClientForge','item/AotAMaterials$DoTArmorMaterial']:
            e='org/dawnoftime/armoroftheages/'+name+'.class';b=z.read(e);h=hashlib.sha256(b).hexdigest();loc=Path('classes')/(h[:12]+'-'+Path(e).name);(D/loc).write_bytes(b);out=subprocess.check_output([prior['javap'],'-v','-c','-p',str(D/loc)],text=True);text=Path('disassembly')/(Path(e).name+'.txt');(D/text).write_text(out);rows.append({'jar':str(jar),'entry':e,'local':str(loc),'sha256':h,'disassembly':str(text),'disassembly_sha256':sha(D/text)})
    (D/'factory-provenance.json').write_text(json.dumps({'capture_factory_sha256':sha(Path(__file__)),'classes':rows,'mode':'STATIC_JAVAP_ONLY'},ensure_ascii=False,indent=2)+'\n');print('Five exact factory/lifecycle/material classes frozen; no code execution')
if __name__=='__main__':main()
