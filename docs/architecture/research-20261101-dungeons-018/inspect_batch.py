#!/usr/bin/env python3
"""Study four original outpost bodies, not their separately stored camp pieces."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 s=importlib.util.spec_from_file_location('batch',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('repurposed_structures','*结构变体*jar','https://modrinth.com/mod/repurposed-structures',
  ['outposts/badlands/watchtower','outposts/crimson/tower','outposts/end/watchtower','outposts/icy/watchtower'])]
 m.main()
if __name__=='__main__':main()
