#!/usr/bin/env python3
"""Reapply original-source geometry comparison to this independent batch."""
import importlib.util
from pathlib import Path

OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('dedup',OUT.parent/'research-20261101-dungeons-002/check_dedup.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT
if __name__=='__main__':module.main()
