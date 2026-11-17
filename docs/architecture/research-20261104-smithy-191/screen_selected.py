import json,hashlib,importlib.util
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
spec=importlib.util.spec_from_file_location('dedup',ROOT/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prefilter_path=ROOT/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';prefilter=json.loads(prefilter_path.read_text());fixed_index_path=ROOT/'docs/architecture/research-20261104-smithy-090/pre-render-current-fingerprint-screen.json';fixed_index=json.loads(fixed_index_path.read_text());history={}
indices=list(fixed_index['historical_indices'])+[str(p)for batch in range(90,191)for n in ['sources.json','manual-review.json']if (p:=ROOT/f'docs/architecture/research-20261104-smithy-{batch:03d}'/n).is_file()]
for p in indices:m.find_records(json.loads(Path(p).read_text()),p,history)
cached_path=ROOT/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json';cached=json.loads(cached_path.read_text());cache={(r['source']['archive'],r['source']['member']):r['fingerprints']for r in cached['entries']}
delta_path=ROOT/'docs/architecture/research-20261104-smithy-153/pre-render-history-screen.json';delta=json.loads(delta_path.read_text())
for r in delta['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
extra_path=ROOT/'docs/architecture/research-20261104-smithy-154/pre-render-history-screen.json'
for r in json.loads(extra_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
newest_path=ROOT/'docs/architecture/research-20261104-smithy-155/pre-render-history-screen.json'
for r in json.loads(newest_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
latest_path=ROOT/'docs/architecture/research-20261104-smithy-156/pre-render-history-screen.json'
for r in json.loads(latest_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
current_previous_path=ROOT/'docs/architecture/research-20261104-smithy-157/pre-render-history-screen.json'
for r in json.loads(current_previous_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta158_path=ROOT/'docs/architecture/research-20261104-smithy-158/pre-render-history-screen.json'
for r in json.loads(delta158_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta159_path=ROOT/'docs/architecture/research-20261104-smithy-159/pre-render-history-screen.json'
for r in json.loads(delta159_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta160_path=ROOT/'docs/architecture/research-20261104-smithy-160/pre-render-history-screen.json'
for r in json.loads(delta160_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta161_path=ROOT/'docs/architecture/research-20261104-smithy-161/pre-render-history-screen.json'
for r in json.loads(delta161_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta162_path=ROOT/'docs/architecture/research-20261104-smithy-162/pre-render-history-screen.json'
for r in json.loads(delta162_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta163_path=ROOT/'docs/architecture/research-20261104-smithy-163/pre-render-history-screen.json'
for r in json.loads(delta163_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta165_path=ROOT/'docs/architecture/research-20261104-smithy-165/pre-render-history-screen.json'
for r in json.loads(delta165_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta166_path=ROOT/'docs/architecture/research-20261104-smithy-166/pre-render-history-screen.json'
for r in json.loads(delta166_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta168_path=ROOT/'docs/architecture/research-20261104-smithy-168/pre-render-history-screen.json'
for r in json.loads(delta168_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta169_path=ROOT/'docs/architecture/research-20261104-smithy-169/pre-render-history-screen.json'
for r in json.loads(delta169_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta171_path=ROOT/'docs/architecture/research-20261104-smithy-171/pre-render-history-screen.json'
for r in json.loads(delta171_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta172_path=ROOT/'docs/architecture/research-20261104-smithy-172/pre-render-history-screen.json'
for r in json.loads(delta172_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta174_path=ROOT/'docs/architecture/research-20261104-smithy-174/pre-render-history-screen.json'
for r in json.loads(delta174_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta175_path=ROOT/'docs/architecture/research-20261104-smithy-175/pre-render-history-screen.json'
for r in json.loads(delta175_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta176_path=ROOT/'docs/architecture/research-20261104-smithy-176/pre-render-history-screen.json'
for r in json.loads(delta176_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta178_path=ROOT/'docs/architecture/research-20261104-smithy-178/pre-render-history-screen.json'
for r in json.loads(delta178_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta179_path=ROOT/'docs/architecture/research-20261104-smithy-179/pre-render-history-screen.json'
for r in json.loads(delta179_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta180_path=ROOT/'docs/architecture/research-20261104-smithy-180/pre-render-history-screen.json'
for r in json.loads(delta180_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta181_path=ROOT/'docs/architecture/research-20261104-smithy-181/pre-render-history-screen.json'
for r in json.loads(delta181_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta182_path=ROOT/'docs/architecture/research-20261104-smithy-182/pre-render-history-screen.json'
for r in json.loads(delta182_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta183_path=ROOT/'docs/architecture/research-20261104-smithy-183/pre-render-history-screen.json'
for r in json.loads(delta183_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta185_path=ROOT/'docs/architecture/research-20261104-smithy-185/pre-render-history-screen.json'
for r in json.loads(delta185_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta186_path=ROOT/'docs/architecture/research-20261104-smithy-186/pre-render-history-screen.json'
for r in json.loads(delta186_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta187_path=ROOT/'docs/architecture/research-20261104-smithy-187/pre-render-history-screen.json'
for r in json.loads(delta187_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta188_path=ROOT/'docs/architecture/research-20261104-smithy-188/pre-render-history-screen.json'
for r in json.loads(delta188_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta189_path=ROOT/'docs/architecture/research-20261104-smithy-189/pre-render-history-screen.json'
for r in json.loads(delta189_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
delta190_path=ROOT/'docs/architecture/research-20261104-smithy-190/pre-render-history-screen.json'
for r in json.loads(delta190_path.read_text())['rows']:cache[(r['source_archive'],r['member'])]=r['current_source_fingerprints']
assert all(key in cache for key in history)
old=[(h,cache[key])for key,h in history.items()];selected=[];current=[]
(OUT/'history-cache-reuse.json').write_text(json.dumps({'cache_binding':bind(cached_path),'delta_bindings':[bind(delta_path),bind(extra_path),bind(newest_path),bind(latest_path),bind(current_previous_path),bind(delta158_path),bind(delta159_path),bind(delta160_path),bind(delta161_path),bind(delta162_path),bind(delta163_path),bind(delta165_path),bind(delta166_path),bind(delta168_path),bind(delta169_path),bind(delta171_path),bind(delta172_path),bind(delta174_path),bind(delta175_path),bind(delta176_path),bind(delta178_path),bind(delta179_path),bind(delta180_path),bind(delta181_path),bind(delta182_path),bind(delta183_path),bind(delta185_path),bind(delta186_path),bind(delta187_path),bind(delta188_path),bind(delta189_path),bind(delta190_path)],'cached_original_pairs':len(cached['entries']),'current_history_pairs':len(history),'prior_NBT_reopened':0,'semantic_credit':0},ensure_ascii=False,indent=2)+'\n')
for i,part in enumerate(['data/repurposed_structures/structures/villages/warped/houses/weaponsmith_1.nbt', 'data/repurposed_structures/structures/villages/ocean/houses/masons_house_1.nbt', 'data/repurposed_structures/structures/villages/cherry/houses/armorer_house_2.nbt'],1):
 a=next(a for a in prefilter['entries']if a['member'].endswith(part));jar=a['source_archive'];inventory_path=Path(prefilter['fixed_archive_inventory']['path']);inventory_bytes=inventory_path.read_bytes();assert hashlib.sha256(inventory_bytes).hexdigest()==prefilter['fixed_archive_inventory']['sha256'];inv=json.loads(inventory_bytes);prior=next(f for f in inv['archives']if f['path']==jar);fixed=bind(jar);assert fixed['sha256']==prior['sha256']
 aliases=[r['member']for r in prefilter['entries']if r['source_archive']==jar and r['nbt_sha256']==a['nbt_sha256']and r['member']!=a['member']];known=[h for h in history.values()if h['archive']==jar and h['member']in [a['member']]+aliases]
 d=m.load({'archive':jar,'member':a['member']});matches=[]
 for h,hd in old:
  keys=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==hd[k]]
  if keys:matches.append({'source':h,'exact_keys':keys})
 within=[{'source':n,'exact_keys':[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==dd[k]]}for n,dd in current if any(d[k]==dd[k]for k in ['nbt_sha256','role_sha256','occupancy_sha256'])]
 row={'current_source_fingerprints':{k:v for k,v in d.items()if k!='variants'},**a,'id':f'F{i:02d}','fixed_archive':fixed,'same_bytes_aliases':aliases,'known_history':known,'historical_exact_matches':matches,'within_batch_exact_matches':within,'eligible_for_new_source_study':not known and not matches and not within};selected.append(row);current.append((a['member'],d));print(row['id'],a['member'],'eligible',row['eligible_for_new_source_study'],'aliases',len(aliases))
(OUT/'pre-render-history-screen.json').write_text(json.dumps({'history_unique_archive_member_pairs':len(history),'historical_indices':indices,'prefilter_binding':bind(prefilter_path),'fixed_archive_index_binding':bind(inventory_path),'history_fixed_index_binding':bind(fixed_index_path),'rows':selected,'credit':0,'no_old_acceptance_rerun':True},ensure_ascii=False,indent=2)+'\n')
# Eligibility false is retained as exclusion, not an exception or semantic credit.

