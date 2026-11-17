from pathlib import Path
import json,hashlib,ast,re,zipfile
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((B/'acquisition.json').read_text());r=json.loads((B/'special-arrow-render-review.json').read_text());checks=[]
def ck(label,value):checks.append(dict(check=label,pass_=bool(value)));assert value,label
for s in r['sources']:
 p=(B/s['local']).resolve();ck(s['id']+' source hash',hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']);n=len(p.read_bytes().splitlines())
 for a,b in s['ranges']:ck(s['id']+f' actual range {a}-{b}',1<=a<=b<=n)
ids={s['id'] for s in r['sources']}
for e in r['evidence']:
 ck(e['id']+' zero credit',e['new_reference_credit']==0)
 for s in e['sources']:ck(e['id']+' source exists '+s['source'],s['source'] in ids)
ck('Neo source archive sha1',hashlib.sha1((B/m['source_archive']).read_bytes()).hexdigest()==m['source_sha1'])
ck('mapping hash',hashlib.sha256(Path(m['mapping_cache']).read_bytes()).hexdigest()==m['mapping_sha256'])
fn=next(n for n in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
with zipfile.ZipFile(m['base_source_cache']) as z:
 for e in m['native']:
  raw=z.read(e['path']);ck(e['id']+' base entry',hashlib.sha256(raw).hexdigest()==e['base_entry_sha256'])
  if e['patch']:data,hunks=ns['patch_exact'](raw.decode(),(B/e['patch']).read_text());ck(e['id']+' hunk receipt',hunks==e['patch_hunks'])
  else:data='\n'.join(raw.decode().splitlines())+'\n'
  ck(e['id']+' exact reconstructed bytes',data==(B/e['srg']).read_text());view=re.sub(r'\b[mf]_\d+_\b',lambda x:e['symbols'].get(x[0],x[0]),data);ck(e['id']+' mapped view',view==(B/e['reading_view']).read_text())
for e in m['mod_sources']:
 data=(B/e['local']).read_bytes();ck(e['id']+' pinned git blob',hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==e['git_blob_sha1'])
a=json.loads((B/'atlas-check.json').read_text());ck('PNG declaration',a['size']==a['declaration']);ck('96 bounded faces',len(a['faces'])==96 and all(f['in_bounds'] for f in a['faces']));ck('zero accepted / no production',r['new_accepted_gate_credit']==0 and not r['production_modified'])
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='来源hash、精确patch、阅读范围、UV和报告引用的一致性；不替代语义独立复核或运行验证',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
