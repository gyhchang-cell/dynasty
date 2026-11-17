#!/usr/bin/env python3
"""Eight local library-house studies, with no automatic religious-complex credit."""
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]

def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
 discovery=load('discovery',OUT.parent/'research-20261101-dungeons-004/inspect_batch.py')
 renderer=load('renderer',OUT.parent/'research-20261101-dungeons-001/inspect_batch.py')
 renderer.OUT=OUT
 renderer.SELECTION=[('trek','*远足*jar','https://modrinth.com/datapack/trek',[
  'village/cherry/houses/cherry_library_1','village/swamp/houses/swamp_library_1','village/swamp_vanilla/houses/swamp_library_1']),
  ('kaisyn','*城镇与塔楼*jar','https://modrinth.com/mod/towns-and-towers',[
  'village/flower_forest_japanese/houses/flower_forest_library_1',
  'village/badlands_pueblo/houses/badlands_library_1',
  'village/birch_forest_romanian/houses/birch_forest_cartographer_and_library_1']),
  ('terralith','*Terralith*jar','https://modrinth.com/datapack/terralith',[
  'village/fortified/houses/library','village/desert/houses/library1'])]
 paths=[ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json']
 paths+=sorted((ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for name in ['sources.json','scope-expansion-sources.json','manual-review.json','outpost-scope-register.json']:
   if (folder/name).is_file():paths.append(folder/name)
 seen=set()
 for p in paths:discovery.collect(json.loads(p.read_text()),seen)
 selected=[f'data/{ns}/structures/{n}.nbt' for ns,_,_,names in renderer.SELECTION for n in names]
 assert len(selected)==len(set(selected))==8 and not set(selected)&seen
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(local_only=True,network_requests=0,java_run=False,game_run=False,
  formal_credit_added=0,indices_checked=[str(p) for p in paths],selected_members=selected,
  proposed_relevance='DUN04/DUN07 small archive/reading rooms only; not entire cliff monastery, three-island temple or Daoist-style acceptance.',
  family_warning='Compare two swamp members as a possible variant family; filenames and biome swaps are not independent designs.',
  prefilter_is_not_semantic_dedup=True),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
