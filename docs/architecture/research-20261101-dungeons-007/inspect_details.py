#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT
module.SPECS={'F01':(3,7,6,11),'F02':(7,12,9,8),'F03':(2,5,4,5),'F04':(2,4,2,5),
 'F05':(1,3,3,6),'F06':(5,8,8,3),'F07':(4,7,6,13),'F08':(4,8,14,16)}
if __name__=='__main__':module.main()
