from pathlib import Path
import ast,json,re,hashlib,zipfile,datetime
from html.parser import HTMLParser
B=Path(__file__).resolve().parent;m=json.loads((B/'acquisition.json').read_text());r=json.loads((B/'render-sync-review.json').read_text());checks=[]
def check(n,ok):checks.append(dict(check=n,passed=bool(ok)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
fn=next(n for n in ast.parse((B/'../batch-09/extract-selected-native.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
with zipfile.ZipFile(m['base_source_cache']) as base,zipfile.ZipFile(B/m['forge_source_archive']) as forge:
 check('forge_sha1',hashlib.sha1((B/m['forge_source_archive']).read_bytes()).hexdigest()==m['forge_source_sha1'])
 for f in m['files']:
  raw=base.read(f['path']);check(f['id']+':base_hash',hashlib.sha256(raw).hexdigest()==f['base_entry_sha256']);data=raw.decode()
  if f['patch']:
   pr=(B/f['patch']).read_bytes();check(f['id']+':patch_bytes',pr==forge.read('patches/'+f['path']+'.patch'));data,hunks=ns['patch_exact'](data,pr.decode());check(f['id']+':hunks',hunks==f['patch_hunks'])
  else:data='\n'.join(data.splitlines())+'\n'
  check(f['id']+':exact_srg',data==(B/f['srg']).read_text())
  view=re.sub(r'\b[mf]_\d+_\b',lambda x:f['symbols'].get(x[0],x[0]),data);check(f['id']+':exact_reading_view',view==(B/f['reading_view']).read_text())
  for k in ['srg','reading_view']:check(f['id']+':'+k+'_hash',sha(B/f[k])==f[k+'_sha256'])
registry={s['id']:s for s in r['source_registry']}
for s in registry.values():
 p=B/s['local'];check(s['id']+':hash',sha(p)==s['sha256']);check(s['id']+':ranges',all(1<=a<=z<=len(p.read_text().splitlines()) for a,z in s['reviewed_ranges']));check(s['id']+':provenance',(B/s['provenance']).exists())
for e in r['evidence']:
 for ref in e['support']:
  source=registry[ref['source']];check(e['id']+':citation:'+ref['source'],all(all(any(x<=i<=y for x,y in source['reviewed_ranges']) for i in range(a,z+1)) for a,z in ref['ranges']))
 check(e['id']+':zero_credit',e['independent_reference_credit']==0)
for a in m['assets']:
 data=(B/a['local']).read_bytes();check(a['path']+':blob',hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==a['git_blob_sha1']);check(a['path']+':sha256',hashlib.sha256(data).hexdigest()==a['sha256'])
sh=json.loads((B/'shader-provenance.json').read_text())
for f in sh['files']:check(f['entry']+':hash',sha(B/f['local'])==f['sha256'])
check('pinned_shader_artifact',sh['verified_client_sha1']==sh['official_client_download']['sha1'])
atlas=json.loads((B/'atlas-check.json').read_text())
for a in atlas['results']:check(a['texture']+':uv_dimensions',a['dimensions_match'] and a['all_cuboids_parsed'] and a['all_face_bounds_in_atlas']);check(a['texture']+':no_image_rewrite',sha(B/a['texture'])==a['texture_sha256'])
class Links(HTMLParser):
 def handle_starttag(self,t,attrs):
  for k,v in attrs:
   if k in ['href','src'] and v and '://' not in v and v!='local-verification.json':check('link:'+v,(B/v).exists())
Links().feed((B/'index.html').read_text())
check('no_art_or_gate_credit',r['new_accepted_gate_credit']==r['new_source_families']==0 and r['global_accepted_total'] is None)
result=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS' if all(x['passed'] for x in checks) else 'FAIL',checks_count=len(checks),native_variants=len(m['files']),exact_patch_hunks=sum(len(f['patch_hunks']) for f in m['files']),original_png_viewed=2,evidence=len(r['evidence']),new_credit=0,checks=checks,limitation='Static hash/patch/range/atlas/link consistency only; not independent semantic review, native client or GPU rendering.')
(B/'local-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False));print('FAILURES',[x for x in checks if not x['passed']]);raise SystemExit(result['status']!='PASS')
