import json,re,sys,hashlib,importlib.util,math
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
R=Path('/Users/a15356015027/Desktop/dynasty');P=R/'docs/architecture/research-20261104-smithy-285';P.mkdir(exist_ok=False);sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
sp=importlib.util.spec_from_file_location('dd',R/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
base=json.loads((R/'docs/architecture/research-20261104-smithy-282/additional-smith-history-screen.json').read_text());h={}
for n in base['historical_indices']+[str(R/'docs/architecture/research-20261104-smithy-282/bounded-source-audit.json'),str(R/'docs/architecture/research-20261104-smithy-282/additional-profession-components.json'),str(R/'docs/architecture/research-20261104-smithy-283/manual-review.json')]:m.find_records(json.loads(Path(n).read_text()),n,h)
meta=json.loads((R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json').read_text());selected=[]
for a in meta['entries']:
 n=a['member'];size=a['size']
 if (a['source_archive'],n)in h or '/houses/'not in n or '/zombie/'in n or '/professions' in n:continue
 if not(5<=min(size[0],size[2]) and math.prod(size)<=4500):continue
 if re.search('smith|forge|armorer|tannery|library|cartograph|church|temple|animal|farm|butcher|shepherd|fisher|mason|fletch',n,re.I):continue
 selected.append(a)
total_candidates=len(selected);selected=selected[60:180];inv=json.loads(Path(meta['fixed_archive_inventory']['path']).read_text());archives={};rows=[]
for a in selected:
 jar=a['source_archive']
 if jar not in archives:
  b=Path(jar).read_bytes();sha=hashlib.sha256(b).hexdigest();fixed=next(x for x in inv['archives']if x['path']==jar);assert sha==fixed['sha256'];archives[jar]={'sha256':sha,'zip':ZipFile(jar)}
 z=archives[jar]['zip'];bb=z.read(a['member']);assert hashlib.sha256(bb).hexdigest()==a['nbt_sha256'];d=read(bb);pal=d['palette'];co=Counter(pal[b['state']]['Name']for b in d['blocks']);devices={k:v for k,v in co.items()if any(t in k for t in ['furnace','anvil','smithing_table','grindstone','lava','stonecutter','cauldron','brewing_stand'])};flag=any('anvil'in k or 'blast_furnace'in k or 'smithing_table'in k for k in devices)or 'minecraft:grindstone'in devices
 rows.append({'source':a,'archive_sha256':archives[jar]['sha256'],'devices_machine_only':devices,'potential_smith_devices_not_qualification':flag,'no_semantic_whole_study':True})
 if flag:print('POTENTIAL',a['member'],a['size'],devices)
for a in archives.values():a['zip'].close()
(P/'bounded-anonymous-functional-screen.json').write_text(json.dumps({'selection':'positions60..179 fixed metadata order unseen archive/member /houses nonzombie nonoccupation, horizontal>=5, volume<=4500; not exhaustive','total_matching_candidates_before_slice':total_candidates,'historical_archive_member_pairs':len(h),'rows':rows,'machine_only_credit':0,'potential_count':sum(r['potential_smith_devices_not_qualification']for r in rows),'complete_whole_studies':0},ensure_ascii=False,indent=2)+'\n');(P/'screen_anonymous.py').write_text(Path('/tmp/dynasty-research284-screen.py').read_text());print('SCANNED',len(rows),'POTENTIAL',sum(r['potential_smith_devices_not_qualification']for r in rows))
