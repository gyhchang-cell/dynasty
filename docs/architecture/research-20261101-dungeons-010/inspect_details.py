#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
m.SPECS={'F01':(2,8,3,3),'F02':(10,17,7,16),'F03':(3,8,16,12),'F04':(3,7,4,6),'F05':(7,12,15,11)}
if __name__=='__main__':m.main()
