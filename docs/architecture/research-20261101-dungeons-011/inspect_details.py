#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
m.SPECS={'F01':(6,18,9,10),'F02':(9,23,12,11),'F03':(8,19,13,7),'F04':(13,20,6,7)}
if __name__=='__main__':m.main()
