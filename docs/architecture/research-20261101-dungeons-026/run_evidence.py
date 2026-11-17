#!/usr/bin/env python3
"""Offline sections, source auditing and dedup for new screening candidates."""
import importlib.util
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 detail=module('detail',BASE/'research-20261101-dungeons-002/inspect_details.py')
 audit=module('audit',BASE/'research-20261101-dungeons-017/audit_sources.py')
 dedup=module('dedup',BASE/'research-20261101-dungeons-002/check_dedup.py')
 original_load=dedup.load;cache={}
 def cached(row):
  key=(row['archive'],row['member'])
  if key not in cache:cache[key]=original_load(row)
  return cache[key]
 dedup.load=cached
 specs={24:{'F01':(3,14,3,7),'F02':(1,3,7,5),'F03':(3,10,21,11)},
  25:{'F01':(12,28,13,12),'F02':(3,16,14,14),'F03':(3,16,14,14)}}
 for n in [24,25]:
  folder=BASE/f'research-20261101-dungeons-{n:03d}'
  detail.OUT=folder;detail.SPECS=specs[n];detail.main()
  audit.OUT=folder;audit.main()
  dedup.OUT=folder;dedup.main()
 folder=BASE/'research-20261101-dungeons-025'
 src=json.loads((folder/'sources.json').read_text())
 a=audit.load(src['candidates'][1])[1];b=audit.load(src['candidates'][2])[1];rows=[]
 for lo,hi in [(0,26),(0,10)]:
  left={p:s for p,s in a.items()if lo<=p[1]<=hi};right={p:s for p,s in b.items()if lo<=p[1]<=hi}
  common=left.keys()&right.keys();union=left.keys()|right.keys()
  rows.append(dict(y_band_inclusive=[lo,hi],left_nonair=len(left),right_nonair=len(right),common_positions=len(common),union_positions=len(union),
   occupancy_jaccard=len(common)/len(union),same_original_name_and_properties=sum(left[p]==right[p]for p in common)))
 (folder/'pair-evidence.json').write_text(json.dumps(dict(pair=['025-F02','025-F03'],measurements=rows,
  coordinate_transform='None; original axes.',automatic_credit=0,
  limits='Lower-band sameness is not whole-template equality. Damage states of one design are not additional independent buildings.'),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
