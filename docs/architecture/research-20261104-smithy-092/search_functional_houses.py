"""New name-negative bounded functional source prefilter; NOT actual building study credit."""
import sys,json,re,hashlib,importlib.util
from pathlib import Path
from zipfile import ZipFile
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
spec=importlib.util.spec_from_file_location('dedup',ROOT/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ref=ROOT/'docs/architecture/continuation-20261022/references';indices=[ref/'full-buildings.json']+sorted(ref.glob('whole-candidates*/candidates.json'))
for p in sorted((ROOT/'docs/architecture').glob('research-*')):
 if p==OUT:continue
 for n in ['sources.json','scope-expansion-sources.json','manual-review.json']:
  if (p/n).is_file():indices.append(p/n)
history={}
for p in indices:m.find_records(json.loads(p.read_text()),str(p),history)
known={(h['archive'],h['member'])for h in history.values()}
meta=ROOT/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';entries=json.loads(meta.read_text())['entries'];groups=defaultdict(list)
for a in entries:
 n=a['member'];size=a.get('size',[])
 if (a['source_archive'],n)in known or re.search('smith|forge|armorer',Path(n).stem,re.I):continue
 if not re.search('house|cottage|workshop|building|merchant|trader',n,re.I):continue
 if re.search('/(rooms?|pieces?|parts?|floors?|bridges?)/',n,re.I):continue
 if len(size)!=3 or not(5<=size[0]<=50 and 4<=size[1]<=50 and 5<=size[2]<=50 and size[0]*size[1]*size[2]<=70000):continue
 groups[a['source_archive']].append(a)
primary={'minecraft:smithing_table','minecraft:grindstone','minecraft:blast_furnace','minecraft:anvil','minecraft:chipped_anvil','minecraft:damaged_anvil'}
rows=[];fixed=[];errors=[];scanned=0
for jar,candidates in groups.items():
 fixed.append(bind(jar))
 with ZipFile(jar)as z:
  for a in candidates:
   try:
    b=z.read(a['member']);h=hashlib.sha256(b).hexdigest();assert h==a['nbt_sha256'];d=read(b);pal=d.get('palette')or d['palettes'][0];counts=Counter(pal[x['state']]['Name']for x in d['blocks']);scanned+=1
    hits=primary&set(counts)
    if not hits and not ('minecraft:lava'in counts and ('minecraft:furnace'in counts or 'minecraft:lava_cauldron'in counts)):continue
    rows.append({'source_archive':jar,'member':a['member'],'nbt_sha256':h,'size':d['size'],'DataVersion':d['DataVersion'],'stored_records':len(d['blocks']),'functional_marker_counts':{n:counts[n]for n in sorted(hits|({'minecraft:lava','minecraft:furnace','minecraft:lava_cauldron'}&set(counts)))},'functional_positions':[{'pos':x['pos'],'state':pal[x['state']]}for x in d['blocks']if pal[x['state']]['Name']in primary],'original_entities_count':len(d.get('entities',[])),'actual_visual_reading':False,'whole_boundary_unproven':True,'semantic_credit':0})
   except Exception as e:errors.append({'member':a['member'],'archive':jar,'error':repr(e)})
obj={'fixed_metadata':bind(meta),'historical_indices':list(map(str,indices)),'history_unique_archive_member_pairs':len(history),'selection':'Only new historical-name-negative house/cottage/workshop/building/merchant/trader paths without room/part/floor/bridge path; x/z5..50,y4..50,volume<=70000. Actual functional block prefilter, not complete-building or semantic admission.','selected_metadata_candidates':sum(map(len,groups.values())),'source_bodies_machine_scanned_not_studied':scanned,'fixed_archives':fixed,'rows':rows,'errors':errors,'actual_visual_readings':0,'building_credit_added':0,'java_run':False,'all_local_sources_exhausted_claimed':False}
(OUT/'name-negative-functional-prefilter.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('NEW_MACHINE_SCAN',scanned,'archives',len(fixed),'marker candidates',len(rows),'errors',len(errors),'history',len(history))
for a in rows[:28]:print(Path(a['source_archive']).name,a['member'],a['size'],a['functional_marker_counts'])
