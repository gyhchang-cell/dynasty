#!/usr/bin/env python3
"""Inspect uncredited tower/pillar candidates; whole defensive use still needs proof."""
import importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent
def main():
 spec=importlib.util.spec_from_file_location('renderer',OUT.parent/'research-20261101-dungeons-017/inspect_batch.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT
 m.SELECTION=[('legendary_monsters','*legendarymonsters*jar',None,[
  'shulker_tower_new_old']),('betterendisland','*YungsBetterEndIsland*jar','https://www.curseforge.com/minecraft/mc-mods/yungs-better-end-island',[
  'tower_initial','tower_broken'])]
 m.main()
if __name__=='__main__':main()
