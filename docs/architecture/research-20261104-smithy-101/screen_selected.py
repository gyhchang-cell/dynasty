import json,hashlib,importlib.util
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
spec=importlib.util.spec_from_file_location('dedup',ROOT/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prefilter_path=ROOT/'docs/architecture/research-20261104-smithy-097/broader-path-functional-prefilter.json';prefilter=json.loads(prefilter_path.read_text());history={}
indices=list(prefilter['historical_indices'])+[str(ROOT/f'docs/architecture/research-20261104-smithy-{batch}'/n)for batch in ['097','098','099','100']for n in ['sources.json','manual-review.json']]
for p in indices:m.find_records(json.loads(Path(p).read_text()),p,history)
old=[(h,m.load(h))for h in history.values()];selected=[];current=[]
for i,part in enumerate(['tour_desert_2.nbt','tour_2.nbt'],1):
 a=next(a for a in prefilter['rows']if a['member'].endswith(part));jar=a['source_archive'];fixed=next(f for f in prefilter['fixed_archives']if f['path']==jar);assert bind(jar)==fixed
 with ZipFile(jar)as z:hashes={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if '/structures/'in n and n.endswith('.nbt')}
 aliases=[n for n,h in hashes.items()if h==a['nbt_sha256']and n!=a['member']];known=[h for h in history.values()if h['archive']==jar and h['member']in [a['member']]+aliases]
 d=m.load({'archive':jar,'member':a['member']});matches=[]
 for h,hd in old:
  keys=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==hd[k]]
  if keys:matches.append({'source':h,'exact_keys':keys})
 within=[{'source':n,'exact_keys':[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==dd[k]]}for n,dd in current if any(d[k]==dd[k]for k in ['nbt_sha256','role_sha256','occupancy_sha256'])]
 row={**a,'id':f'F{i:02d}','fixed_archive':fixed,'same_bytes_aliases':aliases,'known_history':known,'historical_exact_matches':matches,'within_batch_exact_matches':within,'eligible_for_new_source_study':not known and not matches and not within};selected.append(row);current.append((a['member'],d));print(row['id'],a['member'],'eligible',row['eligible_for_new_source_study'],'aliases',len(aliases))
(OUT/'pre-render-history-screen.json').write_text(json.dumps({'history_unique_archive_member_pairs':len(history),'historical_indices':indices,'prefilter_binding':bind(prefilter_path),'rows':selected,'credit':0,'no_old_acceptance_rerun':True},ensure_ascii=False,indent=2)+'\n')
assert all(a['eligible_for_new_source_study']for a in selected)
