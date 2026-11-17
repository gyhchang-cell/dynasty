#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 s=importlib.util.spec_from_file_location('detail',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 m.SPECS={'F01':(2,10,3,3),'F02':(5,14,6,4),'F03':(4,8,8,6),'F04':(3,18,8,6)}
 m.main()
if __name__=='__main__':main()
