import json,importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
spec=importlib.util.spec_from_file_location('dedup',ROOT/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
ref=ROOT/'docs/architecture/continuation-20261022/references';indices=[ref/'full-buildings.json']+sorted(ref.glob('whole-candidates*/candidates.json'))
for f in sorted((ROOT/'docs/architecture').glob('research-*')):
 if f==OUT:continue
 for n in ['sources.json','scope-expansion-sources.json','manual-review.json']:
  if (f/n).is_file():indices.append(f/n)
history={}
for p in indices:mod.find_records(json.loads(p.read_text()),str(p),history)

import re,hashlib
from zipfile import ZipFile
metadata=ROOT/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';allentries=json.loads(metadata.read_text())['entries'];known={(a['archive'],a['member'])for a in history.values()}
new=[a for a in allentries if re.search('smith|forge|armorer',Path(a['member']).stem,re.I)and(a['source_archive'],a['member'])not in known]
old=[(a,mod.load(a))for a in history.values()];rows=[];archivebindings={};aliases={};fingerprints={}
for a in new:
 jar=a['source_archive'];member=a['member']
 if jar not in archivebindings:
  b=Path(jar).read_bytes();archivebindings[jar]={'path':jar,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
  with ZipFile(jar)as z:aliases[jar]={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.nbt')and '/structures/'in n}
 checkhash=aliases[jar][member];assert checkhash==a['nbt_sha256']
 samebytes=[n for n,h in aliases[jar].items()if h==checkhash and n!=member];historysamebytes=[h for h in history.values()if h['archive']==jar and h['member']in samebytes]
 d=mod.load({'archive':jar,'member':member});matches=[]
 for h,hd in old:
  same=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==hd[k]]
  if same:matches.append({'source':h,'exact_keys':same})
 within=[{'source':h,'exact_keys':[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==hd[k]]}for h,hd in fingerprints.values()if any(d[k]==hd[k]for k in ['nbt_sha256','role_sha256','occupancy_sha256'])]
 r={'source_archive':jar,'member':member,'size':a['size'],'nbt_sha256':checkhash,'same_bytes_aliases':samebytes,'alias_history_matches':historysamebytes,'historical_exact_matches':matches,'earlier_current_exact_matches':within,'role_sha256':d['role_sha256'],'occupancy_sha256':d['occupancy_sha256'],'credit':0,'actual_visual_reading':False}
 rows.append(r);fingerprints[(jar,member)]=({'archive':jar,'member':member},d)
obj={'fixed_metadata_binding':{'path':str(metadata),'sha256':hashlib.sha256(metadata.read_bytes()).hexdigest()},'history_unique_archive_member_pairs':len(history),'historical_indices':list(map(str,indices)),'fixed_archives':list(archivebindings.values()),'rows':rows,'candidates_screened':len(rows),'actual_visual_readings':0,'whole_reference_credit':0,'boundary':'Only current new keyword candidates fingerprinted against historical fingerprints, not old acceptance rerun; exact occupancy/role may be material variants, absence of match is NOT semantic independence. Misc stations/components/ruins still need whole relevance.'}
(OUT/'pre-render-current-fingerprint-screen.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('HISTORY',len(history),'CANDIDATES',len(rows),'OLD_EXACT',sum(bool(a['historical_exact_matches']or a['alias_history_matches'])for a in rows),'INTRABATCH_ONLY',sum(bool(a['earlier_current_exact_matches'])and not a['historical_exact_matches']and not a['alias_history_matches']for a in rows))
for a in rows:
 if not a['historical_exact_matches']and not a['earlier_current_exact_matches']and not a['alias_history_matches']:print('NO_EXACT_NOT_SEMANTIC',Path(a['source_archive']).name,a['member'],a['size'])
