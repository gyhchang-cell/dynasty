#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT
module.SPECS={'F01':(7,12,14,16),'F02':(4,7,9,4),'F03':(4,7,5,2),'F04':(4,6,8,10),
 'F05':(7,25,3,20),'F06':(5,10,17,15),'F07':(3,5,10,7),'F08':(8,14,14,21)}
if __name__=='__main__':module.main()
