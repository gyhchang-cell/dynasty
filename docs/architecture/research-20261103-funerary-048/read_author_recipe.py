"""Read original altar assembly registration with Python; no Java execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def main():
    path=BASE/'research-20261103-funerary-043/read_class.py'
    spec=importlib.util.spec_from_file_location('class_reader043',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    src=json.loads((OUT/'sources.json').read_text());archive=Path(src['source_archives'][0]['path']);rows=[];lines=[]
    members=['com/github/tartaricacid/touhoulittlemaid/block/multiblock/MultiBlockAltar.class',
        'com/github/tartaricacid/touhoulittlemaid/block/multiblock/MultiBlockManager.class',
        'com/github/tartaricacid/touhoulittlemaid/compat/patchouli/MultiblockRegistry.class']
    with ZipFile(archive) as z:
        for member in members:
            raw=z.read(member);data,resolve=m.parse(raw)
            for method in data['methods']:
                if 'code_hex' not in method:continue
                ins=m.decode(bytes.fromhex(method['code_hex']),resolve);method['instructions']=ins
                lines.append('\n'+member+' :: '+method['name']+method['descriptor'])
                lines.extend(f"{e['pc']:4d} {e['mnemonic']:18s} {str(e['operands']):18s} {e['reference'] or ''} {e['branch_targets']}" for e in ins)
            rows.append(dict(member=member,sha256=hashlib.sha256(raw).hexdigest(),class_data=data))
    report=dict(source_archive=str(archive),source_archive_sha256=src['source_archives'][0]['sha256'],classes=rows,
        decoder=dict(path=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest()),
        java_run=False,classes_loaded=False,code_executed=False,building_credit_added=0)
    (OUT/'class-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (OUT/'class-reading.txt').write_text('\n'.join(lines)+'\n')
    print([(r['member'],len(r['class_data']['methods'])) for r in rows])
if __name__=='__main__':main()
