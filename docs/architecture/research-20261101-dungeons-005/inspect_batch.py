#!/usr/bin/env python3
"""Study urban-house candidates; cottage variants receive no automatic credit."""
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
 discovery=load('discovery',OUT.parent/'research-20261101-dungeons-004/inspect_batch.py')
 renderer=load('renderer',OUT.parent/'research-20261101-dungeons-001/inspect_batch.py')
 renderer.OUT=OUT
 renderer.SELECTION=[('trek','*远足*jar','https://modrinth.com/datapack/trek',[
  'overworld/medium/plains_cottage','overworld/medium/spruce_cottage','overworld/medium/snow_cottage',
  'overworld/medium/maison','overworld/medium/haunted_house','overworld/medium/explorer_cabin',
  'overworld/medium/sorcerers_house','overworld/rare/wooden_manor'])]
 paths=[ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json']
 paths+=sorted((ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for name in ('sources.json','scope-expansion-sources.json','manual-review.json','acceptance-index.json'):
   p=folder/name
   if p.is_file():paths.append(p)
 seen=set()
 for p in paths:discovery.collect(json.loads(p.read_text()),seen)
 selected=[f'data/{ns}/structures/{n}.nbt' for ns,_,_,names in renderer.SELECTION for n in names]
 assert len(selected)==len(set(selected))==8 and not set(selected)&seen
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(local_only=True,network_requests=0,formal_credit_added=0,
  java=False,game=False,selected_members=selected,indices_checked=[str(p) for p in paths],
  previous_member_prefilter_count=len(seen),prefilter_is_not_semantic_dedup=True,
  skill='find-skills applied; offline tools sufficient',
  family_warning='Plains/spruce/snow cottage filenames do not establish distinct designs. Compare original geometry, functional layout and variant families before any proposal.'),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
