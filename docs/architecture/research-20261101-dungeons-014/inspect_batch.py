#!/usr/bin/env python3
"""Four narrow tower candidates, with no presumption of family independence."""
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 discovery=module('discovery',OUT.parent/'research-20261101-dungeons-004/inspect_batch.py')
 renderer=module('renderer',OUT.parent/'research-20261101-dungeons-001/inspect_batch.py');renderer.OUT=OUT
 renderer.SELECTION=[('kaisyn','*城镇与塔楼*jar','https://modrinth.com/mod/towns-and-towers',[
  'outpost/towers/flower_forest/base_plate','outpost/towers/meadow/base_plate',
  'outpost/towers/savanna/base_plate','outpost/towers/snowy_taiga/base_plate'])]
 paths=[ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json']+sorted((ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for name in ['sources.json','scope-expansion-sources.json','manual-review.json','outpost-scope-register.json','urban-lodging-scope-register.json']:
   if (folder/name).is_file():paths.append(folder/name)
 seen=set()
 for p in paths:discovery.collect(json.loads(p.read_text()),seen)
 members=[f'data/{ns}/structures/{n}.nbt' for ns,_,_,names in renderer.SELECTION for n in names]
 assert len(members)==len(set(members))==4 and not set(members)&seen
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(local_only=True,network_requests=0,java_run=False,game_run=False,
  formal_credit_added=0,indices_checked=[str(p) for p in paths],selected_members=members,
  proposed_relevance='DUN03 narrow whole watchtowers; study complete spatial organization before any family or scope credit.',prefilter_is_not_semantic_dedup=True),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
