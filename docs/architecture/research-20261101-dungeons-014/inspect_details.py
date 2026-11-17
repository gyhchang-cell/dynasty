#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
m.SPECS={'F01':(11,18,6,8),'F02':(13,22,8,9),'F03':(13,20,3,6),'F04':(12,24,6,3)}
if __name__=='__main__':m.main()
