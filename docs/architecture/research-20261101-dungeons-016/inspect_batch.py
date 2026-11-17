#!/usr/bin/env python3
"""Study five fixed-local TREK watchtower bodies; variants are not automatic credit."""
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 discovery=module('discovery',OUT.parent/'research-20261101-dungeons-004/inspect_batch.py')
 renderer=module('renderer',OUT.parent/'research-20261101-dungeons-001/inspect_batch.py');renderer.OUT=OUT
 names=['pillager_watchtower','pillager_watchtower_dark_forest','pillager_watchtower_mangrove','pillager_watchtower_swamp','pillager_watchtower_modern']
 renderer.SELECTION=[('minecraft','*远足*jar','https://modrinth.com/datapack/trek',['pillager_outpost/'+n for n in names])]
 paths=[OUT.parent/'continuation-20261022/references/full-buildings.json']+sorted((OUT.parent/'continuation-20261022/references').glob('whole-candidates*/candidates.json'))
 for f in sorted(OUT.parent.glob('research-*')):
  if f==OUT:continue
  for n in ('sources.json','scope-expansion-sources.json','manual-review.json'):
   if (f/n).is_file():paths.append(f/n)
 seen=set()
 for p in paths:discovery.collect(json.loads(p.read_text()),seen)
 members=['data/minecraft/structures/pillager_outpost/'+n+'.nbt' for n in names]
 assert len(set(members))==5 and not set(members)&seen
 renderer.main()
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(selected_members=members,indices_checked=[str(p) for p in paths],
  local_only=True,network_requests=0,java_run=False,game_run=False,formal_credit_added=0,
  limits='Five unstudied stored bodies, not five independent designs. Namespace minecraft is overridden by this fixed TREK JAR; not a claim of vanilla provenance. External feature plates are not assembled or credited.'),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
