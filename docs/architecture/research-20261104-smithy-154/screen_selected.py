import json,hashlib,importlib.util
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
spec=importlib.util.spec_from_file_location('dedup',ROOT/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prefilter_path=ROOT/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';prefilter=json.loads(prefilter_path.read_text());fixed_index_path=ROOT/'docs/architecture/research-20261104-smithy-090/pre-render-current-fingerprint-screen.json';fixed_index=json.loads(fixed_index_path.read_text());history={}
indices=list(fixed_index['historical_indices'])+[str(p)for batch in range(90,154)for n in ['sources.json','manual-review.json']if (p:=ROOT/f'docs/architecture/research-20261104-smithy-{batch:03d}'/n).is_file()]
for p in indices:m.find_records(json.loads(Path(p).read_text()),p,history)
cached_path=ROOT/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json';cached=json.loads(cached_path.read_text());cache={(r['source']['archive'],r['source']['member']):r['fingerprints']for r in cached['entries']}
delta_path=ROOT/'docs/architecture/research-20261104-smithy-153/pre-render-history-screen.json';delta=json.loads(delta_path.read_text())
for r in delta['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
assert all(key in cache for key in history)
old=[(h,cache[key])for key,h in history.items()];selected=[];current=[]
(OUT/'history-cache-reuse.json').write_text(json.dumps({'cache_binding':bind(cached_path),'delta_binding':bind(delta_path),'cached_original_pairs':len(cached['entries']),'current_history_pairs':len(history),'prior_NBT_reopened':0,'semantic_credit':0},ensure_ascii=False,indent=2)+'\n')
for i,part in enumerate(['data/kaisyn/structures/village/badlands_pueblo/houses/badlands_mason_1.nbt'],1):
 a=next(a for a in prefilter['entries']if a['member'].endswith(part));jar=a['source_archive'];inventory_path=Path(prefilter['fixed_archive_inventory']['path']);inventory_bytes=inventory_path.read_bytes();assert hashlib.sha256(inventory_bytes).hexdigest()==prefilter['fixed_archive_inventory']['sha256'];inv=json.loads(inventory_bytes);prior=next(f for f in inv['archives']if f['path']==jar);fixed=bind(jar);assert fixed['sha256']==prior['sha256']
 aliases=[r['member']for r in prefilter['entries']if r['source_archive']==jar and r['nbt_sha256']==a['nbt_sha256']and r['member']!=a['member']];known=[h for h in history.values()if h['archive']==jar and h['member']in [a['member']]+aliases]
 d=m.load({'archive':jar,'member':a['member']});matches=[]
 for h,hd in old:
  keys=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==hd[k]]
  if keys:matches.append({'source':h,'exact_keys':keys})
 within=[{'source':n,'exact_keys':[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==dd[k]]}for n,dd in current if any(d[k]==dd[k]for k in ['nbt_sha256','role_sha256','occupancy_sha256'])]
 row={'current_source_fingerprints':{k:v for k,v in d.items()if k!='variants'},**a,'id':f'F{i:02d}','fixed_archive':fixed,'same_bytes_aliases':aliases,'known_history':known,'historical_exact_matches':matches,'within_batch_exact_matches':within,'eligible_for_new_source_study':not known and not matches and not within};selected.append(row);current.append((a['member'],d));print(row['id'],a['member'],'eligible',row['eligible_for_new_source_study'],'aliases',len(aliases))
(OUT/'pre-render-history-screen.json').write_text(json.dumps({'history_unique_archive_member_pairs':len(history),'historical_indices':indices,'prefilter_binding':bind(prefilter_path),'fixed_archive_index_binding':bind(inventory_path),'history_fixed_index_binding':bind(fixed_index_path),'rows':selected,'credit':0,'no_old_acceptance_rerun':True},ensure_ascii=False,indent=2)+'\n')
assert all(a['eligible_for_new_source_study']for a in selected)
