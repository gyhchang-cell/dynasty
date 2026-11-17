#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT
module.SPECS={'F01':(4,15,20,11),'F02':(4,8,10,11),'F03':(5,9,12,18),'F04':(5,10,11,12)}
if __name__=='__main__':module.main()
