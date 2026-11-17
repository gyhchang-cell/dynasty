#!/usr/bin/env python3
"""Fresh rotated geometry audit, separating prior self-studies from other designs."""
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('dedup',OUT.parent/'research-20261101-dungeons-002/check_dedup.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
def main():
 m.main()
 p=OUT/'dedup-evidence.json';d=json.loads(p.read_text());sources=json.loads((OUT/'sources.json').read_text())
 for e,c in zip(d['entries'],sources['candidates']):
  assert e['id']==c['id']
  matches=e['historical_exact_matches']
  same=[v for v in matches if v['archive']==c['source_archive'] and v['member']==c['member']]
  assert len(same)==1
  e['prior_self_records_not_new_discovery']=same
  e['other_historical_exact_matches']=[v for v in matches if v not in same]
  assert not e['other_historical_exact_matches']
 d['prior_self_identities']=13
 d['other_historical_pairs_per_proposal']=d['historical_unique_local_archive_member_pairs']-1
 d['history_excluding_all_thirteen_reviewed_identities']=d['historical_unique_local_archive_member_pairs']-13
 d['formal_credit_added']=0
 d['scope_acceptance_not_implied']=True
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print('Separated thirteen prior self-studies from other exact matches; semantic scope review remains required.')
if __name__=='__main__':main()
