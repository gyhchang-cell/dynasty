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
 for e in d['entries']:
  for pool in e['outgoing_pools']:
   if pool['pool']=='minecraft:empty':pool['status']='TERMINAL_EMPTY'
 d['batch_note']='Four narrow whole tower candidates; one-level outgoing definitions checked, no actor or empty-terminal building credit.'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
