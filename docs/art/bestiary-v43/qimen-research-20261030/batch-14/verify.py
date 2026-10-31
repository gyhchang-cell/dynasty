from pathlib import Path
import json,hashlib,re,zipfile,ast
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((B/'framework-consumers.json').read_text());v=json.loads((B/'fluid-scroll-review.json').read_text());checks=[]
def ck(name,val):checks.append(dict(check=name,passed=bool(val)));assert val,name
s={x['id']:x for x in v['sources']}
for x in s.values():
 p=B/x['local'];ck(x['id']+' hash',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);length=len(p.read_bytes().splitlines())
 for a,b in x['reviewed_ranges']:ck(x['id']+f' reviewed {a}-{b}',1<=a<=b<=length)
for e in v['evidence']:
 ck(e['id']+' credit',e['credit_added']==0)
 for ref in e['sources']:
  ck(e['id']+' source '+ref['source'],ref['source'] in s)
  for a,b in ref['ranges']:ck(e['id']+f' actual range {ref["source"]} {a}-{b}',any(c<=a<=b<=d for c,d in s[ref['source']]['reviewed_ranges']))
archive=R/m['archive'];ck('Forge artifact SHA1',hashlib.sha1(archive.read_bytes()).hexdigest()==m['source_sha1']=='c5626b71a9e9c1f2f061ceeb2d8cb5cc961ee42a')
with zipfile.ZipFile(archive) as z:
 for x in m['files']:ck(x['id']+' exact archive entry',z.read(x['entry'])==(B/x['local']).read_bytes())
 n=json.loads((B/'native-consumer.json').read_text());ck('FriendlyByteBuf exact patch',z.read('patches/'+n['path']+'.patch')==(B/n['patch']).read_bytes())
a=json.loads((B/'message-acquisition.json').read_text());raw=(B/a['local']).read_bytes();ck('message fixed tree',hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==a['expected_blob']==a['git_blob_sha1'] and a['git_tree_match'])
fn=next(x for x in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
with zipfile.ZipFile(n['base_source_cache']) as z:
 raw=z.read(n['path']);ck('ByteBuf base bytes',hashlib.sha256(raw).hexdigest()==n['base_entry_sha256']);data,hunks=ns['patch_exact'](raw.decode(),(B/n['patch']).read_text());ck('ByteBuf exact reconstruction',data==(B/n['srg']).read_text() and hunks==n['patch_hunks']);ck('ByteBuf symbols',re.sub(r'\b[mf]_\d+_\b',lambda x:n['symbols'].get(x[0],x[0]),data)==(B/n['reading_view']).read_text())
ck('zero accepted/not runtime',v['new_source_families']==0 and v['new_accepted_gate_credit']==0 and not v['production_changed'] and not v['java_game_started'])
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='固定来源、精确框架条目、ByteBuf patch、范围包含；不运行输入、流体、网络或结算',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
