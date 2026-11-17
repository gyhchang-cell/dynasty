from pathlib import Path
import json,hashlib,re,zipfile,ast
B=Path(__file__).resolve().parent;R=B.parent;v=json.loads((B/'model-texture-review.json').read_text());checks=[]
def ck(n,b):checks.append(dict(check=n,passed=bool(b)));assert b,n
for x in json.loads((B/'asset-acquisition.json').read_text())['rows']:
 data=(B/x['local']).read_bytes();ck(x['path']+' fixed blob',hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==x['expected_blob']);ck(x['path']+' sha256',hashlib.sha256(data).hexdigest()==x['sha256'])
s={x['id']:x for x in v['sources']}
for x in s.values():
 p=B/x['local'];ck(x['id']+' bytes',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'])
 for a,b in x['reviewed_ranges']:ck(x['id']+f' range {a}-{b}',1<=a<=b<=len(p.read_bytes().splitlines()))
for x in v['evidence']:
 ck(x['id']+' zero',x['credit_added']==0)
 for ref in x['sources']:ck(x['id']+' ref '+ref,ref in s)
m=json.loads((B/'native-consumers.json').read_text());ck('Forge47.1.0 exact archive',hashlib.sha1((B/m['forge_source_archive']).read_bytes()).hexdigest()==m['forge_source_sha1']);ck('mapping fixed',hashlib.sha256(Path(m['mapping_cache']).read_bytes()).hexdigest()==m['mapping_sha256'])
fn=next(x for x in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
with zipfile.ZipFile(m['base_source_cache']) as z:
 for x in m['files']:
  raw=z.read(x['path']);ck(x['id']+' base',hashlib.sha256(raw).hexdigest()==x['base_entry_sha256']);patch=(B/x['patch']).read_text();data,hunks=ns['patch_exact'](raw.decode(),patch) if patch else ('\n'.join(raw.decode().splitlines())+'\n',0);ck(x['id']+' exact patch',data==(B/x['srg']).read_text() and hunks==x['patch_hunks']);ck(x['id']+' mapped',re.sub(r'\b[mf]_\d+_\b',lambda a:x['symbols'].get(a[0],a[0]),data)==(B/x['reading_view']).read_text())
t=json.loads((B/'conditional-override-trace.json').read_text());ck('256 unique condition rows',len({tuple(x['properties'].items()) for x in t['states']})==256);ck('hook always final winner',all(x['model']=='grapplemod:item/hook' for x in t['states'] if x['properties']['hook']));ck('not game/not production/no new reference',not v['java_game_started'] and not v['production_changed'] and v['new_source_families']==v['new_accepted_gate_credit']==0)
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='固定源/同版本Forge精确补丁/引用/条件回放，不是游戏烘焙或渲染检查',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
