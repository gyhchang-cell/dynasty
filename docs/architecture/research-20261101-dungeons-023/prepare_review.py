#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 s=importlib.util.spec_from_file_location('prepare',OUT.parent/'research-20261101-dungeons-021/prepare_review.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('T01',12,'F03',(2,9,6,8)),('C01','WHOLE','W008',(2,6,5,5)),('C02',11,'F03',(3,12,6,7))];m.main()
if __name__=='__main__':main()
