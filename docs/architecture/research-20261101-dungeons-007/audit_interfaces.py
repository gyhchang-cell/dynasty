#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('interfaces',OUT.parent/'research-20261101-dungeons-003/audit_interfaces.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT
if __name__=='__main__':
 with contextlib.redirect_stdout(io.StringIO()):module.main()
 p=OUT/'interface-audit.json';d=json.loads(p.read_text());d.pop('quarry',None)
 d['batch_note']='Eight library-house sources; do not turn external village-road sockets or entity pools into missing rooms or additional complete designs.'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print('Audited eight library-house outgoing interfaces; no automatic credit.')
