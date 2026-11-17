#!/usr/bin/env python3
"""Use the established offline renderer with feature positions for this batch."""
import importlib.util
from pathlib import Path

OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('details',OUT.parent/'research-20261101-dungeons-002/inspect_details.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT
module.SPECS={
 'F01':(16,28,11,24), 'F02':(10,23,20,22),
 'F03':(15,39,32,36), 'F04':(5,8,19,18),
 'F05':(11,23,20,10), 'F06':(14,21,39,17),
 'F07':(3,5,10,5), 'F08':(5,12,13,14),
 'F09':(3,5,3,8), 'F10':(5,10,8,8),
 'F11':(10,25,7,11), 'F12':(12,23,14,20),
}
if __name__=='__main__':module.main()
