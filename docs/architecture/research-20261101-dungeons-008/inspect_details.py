#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
m.SPECS={'F01':(1,4,4,2),'F02':(1,5,5,3),'F03':(3,5,6,7),'F04':(3,6,12,8)}
if __name__=='__main__':m.main()
