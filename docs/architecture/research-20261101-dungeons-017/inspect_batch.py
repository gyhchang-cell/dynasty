#!/usr/bin/env python3
"""Fixed local full watchpost candidates. Source discovery is never credit."""
import hashlib
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
SELECTION=[('minecraft','*远足*jar','https://modrinth.com/datapack/trek',
 ['pillager_outpost/pillager_watchtower_forest','pillager_outpost/pillager_watchtower_medium']),
 ('trek','*远足*jar','https://modrinth.com/datapack/trek',
 ['overworld/medium/mangrove_watchtower_1','overworld/medium/mangrove_watchtower_2'])]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def exact_value(value,identifier):
 if isinstance(value,str):return value==identifier
 if isinstance(value,dict):return any(exact_value(v,identifier) for v in value.values())
 if isinstance(value,list):return any(exact_value(v,identifier) for v in value)
 return False
def main():
 discover=module('discover',BASE/'research-20261101-dungeons-004/inspect_batch.py')
 paths=[BASE/'continuation-20261022/references/full-buildings.json',*sorted(BASE.glob('continuation-20261022/references/whole-candidates*/candidates.json'))]
 for p in sorted(BASE.glob('research-*')):
  if p==OUT:continue
  paths.extend(p/n for n in ['sources.json','scope-expansion-sources.json','manual-review.json'] if (p/n).is_file())
 seen=set()
 for p in paths:discover.collect(json.loads(p.read_text()),seen)
 members=[f'data/{ns}/structures/{n}.nbt' for ns,_,_,names in SELECTION for n in names]
 assert len(members)==len(set(members)) and not set(members)&seen
 renderer=module('renderer',BASE/'research-20261101-dungeons-001/inspect_batch.py');renderer.OUT=OUT;renderer.SELECTION=SELECTION;renderer.main()
 # The older renderer's string-substring search can confuse a body identifier
 # with the same identifier plus "_ground". Keep only exact JSON string values.
 source=json.loads((OUT/'sources.json').read_text())
 for c in source['candidates']:
  prefix,tail=c['member'].split('/structures/',1);identifier=prefix.split('/')[-1]+':'+tail[:-4]
  c['pool_references']=[r for r in c['pool_references'] if exact_value(r['data'],identifier)]
 (OUT/'sources.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
 (OUT/'discovery-boundary.json').write_text(json.dumps(dict(selected_members=members,indices_checked=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],
  local_only=True,network_requests=0,java_run=False,game_run=False,formal_credit_added=0,prefilter_is_not_semantic_dedup=True),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
