"""Exclude archive/member, same-byte alias and exact historical families BEFORE rendering."""
import json,hashlib,importlib.util
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
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
old=[(h,m.load(h))for h in history.values()]
previous=ROOT/'docs/architecture/research-20261104-smithy-090/pre-render-current-fingerprint-screen.json'
prefilter=json.loads(previous.read_text());fixed=next(a for a in prefilter['fixed_archives']if 'repurposed_structures-' in a['path']);assert bind(fixed['path'])==fixed
rows=[];current=[]
with ZipFile(fixed['path'])as z:
 hashes={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if '/structures/'in n and n.endswith('.nbt')}
 for basename in ['tool_smith_1','weapon_smith_1']:
  member=f'data/repurposed_structures/structures/villages/swamp/houses/{basename}.nbt';rawhash=hashes[member]
  prior=next(a for a in prefilter['rows']if a['source_archive']==fixed['path']and a['member']==member);assert rawhash==prior['nbt_sha256']
  aliases=[n for n,h in hashes.items()if h==rawhash and n!=member]
  known=[h for h in history.values()if h['archive']==fixed['path']and h['member']in [member]+aliases]
  d=m.load({'archive':fixed['path'],'member':member});matches=[]
  for h,hd in old:
   keys=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==hd[k]]
   if keys:matches.append({'source':h,'exact_keys':keys})
  within=[{'member':n,'exact_keys':[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==dd[k]]}for n,dd in current if any(d[k]==dd[k]for k in ['nbt_sha256','role_sha256','occupancy_sha256'])]
  eligible=not known and not matches and not within
  rows.append({'canonical_member':member,'same_bytes_aliases':aliases,'original_nbt_sha256':rawhash,'known_history':known,'exact_history_matches':matches,'within_batch_exact':within,'eligible_for_new_source_study':eligible,'credit':0})
  current.append((member,d));print(member,'eligible',eligible,'aliases',len(aliases),'history exact',len(matches))
obj={'fixed_archive':fixed,'history_unique_archive_member_pairs':len(history),'historical_indices':list(map(str,indices)),'rows':rows,'reused_prior_prefilter_binding':bind(previous),'purpose':'Current two selected input comparison only; no old acceptance or PNG rerun. No-exact is not semantic independence.','credit':0}
(OUT/'pre-render-history-screen.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
assert all(a['eligible_for_new_source_study']for a in rows)
print('HISTORY',len(history))
