#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 s=importlib.util.spec_from_file_location('prepare',OUT.parent/'research-20261101-dungeons-021/prepare_review.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('T01',16,'F01',(7,15,4,10)),('H01',11,'F04',(7,15,6,7)),('C01',18,'F01',(6,14,4,10))];m.main()
if __name__=='__main__':main()
