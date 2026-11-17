from pathlib import Path
import ast, hashlib, json, re, zipfile, datetime
from html.parser import HTMLParser
B=Path(__file__).resolve().parent
m=json.loads((B/'native-source-manifest.json').read_text())
r=json.loads((B/'ownership-lifecycle-review.json').read_text())
checks=[]
def check(name,condition):
 checks.append(dict(check=name,passed=bool(condition)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def covered(a,z,ranges):
 return all(any(x<=n<=y for x,y in ranges) for n in range(a,z+1))
# Extract only the pure exact-context patch function; do not execute the extraction module.
tree=ast.parse((B/'extract-selected-native.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch_exact')
namespace={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-function-only','exec'),namespace)
patch_exact=namespace['patch_exact']
check('mapping_hash',sha(Path(m['mapping_cache']))==m['mapping_sha256'])
forge=B/m['forge_source_archive']
check('official_forge_archive_sha1',hashlib.sha1(forge.read_bytes()).hexdigest()==m['forge_source_sha1'])
with zipfile.ZipFile(m['base_source_cache']) as base,zipfile.ZipFile(forge) as patches:
 for f in m['files']:
  label=f['id'];raw=base.read(f['path'])
  check(label+':base_entry_sha256',hashlib.sha256(raw).hexdigest()==f['base_entry_sha256'])
  data=raw.decode()
  if f['patch']:
   p=B/f['patch'];entry='patches/'+f['path']+'.patch'
   check(label+':official_patch_bytes',p.read_bytes()==patches.read(entry))
   data,hunks=patch_exact(data,p.read_text())
   check(label+':exact_patch_hunks',hunks==f['patch_hunks'])
  else:
   check(label+':no_omitted_forge_patch',f['version']!='forge-47.3.0' or 'patches/'+f['path']+'.patch' not in patches.namelist())
   data='\n'.join(data.splitlines())+'\n'
  check(label+':srg_reconstruction',(B/f['srg']).read_text()==data)
  view=re.sub(r'\b[mf]_\d+_\b',lambda x:f['symbols'].get(x[0],x[0]),data)
  check(label+':reading_view_reconstruction',(B/f['reading_view']).read_text()==view)
  for key in ['srg','reading_view']:
   check(label+':'+key+'_sha256',sha(B/f[key])==f[key+'_sha256'])
registry={s['id']:s for s in r['source_registry']}
check('unique_source_ids',len(registry)==len(r['source_registry']))
for s in registry.values():
 p=B/s['local'];lines=len(p.read_text().splitlines())
 check(s['id']+':review_source_hash',sha(p)==s['sha256'])
 check(s['id']+':review_line_bounds',lines==s['lines'] and all(1<=a<=z<=lines for a,z in s['reviewed_ranges']))
 if s['read_status']=='FULL_FILE_READ':check(s['id']+':full_read_exact',s['reviewed_ranges']==[[1,lines]])
 for origin in re.findall(r'(\.\./[^; ]+\.json)',s['provenance']):check(s['id']+':provenance_exists:'+origin,(B/origin).exists())
 if s['local'].startswith('../batch-08/'):
  old=json.loads((B/'../batch-08/native-reconstruction.json').read_text())
  candidates=[f for f in old['files'] if (B/'../batch-08'/f['reading_view']).resolve()==p.resolve()]
  check(s['id']+':matches_historical_manifest',len(candidates)==1 and candidates[0]['reading_view_sha256']==s['sha256'])
for e in r['evidence']:
 check(e['id']+':zero_reference_credit',e['independent_reference_credit']==0)
 for ref in e['support']:
  s=registry[ref['source']]
  check(e['id']+':reviewed_citation:'+s['id'],all(covered(a,z,s['reviewed_ranges']) for a,z in ref['ranges']))
ids={e['id'] for e in r['evidence']}
for t in r['state_traces']:
 check(t['id']+':evidence_exists',all(e in ids for e in t['evidence']))
 check(t['id']+':not_runtime',t['kind']=='CONDITIONAL_SOURCE_WALKTHROUGH_NOT_EXECUTED' and t['new_reference_credit']==0)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k=='href' and v:self.links.append(v)
p=Links();p.feed((B/'index.html').read_text())
for link in set(p.links):
 if '://' not in link and link!='local-verification.json':check('html_link:'+link,(B/link.split('#')[0]).exists())
root=json.loads((B.parent/'progress.json').read_text());progress=json.loads((B/'progress.json').read_text())
check('no_self_acceptance',root['this_batch']['new_accepted_gate_credit']==progress['new_accepted_gate_credit']==r['new_accepted_gate_credit']==0)
check('source_family_credit_unchanged',root['this_batch']['source_studies']==progress['new_source_studies']==0)
check('no_false_global_totals',r['global_accepted_totals'] is None and all(w['global_accepted_total'] is None and not w['gate_met'] for w in root['weapon_scopes']))
check('unread_entitytype_explicit',next(f for f in m['files'] if f['id']=='V-EntityType')['read_status']=='EXTRACTED_NOT_REVIEWED')
check('current_window_preserved',progress['deadline']=='2026-10-31T12:09:23+08:00' and root['continuation_window']['deadline']==progress['deadline'])
check('no_runtime_claim',not progress['production_changes'] and not progress['java_game_started'] and not progress['shared_jar_touched'] and not progress['publishing'])
result=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS' if all(x['passed'] for x in checks) else 'FAIL',checks_count=len(checks),checks=checks,source_variants=len(m['files']),reviewed_new_source_variants=sum(bool(f['reviewed_ranges']) for f in m['files']),exact_patch_hunks=sum(len(f['patch_hunks']) for f in m['files']),evidence=len(r['evidence']),conditional_traces=len(r['state_traces']),limitations='Local hash/range/provenance/link verification only. Not independent semantic acceptance, model/art validation, compilation or game test.',new_accepted_gate_credit=0)
(B/'local-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False))
print('FAILED',json.dumps([x for x in checks if not x['passed']],ensure_ascii=False))
raise SystemExit(0 if result['status']=='PASS' else 1)
