#!/usr/bin/env python3
"""Two dimension-screened complete local Terralith candidates, not new credit."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 s=importlib.util.spec_from_file_location('batch',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('terralith','*地形生成*Terralith*jar','https://modrinth.com/datapack/terralith',
  ['village/desert/houses/castle','unsorted/stonebricks_tower_ruin'])];m.main()
if __name__=='__main__':main()
