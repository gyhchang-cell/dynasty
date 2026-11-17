#!/usr/bin/env python3
"""Compare research-only authored composite to old sources without new design credit."""
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 audit=module('audit',BASE/'research-20261101-dungeons-017/audit_sources.py');audit.OUT=OUT;audit.main()
 dd=module('dedup',BASE/'research-20261101-dungeons-002/check_dedup.py');dd.OUT=OUT
 original=dd.load;cache={}
 def cached(row):
  key=(row['archive'],row['member'])
  if key not in cache:cache[key]=original(row)
  return cache[key]
 dd.load=cached;dd.main()
 report=json.loads((OUT/'dedup-evidence.json').read_text());history={}
 for p in report['historical_indices_checked']:dd.find_records(json.loads(Path(p).read_text()),p,history)
 cells={tuple(e['position']):e['state']for e in json.loads((OUT/'assembly-original-states.json').read_text())['states']}
 current=dd.variants(cells)[0];nearest=[];matches=[]
 oh=dd.geometry_hash({p:1 for p in cells},[18,58,18]);rh=dd.geometry_hash({p:dd.role(s['Name'])for p,s in cells.items()},[18,58,18])
 for row in history.values():
  data=cached(row);same=[]
  if data['occupancy_sha256']==oh:same.append('occupancy_sha256')
  if data['role_sha256']==rh:same.append('role_sha256')
  if same:matches.append(dict(source_archive=row['archive'],member=row['member'],reasons=same))
  best=0.0
  for v in data['variants']:
   intersection=len(current&v);best=max(best,intersection/(len(current)+len(v)-intersection))
  nearest.append(dict(source_archive=row['archive'],member=row['member'],occupancy_jaccard=round(best,5)))
 (OUT/'assembly-dedup-evidence.json').write_text(json.dumps(dict(id='A01',historical_unique_archive_member_pairs=len(history),
  occupancy_sha256=oh,role_sha256=rh,historical_geometry_matches=matches,
  nearest_occupancy_only=sorted(nearest,key=lambda r:-r['occupancy_jaccard'])[:5],
  method='Four quarter-turn occupancy overlap, minima aligned, no scale matching; geometry heuristic only, never admission or design-novelty proof.',
  building_credit=0),ensure_ascii=False,indent=2)+'\n')
 print('Compared authored composite to',len(history),'prior archive/member identities; no automatic admission.')
if __name__=='__main__':main()
