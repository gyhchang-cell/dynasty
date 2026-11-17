#!/usr/bin/env python3
"""Reread old complete fortifications against unchanged narrow purpose scopes."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 spec=importlib.util.spec_from_file_location('prepare',OUT.parent/'research-20261101-dungeons-021/prepare_review.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('T01',2,'F02',(3,20,7,7)),('T02',2,'F06',(3,12,11,10)),
  ('C01',15,'F01',(6,21,9,9)),('C02',13,'F01',(12,20,10,10))]
 m.main()
if __name__=='__main__':main()
