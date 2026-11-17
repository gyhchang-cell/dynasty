#!/usr/bin/env python3
"""Follow keyword-negative metadata leads; do not pre-credit them as guard towers."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 spec=importlib.util.spec_from_file_location('renderer',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('goetyawaken','*goetyawaken*jar','https://github.com/k1sak1/goetyawaken/issues',[
  'boreal_spire','boreal_spire1','boreal_spire2','illager_station'])]
 m.main()
if __name__=='__main__':main()
