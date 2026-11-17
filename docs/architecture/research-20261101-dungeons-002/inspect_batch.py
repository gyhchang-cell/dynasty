#!/usr/bin/env python3
"""Next offline batch: original complete-layout candidates, never game assets."""
import importlib.util
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PREVIOUS=OUT.parent/'research-20261101-dungeons-001/inspect_batch.py'

def collect_members(value,result):
 if isinstance(value,dict):
  for key in ('member','complete_building_identity'):
   if isinstance(value.get(key),str):result.add(value[key])
  for child in value.values():collect_members(child,result)
 elif isinstance(value,list):
  for child in value:collect_members(child,result)

def main():
 spec=importlib.util.spec_from_file_location('previous_batch_renderer',PREVIOUS)
 renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
 renderer.OUT=OUT
 renderer.SELECTION=[
  ('ati_structures','*ATi*jar','https://www.curseforge.com/minecraft/mc-mods/ati-structures',[
   'castillo','dark_keep','deepslate_keep','granite_fort','old_fort','small_keep','woodland_keep','wither_keep',
   'dojo','mosque','underground_monument','warden_monument']),
  ('trek','*远足*jar','https://modrinth.com/datapack/trek',[
   'overworld/rare/pyramide_of_anubis','overworld/rare/maya','overworld/rare/sunken_city','overworld/rare/villager_fortress']),
 ]
 seen=set();indices=[]
 locations=[ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json']
 locations+=sorted((ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for filename in ('sources.json','scope-expansion-sources.json','manual-review.json'):
   path=folder/filename
   if path.is_file():locations.append(path)
 for path in locations:
  collect_members(json.loads(path.read_text()),seen);indices.append(str(path))
 selected=[f'data/{ns}/structures/{name}.nbt' for ns,_,_,names in renderer.SELECTION for name in names]
 assert len(set(selected))==16
 assert not set(selected)&seen,sorted(set(selected)&seen)
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(
  local_only=True,network_requests=0,skill='find-skills applied; existing offline tools selected',
  historical_indices_checked=indices,prior_member_names=len(seen),new_selected_members=selected,
  stage='Member-name prefilter only; actual views, completeness, family dedup and relevance still required',
  prompt_write=False,java=False,game=False,formal_credit_added=0),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
