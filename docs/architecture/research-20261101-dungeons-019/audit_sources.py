#!/usr/bin/env python3
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 s=importlib.util.spec_from_file_location('audit',OUT.parent/'research-20261101-dungeons-017/audit_sources.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT;m.main()
if __name__=='__main__':main()
