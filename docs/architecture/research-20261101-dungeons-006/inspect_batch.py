#!/usr/bin/env python3
"""Four local complete-outpost candidates; discovery is not reference credit."""
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
  'overworld/medium/desert_outpost','overworld/medium/jungle_outpost']),
  ('terralith','*Terralith*jar','https://modrinth.com/datapack/terralith',[
  'regular/desert_outpost','unsorted/villager_outpost'])]
 paths=sorted((ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 paths+=[ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json']
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for name in ['sources.json','scope-expansion-sources.json','manual-review.json','outpost-scope-register.json']:
   if (folder/name).is_file():paths.append(folder/name)
 seen=set()
 for p in paths:discovery.collect(json.loads(p.read_text()),seen)
 selected=[f'data/{ns}/structures/{name}.nbt' for ns,_,_,names in renderer.SELECTION for name in names]
 assert len(selected)==4 and not set(selected)&seen
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(local_only=True,network_requests=0,
  indices_checked=[str(p) for p in paths],selected_members=selected,formal_credit_added=0,
  purpose='Inspect complete outpost spatial organizations against isolated DUN03 outpost scopes, without automatically sharing scope credits.',
  exclusions=['End city tower_base/tower_piece/tower_top are unassembled components, not extra complete buildings.',
   'Towns and Towers tower_pieces and outpost_captain entity are not complete architectural examples.',
   'Repurposed watchtower/watchtower_aged and Trek mangrove variants require family review; filenames are not independent credits.'],
  prefilter_is_not_semantic_dedup=True,java_run=False,game_run=False),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
