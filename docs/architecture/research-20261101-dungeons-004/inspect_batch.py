#!/usr/bin/env python3
"""Fixed local urban-building sources; original templates, no new assets."""
import importlib.util
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]

def collect(v,result):
 if isinstance(v,dict):
  for k in ('member','source_member','complete_building_identity'):
   if isinstance(v.get(k),str): result.add(v[k])
  for child in v.values(): collect(child,result)
 elif isinstance(v,list):
  for child in v:collect(child,result)

def main():
 spec=importlib.util.spec_from_file_location('renderer',OUT.parent/'research-20261101-dungeons-001/inspect_batch.py')
 renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
 renderer.OUT=OUT
 renderer.SELECTION=[('ati_structures','*ATi*jar','https://www.curseforge.com/minecraft/mc-mods/ati-structures',[
  'tavern','villager_inn','old_home','old_residence','manor','marble_chateau','illager_homestead','storage_shack'])]
 seen=set();indices=[]
 paths=[ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json']
 paths+=sorted((ROOT/'docs/architecture/continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 for folder in sorted(OUT.parent.glob('research-*')):
  if folder==OUT:continue
  for name in ('sources.json','scope-expansion-sources.json','manual-review.json','acceptance-index.json'):
   p=folder/name
   if p.is_file():paths.append(p)
 for p in paths:collect(json.loads(p.read_text()),seen);indices.append(str(p))
 selected=[f'data/{ns}/structures/{n}.nbt' for ns,_,_,names in renderer.SELECTION for n in names]
 assert len(selected)==len(set(selected))==8 and not set(selected)&seen
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(local_only=True,network_requests=0,
  selected_members=selected,indices_checked=indices,previous_member_prefilter_count=len(seen),
  prefilter_is_not_semantic_dedup=True,skill='find-skills applied; installed offline tools sufficient',
  formal_credit_added=0,java=False,game=False),ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
