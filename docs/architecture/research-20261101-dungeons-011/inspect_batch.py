#!/usr/bin/env python3
"""Four new whole tower candidates from fixed local sources, never game execution."""
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 discovery=load('discovery',OUT.parent/'research-20261101-dungeons-004/inspect_batch.py')
 renderer=load('renderer',OUT.parent/'research-20261101-dungeons-001/inspect_batch.py');renderer.OUT=OUT
 renderer.SELECTION=[('kaisyn','*城镇与塔楼*jar','https://modrinth.com/mod/towns-and-towers',[
  'outpost/towers/birch/base_plate','outpost/towers/exclusives/oriental/base_plate',
  'outpost/towers/exclusives/swedish/base_plate','outpost/towers/exclusives/tudor/base_plate'])]
 paths=[ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json']
 paths+=sorted((ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for name in ['sources.json','scope-expansion-sources.json','manual-review.json','outpost-scope-register.json']:
   if (folder/name).is_file():paths.append(folder/name)
 seen=set()
 for p in paths:discovery.collect(json.loads(p.read_text()),seen)
 selected=[f'data/{ns}/structures/{n}.nbt' for ns,_,_,names in renderer.SELECTION for n in names]
 assert len(selected)==len(set(selected))==4 and not set(selected)&seen
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(local_only=True,network_requests=0,
  java_run=False,game_run=False,formal_credit_added=0,indices_checked=[str(p) for p in paths],selected_members=selected,
  proposed_relevance='DUN03 whole guard/lookout towers; do not conflate this tower scope with fortified courtyard scopes.',
  prefilter_is_not_semantic_dedup=True),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
