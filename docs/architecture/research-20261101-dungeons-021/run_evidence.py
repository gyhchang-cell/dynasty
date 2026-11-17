#!/usr/bin/env python3
"""Audit old-source rereads and compare their geometry; never grant credit."""
import importlib.util
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent.parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
 audit=module('audit',BASE/'research-20261101-dungeons-017/audit_sources.py')
 dedup=module('dedup',BASE/'research-20261101-dungeons-002/check_dedup.py')
 original_load=dedup.load;cache={}
 def cached(row):
  key=(row['archive'],row['member'])
  if key not in cache:cache[key]=original_load(row)
  return cache[key]
 dedup.load=cached
 for n in [21,22,23]:
  folder=BASE/f'research-20261101-dungeons-{n:03d}'
  audit.OUT=folder;audit.main()
  dedup.OUT=folder;dedup.main()
  path=folder/'dedup-evidence.json';data=json.loads(path.read_text())
  data.update(new_source_templates=0,
   self_match_policy='Retain original archive/member self matches; these are rereads. No historical exact match is asserted absent. Novelty needs semantic comparison, not a fresh ID.',
   formal_credit_added=0)
  dump(path,data)
 folder=BASE/'research-20261101-dungeons-021'
 src=json.loads((folder/'sources.json').read_text())['candidates']
 cells={c['id']:audit.load(c)[1]for c in src}
 a,b=cells['T01'],cells['T02']
 pairs=[]
 for low,high in [(0,33),(17,26)]:
  left={p:s for p,s in a.items()if low<=p[1]<=high}
  right={p:s for p,s in b.items()if low<=p[1]<=high}
  common=left.keys()&right.keys();union=left.keys()|right.keys()
  pairs.append(dict(y_band_inclusive=[low,high],left_nonair=len(left),right_nonair=len(right),
   common_positions=len(common),union_positions=len(union),occupancy_jaccard=len(common)/len(union),
   same_original_name_and_properties=sum(left[p]==right[p]for p in common)))
 dump(folder/'pair-evidence.json',dict(pair=['013-F03','016-F05'],coordinate_transform='None; original stored axes. Full NBT state dictionaries compared, not just colours.',
  measurements=pairs,automatic_credit=0,
  limits='Occupancy overlap and original-state equality support visual comparison only. A band is not whole-template equality; geometry metrics neither prove design identity nor independent novelty.'))
if __name__=='__main__':main()
