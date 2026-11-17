#!/usr/bin/env python3
import importlib.util
import contextlib
import io
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('interfaces',OUT.parent/'research-20261101-dungeons-003/audit_interfaces.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT
if __name__=='__main__':
 with contextlib.redirect_stdout(io.StringIO()): module.main()
 path=OUT/'interface-audit.json'
 data=json.loads(path.read_text());data.pop('quarry',None)
 data['batch_note']='Eight templates; terrain interfaces only. No room-pool assembly or native terrain acceptance.'
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('Read outgoing interfaces for eight templates; terrain interfaces only, no assembly or credit.')
