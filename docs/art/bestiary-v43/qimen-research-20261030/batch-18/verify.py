from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
B=Path(__file__).resolve().parent;v=json.loads((B/'fifo-magazine-study.json').read_text());checks=[]
def ck(n,b):checks.append(dict(check=n,passed=bool(b)));assert b,n
m=json.loads((B/'selected-source-manifest.json').read_text());ck('fixed archive bytes',hashlib.sha256((B/m['archive']).read_bytes()).hexdigest()==m['archive_sha256'])
with zipfile.ZipFile(B/m['archive']) as z:
 for x in m['files']:
  data=(B/x['local']).read_bytes();ck(x['path']+' exact archive member',z.read(x['archive_entry'])==data);ck(x['path']+' checksum',hashlib.sha256(data).hexdigest()==x['sha256'])
s={x['id']:x for x in v['sources']};ck('unique source IDs',len(s)==len(v['sources']))
for x in s.values():
 p=B/x['local'];ck(x['id']+' source hash',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);lines=len(p.read_bytes().splitlines())
 for a,b in x['reviewed_ranges']:ck(x['id']+f' read {a}-{b}',1<=a<=b<=lines)
for x in v['evidence']:
 ck(x['id']+' zero accepted',x['credit_added']==0)
 for ref in x['sources']:
  ck(x['id']+' source '+ref['source'],ref['source'] in s)
  for a,b in ref['ranges']:ck(x['id']+f' containment {ref["source"]} {a}-{b}',any(c<=a<=b<=d for c,d in s[ref['source']]['reviewed_ranges']))
x=json.loads((B/'texture-inspection.json').read_text())
for p in x['pngs']:
 ck('PNG fixed '+p['path'],hashlib.sha256((B/p['path']).read_bytes()).hexdigest()==p['sha256']);ck('PNG16x16 '+p['path'],list(Image.open(B/p['path']).size)==p['size']==[16,16])
for m in x['models']:
 for p in m['actual_layers']:ck('JSON referenced PNG '+p,(B/p).is_file())
for p in v['actually_viewed']:Image.open(B/p).verify();ck('contact image '+p,True)
ck('not accepted/not production/not game',v['new_accepted_gate_credit']==v['human_creature_model_texture_reference_credit']==0 and not v['production_changed'] and not v['java_game_started'])
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),scope='固定归档、源范围、引用、实际PNG层，不执行Java/游戏或认证全局独立性',results=checks),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))
