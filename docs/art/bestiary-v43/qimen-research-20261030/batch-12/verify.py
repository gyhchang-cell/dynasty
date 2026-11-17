from pathlib import Path
import json,hashlib,ast,re,zipfile
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((B/'native-consumers.json').read_text());v=json.loads((B/'shader-position-review.json').read_text());checks=[]
def ck(name,value):checks.append(dict(check=name,passed=bool(value)));assert value,name
for e in v['sources']:
 p=B/e['local'];ck(e['id']+' hash',hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']);n=len(p.read_bytes().splitlines())
 for a,b in e['reviewed_ranges']:ck(e['id']+f' range {a}-{b}',1<=a<=b<=n)
ids={e['id'] for e in v['sources']}
for e in v['evidence']:
 ck(e['id']+' zero credit',e['credit_added']==0)
 for ref in e['sources']:ck(e['id']+' exists '+ref['source'],ref['source'] in ids)
ck('exact source archive',hashlib.sha1((B/m['source_archive']).read_bytes()).hexdigest()==m['source_sha1']);ck('exact mapping',hashlib.sha256(Path(m['mapping_cache']).read_bytes()).hexdigest()==m['mapping_sha256'])
fn=next(n for n in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
with zipfile.ZipFile(m['base_source_cache']) as z:
 for e in m['files']:
  raw=z.read(e['path']);ck(e['id']+' base bytes',hashlib.sha256(raw).hexdigest()==e['base_entry_sha256'])
  if e['patch']:data,hunks=ns['patch_exact'](raw.decode(),(B/e['patch']).read_text());ck(e['id']+' hunks',hunks==e['patch_hunks'])
  else:data='\n'.join(raw.decode().splitlines())+'\n'
  ck(e['id']+' exact reconstruction',data==(B/e['srg']).read_text());view=re.sub(r'\b[mf]_\d+_\b',lambda x:e['symbols'].get(x[0],x[0]),data);ck(e['id']+' reading view',view==(B/e['reading_view']).read_text())
links=json.loads((B/'task-item-node-links.json').read_text());ck('six real IDs',len(links['rows'])==6 and len({r['item'] for r in links['rows']})==6);ck('mapping no mutations',links['production_mutations'] is False);ck('no self credit',v['new_accepted_gate_credit']==0 and v['new_source_families']==0)
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='固定来源、精确patch、阅读范围和引用一致性；不验证运行Shader/网络/任务自然完成',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
