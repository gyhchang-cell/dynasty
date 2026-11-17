#!/usr/bin/env python3
"""Inspect fortified-village candidates without equating village name and guard use."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 spec=importlib.util.spec_from_file_location('renderer',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('terralith','*地形生成*Terralith*jar','https://modrinth.com/datapack/terralith',[
  'village/fortified/houses/mason','village/fortified/houses/archer','village/fortified/houses/cartographer'])]
 m.main()
if __name__=='__main__':main()
