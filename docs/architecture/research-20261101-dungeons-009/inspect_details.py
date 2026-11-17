#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
m.SPECS={'F01':(6,11,10,11),'F02':(7,14,20,4),'F03':(3,6,11,10),'F04':(5,10,24,6)}
if __name__=='__main__':m.main()
