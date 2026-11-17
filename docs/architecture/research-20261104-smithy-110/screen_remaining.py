"""Supplement the fixed090 catalog with new090..109 fingerprints; zero semantic credit."""
import json,hashlib,importlib.util
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('dedup',ROOT/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
f=ROOT/'docs/architecture/research-20261104-smithy-090/pre-render-current-fingerprint-screen.json';pref=json.loads(f.read_text());hist={};bindings=[]
for i in range(90,110):
 p=ROOT/f'docs/architecture/research-20261104-smithy-{i:03d}/sources.json'
 if p.is_file():
  bindings.append(bind(p));m.find_records(json.loads(p.read_text()),str(p),hist)
old=[(h,m.load(h))for h in hist.values()];fixed=[];alias_maps={}
for a in pref['fixed_archives']:
 assert bind(a['path'])==a;fixed.append(a)
 with ZipFile(a['path'])as z:
  byhash={}
  for n in z.namelist():
   if '/structures/'in n and n.endswith('.nbt'):byhash.setdefault(hashlib.sha256(z.read(n)).hexdigest(),[]).append(n)
  alias_maps[a['path']]=byhash
rows=[]
for a in pref['rows']:
 aliases=alias_maps[a['source_archive']][a['nbt_sha256']];known=[h for h in hist.values()if h['archive']==a['source_archive']and h['member']in aliases]
 inherited=a['historical_exact_matches'];curmatches=[]
 for h,d in old:
  keys=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if d[k]==a[k]]
  if keys:curmatches.append({'source':h,'exact_keys':keys})
 priorcurrent=a['earlier_current_exact_matches']
 size=a['size'];tiny=min(size[0],size[2])<5 or size[1]<4
 explicit_component='/professions_misc/'in a['member'] or '/misc/'in a['member'] or '/chambers/'in a['member'];ruin='ruin'in a['member']
 status='KNOWN_SOURCE_OR_EXACT_ALIAS'if known else'EXACT_OLD_OR_NEW_FINGERPRINT'if inherited or curmatches else'EARLIER_CATALOG_EXACT_VARIANT'if priorcurrent else'UNREVIEWED_COMPONENT_OR_RUIN_NAME_BOUNDARY'if tiny or explicit_component or ruin else'UNREVIEWED_NONEXACT_FUNCTIONAL_CANDIDATE'
 rows.append({**a,'same_source_byte_members':aliases,'known_source_pairs_since090':known,'new_since090_exact_matches':curmatches,'remaining_status':status,'actual_visual_reading_in_this_batch':False,'whole_reference_study_complete_in_this_batch':False,'semantic_independence_proven':False,'formal_credit_added':0})
counts={s:sum(r['remaining_status']==s for r in rows)for s in sorted({r['remaining_status']for r in rows})}
put('catalog-supplement.json',{'original_prefilter':bind(f),'fixed_archives':fixed,'source_index_bindings_since090':bindings,'new_history_pairs_since090':len(hist),'rows':rows,'status_counts':counts,'actual_images_viewed':0,'complete_reference_studies':0,'formal_credit_added':0,'not_an_exhaustive_all_local_sources_claim':True,'method':'Reuse090 fixed raw/role/occupancy fingerprints and original old-history exclusions; compare only appended090..109 source fingerprints. Same-source byte aliases excluded first. Absence of exact match is not semantic admission. Name/size flags unreviewed, not actual complete-building judgments. No historical acceptance rerun.'})
print(json.dumps({'status_counts':counts,'unreviewed_nonexact':[{'member':r['member'],'size':r['size']}for r in rows if r['remaining_status']=='UNREVIEWED_NONEXACT_FUNCTIONAL_CANDIDATE'],'actual_visual_reading':0,'credit':0},ensure_ascii=False))
