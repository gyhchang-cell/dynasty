#!/usr/bin/env python3
"""Selected room layers and full-state pair comparisons, no automatic credit."""
import importlib.util
import itertools
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 d=module('details',BASE/'research-20261101-dungeons-002/inspect_details.py');d.OUT=OUT
 d.SPECS={'F01':(12,25,13,13),'F02':(12,25,13,13),'F03':(12,25,13,13),'F04':(4,13,10,13)};d.main()
 a=module('audit',BASE/'research-20261101-dungeons-017/audit_sources.py');a.OUT=OUT;a.main()
 dd=module('dedup',BASE/'research-20261101-dungeons-002/check_dedup.py');dd.OUT=OUT;dd.main()
 src=json.loads((OUT/'sources.json').read_text());cells={c['id']:a.load(c)[1]for c in src['candidates']};pairs=[]
 for left,right in itertools.combinations(['F01','F02','F03'],2):
  ca,cb=cells[left],cells[right];common=ca.keys()&cb.keys();union=ca.keys()|cb.keys()
  differences=[dict(position=list(p),left=ca.get(p),right=cb.get(p))for p in sorted(union)if ca.get(p)!=cb.get(p)]
  pairs.append(dict(pair=[left,right],left_nonair=len(ca),right_nonair=len(cb),common_positions=len(common),union_positions=len(union),
   occupancy_jaccard=len(common)/len(union),same_original_name_and_properties=sum(ca[p]==cb[p]for p in common),
   differences=differences))
 (OUT/'pair-evidence.json').write_text(json.dumps(dict(pairs=pairs,coordinate_transform='None; original axes, names and properties.',automatic_credit=0,
  limits='Three spire variants are reviewed as at most one family. Inventory, mobs and furniture changes do not create independent buildings.'),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
