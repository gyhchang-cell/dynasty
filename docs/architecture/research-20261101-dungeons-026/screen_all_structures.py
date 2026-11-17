#!/usr/bin/env python3
"""Complement keyword search with size metadata of every fixed structure NBT."""
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 screen=BASE/'research-20261101-dungeons-024/fixed-source-screen.json'
 old=json.loads(screen.read_text());existing={(r['source_archive'],r['member']):r for r in old['entries']}
 rows=[];errors=[]
 for archive in old['archives']:
  jar=Path(archive['path']);assert sha(jar.read_bytes())==archive['sha256']
  with ZipFile(jar)as z:
   for member in z.namelist():
    if not(member.endswith('.nbt')and '/structures/'in member):continue
    previous=existing.get((str(jar),member));raw=z.read(member)
    row=dict(source_archive=str(jar),member=member,nbt_sha256=sha(raw),
     keyword_match=previous is not None,actual_visual_reading=False,building_credit=0)
    try:
     d=read(raw);size=d.get('size');blocks=d.get('blocks',[])
     if not size:row['status']='NO_SIZE'
     else:
      sx,sy,sz=size;scopes=[]
      if 29<=max(sx,sz)<=36 and 17<=sy<=30:scopes.append('GARRISON_SIZE_PREFILTER')
      if 15<=max(sx,sz)<=27 and 25<=sy<=53:scopes.append('WATCHPOST_SIZE_PREFILTER')
      if 24<=max(sx,sz)<=29 and 15<=min(sx,sz)<=17:scopes.append('HALL_SIZE_PREFILTER')
      row.update(size=size,size_prefilter_scopes=scopes,status='SIZE_MATCH_ONLY'if scopes else'OUTSIDE_CURRENT_SIZE_PREFILTER')
      if scopes:
       pal=d.get('palette')or d['palettes'][0]
       cells=[b for b in blocks if pal[b['state']]['Name']not in AIR]
       row.update(occupied_bounds=[[min(b['pos'][i]for b in cells),max(b['pos'][i]for b in cells)]for i in range(3)]if cells else None,
        jigsaw_count=sum(pal[b['state']]['Name']=='minecraft:jigsaw'for b in blocks),
        lower_doors=[dict(position=b['pos'],state=pal[b['state']])for b in blocks if pal[b['state']]['Name'].endswith('_door')and pal[b['state']].get('Properties',{}).get('half')=='lower'])
    except Exception as e:row.update(status='PARSE_ERROR',error=type(e).__name__+': '+str(e));errors.append(row.copy())
    rows.append(row)
 result=dict(fixed_archive_inventory=dict(path=str(screen),sha256=sha(screen.read_bytes())),entries=rows,errors=errors,
  archive_count=len(old['archives']),structure_members_enumerated=len(rows),all_structure_members_parsed=len(rows)-len(errors),
  newly_covered_keyword_negative_members=sum(not r['keyword_match']for r in rows),
  actual_visual_readings=0,building_credit_added=0,local_only=True,network_requests=0,java_run=False,game_run=False,
  limits='All stored /structures/*.nbt in the fixed 292 mods only. Metadata screening is not visual study or completeness/use/novelty certification. Excludes procedural Java structures, nested archives, other folders, screenshots and remote designs. No global source exhaustion claim.')
 (OUT/'all-structure-metadata.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('members',len(rows),'errors',len(errors),'keyword-negative',result['newly_covered_keyword_negative_members'])
 fresh=[r for r in rows if not r['keyword_match']and r.get('size_prefilter_scopes')]
 print('Additional size-only hits',len(fresh))
 print('Full rows saved in all-structure-metadata.json; no automatic visual or reference credit.')
if __name__=='__main__':main()
