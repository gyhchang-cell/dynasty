#!/usr/bin/env python3
"""Bounded offline filename/size screening, never building-reference credit."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent;ROOT=OUT.parents[2]
MODS=Path('/Users/a15356015027/Desktop/专业剪辑软件/虚饰作品 v1.3/overrides/mods')
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
PATTERN=re.compile(r'outpost|tower|fort|keep|garrison|barrack|watch|camp|castle|citadel|guard|stronghold|bastion',re.I)
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
 spec=importlib.util.spec_from_file_location('dedup',BASE/'research-20261101-dungeons-002/check_dedup.py')
 dd=importlib.util.module_from_spec(spec);spec.loader.exec_module(dd)
 indices=[dd.REF/'full-buildings.json']+sorted(dd.REF.glob('whole-candidates*/candidates.json'))
 for folder in sorted(BASE.glob('research-*')):
  if folder==OUT:continue
  for name in ['sources.json','scope-expansion-sources.json','manual-review.json']:
   p=folder/name
   if p.is_file():indices.append(p)
 history={}
 for p in indices:dd.find_records(json.loads(p.read_text()),str(p),history)
 archives=[];rows=[];errors=[]
 for jar in sorted(MODS.glob('*.jar')):
  with ZipFile(jar)as z:
   allnbt=[n for n in z.namelist()if n.endswith('.nbt')and '/structures/'in n]
   names=[n for n in allnbt if PATTERN.search(n)]
   archives.append(dict(path=str(jar),sha256=sha(jar.read_bytes()),structure_nbt_members=len(allnbt),keyword_matches=len(names)))
   for member in names:
    row=dict(source_archive=str(jar),member=member,previous_archive_member_identity=(str(jar),member)in history,
     filename_screen_only=True,actual_visual_reading=False,building_credit=0)
    if not row['previous_archive_member_identity']:
     raw=z.read(member)
     try:
      d=read(raw);pal=d.get('palette')or d.get('palettes',[[]])[0]
      sz=d.get('size');blocks=d.get('blocks',[])
      if not sz:row['status']='NO_STRUCTURE_SIZE'
      else:
       sx,sy,sz_=sz
       # These are bounds of the unchanged current scope definitions, not
       # a certificate of whole-building completeness, military use or novelty.
       scopes=[]
       if 29<=max(sx,sz_)<=36 and 17<=sy<=30:scopes.append('GARRISON_SIZE_PREFILTER')
       if 15<=max(sx,sz_)<=27 and 25<=sy<=53:scopes.append('WATCHPOST_SIZE_PREFILTER')
       if 24<=max(sx,sz_)<=29 and 15<=min(sx,sz_)<=17:scopes.append('HALL_SIZE_PREFILTER')
       row.update(size=sz,nbt_sha256=sha(raw),stored_blocks=len(blocks),
        jigsaw_count=sum(pal[b['state']]['Name']=='minecraft:jigsaw'for b in blocks),
        size_prefilter_scopes=scopes,status='SIZE_MATCH_REQUIRES_WHOLE_DESIGN_REVIEW'if scopes else'OUTSIDE_CURRENT_SIZE_PREFILTER',
        filename_screen_only=False)
     except Exception as e:row.update(status='PARSE_ERROR',error=type(e).__name__+': '+str(e));errors.append(row.copy())
    else:row['status']='PREVIOUS_IDENTITY_NOT_NEW'
    rows.append(row)
 dump('fixed-source-screen.json',dict(archives=archives,entries=rows,errors=errors,
  historical_indices=[dict(path=str(p),sha256=sha(p.read_bytes()))for p in indices],
  historical_unique_archive_member_pairs=len(history),
  method='Enumerate only this fixed mods directory. Parse previously unstudied structure filenames matching the recorded keyword regex; do not claim keyword-negative structures or procedural Java-generated buildings exhausted.',
  keyword_regex=PATTERN.pattern,archives_enumerated=len(archives),keyword_candidates=len(rows),
  newly_parsed=sum(not r['previous_archive_member_identity']for r in rows),actual_visual_readings=0,building_credit_added=0,
  local_only=True,network_requests=0,java_run=False,game_run=False,production_changes=0,checklist_deletions=0))
 counts=Counter(Path(r['source_archive']).name for r in rows if r.get('size_prefilter_scopes'))
 print('archives',len(archives),'keyword candidates',len(rows),'newly parsed',sum(not r['previous_archive_member_identity']for r in rows),'errors',len(errors))
 for name,c in counts.items():print(name,c)
 for r in rows:
  if r.get('size_prefilter_scopes'):print(Path(r['source_archive']).name,r['member'],r['size'],'jigsaws',r['jigsaw_count'],r['size_prefilter_scopes'])
if __name__=='__main__':main()
