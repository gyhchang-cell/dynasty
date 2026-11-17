#!/usr/bin/env python3
"""Continue original local building research; no architecture asset writes."""
import importlib.util
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]

def collect(value,result):
 if isinstance(value,dict):
  for key in ('member','source_member','complete_building_identity'):
   if isinstance(value.get(key),str):result.add(value[key])
  for v in value.values():collect(v,result)
 elif isinstance(value,list):
  for v in value:collect(v,result)

def main():
 previous=OUT.parent/'research-20261101-dungeons-001/inspect_batch.py'
 spec=importlib.util.spec_from_file_location('renderer',previous)
 renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
 renderer.OUT=OUT
 renderer.SELECTION=[
  ('ati_structures','*ATi*jar','https://www.curseforge.com/minecraft/mc-mods/ati-structures',[
   'desert_outpost','herobrine_stronghold','jungle_grotto','jungle_settlement',
   'overgrown_outpost','steam_house','storage_house','quarry']),
  ('trek','*远足*jar','https://modrinth.com/datapack/trek',[
   'overworld/medium/fort','overworld/medium/birch_fort','overworld/medium/ice_fort',
   'overworld/rare/pillager_mansion']),
 ]
 seen=set();indices=[]
 paths=[ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json']
 paths+=sorted((ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for name in ('sources.json','scope-expansion-sources.json','manual-review.json'):
   p=folder/name
   if p.is_file():paths.append(p)
 for p in paths:collect(json.loads(p.read_text()),seen);indices.append(str(p))
 selected=[f'data/{ns}/structures/{n}.nbt' for ns,_,_,names in renderer.SELECTION for n in names]
 assert len(selected)==len(set(selected))==12
 assert not set(selected)&seen
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(
  local_only=True,network_requests=0,java=False,game=False,formal_credit_added=0,
  selected_members=selected,previous_member_prefilter_count=len(seen),indices_checked=indices,
  prefilter_is_not_design_family_dedup=True,skill='find-skills applied; existing offline tools sufficient'),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
