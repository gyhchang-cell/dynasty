#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 s=importlib.util.spec_from_file_location('detail',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 m.SPECS={f'F{i:02}':(6,14,6,7) for i in range(1,5)};m.main()
if __name__=='__main__':main()
