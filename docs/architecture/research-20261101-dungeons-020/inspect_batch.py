#!/usr/bin/env python3
"""One intact local forest fort body; separate ground tile is not another fort."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 s=importlib.util.spec_from_file_location('batch',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('simply_houses','*简易房屋*jar','https://www.curseforge.com/minecraft/mc-mods/simply-houses',
  ['forest_fort/forest_fort'])];m.main()
if __name__=='__main__':main()
