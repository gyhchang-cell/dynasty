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
 p=OUT/'interface-audit.json';data=json.loads(p.read_text());data.pop('quarry',None)
 data['batch_note']='Eight templates; actual sockets select entity pools, not missing room templates.'
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('Read outgoing interfaces for eight house templates; no assembly or credit.')
