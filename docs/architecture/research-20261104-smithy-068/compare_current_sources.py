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
old=[(h,mod.load(h))for h in history.values()]
loosepath=ROOT/'docs/architecture/research-20261104-smithy-063/dedup-evidence.json';loose=json.loads(loosepath.read_text())['explicit_accepted_loose'];current=[];entries=[]
for c in json.loads((OUT/'sources.json').read_text())['candidates']:
 d=mod.load({'archive':c['source_archive'],'member':c['member']});current.append((c,d));matches=[];near=[]
 for h,hd in old:
  same=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==hd[k]]
  if same:matches.append({'source':h,'reasons':same})
  a=d['variants'][0];j=max(len(a&b)/len(a|b)for b in hd['variants']);near.append({'archive':h['archive'],'member':h['member'],'occupancy_jaccard':round(j,5)})
 lm=[]
 for h in loose:
  same=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if h.get(k)==d[k]]
  if same:lm.append({'source':h,'reasons':same})
 e={'id':c['id'],**{k:v for k,v in d.items()if k!='variants'},'historical_exact_matches':matches,'loose_exact_matches':lm,'nearest_occupancy_only':sorted(near,key=lambda x:-x['occupancy_jaccard'])[:5]};entries.append(e);print(e['id'],'exact',len(matches),'loose',len(lm),'nearest',e['nearest_occupancy_only'][:3])
pairs=[]
for i,(a,ad)in enumerate(current):
 for b,bd in current[i+1:]:pairs.append({'a':a['id'],'b':b['id'],'exact_keys':[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if ad[k]==bd[k]]})
r={'historical_indices_checked':list(map(str,indices)),'historical_unique_local_archive_member_pairs':len(old),'history_units':'Archive/member pairs include components and held studies; never semantic credit totals. Only current new input comparison, no historical acceptance rerun.','explicit_accepted_loose':loose,'loose_fingerprints_reused_from':str(loosepath),'entries':entries,'within_batch_pairs':pairs,'method':'Raw, role and occupancy hashes plus maximum four-rotation minimum-aligned occupancy Jaccard. Heuristic not semantic independence proof.','formal_credit_added':0};(OUT/'dedup-evidence.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('HISTORY',len(old))
