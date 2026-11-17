from pathlib import Path
import json,hashlib,re,ast,zipfile
B=Path(__file__).resolve().parent;R=B.parent;v=json.loads((B/'hit-save-review.json').read_text());checks=[]
def ck(n,b):checks.append(dict(check=n,passed=bool(b)));assert b,n
s={x['id']:x for x in v['sources']}
for x in s.values():
 p=B/x['local'];ck(x['id']+' SHA256',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);n=len(p.read_bytes().splitlines())
 for a,b in x['reviewed_ranges']:ck(x['id']+f' read {a}-{b}',1<=a<=b<=n)
for e in v['evidence']:
 ck(e['id']+' zero credit',e['credit_added']==0)
 for ref in e['sources']:
  ck(e['id']+' source '+ref['source'],ref['source'] in s)
  for a,b in ref['ranges']:ck(e['id']+f' range containment {ref["source"]} {a}-{b}',any(c<=a<=b<=d for c,d in s[ref['source']]['reviewed_ranges']))
fn=next(x for x in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
for batch,ids in [('batch-08',['AbstractArrow','Projectile']),('batch-09',['Entity'])]:
 m=json.loads((R/batch/('native-reconstruction.json' if batch=='batch-08' else 'native-source-manifest.json')).read_text())
 with zipfile.ZipFile(m['base_source_cache']) as z:
  for id in ids:
   f=next(x for x in m['files'] if x['version']=='forge-47.3.0' and x['path'].endswith('/'+id+'.java'));raw=z.read(f['path']);ck(id+' fixed base',hashlib.sha256(raw).hexdigest()==f['base_entry_sha256']);data,hunks=ns['patch_exact'](raw.decode(),(R/batch/f['patch']).read_text());ck(id+' exact Forge patch',data==(R/batch/f['srg']).read_text() and hunks==f['patch_hunks']);ck(id+' exact mapped view',re.sub(r'\b[mf]_\d+_\b',lambda x:f['symbols'].get(x[0],x[0]),data)==(B/s[id]['local']).read_text())
ck('not runtime/not production',not v['java_game_started'] and not v['production_changed']);ck('same family no credit',v['new_source_families']==v['new_accepted_gate_credit']==0)
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='固定内容、精确Forge重建、阅读范围与引用；不验证实际碰撞、事件、读档、燃烧或持物',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
