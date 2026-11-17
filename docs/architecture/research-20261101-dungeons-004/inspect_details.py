#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT
module.SPECS={'F01':(9,17,14,23),'F02':(7,13,31,18),'F03':(8,12,12,12),
 'F04':(14,19,13,9),'F05':(7,14,20,35),'F06':(10,26,13,11),
 'F07':(3,8,9,8),'F08':(3,6,13,5)}
if __name__=='__main__':module.main()
