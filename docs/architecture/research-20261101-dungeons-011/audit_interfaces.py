#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('interfaces',OUT.parent/'research-20261101-dungeons-003/audit_interfaces.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
if __name__=='__main__':
 m.main()
 p=OUT/'interface-audit.json';d=json.loads(p.read_text());d.pop('quarry',None)
 d['batch_note']='Four whole tower candidates; oriental cat actor pool absent from this fixed archive, not automatically a missing room.'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
