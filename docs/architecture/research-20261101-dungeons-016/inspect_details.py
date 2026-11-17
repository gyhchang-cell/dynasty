#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
m.SPECS={'F01':(6,14,4,10),'F02':(8,16,8,7),'F03':(8,16,8,7),'F04':(8,16,8,7),'F05':(17,23,9,6)}
if __name__=='__main__':m.main()
