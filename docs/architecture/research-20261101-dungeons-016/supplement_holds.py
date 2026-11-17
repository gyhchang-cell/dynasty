#!/usr/bin/env python3
"""Additional raw sections for two prior holds and four already-studied controls."""
import hashlib
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
SELECTION=[('H01',11,'F04',(7,14,7,8)),('H02',12,'F03',(6,12,16,5)),
           ('T01',13,'F02',(6,18,8,10)),('T02',15,'F03',(2,12,5,4)),('T03',14,'F02',(2,23,5,7))]
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 folder=OUT/'hold-sections';folder.mkdir(exist_ok=True)
 records=[];specs={}
 for ident,batch,oldid,cuts in SELECTION:
  p=BASE/f'research-20261101-dungeons-{batch:03d}/sources.json'
  row=next(e for e in json.loads(p.read_text())['candidates'] if e['id']==oldid).copy()
  row['id']=ident;row['prior_identity']=f'{batch:03d}-{oldid}';row['original_index']=ev(p)
  records.append(row);specs[ident]=cuts
 p=BASE/'continuation-20261022/references/whole-candidates/candidates.json'
 old=next(e for e in json.loads(p.read_text())['candidates'] if e['id']=='W008')
 records.append(dict(id='T04',prior_identity='W008',source_archive=old['source_jar'],source_archive_sha256=old['source_jar_sha256'],
                     member=old['member'],nbt_sha256=old['nbt_sha256'],size=old['size'],doors=old['doors'],original_index=ev(p)))
 specs['T04']=(3,9,10,4)
 (folder/'sources.json').write_text(json.dumps(dict(candidates=records,new_source_templates=0,formal_credit_added=0,
  note='All six identities were studied previously. Six supplementary section sheets are not six new buildings.'),ensure_ascii=False,indent=2)+'\n')
 s=importlib.util.spec_from_file_location('details',BASE/'research-20261101-dungeons-002/inspect_details.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=folder;m.SPECS=specs;m.main()
if __name__=='__main__':main()
