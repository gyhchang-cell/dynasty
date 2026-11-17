from pathlib import Path
import json,hashlib,re,zipfile,ast
B=Path(__file__).resolve().parent;R=B.parent;v=json.loads((B/'input-consumer-review.json').read_text());checks=[]
def ck(n,b):checks.append(dict(check=n,passed=bool(b)));assert b,n
s={x['id']:x for x in v['sources']};ck('unique source IDs',len(s)==len(v['sources']))
for x in s.values():
 p=B/x['local'];ck(x['id']+' hash',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);n=len(p.read_bytes().splitlines())
 for a,b in x['reviewed_ranges']:ck(x['id']+f' read {a}-{b}',1<=a<=b<=n)
for e in v['evidence']:
 ck(e['id']+' zero',e['credit_added']==0)
 for ref in e['sources']:
  ck(e['id']+' ref '+ref['source'],ref['source'] in s)
  for a,b in ref['ranges']:ck(e['id']+f' containment {ref["source"]} {a}-{b}',any(c<=a<=b<=d for c,d in s[ref['source']]['reviewed_ranges']))
m=json.loads((B/'native-consumers.json').read_text());ck('exact Forge archive',hashlib.sha1((B/m['forge_source_archive']).read_bytes()).hexdigest()==m['forge_source_sha1']);ck('fixed mapping',hashlib.sha256(Path(m['mapping_cache']).read_bytes()).hexdigest()==m['mapping_sha256'])
fn=next(x for x in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
with zipfile.ZipFile(m['base_source_cache']) as z:
 for x in m['files']:
  raw=z.read(x['path']);ck(x['id']+' fixed base',hashlib.sha256(raw).hexdigest()==x['base_entry_sha256']);patch=(B/x['patch']).read_text();data,hunks=ns['patch_exact'](raw.decode(),patch) if patch else ('\n'.join(raw.decode().splitlines())+'\n',0);ck(x['id']+' exact patch',data==(B/x['srg']).read_text() and hunks==x['patch_hunks']);ck(x['id']+' mapped view',re.sub(r'\b[mf]_\d+_\b',lambda a:x['symbols'].get(a[0],a[0]),data)==(B/x['reading_view']).read_text())
with zipfile.ZipFile(B/m['forge_source_archive']) as z:
 for x in json.loads((B/'forge-helper-provenance.json').read_text())['files']:ck('official Forge helper '+x['entry'],z.read(x['entry'])==(B/x['local']).read_bytes())
ck('no game/no production/zero new credit',not v['java_game_started'] and not v['production_changed'] and v['new_source_studies']==v['new_accepted_gate_credit']==0)
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='精确Forge47.4.9源重建、范围与消费者引用；非运行/网络/统计验证',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
